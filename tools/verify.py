"""Verify course content with real (local) Python before marking anything done.

Run from the repo root in the conda env:
    conda activate robotics-course
    python tools/verify.py                # everything
    python tools/verify.py m00.l03        # one lesson
    python tools/verify.py m00            # one module (lessons + quiz + project + no-hands)
    python tools/verify.py tracks         # track pages (sprints, C, interview)

For every lesson it checks:
  1. lesson.json has every required part (3+ worked examples, visual, predict,
     challenge, bug, explain-back with rubric, where-you-saw-this, 3 hint tiers)
     and lesson.md embeds every item.
  2. Each worked example runs and prints exactly its expectedOutput.
  3. Each predict question's correct choice equals the real output, and no
     other choice does.
  4. Hidden tests: the starter FAILS, the reference solution PASSES, and every
     known-wrong solution FAILS at least one test.
  5. Find-the-bug: the buggy file FAILS and the fixed reference PASSES.
  6. Tracer visuals run.

Reference and wrong solutions live in verification/ (a clone of the PRIVATE
answer-key repo, gitignored here). Without it, step 4/5 are skipped and the
run is reported as INCOMPLETE: a lesson can't be marked done that way.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
KEY = ROOT / "verification"
sys.path.insert(0, str(ROOT / "app" / "py"))

PY = sys.executable
EMBED_RE = re.compile(r"^\{\{\s*([a-z]+)(?::([\w.-]+))?\s*\}\}\s*$", re.M)


class Report:
    def __init__(self):
        self.rows = []
        self.failures = 0
        self.skipped = 0

    def ok(self, scope, what):
        self.rows.append(("PASS", scope, what))

    def fail(self, scope, what):
        self.rows.append(("FAIL", scope, what))
        self.failures += 1

    def skip(self, scope, what):
        self.rows.append(("SKIP", scope, what))
        self.skipped += 1

    def check(self, cond, scope, what):
        (self.ok if cond else self.fail)(scope, what)
        return cond


def run_script(code, cwd=None, timeout=20):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "solution.py"
        path.write_text(code, encoding="utf-8")
        env = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8")
        try:
            proc = subprocess.run([PY, str(path)], cwd=cwd or tmp, capture_output=True,
                                  text=True, timeout=timeout, env=env, encoding="utf-8")
        except subprocess.TimeoutExpired:
            return "", "TimeoutError"
        err = ""
        if proc.returncode != 0:
            last = [l for l in proc.stderr.strip().splitlines() if l.strip()]
            err = last[-1] if last else f"exit {proc.returncode}"
        return proc.stdout, err


def run_pytest(solution_code, test_code, test_name, extra_files=None, timeout=60):
    """Return (passed: bool, summary: str)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        (tmpd / "solution.py").write_text(solution_code, encoding="utf-8")
        (tmpd / test_name).write_text(test_code, encoding="utf-8")
        for rel, content in (extra_files or {}).items():
            dest = tmpd / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        # The simulator is importable in tests, exactly like in the browser.
        shutil.copy(ROOT / "app" / "py" / "pfr_sim.py", tmpd / "pfr_sim.py")
        env = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=line",
                                   "--color=no", test_name], cwd=tmp, capture_output=True,
                                  text=True, timeout=timeout, env=env, encoding="utf-8")
        except subprocess.TimeoutExpired:
            return False, "timeout"
        tail = [l for l in proc.stdout.strip().splitlines() if l.strip()]
        summary = tail[-1] if tail else proc.stderr.strip()[-200:]
        # "no tests ran" (exit 5) is a failure too.
        return proc.returncode == 0, summary


def read(path):
    return Path(path).read_text(encoding="utf-8")


def norm(text):
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


# --------------------------------------------------------------------- lessons

REQUIRED = ["id", "title", "minutes", "objectives", "skills", "whereYouSawThis", "examples",
            "predict", "visualizations", "challenge", "bug", "explainBack", "hints"]


