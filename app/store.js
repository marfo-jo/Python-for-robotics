// Learner progress. Lives in localStorage when available; every access is
// wrapped so the site still works (in memory) in private windows or when
// storage is blocked. Export/import uses the same JSON shape.

const KEY = "pfr.progress.v1";
const SCHEMA_VERSION = 1;
const LEITNER_DAYS = [1, 3, 7, 14, 30];

function blank() {
  return {
    version: SCHEMA_VERSION,
    createdAt: new Date().toISOString(),
    lessons: {},     // lessonId -> lesson record (see lessonRecord)
    quizzes: {},     // moduleId -> { best, passed, attempts: [{at, score, total}] }
    noHands: {},     // moduleId -> { passed, at }
    projects: {},    // moduleId -> { passed, at, code }
    tracks: {},      // pageId -> { checks: {itemId: true}, quiz: {...}, notes }
    review: {},      // itemId -> { box, due, lapses, ref }
    activity: {},    // 'YYYY-MM-DD' -> count
    streak: { best: 0 },
    settings: { theme: "auto" },
  };
}

let state = load();
const listeners = new Set();

function storage() {
  try {
    const s = window.localStorage;
    const probe = "__pfr_probe__";
    s.setItem(probe, "1");
    s.removeItem(probe);
    return s;
  } catch {
    return null;
  }
}

function load() {
  const s = storage();
  if (!s) return blank();
  try {
    const raw = s.getItem(KEY);
    if (!raw) return blank();
    return migrate(JSON.parse(raw));
  } catch {
    return blank();
  }
}

function migrate(data) {
  const fresh = blank();
  if (!data || typeof data !== "object") return fresh;
  // v1 is the first schema: fill any missing top-level keys.
  for (const key of Object.keys(fresh)) {
    if (data[key] === undefined) data[key] = fresh[key];
  }
  data.version = SCHEMA_VERSION;
  return data;
}

export const storageAvailable = () => storage() !== null;

