// Skills radar (hand-written SVG so it themes with CSS variables).
const NS = "http://www.w3.org/2000/svg";

function svg(tag, attrs, text) {
  const el = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (text !== undefined) el.textContent = text;
  return el;
}

// axes: [{id, label}], values: {id: 0..1}
export function renderRadar(el, axes, values) {
  const size = 320, c = size / 2, r = 110;
  const root = svg("svg", { viewBox: `0 0 ${size} ${size}`, class: "radar", role: "img",
    "aria-label": "Skills radar: " + axes.map((a) => `${a.label} ${Math.round(100 * (values[a.id] || 0))}%`).join(", ") });
  const angle = (i) => -Math.PI / 2 + (2 * Math.PI * i) / axes.length;
  const pt = (i, f) => [c + r * f * Math.cos(angle(i)), c + r * f * Math.sin(angle(i))];
  for (const f of [0.25, 0.5, 0.75, 1]) {
    root.append(svg("polygon", { class: "radar-grid", points: axes.map((_, i) => pt(i, f).join(",")).join(" ") }));
  }
  axes.forEach((a, i) => {
    const [x, y] = pt(i, 1);
    root.append(svg("line", { class: "radar-grid", x1: c, y1: c, x2: x, y2: y }));
    const [lx, ly] = pt(i, 1.22);
    root.append(svg("text", { x: lx, y: ly, class: "radar-label", "text-anchor": "middle", "dominant-baseline": "middle" }, a.label));
  });
  const pts = axes.map((a, i) => pt(i, Math.max(0.02, Math.min(1, values[a.id] || 0))).join(",")).join(" ");
  root.append(svg("polygon", { class: "radar-area", points: pts }));
  el.append(root);
}
