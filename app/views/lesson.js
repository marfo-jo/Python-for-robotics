// Lesson page: prose with embedded worked examples, predict-the-output
// questions, interactive visuals, the graded challenge, find-the-bug, and
// explain-it-back, followed by the mastery checklist.
import { h, clear, button, toast } from "../ui.js";
import { renderInto } from "../md.js";
import { createEditor } from "../editor.js";
import { loadLesson, loadModule, loadText } from "../content.js";
import { runCode } from "../runner/runner.js";
import { VIZ } from "../viz/index.js";
import { renderExercise, renderOutput } from "./exercise.js";
import { openTutor } from "./tutor-panel.js";
import { tutorAvailable } from "../tutor/tutor.js";
import { refBlock } from "./reference.js";
import * as store from "../store.js";

// Reference tables an item declares ("refs": [...]) appear right next to it.
function refsFor(item) {
  const host = h("div", {});
  refBlock(item?.refs).then((block) => block && host.append(block));
  return host;
}

export async function renderLesson(root, curriculum, moduleId, lessonId) {
  const lesson = await loadLesson(moduleId, lessonId);
  const mod = lesson.module;
  const index = mod.lessons.indexOf(lessonId);
  if (!store.lessonUnlocked(curriculum, mod, index)) {
    root.append(h("div", { class: "card locked" }, h("h1", {}, `🔒 ${lesson.title}`),
      h("p", {}, "This lesson unlocks when you master the previous one. Mastery means: predictions attempted, challenge passed, bug fixed, and explanation done."),
      h("a", { href: `#/m/${moduleId}`, class: "btn" }, "Back to module")));
    return;
  }
  const rec = store.lessonRecord(lesson.id);
  const tutorCtx = () => ({ lessonTitle: lesson.title, objectives: lesson.objectives });

  const header = h("header", { class: "lesson-head" },
    h("div", { class: "crumbs" }, h("a", { href: `#/m/${moduleId}` }, mod.title), ` · Lesson ${index + 1} of ${mod.lessons.length}`),
    h("h1", {}, lesson.title),
    h("div", { class: "meta" }, `About ${lesson.minutes} minutes`),
    h("div", { class: "objectives" }, h("strong", {}, "You will be able to:"),
      h("ul", {}, lesson.objectives.map((o) => h("li", {}, o)))),
    lesson.whereYouSawThis ? h("div", { class: "where" }, h("strong", {}, "Where you saw this: "),
      `${lesson.whereYouSawThis.course}: ${lesson.whereYouSawThis.topic}`) : null);

  const body = h("article", { class: "lesson-body" });
  renderInto(body, lesson.md);
  const checklist = h("div", { class: "card mastery" });
  root.append(header, body, checklist);

  const refresh = () => renderChecklist(checklist, lesson, mod, moduleId, index);

  for (const slot of body.querySelectorAll(".embed")) {
    const kind = slot.dataset.embed;
    const id = slot.dataset.id;
    try {
      if (kind === "example") await embedExample(slot, lesson, id);
      else if (kind === "predict") embedPredict(slot, lesson, id, refresh);
      else if (kind === "viz") embedViz(slot, lesson, id);
      else if (kind === "challenge") await embedChallenge(slot, lesson, rec, tutorCtx, refresh);
      else if (kind === "bug") await embedBug(slot, lesson, rec, tutorCtx, refresh);
      else if (kind === "explain") await embedExplain(slot, lesson, rec, refresh);
      else if (kind === "ref") slot.append(await refBlock([id]));
      else slot.append(h("div", { class: "alert bad" }, `Unknown embed ${kind}`));
    } catch (err) {
      slot.append(h("div", { class: "alert bad" }, `Could not load ${kind}:${id}: ${err.message}`));
    }
  }
  refresh();
}

async function embedExample(slot, lesson, id) {
  const ex = lesson.examples.find((e) => e.id === id);
  const code = await loadText(`${lesson.base}/${ex.file}`);
  const out = h("div", { class: "output" });
  const host = h("div", {});
  slot.append(h("div", { class: "example" },
    h("div", { class: "example-title" }, ex.title || "Worked example"), host,
    h("div", { class: "row" }, button("Run example", async () => {
      clear(out).append(h("div", { class: "muted" }, "Running…"));
      renderOutput(out, await runCode(cm.getValue()));
    }), h("span", { class: "muted" }, "You can edit the example and re-run it. Experiment!")),
    out));
  const cm = createEditor(host, { value: code.trimEnd(), minLines: 2 });
}

