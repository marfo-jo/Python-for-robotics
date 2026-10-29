// Protocol reference tables (content/reference/nmea.json). Questions test
// Python skills, not memorized protocol details, so any item that depends on
// a field layout or format declares "refs": ["gga", ...] and the table is
// shown right next to it. Prose can embed one with {{ref:gga}}.
import { h } from "../ui.js";
import { loadJSON } from "../content.js";

const REF_FILE = "content/reference/nmea.json";

export async function refBlock(ids, { open = true } = {}) {
  if (!ids || !ids.length) return null;
  const data = await loadJSON(REF_FILE);
  const wrap = h("div", { class: "refs" });
  for (const id of ids) {
    const ref = data[id];
    if (!ref) {
      wrap.append(h("div", { class: "alert bad" }, `Unknown reference "${id}"`));
      continue;
    }
    wrap.append(h("details", { class: "ref", open },
      h("summary", {}, `📖 Reference: ${ref.title}`, h("span", { class: "muted" }, " (look it up, don't memorize it)")),
      ref.example ? h("div", { class: "ref-example" }, "Example: ", h("code", {}, ref.example)) : null,
      h("table", { class: "ref-table" },
        h("tr", {}, ref.columns.map((c) => h("th", {}, c))),
        ref.rows.map((row) => h("tr", {}, row.map((cell, i) => h("td", {}, i === 1 && cell ? h("code", {}, cell) : cell))))),
      ref.notes ? h("ul", { class: "ref-notes" }, ref.notes.map((n) => h("li", {}, n))) : null));
  }
  return wrap;
}

// Fill {{ref:id}} slots produced by md.js inside an already-rendered element.
export async function fillRefSlots(el) {
  for (const slot of el.querySelectorAll('.embed[data-embed="ref"]')) {
    const block = await refBlock([slot.dataset.id]);
    if (block) slot.append(block);
  }
}
