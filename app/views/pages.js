// Dashboard, module overview, mastery quiz, review queue, tracks, simulator,
// project, No Hands checkpoint, and settings pages.
import { h, clear, button, toast, shuffle, download, section } from "../ui.js";
import { renderInto } from "../md.js";
import { createEditor } from "../editor.js";
import { loadModule, loadText, loadJSON, loadAllLessonMeta, findTrackPage } from "../content.js";
import { runSim } from "../runner/runner.js";
import { renderRadar } from "../viz/radar.js";
import { createSimView } from "../viz/sim-view.js";
import { renderExercise } from "./exercise.js";
import { openTutor } from "./tutor-panel.js";
import { tutorAvailable } from "../tutor/tutor.js";
import * as store from "../store.js";

// ------------------------------------------------------------ dashboard

export async function renderDashboard(root, curriculum) {
  const st = store.getState();
  const lessons = await loadAllLessonMeta();
  const next = await nextLesson(curriculum);
  const due = store.dueReviewItems().length;
  const today = store.dayKey();
  const week = (curriculum.roadmap || []).find((w) => w.start <= today && today <= w.end);

  root.append(h("h1", {}, "Python for Robotics"));
  root.append(h("div", { class: "grid two" },
    section("Today",
      h("p", { class: "streak" }, `🔥 Streak: ${store.currentStreak()} day(s)`, h("span", { class: "muted" }, `  (best ${st.streak.best || 0})`)),
      next ? h("p", {}, "Next lesson: ", h("a", { href: `#/l/${next.moduleId}/${next.id}` }, next.title)) : h("p", {}, "All available lessons mastered. Take the next module quiz!"),
      h("p", {}, h("a", { href: "#/review" }, `Review queue: ${due} due`)),
      h("div", { class: "row" },
        next ? h("a", { class: "btn primary", href: `#/l/${next.moduleId}/${next.id}` }, "Continue") : null,
        h("a", { class: "btn", href: "#/review?tired=1", title: "Review queue plus one small drill. Keeps your streak alive." }, "Tired day (30 min)")),
      week ? h("div", { class: "this-week" }, h("strong", {}, `This week (${week.label}): `), h("ul", {}, week.focus.map((f) => h("li", {}, f)))) : null),
    section("Skills radar", radarFor(curriculum, lessons),
      h("p", { class: "muted" }, "Grows as you master lessons. Each axis is measured against the full curriculum, so early on it should look small."))));

  const resume = store.resumeReadySkills(curriculum);
  root.append(section("Resume-ready skills",
    resume.length ? h("ul", {}, resume.map((s) => h("li", {}, s)))
      : h("p", { class: "muted" }, "Nothing yet. A skill appears here only after you pass its module's mastery quiz AND its No Hands checkpoint.")));

  root.append(section("Tracks",
    h("ul", { class: "tracklinks" }, curriculum.tracks.map((t) =>
      h("li", {}, h("a", { href: `#/t/${t.id}` }, t.title), h("span", { class: "muted" }, ` · ${t.summary}`))))));
}

function radarFor(curriculum, lessons) {
  const el = h("div", {});
  const pts = store.skillPoints(lessons);
  const values = {};
  for (const axis of curriculum.skillAxes) values[axis.id] = (pts[axis.id] || 0) / (axis.target || 1);
  renderRadar(el, curriculum.skillAxes, values);
  return el;
}

async function nextLesson(curriculum) {
  for (const entry of curriculum.modules.filter((m) => m.status === "ready")) {
    if (!store.moduleUnlocked(curriculum, entry.id)) continue;
    const mod = await loadModule(entry.id);
    for (const id of mod.lessons) {
      const rec = store.getState().lessons[id];
      if (!rec || !rec.masteredAt) {
        const meta = await loadJSON(`${mod.base}/${mod.lessonDirs[id]}/lesson.json`);
        return { ...meta, moduleId: entry.id };
      }
    }
  }
  return null;
}