function embedPredict(slot, lesson, id, refresh) {
  const p = lesson.predict.find((x) => x.id === id);
  const rec = store.lessonRecord(lesson.id);
  const host = h("div", {});
  const choices = h("div", { class: "choices", role: "radiogroup", "aria-label": "Your prediction" });
  const result = h("div", {});
  let picked = null;
  p.choices.forEach((c, i) => {
    const btn = h("button", { class: "choice mono", type: "button", role: "radio", "aria-checked": "false" }, c);
    btn.addEventListener("click", () => {
      if (rec.predict[p.id] !== undefined) return;
      picked = i;
      choices.querySelectorAll(".choice").forEach((b, k) => {
        b.classList.toggle("picked", k === i);
        b.setAttribute("aria-checked", k === i ? "true" : "false");
      });
    });
    choices.append(btn);
  });
  const lockBtn = button("Lock in my prediction", () => {
    if (picked === null) return toast("Pick an answer first. Commit before you run.");
    const correct = picked === p.answer;
    store.updateLesson(lesson.id, { predict: { ...rec.predict, [p.id]: correct } });
    if (!correct) store.reviewMiss(`${lesson.id}:${p.id}`, { kind: "predict", lessonId: lesson.id, itemId: p.id });
    store.recordActivity();
    reveal(picked);
    refresh();
  }, "btn primary");
  function reveal(choice) {
    lockBtn.remove();
    choices.querySelectorAll(".choice").forEach((b, k) => {
      b.disabled = true;
      if (k === p.answer) b.classList.add("correct");
      else if (k === choice) b.classList.add("wrong");
    });
    const correct = rec.predict[p.id];
    const runOut = h("div", { class: "output" });
    clear(result).append(
      h("div", { class: `alert ${correct ? "ok" : "bad"}` }, correct ? "Correct prediction." : "Not quite. This one goes into your review queue."),
      h("p", {}, p.why),
      h("div", { class: "row" }, button("Run it and see", async () => renderOutput(runOut, await runCode(p.code)))),
      runOut);
  }
  slot.append(h("div", { class: "predict" },
    h("div", { class: "example-title" }, "Predict the output"),
    p.question ? h("p", {}, p.question) : null, refsFor(p), host, choices, lockBtn, result));
  createEditor(host, { value: p.code.trimEnd(), readOnly: true, minLines: 1 });
  if (rec.predict[p.id] !== undefined) reveal(null);
}

function embedViz(slot, lesson, id) {
  const v = lesson.visualizations.find((x) => x.id === id);
  const render = VIZ[v.component];
  if (!render) throw new Error(`no visualization named ${v.component}`);
  const stage = h("div", { class: "viz-stage" });
  const wrap = h("figure", { class: "viz" }, v.title ? h("div", { class: "example-title" }, v.title) : null);
  const notice = v.notice ? h("figcaption", { class: "notice" }, h("strong", {}, "What to notice: "), v.notice) : null;
  // predictFirst: the code and inputs are always visible (the question is about
  // them). The component places the gate after its inputs and keeps only the
  // interactive part (step-through, split table, XOR stepper) hidden.
  let gate = null;
  let unlock = () => {};
  if (v.predictFirst) {
    const pf = v.predictFirst;
    const answer = h("textarea", { rows: 2, placeholder: "Write your prediction from the code above, then step through it…", "aria-label": "Your prediction" });
    gate = h("div", { class: "predict-first" },
      h("p", {}, h("strong", {}, "Predict first: "), pf.question), refsFor(pf), answer,
      button("I've predicted, show the visual", () => {
        if (answer.value.trim().length < 3) return toast("Write a prediction first, even a guess.");
        gate.replaceWith(h("div", { class: "alert info" }, h("strong", {}, "Your prediction: "), answer.value,
          pf.reveal ? h("div", {}, h("strong", {}, "Check: "), pf.reveal) : null));
        unlock();
        if (notice) notice.hidden = false;
      }, "btn primary"));
    if (notice) notice.hidden = true;
  }
  wrap.append(stage);
  if (notice) wrap.append(notice);
  slot.append(wrap);
  unlock = render(stage, v.props || {}, gate) || unlock;
}

async function embedChallenge(slot, lesson, rec, tutorCtx, refresh) {
  const ch = lesson.challenge;
  const [starter, tests] = await Promise.all([loadText(`${lesson.base}/${ch.starter}`), loadText(`${lesson.base}/${ch.tests}`)]);
  slot.append(refsFor(ch));
  if (rec.challengePassed) slot.append(h("div", { class: "alert ok" }, "✓ Challenge passed. You can keep experimenting."));
  renderExercise(slot, {
    starter, tests, testName: "test_challenge.py",
    saved: rec.code.challenge, onSave: (v) => store.saveCode(lesson.id, "challenge", v),
    hints: lesson.hints?.challenge, hintTier: rec.hintTier,
    onHint: (t) => store.updateLesson(lesson.id, { hintTier: t }),
    attempts: rec.attempts, onAttempt: (n) => store.updateLesson(lesson.id, { attempts: n }),
    timeoutMs: ch.timeLimitMs,
    tutorCtx: () => ({ ...tutorCtx(), task: ch.task }),
    onPass: () => {
      const first = !rec.challengePassed;
      store.updateLesson(lesson.id, { challengePassed: true });
      store.recordActivity();
      if (first) toast("Challenge passed! 🎉", "ok");
      refresh();
    },
  });
}