def verify_lesson(rep, module_dir, lesson_dir, lesson_id):
    base = module_dir / lesson_dir
    scope = lesson_id
    try:
        meta = json.loads(read(base / "lesson.json"))
        md = read(base / "lesson.md")
    except Exception as exc:  # noqa: BLE001
        rep.fail(scope, f"cannot read lesson files: {exc}")
        return
    missing = [k for k in REQUIRED if k not in meta]
    if not rep.check(not missing, scope, f"lesson.json has required keys {'(missing: ' + ', '.join(missing) + ')' if missing else ''}"):
        return
    rep.check(meta["id"] == lesson_id, scope, f"id matches module.json ({meta['id']})")
    rep.check(len(meta["examples"]) >= 3, scope, f"{len(meta['examples'])} worked examples (need 3+)")
    rep.check(len(meta["visualizations"]) >= 1, scope, "has an interactive visualization")
    rep.check(len(meta["predict"]) >= 1, scope, f"{len(meta['predict'])} predict-the-output questions")
    rep.check(len(meta["hints"].get("challenge", [])) == 3, scope, "challenge has 3 hint tiers")
    rep.check(len(meta["explainBack"].get("rubric", [])) >= 2, scope, "explain-back has a rubric")
    wy = meta["whereYouSawThis"]
    rep.check(bool(wy.get("course")) and bool(wy.get("topic")), scope, "has 'Where you saw this'")

    embeds = {(k, i or "") for k, i in EMBED_RE.findall(md)}
    expected = ({("example", e["id"]) for e in meta["examples"]} |
                {("predict", p["id"]) for p in meta["predict"]} |
                {("viz", v["id"]) for v in meta["visualizations"]} |
                {("challenge", ""), ("bug", ""), ("explain", "")})
    rep.check(expected <= embeds, scope, f"lesson.md embeds every item {sorted(expected - embeds) or ''}")
    rep.check(embeds <= expected, scope, f"lesson.md has no unknown embeds {sorted(embeds - expected) or ''}")

    for ex in meta["examples"]:
        out, err = run_script(read(base / ex["file"]))
        exp = ex.get("expectedOutput")
        if exp is None:
            rep.fail(scope, f"example {ex['id']} has no expectedOutput")
        elif err:
            rep.fail(scope, f"example {ex['id']} crashed: {err}")
        else:
            rep.check(norm(out) == norm(exp), scope,
                      f"example {ex['id']} output matches" + ("" if norm(out) == norm(exp) else f" (got {out!r})"))

    for p in meta["predict"]:
        out, err = run_script(p["code"])
        actual = norm(out) if not err else err.split(":")[0].strip()
        if err and norm(out):
            actual = norm(out) + "\n" + err.split(":")[0].strip()
        choices = [norm(c) for c in p["choices"]]
        good = choices[p["answer"]] == actual
        others = [i for i, c in enumerate(choices) if c == actual and i != p["answer"]]
        rep.check(good and not others, scope,
                  f"predict {p['id']} answer matches real output" + ("" if good else f" (real: {actual!r})"))
        rep.check(len(set(choices)) == len(choices), scope, f"predict {p['id']} choices are distinct")

    for v in meta["visualizations"]:
        if v["component"] == "tracer":
            import pfr_harness  # noqa: PLC0415
            res = json.loads(pfr_harness.trace_user(v["props"]["code"]))
            ok = (res["error"] is None) or v["props"].get("expectError")
            rep.check(bool(ok) and res["steps"], scope, f"tracer {v['id']} runs ({len(res['steps'])} steps)")

    # Hidden tests
    ch = meta["challenge"]
    tests = read(base / ch["tests"])
    starter = read(base / ch["starter"])
    passed, summary = run_pytest(starter, tests, "test_challenge.py")
    rep.check(not passed, scope, f"challenge starter fails the tests ({summary})")
    key = KEY / lesson_id
    ref = key / "challenge.py"
    if not ref.exists():
        rep.skip(scope, "challenge reference missing in verification/ (answer key)")
    else:
        passed, summary = run_pytest(read(ref), tests, "test_challenge.py")
        rep.check(passed, scope, f"challenge reference passes ({summary})")
        wrongs = sorted(key.glob("wrong_*.py"))
        rep.check(len(wrongs) >= 2, scope, f"{len(wrongs)} known-wrong challenge solutions (need 2+)")
        for w in wrongs:
            passed, summary = run_pytest(read(w), tests, "test_challenge.py")
            rep.check(not passed, scope, f"{w.name} fails ({summary})")

    bug = meta["bug"]
    btests = read(base / bug["tests"])
    passed, summary = run_pytest(read(base / bug["file"]), btests, "test_bug.py")
    rep.check(not passed, scope, f"buggy file fails its tests ({summary})")
    fixed = key / "bug_fixed.py"
    if not fixed.exists():
        rep.skip(scope, "bug fix reference missing in verification/")
    else:
        passed, summary = run_pytest(read(fixed), btests, "test_bug.py")
        rep.check(passed, scope, f"bug fix reference passes ({summary})")


