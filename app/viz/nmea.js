// Interactive NMEA visuals for Module 0.
//  - renderNmeaFields: edit a sentence and see split(',') and indexes live.
//  - renderXorChecksum: step through the XOR checksum one character at a time.
import { h, clear, button } from "../ui.js";

const GGA_FIELDS = ["sentence id", "UTC time hhmmss.ss", "latitude ddmm.mmmm", "N/S",
  "longitude dddmm.mmmm", "E/W", "fix quality (0 = none)", "satellites used", "HDOP",
  "altitude", "altitude units", "geoid separation", "units", "DGPS age", "DGPS station*checksum"];

export function renderNmeaFields(el, { sentence, fieldNames = GGA_FIELDS }) {
  const input = h("input", { type: "text", class: "mono wide", value: sentence, "aria-label": "NMEA sentence", spellcheck: "false" });
  const sliceStart = h("input", { type: "number", value: 0, min: -99, max: 99, class: "small", "aria-label": "slice start" });
  const sliceEnd = h("input", { type: "number", value: 6, min: -99, max: 99, class: "small", "aria-label": "slice end" });
  const charRow = h("div", { class: "char-row mono" });
  const sliceOut = h("code", {});
  const table = h("div", {});

  function update() {
    const s = input.value;
    clear(charRow);
    const a = Number(sliceStart.value);
    const b = Number(sliceEnd.value);
    const norm = (i) => (i < 0 ? Math.max(s.length + i, 0) : Math.min(i, s.length));
    const lo = norm(a), hi = norm(b);
    [...s].forEach((ch, i) => {
      charRow.append(h("span", { class: `char ${i >= lo && i < hi ? "in-slice" : ""} ${ch === "," ? "comma" : ""}`, title: `index ${i} (also ${i - s.length})` },
        h("span", { class: "ch" }, ch), h("span", { class: "idx" }, i)));
    });
    sliceOut.textContent = `sentence[${a}:${b}]  →  ${JSON.stringify(s.slice(lo, hi))}`;
    const parts = s.split(",");
    clear(table);
    table.append(h("table", { class: "vars" },
      h("caption", {}, `sentence.split(",") → a list with ${parts.length} items`),
      h("tr", {}, h("th", {}, "index"), h("th", {}, "value"), h("th", {}, "meaning")),
      parts.map((p, i) => h("tr", { class: p === "" ? "empty-field" : "" },
        h("td", {}, `[${i}]`), h("td", {}, h("code", {}, JSON.stringify(p))),
        h("td", { class: "muted" }, fieldNames[i] || "")))));
  }
  [input, sliceStart, sliceEnd].forEach((x) => x.addEventListener("input", update));
  el.append(h("div", { class: "viz-nmea" },
    h("label", {}, "Sentence (edit me): ", input),
    h("div", { class: "row" }, h("label", {}, "slice start ", sliceStart), h("label", {}, " end ", sliceEnd), sliceOut),
    charRow, table));
  update();
}

export function renderXorChecksum(el, { sentence }) {
  const input = h("input", { type: "text", class: "mono wide", value: sentence, "aria-label": "NMEA sentence", spellcheck: "false" });
  const body = h("div", {});
  let step = 0;
  const slider = h("input", { type: "range", min: 0, max: 0, value: 0, "aria-label": "Characters processed" });

  function payload() {
    const s = input.value;
    const start = s.startsWith("$") ? 1 : 0;
    const star = s.indexOf("*");
    return { text: s.slice(start, star === -1 ? s.length : star), given: star === -1 ? null : s.slice(star + 1, star + 3).toUpperCase() };
  }
  const bits = (n) => n.toString(2).padStart(8, "0");

  function update() {
    const { text, given } = payload();
    slider.max = text.length;
    step = Math.min(step, text.length);
    slider.value = step;
    let acc = 0;
    for (let i = 0; i < step; i++) acc ^= text.charCodeAt(i);
    clear(body);
    const cur = step > 0 ? text[step - 1] : null;
    body.append(
      h("div", { class: "char-row mono" }, [...text].map((ch, i) =>
        h("span", { class: `char ${i < step ? "done" : ""} ${i === step - 1 ? "current" : ""}` }, h("span", { class: "ch" }, ch)))),
      h("table", { class: "vars bits" },
        h("tr", {}, h("th", {}, ""), h("th", {}, "char"), h("th", {}, "ord()"), h("th", {}, "binary")),
        cur ? h("tr", {}, h("td", {}, "this char"), h("td", {}, JSON.stringify(cur)), h("td", {}, cur.charCodeAt(0)), h("td", { class: "mono" }, bits(cur.charCodeAt(0)))) : null,
        h("tr", { class: "changed" }, h("td", {}, "checksum so far"), h("td", {}, ""), h("td", {}, acc), h("td", { class: "mono" }, bits(acc)))),
      h("p", {}, `After ${step} of ${text.length} characters: checksum = ${acc} = 0x`, h("strong", {}, acc.toString(16).toUpperCase().padStart(2, "0")),
        given ? (step === text.length ? (given === acc.toString(16).toUpperCase().padStart(2, "0")
          ? h("span", { class: "ok" }, `  ✓ matches the *${given} in the sentence`)
          : h("span", { class: "bad" }, `  ✗ the sentence says *${given}: corrupted (or edited!)`)) : ` (sentence says *${given})`) : ""));
  }
  slider.addEventListener("input", () => { step = Number(slider.value); update(); });
  input.addEventListener("input", update);
  el.append(h("div", { class: "viz-xor" },
    h("label", {}, "Sentence (try changing one character): ", input),
    h("div", { class: "row" }, button("◀", () => { step = Math.max(0, step - 1); update(); }),
      slider, button("▶", () => { step += 1; update(); }), button("All", () => { step = 1e9; update(); })),
    body));
  update();
}
