// Step-through code tracer: shows which line runs next, the variables at that
// moment, and the output so far. Data comes from pfr_harness.trace_user.
// With a predict-first gate, the code stays visible and only the step-through
// (controls, note, panels) waits until the learner commits a prediction.
import { h, clear, button } from "../ui.js";
import { createEditor } from "../editor.js";
import { traceCode } from "../runner/runner.js";

export function renderTracer(el, { code, editable = false }, gate = null) {
  let steps = [];
  let index = 0;
  let timer = null;

  const editorHost = h("div", { class: "tracer-code" });
  const varsBox = h("div", { class: "tracer-vars", "aria-live": "polite" });
  const outBox = h("pre", { class: "tracer-out" });
  const counter = h("span", { class: "tracer-count" }, "not started");
  const slider = h("input", { type: "range", min: 0, max: 0, value: 0, "aria-label": "Step", disabled: true });
  const note = h("div", { class: "tracer-note" });

  const cm = createEditor(editorHost, { value: code.trimEnd(), readOnly: !editable, minLines: 3 });
  let activeLine = null;

  function show(i) {
    if (!steps.length) return;
    index = Math.max(0, Math.min(i, steps.length - 1));
    const step = steps[index];
    if (activeLine !== null) cm.removeLineClass(activeLine, "background", "cm-active-step");
    activeLine = step.line - 1;
    cm.addLineClass(activeLine, "background", "cm-active-step");
    cm.scrollIntoView({ line: activeLine, ch: 0 }, 60);
    slider.value = index;
    counter.textContent = `step ${index + 1} of ${steps.length}`;
    const lineText = cm.getLine(activeLine).trim();
    note.textContent = step.event === "return"
      ? `${step.func === "<module>" ? "Program finished" : `${step.func}() returns ${step.returned}`}`
      : `About to run line ${step.line}: ${lineText}`;
    clear(varsBox);
    if (step.stack.length > 1) {
      varsBox.append(h("div", { class: "tracer-stack" }, "Call stack: ", step.stack.join(" → ")));
    }
    const before = index > 0 ? steps[index - 1].vars : {};
    varsBox.append(varTable(step.func === "<module>" ? "Variables" : `Local variables in ${step.func}()`, step.vars, before));
    if (step.globals && Object.keys(step.globals).length) {
      varsBox.append(varTable("Global variables", step.globals, {}));
    }
    outBox.textContent = step.out || "";
  }

  function varTable(title, vars, before) {
    const names = Object.keys(vars);
    if (!names.length) return h("div", { class: "muted" }, `${title}: (none yet)`);
    return h("table", { class: "vars" },
      h("caption", {}, title),
      h("tr", {}, h("th", {}, "name"), h("th", {}, "value"), h("th", {}, "type")),
      names.map((n) => {
        const changed = !before[n] || before[n].repr !== vars[n].repr;
        return h("tr", { class: changed ? "changed" : "" },
          h("td", {}, n), h("td", {}, h("code", {}, vars[n].repr)), h("td", { class: "muted" }, vars[n].type));
      }));
  }

  async function load() {
    stop();
    counter.textContent = "tracing…";
    const res = await traceCode(cm.getValue());
    steps = res.steps || [];
    if (res.error && !steps.length) {
      counter.textContent = `error: ${res.error.type}: ${res.error.message}`;
      return;
    }
    slider.max = Math.max(steps.length - 1, 0);
    slider.disabled = false;
    show(0);
    if (res.error) note.textContent += `  (the program then stops with ${res.error.type}: ${res.error.message})`;
    if (res.truncated) note.textContent += "  (trace stopped after the step limit)";
  }

  function stop() {
    if (timer) clearInterval(timer);
    timer = null;
  }
  function play() {
    if (!steps.length) return;
    stop();
    timer = setInterval(() => {
      if (index >= steps.length - 1) return stop();
      show(index + 1);
    }, 700);
  }

  slider.addEventListener("input", () => show(Number(slider.value)));
  const stepper = h("div", { class: "tracer-stepper" },
    h("div", { class: "tracer-controls" },
      button("▶ Trace it", load, "btn primary"),
      button("⏮", () => show(0), "btn", { "aria-label": "First step" }),
      button("◀ Back", () => show(index - 1), "btn"),
      button("Step ▶", () => show(index + 1), "btn"),
      button("Play", play, "btn"),
      button("Pause", stop, "btn"),
      slider, counter),
    note,
    h("div", { class: "tracer-panels" },
      varsBox,
      h("div", {}, h("div", { class: "panel-title" }, "Output so far"), outBox)));
  if (gate) stepper.hidden = true;
  el.append(h("div", { class: "tracer" }, editorHost, gate, stepper));
  return () => { stepper.hidden = false; };
}
