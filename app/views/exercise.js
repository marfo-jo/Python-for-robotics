// A graded code exercise: editor + Run + Submit (hidden pytest tests) +
// beginner error explanations + tiered hints + optional tutor.
// Used for lesson challenges, find-the-bug, projects, and No Hands checkpoints.
import { h, clear, button, toast } from "../ui.js";
import { createEditor } from "../editor.js";
import { runCode, runTests } from "../runner/runner.js";
import { explainError } from "../runner/explain.js";
import { openTutor } from "./tutor-panel.js";
import { ATTEMPTS_FOR_SOLUTION } from "../tutor/tutor.js";

export function renderOutput(box, res) {
  clear(box);
  if (res.packageErrors && res.packageErrors.length) {
    box.append(h("div", { class: "alert warn" },
      "A library failed to load in the browser: ", res.packageErrors.join("; "),
      ". If this lesson has local instructions, run it locally instead."));
  }
  if (res.stdout) box.append(h("div", { class: "panel-title" }, "Output"), h("pre", { class: "stdout" }, res.stdout));
  if (res.truncated) box.append(h("div", { class: "muted" }, "(output truncated)"));
  (res.figures || []).forEach((png) => box.append(h("img", { class: "figure", src: `data:image/png;base64,${png}`, alt: "Plot produced by your code" })));
  if (res.error) box.append(errorBlock(res.error));
  if (!res.stdout && !res.error && !(res.figures || []).length) box.append(h("div", { class: "muted" }, "(ran with no output)"));
}

export function errorBlock(error) {
  const ex = explainError(error);
  return h("div", { class: "error-block" },
    h("div", { class: "panel-title" }, "Error"),
    error.traceback ? h("pre", { class: "traceback" }, error.traceback) : h("pre", { class: "traceback" }, `${error.type}: ${error.message}`),
    h("details", { class: "explain", open: true },
      h("summary", {}, `What this means: ${ex.title}`),
      h("p", {}, ex.explain),
      h("p", {}, h("strong", {}, "Try: "), ex.tip),
      ex.lineno ? h("p", { class: "muted" }, `Python reported line ${ex.lineno}. It's highlighted in the editor.`) : null,
      h("details", {}, h("summary", {}, "How to read any traceback"), h("ol", {}, ex.guide.map((g) => h("li", {}, g))))));
}

function testResults(res) {
  const box = h("div", { class: "test-results" });
  if (res.error) { box.append(errorBlock(res.error)); return box; }
  if (res.collectErrors && res.collectErrors.length) {
    const msg = res.collectErrors.join("\n");
    const imp = /ImportError: cannot import name '(\w+)'/.exec(msg);
    box.append(h("div", { class: "alert bad" },
      imp ? `The tests couldn't find a function named ${imp[1]}. Define it with exactly that name.`
        : "Your code crashed before the tests could run. Click Run to see the error."),
    h("details", {}, h("summary", {}, "Details"), h("pre", { class: "traceback" }, msg)));
    return box;
  }
  const { passed, total } = res;
  box.append(h("div", { class: `alert ${res.ok ? "ok" : "bad"}` },
    res.ok ? `All ${total} tests passed.` : `${passed} of ${total} tests passed.`));
  box.append(h("ul", { class: "tests" }, (res.tests || []).map((t) =>
    h("li", { class: t.outcome },
      h("span", { class: "mark" }, t.outcome === "passed" ? "✓" : "✗"),
      h("span", {}, t.doc || t.name),
      t.message ? h("pre", { class: "test-msg" }, t.message) : null))));
  return box;
}

