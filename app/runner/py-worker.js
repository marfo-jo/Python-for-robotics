// Pyodide runs here, off the main thread, so an infinite loop in learner code
// never freezes the page. The main thread kills and restarts this worker on
// timeout (see runner.js).
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

const PY_FILES = ["pfr_harness.py", "pfr_sim.py"];
let pyodide = null;
let harness = null;

async function init() {
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/",
  });
  pyodide.FS.mkdirTree("/home/pyodide/pfr");
  pyodide.FS.mkdirTree("/home/pyodide/work");
  for (const name of PY_FILES) {
    const src = await (await fetch(new URL(`../py/${name}`, import.meta.url))).text();
    pyodide.FS.writeFile(`/home/pyodide/pfr/${name}`, src);
  }
  pyodide.runPython("import sys; sys.path.insert(0, '/home/pyodide/pfr')");
  harness = pyodide.pyimport("pfr_harness");
}

// Load any packages the code imports (numpy, matplotlib, cv2...). If a package
// can't load, report it clearly instead of failing with a confusing error.
async function loadPackagesFor(...sources) {
  const failed = [];
  for (const src of sources) {
    if (!src) continue;
    try {
      await pyodide.loadPackagesFromImports(src, {
        errorCallback: (msg) => failed.push(msg),
        messageCallback: () => {},
      });
    } catch (err) {
      failed.push(String(err));
    }
  }
  return failed;
}

const handlers = {
  async init() {
    return { version: pyodide.version };
  },
  // Download packages before the timed run, so a slow first `import numpy`
  // isn't mistaken for an infinite loop.
  async prepare({ sources, needPytest }) {
    const errors = await loadPackagesFor(...sources);
    if (needPytest) await pyodide.loadPackage("pytest", { messageCallback: () => {} });
    return { errors };
  },
  async run({ code, extraFiles }) {
    const pkgErrors = await loadPackagesFor(code);
    const files = pyodide.toPy(extraFiles || {});
    const result = JSON.parse(harness.run_user(code, files));
    files.destroy();
    result.packageErrors = pkgErrors;
    return result;
  },
  async test({ code, tests, testName, extraFiles }) {
    const pkgErrors = await loadPackagesFor(code, tests);
    await pyodide.loadPackage("pytest", { messageCallback: () => {} });
    const files = pyodide.toPy(extraFiles || {});
    const result = JSON.parse(harness.run_tests(code, tests, testName || "test_hidden.py", files));
    files.destroy();
    result.packageErrors = pkgErrors;
    return result;
  },
  async trace({ code, maxSteps }) {
    await loadPackagesFor(code);
    return JSON.parse(harness.trace_user(code, maxSteps || 400));
  },
  async sim({ code, world, seconds, seed }) {
    await loadPackagesFor(code);
    return JSON.parse(harness.run_sim(code, JSON.stringify(world), seconds || 30, seed || 1));
  },
};

const ready = init();

self.onmessage = async (event) => {
  const { id, type, payload } = event.data;
  try {
    await ready;
    const result = await handlers[type](payload || {});
    self.postMessage({ id, ok: true, result });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String(err && err.message ? err.message : err) });
  }
};