# --------------------------------------------------------------------- module extras

def verify_graded(rep, scope, base, cfg, key_prefix, test_name, extra_files=None):
    """Projects and No Hands checkpoints: starter fails, reference passes, wrongs fail."""
    tests = read(base / cfg["tests"])
    passed, summary = run_pytest(read(base / cfg["starter"]), tests, test_name, extra_files)
    rep.check(not passed, scope, f"starter fails ({summary})")
    ref = KEY / f"{key_prefix}.py"
    if not ref.exists():
        rep.skip(scope, f"reference {ref.name} missing in verification/")
        return
    passed, summary = run_pytest(read(ref), tests, test_name, extra_files)
    rep.check(passed, scope, f"reference passes ({summary})")
    wrongs = sorted(ref.parent.glob(f"{ref.stem}_wrong_*.py"))
    rep.check(len(wrongs) >= 2, scope, f"{len(wrongs)} known-wrong solutions (need 2+)")
    for w in wrongs:
        passed, summary = run_pytest(read(w), tests, test_name, extra_files)
        rep.check(not passed, scope, f"{w.name} fails ({summary})")


def verify_quiz(rep, scope, path):
    quiz = json.loads(read(path))
    pool = quiz["pool"]
    rep.check(len(pool) >= 2 * quiz["draw"] - 5, scope, f"quiz pool {len(pool)} for draw {quiz['draw']} (reshuffle needs a large pool)")
    rep.check(quiz.get("passPct") == 80, scope, "pass mark is 80%")
    ids = [q["id"] for q in pool]
    rep.check(len(ids) == len(set(ids)), scope, "quiz ids unique")
    for q in pool:
        good = 0 <= q["answer"] < len(q["choices"]) and len(set(q["choices"])) == len(q["choices"])
        rep.check(good, scope, f"quiz {q['id']} has a valid answer and distinct choices")
        if q.get("code") and q.get("checkOutput"):
            out, err = run_script(q["code"])
            actual = norm(out) if not err else err.split(":")[0].strip()
            rep.check(norm(q["choices"][q["answer"]]) == actual, scope,
                      f"quiz {q['id']} answer matches real output (real: {actual!r})")


def verify_module(rep, entry, only_lesson=None):
    module_dir = CONTENT / "modules" / entry["dir"]
    mod = json.loads(read(module_dir / "module.json"))
    for lid in mod["lessons"]:
        if only_lesson and lid != only_lesson:
            continue
        verify_lesson(rep, module_dir, mod["lessonDirs"][lid], lid)
    if only_lesson:
        return
    mid = entry["id"]
    if mod.get("quiz"):
        verify_quiz(rep, f"{mid}.quiz", module_dir / mod["quiz"])
    else:
        rep.fail(mid, "module has no mastery quiz")
    for name, prefix, test_name in [("project", "project", "test_project.py"), ("noHands", "nohands", "test_nohands.py")]:
        cfg = mod.get(name)
        if not cfg:
            rep.fail(mid, f"module has no {name}")
            continue
        extra = {dest: read(ROOT / src) for dest, src in cfg.get("dataFiles", {}).items()}
        verify_graded(rep, f"{mid}.{name}", module_dir, cfg, f"{mid}/{prefix}", test_name, extra)
    for key in ("robots", "cpp"):
        path = module_dir / mod.get("bridges", {}).get(key, "missing")
        rep.check(path.exists(), mid, f"Bridge box '{key}' present")


# --------------------------------------------------------------------- tracks

