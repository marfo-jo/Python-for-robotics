"""Python-side support for the Python for Robotics site.

Runs inside Pyodide (browser) and also under normal CPython, so the same
behavior can be checked locally by tools/verify.py.

Public functions return JSON strings so the JS side never has to walk
Python objects.
"""
import builtins
import io
import json
import linecache
import os
import sys
import traceback
import types

os.environ.setdefault("MPLBACKEND", "Agg")
sys.dont_write_bytecode = True

USER_FILE = "solution.py"
MAX_OUTPUT = 100_000
WORK_DIR = os.environ.get("PFR_WORK_DIR", "/home/pyodide/work")


class _CappedWriter(io.StringIO):
    """StringIO that stops growing after MAX_OUTPUT characters."""

    def __init__(self):
        super().__init__()
        self.truncated = False

    def write(self, s):
        if self.tell() >= MAX_OUTPUT:
            self.truncated = True
            return len(s)
        return super().write(s)


def _no_input(prompt=""):
    raise RuntimeError(
        "input() is not available in the browser editor. "
        "Put your test values directly in variables instead."
    )


def _register_source(code, filename=USER_FILE):
    # Lets traceback show the learner's source lines for exec'd code.
    linecache.cache[filename] = (len(code), None, code.splitlines(True), filename)


def _error_info(exc, code):
    """Build a learner-facing error dict, keeping only frames from their file."""
    if isinstance(exc, SyntaxError):
        lineno = exc.lineno or 0
        text = (exc.text or "").rstrip("\n")
        stripped = text.lstrip()
        lines = [f'  File "{USER_FILE}", line {lineno}', f"    {stripped}"]
        if exc.offset and stripped:
            col = max(exc.offset - 1 - (len(text) - len(stripped)), 0)
            lines.append("    " + " " * col + "^")
        lines.append(f"{type(exc).__name__}: {exc.msg}")
        tb = "\n".join(lines)
        return {"type": type(exc).__name__, "message": exc.msg, "lineno": lineno,
                "traceback": tb}
    frames = [f for f in traceback.extract_tb(exc.__traceback__)
              if f.filename == USER_FILE]
    lineno = frames[-1].lineno if frames else 0
    lines = ["Traceback (most recent call last):"]
    for f in frames:
        lines.append(f'  File "{f.filename}", line {f.lineno}, in {f.name}')
        if f.line:
            lines.append(f"    {f.line}")
    lines.extend(traceback.format_exception_only(type(exc), exc)[-1:])
    return {"type": type(exc).__name__, "message": str(exc), "lineno": lineno,
            "traceback": "\n".join(l.rstrip("\n") for l in lines)}


def _collect_figures():
    if "matplotlib.pyplot" not in sys.modules:
        return []
    import base64
    plt = sys.modules["matplotlib.pyplot"]
    out = []
    for num in plt.get_fignums():
        buf = io.BytesIO()
        plt.figure(num).savefig(buf, format="png", dpi=100, bbox_inches="tight")
        out.append(base64.b64encode(buf.getvalue()).decode("ascii"))
    plt.close("all")
    return out


def _write_files(files):
    os.makedirs(WORK_DIR, exist_ok=True)
    for rel, content in (files or {}).items():
        path = os.path.join(WORK_DIR, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)


def run_user(code, files=None):
    """Execute learner code as a script. Returns JSON with stdout/error/figures.

    `files` (name -> text) are written to the working directory first, and the
    code runs there, so open("gps_log.txt") works exactly as in the tests.
    """
    _register_source(code)
    out = _CappedWriter()
    err = None
    _write_files(files)
    old_cwd = os.getcwd()
    old_out, old_input = sys.stdout, builtins.input
    sys.stdout, builtins.input = out, _no_input
    try:
        os.chdir(WORK_DIR)
        compiled = compile(code, USER_FILE, "exec")
        exec(compiled, {"__name__": "__main__", "__file__": USER_FILE})
    except SystemExit:
        pass
    except BaseException as exc:  # noqa: BLE001 - we report everything to the learner
        err = _error_info(exc, code)
    finally:
        os.chdir(old_cwd)
        sys.stdout, builtins.input = old_out, old_input
    figures = []
    try:
        figures = _collect_figures()
    except Exception:  # noqa: BLE001
        pass
    return json.dumps({"stdout": out.getvalue(), "truncated": out.truncated,
                       "error": err, "figures": figures})


# --------------------------------------------------------------------------
# Hidden tests (real pytest, same files as local verification)
# --------------------------------------------------------------------------

class _Collector:
    def __init__(self):
        self.docs = {}
        self.results = []
        self.collect_errors = []

    def pytest_collection_modifyitems(self, items):
        for item in items:
            doc = getattr(getattr(item, "obj", None), "__doc__", None)
            self.docs[item.nodeid] = (doc or "").strip().splitlines()[0] if doc else ""

    def pytest_collectreport(self, report):
        if report.failed:
            self.collect_errors.append(_short(report.longrepr))

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
            msg = ""
            if report.failed:
                crash = getattr(report.longrepr, "reprcrash", None)
                msg = crash.message if crash is not None else _short(report.longrepr)
            name = report.nodeid.split("::")[-1]
            self.results.append({"name": name, "doc": self.docs.get(report.nodeid, ""),
                                 "outcome": report.outcome, "message": msg})


def _short(longrepr, limit=1500):
    text = str(longrepr)
    return text[-limit:]


