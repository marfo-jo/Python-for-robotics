// Markdown rendering for lesson prose. Lessons embed interactive items with
// placeholders on their own line, for example:
//   {{example:ex1}}  {{predict:p1}}  {{viz:v1}}  {{challenge}}  {{bug}}  {{explain}}
// These become <div data-embed="..."> slots that the lesson view fills in.
/* global marked, DOMPurify, renderMathInElement */

const EMBED_RE = /^\{\{\s*([a-z]+)(?::([\w.-]+))?\s*\}\}\s*$/gm;

export function renderMarkdown(text) {
  const withSlots = text.replace(EMBED_RE, (_, kind, id) =>
    `\n<div class="embed" data-embed="${kind}" data-id="${id || ""}"></div>\n`);
  const html = marked.parse(withSlots, { gfm: true, breaks: false });
  return DOMPurify.sanitize(html, { ADD_ATTR: ["target"] });
}

export function renderInto(el, text) {
  el.innerHTML = renderMarkdown(text);
  typesetMath(el);
  return el;
}

export function typesetMath(el) {
  if (typeof renderMathInElement !== "function") return;
  renderMathInElement(el, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      // No single-$ delimiter: NMEA sentences ($GPGGA...) are everywhere in lessons.
      { left: "\\(", right: "\\)", display: false },
    ],
    throwOnError: false,
  });
}