def verify_tracks(rep, curriculum):
    for track in curriculum["tracks"]:
        base = CONTENT / "tracks" / track["dir"]
        for page in track["pages"]:
            scope = f"track:{page['id']}"
            if page.get("status") == "planned":
                continue
            rep.check((base / page["file"]).exists(), scope, f"page file {page['file']} exists")
            if page.get("quiz"):
                data = json.loads(read(base / page["quiz"]))
                for q in data.get("items", []):
                    rep.check(0 <= q["answer"] < len(q["choices"]) and len(set(q["choices"])) == len(q["choices"]),
                              scope, f"quiz {q['id']} valid")
                for iq in data.get("interview", []):
                    rep.check(len(iq.get("rubric", [])) >= 2, scope, "interview question has a rubric")
            # Learner-facing test files for local/hardware milestones (pytest):
            for t in page.get("tests", []):
                test_path = ROOT / t["tests"]
                ref = KEY / "tracks" / page["id"] / t["reference"]
                if not test_path.exists():
                    rep.fail(scope, f"test file {t['tests']} missing")
                    continue
                if not ref.exists():
                    rep.skip(scope, f"reference for {t['tests']} missing in verification/")
                    continue
                verify_module_tests(rep, scope, test_path, ref, t)


def verify_module_tests(rep, scope, test_path, ref, t):
    """Sprint/local test files import a learner module by name (t['module'])."""
    name = t["module"]
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        shutil.copy(test_path, tmpd / test_path.name)
        for data in t.get("data", []):
            shutil.copy(ROOT / data, tmpd / Path(data).name)

        def run_with(code):
            (tmpd / f"{name}.py").write_text(code, encoding="utf-8")
            proc = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=line", "--color=no",
                                   test_path.name], cwd=tmp, capture_output=True, text=True, timeout=60,
                                  env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), encoding="utf-8")
            tail = [l for l in proc.stdout.strip().splitlines() if l.strip()]
            return proc.returncode == 0, (tail[-1] if tail else proc.stderr[-200:])

        passed, summary = run_with(read(ref))
        rep.check(passed, scope, f"{test_path.name}: reference passes ({summary})")
        wrongs = sorted(ref.parent.glob(f"{ref.stem}_wrong_*.py"))
        rep.check(len(wrongs) >= 2, scope, f"{test_path.name}: {len(wrongs)} known-wrong versions (need 2+)")
        for w in wrongs:
            passed, summary = run_with(read(w))
            rep.check(not passed, scope, f"{test_path.name}: {w.name} fails ({summary})")


# --------------------------------------------------------------------- main

def main(argv):
    target = argv[1] if len(argv) > 1 else "all"
    curriculum = json.loads(read(CONTENT / "curriculum.json"))
    rep = Report()
    if not KEY.exists():
        print("WARNING: verification/ (answer key) not found. Reference checks will be SKIPPED.\n")
    ready = [m for m in curriculum["modules"] if m["status"] == "ready"]
    for entry in ready:
        if target in ("all", entry["id"]):
            verify_module(rep, entry)
        elif target.startswith(entry["id"] + "."):
            verify_module(rep, entry, only_lesson=target)
    if target in ("all", "tracks"):
        verify_tracks(rep, curriculum)
    if target in ("all", "sim"):
        import pfr_harness  # noqa: PLC0415
        import pfr_sim  # noqa: PLC0415
        worlds = json.loads(read(CONTENT / "sim" / "worlds.json"))
        res = json.loads(pfr_harness.run_sim(read(CONTENT / "sim" / "starter_controller.py"),
                                             json.dumps(worlds["arena"]["world"]), 10, 1))
        rep.check(res["error"] is None and len(res["frames"]) > 0, "sim", "starter controller runs in the arena")
        for k, w in worlds.items():
            pfr_sim.World.from_dict(w["world"])
            rep.ok("sim", f"world '{k}' loads")

    width = max((len(r[1]) for r in rep.rows), default=10)
    for status, scope, what in rep.rows:
        if status != "PASS" or "-v" in argv:
            print(f"{status}  {scope.ljust(width)}  {what}")
    total = len(rep.rows)
    print(f"\n{total - rep.failures - rep.skipped} passed, {rep.failures} failed, {rep.skipped} skipped, of {total} checks.")
    if rep.failures:
        print("RESULT: FAIL")
        return 1
    if rep.skipped:
        print("RESULT: INCOMPLETE (answer-key checks skipped; nothing may be marked done)")
        return 2
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