function save() {
  const s = storage();
  if (s) {
    try {
      s.setItem(KEY, JSON.stringify(state));
    } catch {
      /* quota or blocked: keep working in memory */
    }
  }
  listeners.forEach((fn) => fn(state));
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export const getState = () => state;

// ---------------------------------------------------------------- dates

export function dayKey(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function addDays(key, n) {
  const [y, m, d] = key.split("-").map(Number);
  return dayKey(new Date(y, m - 1, d + n));
}

export function recordActivity() {
  const today = dayKey();
  state.activity[today] = (state.activity[today] || 0) + 1;
  const cur = currentStreak();
  if (cur > (state.streak.best || 0)) state.streak.best = cur;
  save();
}

export function currentStreak() {
  let key = dayKey();
  if (!state.activity[key]) key = addDays(key, -1); // today not done yet: streak still alive
  let n = 0;
  while (state.activity[key]) {
    n += 1;
    key = addDays(key, -1);
  }
  return n;
}

// ---------------------------------------------------------------- lessons

export function lessonRecord(id) {
  if (!state.lessons[id]) {
    state.lessons[id] = {
      challengePassed: false, bugFixed: false, explainDone: false,
      predict: {}, attempts: 0, lastSubmitted: null, hintTier: 0,
      code: {}, explainText: "", masteredAt: null, solutionUnlocked: false,
    };
  }
  return state.lessons[id];
}

export function updateLesson(id, patch) {
  Object.assign(lessonRecord(id), patch);
  save();
}

export function saveCode(lessonId, slot, code) {
  lessonRecord(lessonId).code[slot] = code;
  save();
}

export function isLessonMastered(lesson) {
  const rec = state.lessons[lesson.id];
  if (!rec) return false;
  const predictIds = (lesson.predict || []).map((p) => p.id);
  return rec.challengePassed && rec.bugFixed && rec.explainDone &&
    predictIds.every((pid) => rec.predict[pid] !== undefined);
}

export function markMasteredIfDone(lesson) {
  const rec = lessonRecord(lesson.id);
  if (!rec.masteredAt && isLessonMastered(lesson)) {
    rec.masteredAt = new Date().toISOString();
    save();
    return true;
  }
  return false;
}

// ---------------------------------------------------------------- unlocks

// Module i is unlocked when module i-1's mastery quiz is passed.
// Lesson j is unlocked when its module is unlocked and lesson j-1 is mastered.
export function moduleUnlocked(curriculum, moduleId) {
  const order = curriculum.modules.map((m) => m.id);
  const idx = order.indexOf(moduleId);
  if (idx <= 0) return true;
  const prev = order[idx - 1];
  return Boolean(state.quizzes[prev] && state.quizzes[prev].passed);
}

export function lessonUnlocked(curriculum, module, lessonIndex) {
  if (!moduleUnlocked(curriculum, module.id)) return false;
  if (lessonIndex === 0) return true;
  const prev = module.lessons[lessonIndex - 1];
  return Boolean(state.lessons[prev] && state.lessons[prev].masteredAt);
}

// ---------------------------------------------------------------- quizzes

export function recordQuiz(moduleId, score, total, passPct) {
  const q = state.quizzes[moduleId] || { best: 0, passed: false, attempts: [] };
  const pct = Math.round((100 * score) / total);
  q.attempts.push({ at: new Date().toISOString(), score, total, pct });
  q.best = Math.max(q.best, pct);
  if (pct >= passPct) q.passed = true;
  state.quizzes[moduleId] = q;
  save();
  return q;
}

export function recordNoHands(moduleId) {
  state.noHands[moduleId] = { passed: true, at: new Date().toISOString() };
  save();
}

export function recordProject(moduleId, code) {
  state.projects[moduleId] = { passed: true, at: new Date().toISOString(), code };
  save();
}

// ---------------------------------------------------------------- tracks

export function trackRecord(pageId) {
  if (!state.tracks[pageId]) state.tracks[pageId] = { checks: {}, quiz: null, notes: "" };
  return state.tracks[pageId];
}

export function setTrackCheck(pageId, itemId, value) {
  trackRecord(pageId).checks[itemId] = value;
  save();
}

export function updateTrack(pageId, patch) {
  Object.assign(trackRecord(pageId), patch);
  save();
}

// ---------------------------------------------------------------- spaced repetition

// Missed items enter box 0 (due tomorrow). Each correct review moves the item up
// one box; a miss sends it back to box 0. Leaving the top box retires it.
export function reviewMiss(itemId, ref) {
  const item = state.review[itemId] || { box: 0, lapses: 0, ref };
  item.box = 0;
  item.lapses += 1;
  item.ref = ref || item.ref;
  item.due = addDays(dayKey(), LEITNER_DAYS[0]);
  state.review[itemId] = item;
  save();
}

export function reviewHit(itemId) {
  const item = state.review[itemId];
  if (!item) return;
  item.box += 1;
  if (item.box >= LEITNER_DAYS.length) {
    delete state.review[itemId];
  } else {
    item.due = addDays(dayKey(), LEITNER_DAYS[item.box]);
  }
  save();
}

export function dueReviewItems() {
  const today = dayKey();
  return Object.entries(state.review)
    .filter(([, item]) => item.due <= today)
    .map(([id, item]) => ({ id, ...item }));
}

// ---------------------------------------------------------------- skills

export function skillPoints(lessonsById) {
  const points = {};
  for (const [id, rec] of Object.entries(state.lessons)) {
    if (!rec.masteredAt || !lessonsById[id]) continue;
    for (const [axis, w] of Object.entries(lessonsById[id].skills || {})) {
      points[axis] = (points[axis] || 0) + w;
    }
  }
  return points;
}

export function resumeReadySkills(curriculum) {
  return curriculum.modules
    .filter((m) => state.quizzes[m.id]?.passed && state.noHands[m.id]?.passed)
    .map((m) => m.resumeSkill || m.title);
}

// ---------------------------------------------------------------- settings / io

export function setSetting(key, value) {
  state.settings[key] = value;
  save();
}

export function exportJSON() {
  return JSON.stringify(state, null, 2);
}

export function importJSON(text) {
  const data = JSON.parse(text);
  if (!data || typeof data !== "object" || !data.lessons) {
    throw new Error("This file doesn't look like a Python for Robotics progress export.");
  }
  state = migrate(data);
  save();
}

export function resetAll() {
  state = blank();
  save();
}
