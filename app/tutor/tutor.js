// Optional AI tutor. Works only when the site runs on localhost AND a
// config.local.json (gitignored, never deployed) holds an Anthropic API key.
// Without it, every page still works and self-check rubrics replace grading.
//
// The app (not just the prompt) enforces the solution gate: "solution" mode is
// only offered after 3 real failed attempts AND an explicit request.

const SDK_URL = "https://cdn.jsdelivr.net/npm/@anthropic-ai/sdk@0.133.0/+esm";
const DEFAULT_MODEL = "claude-opus-5-5";
export const ATTEMPTS_FOR_SOLUTION = 3;

let configPromise = null;
let clientPromise = null;

function isLocalhost() {
  return ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname);
}

export function loadTutorConfig() {
  if (!configPromise) {
    configPromise = (async () => {
      if (!isLocalhost()) return null;
      try {
        const res = await fetch("config.local.json", { cache: "no-store" });
        if (!res.ok) return null;
        const cfg = await res.json();
        return cfg && typeof cfg.anthropicApiKey === "string" && cfg.anthropicApiKey.startsWith("sk-") ? cfg : null;
      } catch {
        return null;
      }
    })();
  }
  return configPromise;
}

export async function tutorAvailable() {
  return Boolean(await loadTutorConfig());
}

async function getClient() {
  if (!clientPromise) {
    clientPromise = (async () => {
      const cfg = await loadTutorConfig();
      const { default: Anthropic } = await import(SDK_URL);
      // The key stays on this machine and goes only to the Anthropic API.
      return new Anthropic({ apiKey: cfg.anthropicApiKey, dangerouslyAllowBrowser: true });
    })();
    clientPromise.catch(() => { clientPromise = null; });
  }
  return clientPromise;
}

// Stable across every request so it caches. Volatile details go in messages.
const SYSTEM = `You are the tutor inside "Python for Robotics", a rigorous, freeCodeCamp-style course.

The learner: a Robotics MS student with a BS in Electrical and Electronics Engineering, strong in circuits, Arduino, hardware, PLC troubleshooting, and preventive maintenance, but a Python beginner. Their goal is to write code independently, without AI writing it for them, and to pass robotics co-op interviews. Use electrical-engineering and maintenance analogies (signals, feedback loops, circuits, systematic diagnostics) when they help. Never compare to MATLAB.

How you teach:
- Be Socratic. Ask one focused guiding question at a time. Make the learner do the thinking.
- Encouraging but demanding: celebrate real progress, never lower the bar, never pretend wrong code is fine.
- Explain WHY, not just how. Name the specific beginner mistake when you see one.
- Teach reading tracebacks: point at the last line and the line number before explaining.
- Keep replies short (under about 150 words) unless grading or interviewing.
- Hints come in tiers. Tier 1 "nudge": a question pointing at the right area. Tier 2 "approach": the strategy in words, no code. Tier 3 "pseudocode": plain-language steps, still no Python. Only give the tier requested.

Hard rules:
- Unless the request explicitly says SOLUTION MODE IS UNLOCKED, never write the solution, never write more than one line of Python, and never fix their code for them. If asked, explain kindly that they need to make three real attempts first, and give a hint instead.
- Graded coursework: if the learner appears to be asking for help on a graded course assignment (for example ME5245 Project 2, EECE7150 homework such as structure from motion), decline to work on it and point them to the general concept instead. Course lessons here are independent practice.
- Formatting: plain prose with occasional inline code in backticks. No headings.`;

const MODE_INSTRUCTIONS = {
  hint: (ctx) => `Give a tier ${ctx.hintTier || 1} hint (${["nudge", "approach", "pseudocode"][(ctx.hintTier || 1) - 1]}) for the learner's current code.`,
  error: () => "The learner wants help understanding the error output. Walk them through reading the traceback (last line, then the line number), then ask a question that leads them to the cause. Do not fix the code.",
  grill: () => "Grill mode: ask ONE probing follow-up question about this lesson's concept or the learner's code (edge cases like empty input, dt = 0, wrong units, off-by-one). Wait for their answer. When they answer, say whether it's right and why in two or three sentences, then ask the next question.",
  explain: () => "Grade the learner's 'explain it back' answer against the rubric. For each rubric item say met or not met with one sentence. Then give one sentence on what would make it stronger. End with a final line that is exactly 'VERDICT: PASS' if every rubric item is met, otherwise exactly 'VERDICT: REVISE'.",
  solution: () => "SOLUTION MODE IS UNLOCKED: the learner made at least three real attempts and explicitly asked. Show a correct solution with brief comments, then explain the key idea they were missing and one similar exercise they should try alone.",
  interview: () => "Mock interviewer mode: act as a robotics co-op interviewer. Ask one question at a time. After each answer, score correctness, clarity, and communication from 1 to 5 each with one sentence of feedback, then ask the next question.",
  chat: () => "Answer the learner's question about this lesson, Socratically.",
};

function contextBlock(ctx) {
  const parts = [`Lesson: ${ctx.lessonTitle || "(none)"}`];
  if (ctx.objectives?.length) parts.push(`Objectives: ${ctx.objectives.join("; ")}`);
  if (ctx.task) parts.push(`Exercise: ${ctx.task}`);
  if (ctx.code) parts.push(`Learner code:\n\`\`\`python\n${ctx.code}\n\`\`\``);
  if (ctx.output) parts.push(`Latest output / errors / failing tests:\n${ctx.output}`);
  if (ctx.rubric) parts.push(`Rubric:\n- ${ctx.rubric.join("\n- ")}`);
  if (ctx.explainText) parts.push(`Learner's explanation:\n${ctx.explainText}`);
  parts.push(`Real failed attempts so far: ${ctx.attempts || 0}`);
  return parts.join("\n\n");
}

// Streams a tutor reply. `history` is [{role, content}] for this panel.
// onText receives text chunks. Resolves with the full reply text.
export async function askTutor({ mode, ctx, history, userText, onText }) {
  const cfg = await loadTutorConfig();
  if (!cfg) throw new Error("Tutor is off (no config.local.json on localhost).");
  if (mode === "solution" && !(ctx.attempts >= ATTEMPTS_FOR_SOLUTION && ctx.solutionRequested)) {
    throw new Error("The solution unlocks after 3 real attempts and an explicit request.");
  }
  const client = await getClient();
  const instruction = (MODE_INSTRUCTIONS[mode] || MODE_INSTRUCTIONS.chat)(ctx);
  const turn = `${instruction}\n\n---\n${contextBlock(ctx)}${userText ? `\n\n---\nLearner says: ${userText}` : ""}`;
  const messages = [...history, { role: "user", content: turn }];
  const stream = client.beta.messages.stream({
    model: cfg.model || DEFAULT_MODEL,
    max_tokens: 16000,
    output_config: { effort: cfg.effort || "medium" },
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
    messages,
  });
  let text = "";
  for await (const event of stream) {
    if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
      text += event.delta.text;
      onText && onText(event.delta.text);
    }
  }
  const final = await stream.finalMessage();
  if (final.stop_reason === "refusal") {
    const note = "\n\n(The tutor declined this request.)";
    onText && onText(note);
    text += note;
  }
  history.push({ role: "user", content: turn }, { role: "assistant", content: text || "(no reply)" });
  return text;
}