// ------------------------------------------------------------ module page

export async function renderModule(root, curriculum, moduleId) {
  const mod = await loadModule(moduleId);
  root.append(h("h1", {}, mod.title));
  if (!mod.ready) {
    root.append(h("div", { class: "card" }, h("p", {}, mod.summary || ""), h("p", { class: "muted" }, `Coming soon. Planned for ${mod.planned || "a later session"}.`)));
    return;
  }
  const unlocked = store.moduleUnlocked(curriculum, moduleId);
  if (!unlocked) root.append(h("div", { class: "alert warn" }, "🔒 Locked: pass the previous module's mastery quiz (80%) to unlock."));
  root.append(h("p", {}, mod.summary));
  const lessonList = h("ol", { class: "lesson-list" });
  let allMastered = true;
  for (const [i, id] of mod.lessons.entries()) {
    const meta = await loadJSON(`${mod.base}/${mod.lessonDirs[id]}/lesson.json`);
    const rec = store.getState().lessons[id];
    const mastered = Boolean(rec && rec.masteredAt);
    if (!mastered) allMastered = false;
    const open = store.lessonUnlocked(curriculum, mod, i);
    lessonList.append(h("li", { class: mastered ? "mastered" : open ? "open" : "locked" },
      h("span", { class: "state" }, mastered ? "✓" : open ? "○" : "🔒"),
      open ? h("a", { href: `#/l/${moduleId}/${id}` }, meta.title) : h("span", {}, meta.title),
      h("span", { class: "muted" }, ` · ${meta.minutes} min`)));
  }
  const quiz = store.getState().quizzes[moduleId];
  root.append(section("Lessons", lessonList));
  root.append(section("Prove mastery",
    h("ul", { class: "checklist" },
      h("li", {}, allMastered ? h("a", { href: `#/quiz/${moduleId}` }, "Mastery quiz") : "🔒 Mastery quiz (master every lesson first)",
        quiz ? h("span", { class: "muted" }, ` · best ${quiz.best}%${quiz.passed ? " ✓ passed" : ""}`) : null),
      mod.noHands ? h("li", {}, allMastered ? h("a", { href: `#/nohands/${moduleId}` }, "No Hands checkpoint") : "🔒 No Hands checkpoint",
        store.getState().noHands[moduleId]?.passed ? " ✓ passed" : "") : null,
      mod.project ? h("li", {}, allMastered ? h("a", { href: `#/project/${moduleId}` }, `Module project: ${mod.project.title}`) : `🔒 Module project: ${mod.project.title}`,
        store.getState().projects[moduleId]?.passed ? " ✓ passed" : "") : null)));
  for (const [key, label] of [["robots", "Bridge to Real Robots"], ["cpp", "Bridge to C++"]]) {
    if (!mod.bridges?.[key]) continue;
    const box = h("div", { class: "bridge" });
    renderInto(box, await loadText(`${mod.base}/${mod.bridges[key]}`));
    root.append(h("section", { class: `card bridge-${key}` }, h("h2", {}, label), box));
  }
}

// ------------------------------------------------------------ mastery quiz

