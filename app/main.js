// App entry: hash router, curriculum sidebar, theme, keyboard shortcuts.
import { h, clear } from "./ui.js";
import { loadCurriculum, loadModule } from "./content.js";
import { renderLesson } from "./views/lesson.js";
import { renderDashboard, renderModule, renderQuiz, renderReview, renderTrack, renderSimPage,
  renderProject, renderNoHands, renderSettings, applyTheme } from "./views/pages.js";
import { ensureBooted, onStatus } from "./runner/runner.js";
import * as store from "./store.js";

const main = document.getElementById("main");
const nav = document.getElementById("curriculum-nav");

async function route() {
  const curriculum = await loadCurriculum();
  const [path, query = ""] = (location.hash.slice(1) || "/").split("?");
  const parts = path.split("/").filter(Boolean);
  const params = new URLSearchParams(query);
  clear(main);
  main.focus({ preventScroll: true });
  window.scrollTo(0, 0);
  try {
    switch (parts[0]) {
      case undefined: await renderDashboard(main, curriculum); break;
      case "m": await renderModule(main, curriculum, parts[1]); break;
      case "l": await renderLesson(main, curriculum, parts[1], parts[2]); break;
      case "quiz": await renderQuiz(main, curriculum, parts[1]); break;
      case "project": await renderProject(main, curriculum, parts[1]); break;
      case "nohands": await renderNoHands(main, curriculum, parts[1]); break;
      case "review": await renderReview(main, curriculum, params); break;
      case "t": await renderTrack(main, curriculum, parts[1], parts[2]); break;
      case "sim": await renderSimPage(main); break;
      case "settings": await renderSettings(main); break;
      default: main.append(h("h1", {}, "Not found"), h("a", { href: "#/" }, "Go to the dashboard"));
    }
  } catch (err) {
    console.error(err);
    main.append(h("div", { class: "alert bad" }, `Something went wrong loading this page: ${err.message}`));
  }
  await renderNav(curriculum);
}

async function renderNav(curriculum) {
  const current = location.hash;
  const st = store.getState();
  clear(nav);
  nav.append(link("#/", "🏠 Dashboard", current), link("#/review", `🔁 Review (${store.dueReviewItems().length} due)`, current),
    link("#/sim", "🤖 Simulator", current));
  nav.append(h("div", { class: "nav-heading" }, "Curriculum"));
  for (const entry of curriculum.modules) {
    const unlocked = store.moduleUnlocked(curriculum, entry.id);
    const passed = st.quizzes[entry.id]?.passed;
    const icon = entry.status !== "ready" ? "·" : passed ? "✓" : unlocked ? "○" : "🔒";
    const item = h("div", { class: `nav-module ${entry.status !== "ready" ? "planned" : ""}` },
      link(`#/m/${entry.id}`, `${icon} ${entry.short || entry.title}`, current));
    if (entry.status === "ready" && unlocked && current.includes(`/${entry.id}`)) {
      const mod = await loadModule(entry.id);
      item.append(h("ol", { class: "nav-lessons" }, mod.lessons.map((id, i) => {
        const rec = st.lessons[id];
        const state = rec?.masteredAt ? "✓" : store.lessonUnlocked(curriculum, mod, i) ? "○" : "🔒";
        return h("li", {}, link(`#/l/${entry.id}/${id}`, `${state} ${mod.lessonTitles?.[id] || id}`, current));
      })));
    }
    nav.append(item);
  }
  nav.append(h("div", { class: "nav-heading" }, "Tracks"));
  for (const t of curriculum.tracks) nav.append(link(`#/t/${t.id}`, t.title, current));
  nav.append(h("div", { class: "nav-heading" }, ""), link("#/settings", "⚙ Settings", current));
}

function link(href, label, current) {
  const active = current === href || (href !== "#/" && current.startsWith(href + "/")) || (href === "#/" && (current === "" || current === "#/"));
  return h("a", { href, class: active ? "active" : "", "aria-current": active ? "page" : false }, label);
}

function setupChrome() {
  applyTheme(store.getState().settings.theme || "auto");
  const status = document.getElementById("py-status");
  onStatus((s) => {
    status.textContent = { idle: "Python: idle", loading: "Python: loading…", ready: "Python: ready", running: "Python: running…", error: "Python: failed to load" }[s];
    status.dataset.state = s;
  });
  document.getElementById("nav-toggle").addEventListener("click", () => document.body.classList.toggle("nav-open"));
  nav.addEventListener("click", (e) => { if (e.target.closest("a")) document.body.classList.remove("nav-open"); });
  document.addEventListener("keydown", (e) => {
    const typing = e.target.closest("input, textarea, select, .CodeMirror");
    if (typing) return;
    if (e.key === "?") document.getElementById("help").showModal();
    if (e.key === "g") location.hash = "#/";
    if (e.key === "r") location.hash = "#/review";
  });
  document.getElementById("help-close").addEventListener("click", () => document.getElementById("help").close());
}

setupChrome();
window.addEventListener("hashchange", route);
route();
ensureBooted(); // start loading Python in the background right away
