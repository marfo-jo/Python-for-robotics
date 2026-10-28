// Loads lesson content (data files under content/). App code never hard-codes
// lessons: adding a lesson means adding files and listing it in module.json.

const cache = new Map();

async function fetchText(path) {
  if (cache.has(path)) return cache.get(path);
  const promise = fetch(path, { cache: "no-cache" }).then((res) => {
    if (!res.ok) throw new Error(`Could not load ${path} (${res.status})`);
    return res.text();
  });
  cache.set(path, promise);
  promise.catch(() => cache.delete(path));
  return promise;
}

export const loadText = fetchText;
export const loadJSON = async (path) => JSON.parse(await fetchText(path));

let curriculumPromise = null;
export function loadCurriculum() {
  if (!curriculumPromise) curriculumPromise = loadJSON("content/curriculum.json");
  return curriculumPromise;
}

export async function loadModule(moduleId) {
  const cur = await loadCurriculum();
  const entry = cur.modules.find((m) => m.id === moduleId);
  if (!entry) throw new Error(`Unknown module ${moduleId}`);
  if (entry.status !== "ready") return { ...entry, lessons: [], ready: false };
  const base = `content/modules/${entry.dir}`;
  const mod = await loadJSON(`${base}/module.json`);
  return { ...entry, ...mod, base, ready: true };
}

export async function loadLesson(moduleId, lessonId) {
  const mod = await loadModule(moduleId);
  const ref = mod.lessonDirs[lessonId];
  if (!ref) throw new Error(`Unknown lesson ${lessonId}`);
  const base = `${mod.base}/${ref}`;
  const [meta, md] = await Promise.all([loadJSON(`${base}/lesson.json`), fetchText(`${base}/lesson.md`)]);
  return { ...meta, base, md, module: mod };
}

// Load all lesson.json files for ready modules (used for skills radar totals
// and the review queue). Light: JSON only.
export async function loadAllLessonMeta() {
  const cur = await loadCurriculum();
  const out = {};
  for (const entry of cur.modules.filter((m) => m.status === "ready")) {
    const mod = await loadModule(entry.id);
    await Promise.all(mod.lessons.map(async (id) => {
      try {
        const meta = await loadJSON(`${mod.base}/${mod.lessonDirs[id]}/lesson.json`);
        out[id] = { ...meta, moduleId: entry.id, base: `${mod.base}/${mod.lessonDirs[id]}` };
      } catch (err) {
        console.warn(`Skipping ${id}: ${err.message}`);
      }
    }));
  }
  return out;
}

export async function findTrackPage(trackId, pageId) {
  const cur = await loadCurriculum();
  const track = cur.tracks.find((t) => t.id === trackId);
  if (!track) throw new Error(`Unknown track ${trackId}`);
  const page = pageId ? track.pages.find((p) => p.id === pageId) : null;
  return { track, page };
}