export async function renderQuiz(root, curriculum, moduleId) {
  const mod = await loadModule(moduleId);
  const quiz = await loadJSON(`${mod.base}/${mod.quiz}`);
  const allMastered = mod.lessons.every((id) => store.getState().lessons[id]?.masteredAt);
  root.append(h("h1", {}, `${mod.title}: mastery quiz`));
  if (!allMastered) {
    root.append(h("div", { class: "alert warn" }, "Master every lesson in this module first."));
    return;
  }
  const items = shuffle(quiz.pool).slice(0, quiz.draw).map((q) => {
    const order = shuffle(q.choices.map((_, i) => i));
    return { ...q, order };
  });
  root.append(h("p", {}, `${items.length} questions drawn from a pool of ${quiz.pool.length}. You need ${quiz.passPct}% to pass. Retakes draw a new set in a new order. Closed book: no running code.`));
  const form = h("form", { class: "quiz" });
  items.forEach((q, n) => {
    form.append(h("fieldset", { class: "card" },
      h("legend", {}, `${n + 1}. ${q.q}`),
      q.code ? h("pre", { class: "code" }, q.code) : null,
      q.order.map((ci) => h("label", { class: "choice-row" },
        h("input", { type: "radio", name: `q${n}`, value: ci }), " ", h("span", { class: "mono-ish" }, q.choices[ci]))),
      h("div", { class: "feedback" })));
  });
  const submitBtn = button("Submit quiz", () => {
    let score = 0;
    const misses = [];
    items.forEach((q, n) => {
      const picked = form.querySelector(`input[name=q${n}]:checked`);
      const fs = form.querySelectorAll("fieldset")[n];
      const ok = picked && Number(picked.value) === q.answer;
      if (ok) score += 1;
      else {
        misses.push(q);
        store.reviewMiss(`${moduleId}:quiz:${q.id}`, { kind: "quiz", moduleId, itemId: q.id });
      }
      fs.classList.add(ok ? "right" : "wrong");
      clear(fs.querySelector(".feedback")).append(h("p", {}, ok ? "✓ " : `✗ Correct answer: ${q.choices[q.answer]}. `, q.why || ""));
      fs.querySelectorAll("input").forEach((i) => { i.disabled = true; });
    });
    const res = store.recordQuiz(moduleId, score, items.length, quiz.passPct);
    store.recordActivity();
    const pct = Math.round((100 * score) / items.length);
    submitBtn.replaceWith(h("div", { class: `alert ${pct >= quiz.passPct ? "ok" : "bad"}` },
      `Score: ${score}/${items.length} (${pct}%). `,
      pct >= quiz.passPct ? "Passed. Next module unlocked. 🎉" : `You need ${quiz.passPct}%. Missed items are in your review queue. Review them, then retake.`,
      h("div", {}, `Topics to review: ${[...new Set(misses.map((m) => m.topic || "general"))].join(", ") || "none"}`),
      h("div", { class: "row" }, button("Retake (new questions)", () => location.reload()), h("a", { class: "btn", href: `#/m/${moduleId}` }, "Back to module"))));
    window.scrollTo({ top: 0, behavior: "smooth" });
    void res;
  }, "btn primary");
  root.append(form, submitBtn);
}

// ------------------------------------------------------------ review queue

async function resolveReviewItem(item) {
  const ref = item.ref || {};
  if (ref.kind === "predict") {
    const lessons = await loadAllLessonMeta();
    const lesson = lessons[ref.lessonId];
    const p = lesson?.predict?.find((x) => x.id === ref.itemId);
    if (p) return { q: p.question || "What does this print?", code: p.code, choices: p.choices, answer: p.answer, why: p.why, source: lesson.title };
  }
  if (ref.kind === "quiz") {
    const mod = await loadModule(ref.moduleId);
    const quiz = await loadJSON(`${mod.base}/${mod.quiz}`);
    const q = quiz.pool.find((x) => x.id === ref.itemId);
    if (q) return { ...q, source: `${mod.title} quiz` };
  }
  if (ref.kind === "track") {
    const data = await loadJSON(ref.file);
    const q = data.items.find((x) => x.id === ref.itemId);
    if (q) return { ...q, source: ref.title };
  }
  return null;
}

