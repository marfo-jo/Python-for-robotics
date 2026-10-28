// Main-thread API for running Python. One shared worker; requests are queued so
// a test run never interleaves with a trace. A request that runs too long kills
// the worker (the only way to stop a runaway `while True:`) and starts a fresh one.

const DEFAULT_TIMEOUT_MS = 8000;
const BOOT_TIMEOUT_MS = 120000;

let worker = null;
let booted = null;
let nextId = 1;
const pending = new Map();
let queue = Promise.resolve();
const statusListeners = new Set();
let status = "idle";

function setStatus(s) {
  status = s;
  statusListeners.forEach((fn) => fn(s));
}

export function onStatus(fn) {
  statusListeners.add(fn);
  fn(status);
  return () => statusListeners.delete(fn);
}

function startWorker() {
  worker = new Worker(new URL("./py-worker.js", import.meta.url), { type: "module" });
  worker.onmessage = (event) => {
    const { id, ok, result, error } = event.data;
    const entry = pending.get(id);
    if (!entry) return;
    pending.delete(id);
    clearTimeout(entry.timer);
    ok ? entry.resolve(result) : entry.reject(new Error(error));
  };
  worker.onerror = (event) => {
    for (const [, entry] of pending) {
      clearTimeout(entry.timer);
      entry.reject(new Error(event.message || "Python worker crashed"));
    }
    pending.clear();
  };
  setStatus("loading");
  booted = send("init", {}, BOOT_TIMEOUT_MS)
    .then((info) => { setStatus("ready"); return info; })
    .catch((err) => { setStatus("error"); throw err; });
}

function send(type, payload, timeoutMs) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    const timer = setTimeout(() => {
      pending.delete(id);
      restart();
      reject(Object.assign(new Error("timeout"), { timeout: true }));
    }, timeoutMs);
    pending.set(id, { resolve, reject, timer });
    worker.postMessage({ id, type, payload });
  });
}

function restart() {
  if (worker) worker.terminate();
  for (const [, entry] of pending) {
    clearTimeout(entry.timer);
    entry.reject(Object.assign(new Error("timeout"), { timeout: true }));
  }
  pending.clear();
  startWorker();
}

export function ensureBooted() {
  if (!worker) startWorker();
  return booted;
}

function timeoutError(ms) {
  return {
    type: "TimeoutError",
    message: `Your code ran for more than ${ms / 1000} seconds and was stopped.`,
    lineno: 0,
    traceback: "",
  };
}

// Every public call resolves (never rejects) with a result object, so UI code
// only has one shape to handle. Timeouts become a TimeoutError result.
function call(type, payload, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const job = queue.then(async () => {
    try {
      await ensureBooted();
    } catch (err) {
      return { stdout: "", error: { type: "LoadError", message: "Python failed to load. Check your internet connection and reload the page. (" + err.message + ")", lineno: 0, traceback: "" } };
    }
    setStatus("running");
    try {
      return await send(type, payload, timeoutMs);
    } catch (err) {
      if (err.timeout) return { stdout: "", error: timeoutError(timeoutMs), timedOut: true };
      return { stdout: "", error: { type: "InternalError", message: err.message, lineno: 0, traceback: "" } };
    } finally {
      if (status === "running") setStatus("ready");
    }
  });
  queue = job.catch(() => {});
  return job;
}

export const runCode = (code, timeoutMs) => call("run", { code }, timeoutMs);
export const runTests = (code, tests, opts = {}) =>
  call("test", { code, tests, testName: opts.testName, extraFiles: opts.extraFiles }, opts.timeoutMs || 15000);
export const traceCode = (code, maxSteps) => call("trace", { code, maxSteps }, 10000);
export const runSim = (code, world, seconds, seed) => call("sim", { code, world, seconds, seed }, 20000);