// opts: { title, starter, tests, testName, saved, onSave, onPass, onFail,
//         hints: [], hintTier, onHint, noHands, tutorCtx: () => ctx, attempts, onAttempt,
//         extraFiles, timeoutMs, lessonTitle }
export function renderExercise(parent, opts) {
  const host = h("div", { class: "exercise" });
  const editorHost = h("div", {});
  const out = h("div", { class: "output" });
  const results = h("div", {});
  const hintBox = h("div", { class: "hints" });
  let lastOutput = "";
  let lastFailedCode = null;
  let attempts = opts.attempts || 0;
  const attemptsLabel = h("span", { class: "muted" });

  const cm = createEditor(editorHost, {
    value: opts.saved ?? opts.starter,
    noPaste: opts.noHands,
    onChange: (v) => opts.onSave && opts.onSave(v),
    onRun: () => run(),
    onSubmit: () => submit(),
  });
  editorHost.addEventListener("paste-blocked", () =>
    toast("No Hands checkpoint: pasting is disabled. Type it yourself.", "warn"));

  function updateAttempts() {
    attemptsLabel.textContent = opts.noHands ? "" : `Real attempts: ${attempts}`;
  }

  async function run() {
    cm.markError(0);
    clear(out).append(h("div", { class: "muted" }, "Running…"));
    const res = await runCode(cm.getValue(), opts.timeoutMs);
    renderOutput(out, res);
    if (res.error) cm.markError(res.error.lineno);
    lastOutput = (res.stdout || "") + (res.error ? `\n${res.error.traceback || res.error.type + ": " + res.error.message}` : "");
  }

  async function submit() {
    cm.markError(0);
    clear(results).append(h("div", { class: "muted" }, "Running hidden tests…"));
    const code = cm.getValue();
    const res = await runTests(code, opts.tests, { testName: opts.testName, extraFiles: opts.extraFiles, timeoutMs: opts.timeoutMs });
    clear(results).append(testResults(res));
    if (res.error) cm.markError(res.error.lineno);
    const failing = (res.tests || []).filter((t) => t.outcome !== "passed")
      .map((t) => `FAILED: ${t.doc || t.name}\n${t.message}`).join("\n");
    lastOutput = res.error ? `${res.error.type}: ${res.error.message}` : failing || (res.collectErrors || []).join("\n");
    if (res.ok) {
      opts.onPass && opts.onPass(code);
    } else {
      // A "real" attempt is a failing submission with code that changed since the last one.
      if (code.trim() !== (opts.starter || "").trim() && code !== lastFailedCode) {
        attempts += 1;
        lastFailedCode = code;
        opts.onAttempt && opts.onAttempt(attempts);
        updateAttempts();
        renderSolutionGate();
      }
      opts.onFail && opts.onFail(res);
    }
  }

  function reset() {
    if (confirm("Reset the editor to the starter code? Your current code will be lost.")) cm.setValue(opts.starter);
  }

  function ctx(extra = {}) {
    return { ...(opts.tutorCtx ? opts.tutorCtx() : {}), code: cm.getValue(), output: lastOutput, attempts, ...extra };
  }

  // Tiered hints: each tier unlocks only after the previous one is revealed.
  let tier = opts.hintTier || 0;
  function renderHints() {
    clear(hintBox);
    const hints = opts.hints || [];
    if (!hints.length || opts.noHands) return;
    const names = ["Nudge", "Approach", "Pseudocode"];
    hints.slice(0, tier).forEach((text, i) => hintBox.append(h("div", { class: "hint" }, h("strong", {}, `${names[i] || "Hint"}: `), text)));
    if (tier < hints.length) {
      hintBox.append(button(`Show hint ${tier + 1}: ${names[tier] || "Hint"}`, () => {
        tier += 1;
        opts.onHint && opts.onHint(tier);
        renderHints();
      }, "btn subtle"));
    }
  }

  const solutionGate = h("div", {});
  function renderSolutionGate() {
    clear(solutionGate);
    if (opts.noHands || attempts < ATTEMPTS_FOR_SOLUTION) return;
    solutionGate.append(h("div", { class: "alert warn" },
      `You've made ${attempts} real attempts. You can ask the tutor for the full solution, but try the pseudocode hint and one more attempt first. Learning happens in the struggle.`,
      " ", button("Request full solution from tutor", () => {
        if (confirm("Ask the tutor for the full solution? You'll still need to type it and pass the tests.")) {
          openTutor("solution", ctx({ solutionRequested: true }));
        }
      }, "btn subtle")));
  }

  const tutorRow = opts.noHands ? h("div", { class: "alert info" }, "No Hands: tutor, hints, and pasting are disabled for this checkpoint.")
    : h("div", { class: "row tutor-row" },
      h("span", { class: "muted" }, "Tutor:"),
      button("Hint", () => openTutor("hint", ctx({ hintTier: Math.max(1, Math.min(3, tier || 1)) })), "btn subtle"),
      button("Explain my error", () => openTutor("error", ctx()), "btn subtle"),
      button("Grill me", () => openTutor("grill", ctx()), "btn subtle"));

  host.append(
    opts.title ? h("h3", {}, opts.title) : null,
    editorHost,
    h("div", { class: "row" },
      button("Run (Ctrl+Enter)", run, "btn"),
      button("Submit (Ctrl+Shift+Enter)", submit, "btn primary"),
      button("Reset", reset, "btn subtle"),
      attemptsLabel),
    out, results, hintBox, solutionGate, tutorRow);
  parent.append(host);
  updateAttempts();
  renderHints();
  renderSolutionGate();
  return { editor: cm, run, submit };
}