export async function renderReview(root, curriculum, params) {
  const tired = params.get("tired") === "1";
  root.append(h("h1", {}, tired ? "Tired day: 30 minutes" : "Review queue"));
  if (tired) root.append(h("p", {}, "Clear your due reviews (up to 10), then one small drill. That's it. Your streak survives, and you come back tomorrow."));
  let due = store.dueReviewItems();
  if (tired) due = due.slice(0, 10);
  const items = [];
  for (const it of due) {
    const q = await resolveReviewItem(it);
    if (q) items.push({ ...q, id: it.id });
  }
  if (tired) {
    const drill = await randomDrill();
    if (drill) items.push({ ...drill, id: null, drill: true });
  }
  if (!items.length) {
    root.append(h("div", { class: "card" }, h("p", {}, "Nothing due. Missed predictions and quiz questions land here and come back on a 1, 3, 7, 14, 30 day schedule.")));
    return;
  }
  const stage = h("div", {});
  root.append(stage);
  let i = 0;
  let right = 0;
  const showItem = () => {
    clear(stage);
    if (i >= items.length) {
      store.recordActivity();
      stage.append(h("div", { class: "alert ok" }, `Done: ${right}/${items.length} correct. Streak kept. 🔥`), h("a", { class: "btn", href: "#/" }, "Dashboard"));
      return;
    }
    const q = items[i];
    const order = shuffle(q.choices.map((_, k) => k));
    const fb = h("div", {});
    stage.append(h("div", { class: "card" },
      h("div", { class: "muted" }, `${i + 1} of ${items.length}${q.drill ? " · drill" : ""} · from ${q.source}`),
      h("h2", {}, q.q), q.code ? h("pre", { class: "code" }, q.code) : null,
      h("div", { class: "choices" }, order.map((k) => {
        const b = h("button", { class: "choice mono", type: "button" }, q.choices[k]);
        b.addEventListener("click", () => {
          const ok = k === q.answer;
          if (q.id) (ok ? store.reviewHit(q.id) : store.reviewMiss(q.id));
          if (ok) right += 1;
          stage.querySelectorAll(".choice").forEach((c) => { c.disabled = true; });
          b.classList.add(ok ? "correct" : "wrong");
          fb.append(h("div", { class: `alert ${ok ? "ok" : "bad"}` }, ok ? "✓ " : `✗ Answer: ${q.choices[q.answer]}. `, q.why || ""),
            button("Next", () => { i += 1; showItem(); }, "btn primary"));
        });
        return b;
      })), fb));
  };
  showItem();
}

async function randomDrill() {
  // Drill from lessons you've mastered; before any mastery, from lessons you've opened.
  const lessons = await loadAllLessonMeta();
  const recs = store.getState().lessons;
  const pick = (filter) => Object.entries(lessons).filter(([id]) => filter(recs[id]))
    .flatMap(([, meta]) => (meta.predict || []).map((p) => ({ q: p.question || "What does this print?", code: p.code, choices: p.choices, answer: p.answer, why: p.why, source: meta.title })));
  let pool = pick((r) => r && r.masteredAt);
  if (!pool.length) pool = pick((r) => Boolean(r));
  return pool.length ? pool[Math.floor(Math.random() * pool.length)] : null;
}

// ------------------------------------------------------------ tracks

export async function renderTrack(root, curriculum, trackId, pageId) {
  const { track, page } = await findTrackPage(trackId, pageId);
  if (!page) {
    root.append(h("h1", {}, track.title), h("p", {}, track.summary));
    const groups = {};
    track.pages.forEach((p) => { (groups[p.group || ""] ||= []).push(p); });
    for (const [group, pages] of Object.entries(groups)) {
      root.append(section(group || "Pages", h("ol", { class: "lesson-list" }, pages.map((p) => {
        const rec = store.getState().tracks[p.id];
        const done = rec && rec.done;
        return h("li", { class: done ? "mastered" : "open" }, h("span", { class: "state" }, done ? "✓" : "○"),
          h("a", { href: `#/t/${trackId}/${p.id}` }, p.title), p.due ? h("span", { class: "muted" }, ` · target ${p.due}`) : null);
      }))));
    }
    return;
  }
  const base = `content/tracks/${track.dir}`;
  root.append(h("div", { class: "crumbs" }, h("a", { href: `#/t/${trackId}` }, track.title)), h("h1", {}, page.title));
  if (page.due) root.append(h("p", { class: "meta" }, `Target date: ${page.due}`));
  const body = h("article", { class: "lesson-body" });
  renderInto(body, await loadText(`${base}/${page.file}`));
  wireChecklists(body, page.id);
  root.append(body);
  if (page.quiz) await renderTrackQuiz(root, `${base}/${page.quiz}`, page);
  const rec = store.trackRecord(page.id);
  const doneBtn = button(rec.done ? "✓ Marked complete" : "Mark this page complete", () => {
    store.updateTrack(page.id, { done: true, doneAt: new Date().toISOString() });
    store.recordActivity();
    doneBtn.textContent = "✓ Marked complete";
  }, "btn primary");
  root.append(h("div", { class: "row" }, doneBtn, h("a", { class: "btn", href: `#/t/${trackId}` }, "Back to track")));
}