async function embedBug(slot, lesson, rec, tutorCtx, refresh) {
  const bug = lesson.bug;
  const [buggy, tests] = await Promise.all([loadText(`${lesson.base}/${bug.file}`), loadText(`${lesson.base}/${bug.tests}`)]);
  slot.append(h("div", { class: "bug-report" }, h("strong", {}, "🐞 Bug report: "), bug.report), refsFor(bug));
  if (rec.bugFixed) slot.append(h("div", { class: "alert ok" }, "✓ Bug fixed."));
  renderExercise(slot, {
    starter: buggy, tests, testName: "test_bug.py",
    saved: rec.code.bug, onSave: (v) => store.saveCode(lesson.id, "bug", v),
    hints: lesson.hints?.bug, hintTier: 0,
    tutorCtx: () => ({ ...tutorCtx(), task: `Find and fix the bug: ${bug.report}` }),
    onPass: () => {
      const first = !rec.bugFixed;
      store.updateLesson(lesson.id, { bugFixed: true });
      store.recordActivity();
      if (first) toast(`Bug squashed: ${bug.bugType}. 🐞`, "ok");
      refresh();
    },
  });
}

async function embedExplain(slot, lesson, rec, refresh) {
  const ex = lesson.explainBack;
  const MIN_WORDS = ex.minWords || 40;
  const text = h("textarea", { rows: 6, class: "explain-text", "aria-label": "Your explanation" });
  text.value = rec.explainText || "";
  const count = h("span", { class: "muted" });
  const status = h("div", {});
  const words = () => text.value.trim().split(/\s+/).filter(Boolean).length;
  const updateCount = () => { count.textContent = `${words()} / ${MIN_WORDS} words minimum`; };
  text.addEventListener("input", () => { updateCount(); store.updateLesson(lesson.id, { explainText: text.value }); });
  updateCount();

  const done = () => {
    store.updateLesson(lesson.id, { explainDone: true, explainText: text.value });
    store.recordActivity();
    clear(status).append(h("div", { class: "alert ok" }, "✓ Explanation accepted."));
    refresh();
  };
  const actions = h("div", {});
  const useTutor = await tutorAvailable();
  if (useTutor) {
    actions.append(button("Have the tutor grade it", () => {
      if (words() < MIN_WORDS) return toast(`Write at least ${MIN_WORDS} words.`);
      openTutor("explain", { lessonTitle: lesson.title, rubric: ex.rubric, explainText: text.value },
        { onReply: (reply) => { if (/VERDICT:\s*PASS/.test(reply)) done(); else toast("Not yet. Revise using the tutor's feedback and resubmit."); } });
    }, "btn primary"));
  } else {
    const boxes = ex.rubric.map((r) => h("label", { class: "check" }, h("input", { type: "checkbox" }), " ", r));
    actions.append(h("div", { class: "rubric" },
      h("p", {}, h("strong", {}, "Self-check rubric "), h("span", { class: "muted" }, "(tutor is off). Be honest: check an item only if your text clearly says it.")),
      boxes,
      button("Submit explanation", () => {
        if (words() < MIN_WORDS) return toast(`Write at least ${MIN_WORDS} words.`);
        if (!boxes.every((b) => b.querySelector("input").checked)) return toast("Revise until every rubric item is covered.");
        done();
      }, "btn primary")));
  }
  slot.append(h("div", { class: "explain-back" },
    h("div", { class: "example-title" }, "Explain it back"),
    h("p", {}, ex.prompt), refsFor(ex), text, count, actions, status));
  if (rec.explainDone) status.append(h("div", { class: "alert ok" }, "✓ Explanation accepted."));
}

async function renderChecklist(el, lesson, mod, moduleId, index) {
  const rec = store.lessonRecord(lesson.id);
  const predictDone = (lesson.predict || []).every((p) => rec.predict[p.id] !== undefined);
  const items = [
    ["Predictions attempted", predictDone],
    ["Challenge passed (hidden tests)", rec.challengePassed],
    ["Bug found and fixed", rec.bugFixed],
    ["Explained it back", rec.explainDone],
  ];
  const newlyMastered = store.markMasteredIfDone(lesson);
  if (newlyMastered) toast("Lesson mastered! Next lesson unlocked.", "ok");
  clear(el).append(h("h2", {}, "Mastery checklist"),
    h("ul", { class: "checklist" }, items.map(([label, ok]) => h("li", { class: ok ? "done" : "" }, ok ? "✓ " : "○ ", label))));
  if (rec.masteredAt) {
    const next = mod.lessons[index + 1];
    el.append(h("div", { class: "alert ok" }, "Mastered. ",
      next ? h("a", { href: `#/l/${moduleId}/${next}`, class: "btn primary" }, "Next lesson →")
        : h("a", { href: `#/quiz/${moduleId}`, class: "btn primary" }, "Take the module mastery quiz →")));
  }
}

export { loadModule };