def run_tests(code, test_source, test_name="test_hidden.py", extra_files=None):
    """Run pytest on test_source against learner code saved as solution.py."""
    import pytest

    os.makedirs(WORK_DIR, exist_ok=True)
    with open(os.path.join(WORK_DIR, USER_FILE), "w", encoding="utf-8") as fh:
        fh.write(code)
    with open(os.path.join(WORK_DIR, test_name), "w", encoding="utf-8") as fh:
        fh.write(test_source)
    _write_files(extra_files)
    for mod in [m for m in sys.modules if m in ("solution", test_name[:-3])]:
        del sys.modules[mod]
    if WORK_DIR not in sys.path:
        sys.path.insert(0, WORK_DIR)
    _register_source(code)

    collector = _Collector()
    out = _CappedWriter()
    old_out, old_input = sys.stdout, builtins.input
    sys.stdout, builtins.input = out, _no_input
    old_cwd = os.getcwd()
    try:
        os.chdir(WORK_DIR)
        exit_code = pytest.main(
            [os.path.join(WORK_DIR, test_name), "-q", "-p", "no:cacheprovider",
             "--tb=short", "-rN", "--color=no"],
            plugins=[collector])
    finally:
        os.chdir(old_cwd)
        sys.stdout, builtins.input = old_out, old_input
    passed = sum(r["outcome"] == "passed" for r in collector.results)
    return json.dumps({
        "ok": int(exit_code) == 0 and not collector.collect_errors and passed > 0,
        "passed": passed,
        "total": len(collector.results),
        "tests": collector.results,
        "collectErrors": collector.collect_errors,
        "stdout": out.getvalue()[-5000:],
    })


# --------------------------------------------------------------------------
# Step-through tracer for the code-tracer visualization
# --------------------------------------------------------------------------

class _StopTrace(Exception):
    pass


def _safe_repr(value, limit=80):
    if isinstance(value, types.FunctionType):
        return f"<function {value.__name__}>"
    if isinstance(value, types.ModuleType):
        return f"<module {value.__name__}>"
    if isinstance(value, type):
        return f"<class {value.__name__}>"
    try:
        text = repr(value)
    except Exception:  # noqa: BLE001
        text = "<unprintable>"
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _snapshot(frame_locals):
    snap = {}
    for name, value in frame_locals.items():
        if name.startswith("__") or isinstance(value, types.ModuleType):
            continue
        snap[name] = {"repr": _safe_repr(value), "type": type(value).__name__}
    return snap


def trace_user(code, max_steps=400):
    """Record each executed line of learner code with variables and output."""
    _register_source(code)
    steps = []
    out = _CappedWriter()

    def local_tracer(frame, event, arg):
        if frame.f_code.co_filename != USER_FILE:
            return None
        if event in ("line", "return"):
            if len(steps) >= max_steps:
                raise _StopTrace()
            stack = []
            f = frame
            while f is not None and f.f_code.co_filename == USER_FILE:
                stack.append(f.f_code.co_name)
                f = f.f_back
            step = {"line": frame.f_lineno, "event": event,
                    "func": frame.f_code.co_name,
                    "stack": list(reversed(stack)),
                    "vars": _snapshot(frame.f_locals),
                    "out": out.getvalue()[-2000:]}
            if event == "return":
                step["returned"] = _safe_repr(arg)
            if frame.f_code.co_name != "<module>":
                step["globals"] = _snapshot({k: v for k, v in frame.f_globals.items()
                                             if not callable(v)})
            steps.append(step)
        return local_tracer

    def global_tracer(frame, event, arg):
        if frame.f_code.co_filename == USER_FILE:
            return local_tracer
        return None

    err = None
    truncated = False
    old_out, old_input = sys.stdout, builtins.input
    sys.stdout, builtins.input = out, _no_input
    try:
        compiled = compile(code, USER_FILE, "exec")
        sys.settrace(global_tracer)
        exec(compiled, {"__name__": "__main__", "__file__": USER_FILE})
    except _StopTrace:
        truncated = True
    except BaseException as exc:  # noqa: BLE001
        err = _error_info(exc, code)
    finally:
        sys.settrace(None)
        sys.stdout, builtins.input = old_out, old_input
    return json.dumps({"steps": steps, "error": err, "truncated": truncated,
                       "stdout": out.getvalue()})


# --------------------------------------------------------------------------
# Simulator bridge
# --------------------------------------------------------------------------

def run_sim(code, world_json, seconds=30.0, seed=1):
    """Run learner control code in the 2D simulator; return frames as JSON."""
    import pfr_sim

    _register_source(code)
    out = _CappedWriter()
    old_out, old_input = sys.stdout, builtins.input
    sys.stdout, builtins.input = out, _no_input
    err = None
    result = None
    try:
        ns = {"__name__": "__main__", "__file__": USER_FILE}
        exec(compile(code, USER_FILE, "exec"), ns)
        control = ns.get("control")
        if not callable(control):
            raise NameError("Define a function control(sensors, dt) that returns "
                            "(left_speed, right_speed).")
        world = pfr_sim.World.from_dict(json.loads(world_json))
        result = pfr_sim.run(world, control, seconds=seconds, seed=seed)
    except BaseException as exc:  # noqa: BLE001
        err = _error_info(exc, code)
    finally:
        sys.stdout, builtins.input = old_out, old_input
    payload = {"stdout": out.getvalue(), "error": err}
    if result is not None:
        payload.update(result.to_dict())
    return json.dumps(payload)