// Markdown task lists ("- [ ] item") become saved, clickable checkboxes.
function wireChecklists(body, pageId) {
  const rec = store.trackRecord(pageId);
  body.querySelectorAll('input[type="checkbox"]').forEach((box, i) => {
    const id = `c${i}`;
    box.disabled = false;
    box.checked = Boolean(rec.checks[id]);
    box.addEventListener("change", () => {
      store.setTrackCheck(pageId, id, box.checked);
      if (box.checked) store.recordActivity();
    });
  });
}

async function renderTrackQuiz(root, file, page) {
  const data = await loadJSON(file);
  const rec = store.trackRecord(page.id);
  if (data.items?.length) {
    const form = h("div", { class: "quiz" });
    data.items.forEach((q, n) => {
      const fb = h("div", { class: "feedback" });
      form.append(h("fieldset", { class: "card" }, h("legend", {}, `${n + 1}. ${q.q}`), q.code ? h("pre", { class: "code" }, q.code) : null,
        h("div", { class: "choices" }, q.choices.map((c, k) => {
          const b = h("button", { class: "choice", type: "button" }, c);
          b.addEventListener("click", () => {
            const ok = k === q.answer;
            if (!ok) store.reviewMiss(`${page.id}:${q.id}`, { kind: "track", file, itemId: q.id, title: page.title });
            b.closest("fieldset").querySelectorAll(".choice").forEach((x) => { x.disabled = true; });
            b.classList.add(ok ? "correct" : "wrong");
            clear(fb).append(h("p", {}, ok ? "✓ " : `✗ Answer: ${q.choices[q.answer]}. `, q.why || ""));
            store.recordActivity();
          });
          return b;
        })), fb));
    });
    root.append(section(data.title || "Quiz", form));
  }
  if (data.interview?.length) {
    const useTutor = await tutorAvailable();
    const box = h("div", {});
    data.interview.forEach((iq, n) => {
      const ta = h("textarea", { rows: 5, "aria-label": `Answer to interview question ${n + 1}` });
      ta.value = rec[`iq${n}`] || "";
      ta.addEventListener("input", () => store.updateTrack(page.id, { [`iq${n}`]: ta.value }));
      box.append(h("div", { class: "card" }, h("h3", {}, `Interview question ${n + 1}`), h("p", {}, iq.q), ta,
        useTutor ? button("Mock interviewer: grade my answer", () =>
          openTutor("interview", { lessonTitle: page.title, task: iq.q, explainText: ta.value, rubric: iq.rubric }), "btn")
          : h("details", {}, h("summary", {}, "Self-check rubric (tutor off)"), h("ul", {}, iq.rubric.map((r) => h("li", {}, r))))));
    });
    root.append(section("Interview practice: answer out loud first, then write it", box));
  }
}

// ------------------------------------------------------------ simulator

