// Slide-in tutor drawer shared by all pages. If the tutor is off, it explains
// how to turn it on and points to the self-check alternatives.
import { h, clear, button } from "../ui.js";
import { askTutor, tutorAvailable } from "../tutor/tutor.js";

let drawer = null;
let log = null;
let input = null;
let current = { mode: "chat", ctx: {}, history: [] };
let disabledReason = null;

const MODE_LABELS = {
  hint: "Hint", error: "Explain my error", grill: "Grill me", explain: "Grade my explanation",
  solution: "Full solution", interview: "Mock interviewer", chat: "Ask",
};

function ensureDrawer() {
  if (drawer) return;
  log = h("div", { class: "tutor-log", "aria-live": "polite" });
  input = h("textarea", { rows: 3, placeholder: "Reply to the tutor… (Ctrl+Enter to send)", "aria-label": "Message to tutor" });
  input.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) send(); });
  drawer = h("aside", { class: "tutor-drawer", "aria-label": "AI tutor", hidden: true },
    h("div", { class: "tutor-head" }, h("strong", { id: "tutor-title" }, "Tutor"),
      button("✕", close, "btn subtle", { "aria-label": "Close tutor" })),
    log,
    h("div", { class: "tutor-input" }, input, button("Send", () => send(), "btn primary")));
  document.body.append(drawer);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !drawer.hidden) close(); });
}

function close() {
  drawer.hidden = true;
}

// Opening a new mode or a different context starts a fresh conversation.
export async function openTutor(mode, ctx, { autoSend = true, onReply = null } = {}) {
  ensureDrawer();
  drawer.hidden = false;
  document.getElementById("tutor-title").textContent = `Tutor: ${MODE_LABELS[mode] || mode}`;
  current = { mode, ctx, history: [], onReply };
  clear(log);
  if (!(await tutorAvailable())) {
    disabledReason = true;
    log.append(h("div", { class: "alert info" },
      h("p", {}, "The AI tutor is off. The site works fully without it: use the tiered hints, the error explainer, and the self-check rubrics."),
      h("p", {}, "To turn it on: copy config.local.example.json to config.local.json, put your Anthropic API key in it, and open the site from localhost (python -m http.server). config.local.json is gitignored and never deployed.")));
    return;
  }
  disabledReason = null;
  if (autoSend) send("");
  input.focus();
}

async function send(text) {
  if (disabledReason) return;
  const userText = text === undefined ? input.value.trim() : text;
  if (text === undefined && !userText) return;
  input.value = "";
  if (userText) log.append(h("div", { class: "msg user" }, userText));
  const bubble = h("div", { class: "msg tutor" }, "…");
  log.append(bubble);
  let started = false;
  try {
    const reply = await askTutor({
      mode: current.mode, ctx: current.ctx, history: current.history, userText,
      onText: (t) => {
        if (!started) { bubble.textContent = ""; started = true; }
        bubble.textContent += t;
        log.scrollTop = log.scrollHeight;
      },
    });
    current.onReply && current.onReply(reply);
  } catch (err) {
    bubble.textContent = `Tutor error: ${err.message}`;
    bubble.classList.add("bad");
  }
}