export async function renderSimPage(root) {
  const worlds = await loadJSON("content/sim/worlds.json");
  const starter = await loadText("content/sim/starter_controller.py");
  root.append(h("h1", {}, "Robot simulator"),
    h("p", {}, "Write control(sensors, dt), which returns (left_speed, right_speed) in m/s. Every sensor is noisy, like a real one. See the reference below the editor."));
  const select = h("select", { "aria-label": "World" }, Object.keys(worlds).map((k) => h("option", { value: k }, worlds[k].title || k)));
  const seconds = h("input", { type: "number", value: 30, min: 1, max: 120, class: "small", "aria-label": "Seconds to simulate" });
  const host = h("div", {});
  const status = h("div", {});
  const viewHost = h("div", {});
  root.append(host, h("div", { class: "row" }, h("label", {}, "World ", select), h("label", {}, " Seconds ", seconds),
    button("Run simulation", run, "btn primary")), status, viewHost);
  const cm = createEditor(host, { value: localStorageGet("pfr.sim.code") || starter, onChange: (v) => localStorageSet("pfr.sim.code", v), onRun: run });
  const view = createSimView(viewHost);
  async function run() {
    clear(status).append(h("div", { class: "muted" }, "Simulating…"));
    const res = await runSim(cm.getValue(), worlds[select.value].world, Number(seconds.value) || 30, 1);
    clear(status);
    if (res.stdout) status.append(h("pre", { class: "stdout" }, res.stdout.slice(-3000)));
    if (res.error) {
      const { errorBlock } = await import("./exercise.js");
      status.append(errorBlock(res.error));
      cm.markError(res.error.lineno);
      return;
    }
    cm.markError(0);
    view.load(res);
    view.play();
  }
  const ref = h("div", { class: "card" });
  renderInto(ref, await loadText("content/sim/reference.md"));
  root.append(ref);
}

function localStorageGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch { /* ignore */ } }

// ------------------------------------------------------------ project & no hands

export async function renderProject(root, curriculum, moduleId) {
  const mod = await loadModule(moduleId);
  const p = mod.project;
  const allMastered = mod.lessons.every((id) => store.getState().lessons[id]?.masteredAt);
  root.append(h("div", { class: "crumbs" }, h("a", { href: `#/m/${moduleId}` }, mod.title)), h("h1", {}, `Project: ${p.title}`));
  if (!allMastered) { root.append(h("div", { class: "alert warn" }, "Master every lesson first.")); return; }
  const brief = h("article", { class: "lesson-body" });
  renderInto(brief, await loadText(`${mod.base}/${p.brief}`));
  root.append(brief);
  const [starter, tests, readme] = await Promise.all([loadText(`${mod.base}/${p.starter}`), loadText(`${mod.base}/${p.tests}`), loadText(`${mod.base}/${p.readme}`)]);
  const extraFiles = {};
  for (const [dest, src] of Object.entries(p.dataFiles || {})) extraFiles[dest] = await loadText(src);
  const saved = store.getState().projects[moduleId]?.code || localStorageGet(`pfr.project.${moduleId}`);
  const ex = renderExercise(root, {
    title: "Your project code", starter, tests, testName: "test_project.py", saved, extraFiles, timeoutMs: 30000,
    onSave: (v) => localStorageSet(`pfr.project.${moduleId}`, v),
    hints: p.hints, tutorCtx: () => ({ lessonTitle: `${mod.title} project: ${p.title}`, task: p.title }),
    onPass: (code) => { store.recordProject(moduleId, code); store.recordActivity(); toast("Project passed! Export it to your portfolio.", "ok"); },
  });
  root.append(section("Export to your portfolio",
    h("p", {}, "Download your code and a README template, then put them in your own GitHub repo. Fill in the README yourself: that's part of the project."),
    h("div", { class: "row" },
      button(`Download ${p.exportName || "project.py"}`, () => download(p.exportName || "project.py", ex.editor.getValue(), "text/x-python")),
      button("Download README.md template", () => download("README.md", readme, "text/markdown"))),
    p.resumeBullet ? h("div", { class: "alert info" }, h("strong", {}, "Suggested resume bullet (only after the tests pass, and fill in YOUR numbers): "), p.resumeBullet) : null));
}

export async function renderNoHands(root, curriculum, moduleId) {
  const mod = await loadModule(moduleId);
  const nh = mod.noHands;
  const allMastered = mod.lessons.every((id) => store.getState().lessons[id]?.masteredAt);
  root.append(h("div", { class: "crumbs" }, h("a", { href: `#/m/${moduleId}` }, mod.title)), h("h1", {}, `No Hands checkpoint: ${nh.title}`));
  if (!allMastered) { root.append(h("div", { class: "alert warn" }, "Master every lesson first.")); return; }
  const brief = h("article", { class: "lesson-body" });
  renderInto(brief, await loadText(`${mod.base}/${nh.brief}`));
  const [starter, tests] = await Promise.all([loadText(`${mod.base}/${nh.starter}`), loadText(`${mod.base}/${nh.tests}`)]);
  const timer = h("div", { class: "timer" }, "Press Start when you're ready. Closed book: no notes, no AI, no pasting.");
  const stage = h("div", {});
  root.append(brief, timer, stage);
  const startBtn = button("Start checkpoint", () => {
    startBtn.remove();
    const end = Date.now() + nh.minutes * 60000;
    const tick = setInterval(() => {
      const left = Math.max(0, end - Date.now());
      timer.textContent = `Time left: ${Math.floor(left / 60000)}:${String(Math.floor((left % 60000) / 1000)).padStart(2, "0")}`;
      if (!left) { clearInterval(tick); timer.textContent = "Time's up. You can still finish, but note how long it took."; }
    }, 1000);
    renderExercise(stage, {
      starter, tests, testName: "test_nohands.py", noHands: true,
      onPass: () => { clearInterval(tick); store.recordNoHands(moduleId); store.recordActivity(); toast("No Hands checkpoint passed. That skill is yours. 💪", "ok"); },
    });
  }, "btn primary");
  root.append(startBtn);
}

// ------------------------------------------------------------ settings

export async function renderSettings(root) {
  const st = store.getState();
  const tutorOn = await tutorAvailable();
  const theme = h("select", { "aria-label": "Theme" }, ["auto", "light", "dark"].map((t) => h("option", { value: t, selected: st.settings.theme === t }, t)));
  theme.addEventListener("change", () => { store.setSetting("theme", theme.value); applyTheme(theme.value); });
  const file = h("input", { type: "file", accept: "application/json", "aria-label": "Import progress file" });
  file.addEventListener("change", async () => {
    try {
      store.importJSON(await file.files[0].text());
      toast("Progress imported.", "ok");
      setTimeout(() => location.reload(), 600);
    } catch (err) {
      toast(err.message, "bad");
    }
  });
  root.append(h("h1", {}, "Settings"),
    section("Appearance", h("label", {}, "Theme ", theme)),
    section("Progress",
      h("p", {}, store.storageAvailable() ? "Progress is saved in this browser (localStorage)." : "⚠ Browser storage is blocked. Progress lasts only until you close this tab. Export it!"),
      h("div", { class: "row" },
        button("Export progress (JSON)", () => download(`pfr-progress-${store.dayKey()}.json`, store.exportJSON(), "application/json"), "btn primary"),
        h("label", { class: "btn" }, "Import… ", file),
        button("Reset all progress", () => { if (confirm("Erase ALL progress in this browser? Export first if unsure.")) { store.resetAll(); location.reload(); } }, "btn danger"))),
    section("AI tutor", h("p", {}, tutorOn
      ? "✓ Tutor is on (config.local.json found on localhost)."
      : "Tutor is off. To enable it: copy config.local.example.json to config.local.json in the repo root, add your Anthropic API key, and open the site from http://localhost:8000. The file is gitignored and never deployed.")));
}

export function applyTheme(theme) {
  if (theme === "auto") document.documentElement.removeAttribute("data-theme");
  else document.documentElement.setAttribute("data-theme", theme);
}
