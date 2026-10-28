// Canvas renderer and playback controls for simulator runs (frames come from
// pfr_sim.run via the Python worker). Colors follow the site conventions:
// x red, y green, ground truth solid dark, estimates dashed orange.
import { h, button } from "../ui.js";

function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function createSimView(parent) {
  const canvas = h("canvas", { class: "sim-canvas", width: 800, height: 600, role: "img", "aria-label": "Robot simulator view" });
  const slider = h("input", { type: "range", min: 0, max: 0, value: 0, "aria-label": "Simulation time" });
  const info = h("span", { class: "muted" }, "Run your code to see the robot.");
  let data = null;
  let index = 0;
  let timer = null;

  const stop = () => { if (timer) cancelAnimationFrame(timer); timer = null; };
  function play() {
    if (!data) return;
    stop();
    let last = performance.now();
    const tick = (now) => {
      if (now - last >= data.dt * 1000) {
        last = now;
        if (index >= data.frames.length - 1) return stop();
        show(index + 1);
      }
      timer = requestAnimationFrame(tick);
    };
    timer = requestAnimationFrame(tick);
  }

  function show(i) {
    if (!data) return;
    index = Math.max(0, Math.min(i, data.frames.length - 1));
    slider.value = index;
    draw();
    const f = data.frames[index];
    info.textContent = `t = ${f.t.toFixed(2)} s   x = ${f.x.toFixed(2)}  y = ${f.y.toFixed(2)}  θ = ${f.th.toFixed(2)} rad   ` +
      `range = [${f.ranges.map((r) => r.toFixed(2)).join(", ")}]` +
      (data.collided ? "   ⚠ collision occurred" : "") + (data.reachedGoal ? `   ✓ goal at ${data.timeToGoal}s` : "");
  }

  function draw() {
    const ctx = canvas.getContext("2d");
    const w = data.world;
    const scale = Math.min(canvas.width / w.width, canvas.height / w.height);
    const X = (x) => x * scale;
    const Y = (y) => canvas.height - y * scale;
    ctx.fillStyle = css("--sim-floor");
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // line track
    if (w.line && w.line.length > 1) {
      ctx.strokeStyle = css("--sim-line");
      ctx.lineWidth = Math.max(2, 0.024 * scale);
      ctx.beginPath();
      w.line.forEach(([x, y], k) => (k ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y))));
      ctx.stroke();
    }
    // walls + border
    ctx.strokeStyle = css("--sim-wall");
    ctx.lineWidth = 4;
    ctx.strokeRect(1, 1, X(w.width) - 2, canvas.height - 2);
    for (const [x1, y1, x2, y2] of w.walls) {
      ctx.beginPath(); ctx.moveTo(X(x1), Y(y1)); ctx.lineTo(X(x2), Y(y2)); ctx.stroke();
    }
    ctx.fillStyle = css("--sim-wall");
    for (const [x, y, r] of w.obstacles) {
      ctx.beginPath(); ctx.arc(X(x), Y(y), r * scale, 0, 2 * Math.PI); ctx.fill();
    }
    if (w.goal) {
      ctx.strokeStyle = css("--ok");
      ctx.setLineDash([6, 4]);
      ctx.beginPath(); ctx.arc(X(w.goal[0]), Y(w.goal[1]), w.goal[2] * scale, 0, 2 * Math.PI); ctx.stroke();
      ctx.setLineDash([]);
    }
    // ground-truth path so far
    ctx.strokeStyle = css("--truth");
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.frames.slice(0, index + 1).forEach((f, k) => (k ? ctx.lineTo(X(f.x), Y(f.y)) : ctx.moveTo(X(f.x), Y(f.y))));
    ctx.stroke();
    // GPS fixes (noisy measurements)
    ctx.fillStyle = css("--estimate");
    data.frames.slice(0, index + 1).forEach((f) => {
      if (f.gps) { ctx.beginPath(); ctx.arc(X(f.gps[0]), Y(f.gps[1]), 3, 0, 2 * Math.PI); ctx.fill(); }
    });
    // robot + range beams
    const f = data.frames[index];
    const angles = [-Math.PI / 2, -Math.PI / 4, 0, Math.PI / 4, Math.PI / 2];
    ctx.strokeStyle = css("--beam");
    ctx.lineWidth = 1;
    f.ranges.forEach((r, k) => {
      const a = f.th + angles[k];
      ctx.beginPath(); ctx.moveTo(X(f.x), Y(f.y)); ctx.lineTo(X(f.x + r * Math.cos(a)), Y(f.y + r * Math.sin(a))); ctx.stroke();
    });
    ctx.fillStyle = css("--robot");
    ctx.beginPath(); ctx.arc(X(f.x), Y(f.y), 0.09 * scale, 0, 2 * Math.PI); ctx.fill();
    // body axes: x red (heading), y green
    const axis = (dx, dy, color) => {
      ctx.strokeStyle = color; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(X(f.x), Y(f.y));
      ctx.lineTo(X(f.x + 0.14 * dx), Y(f.y + 0.14 * dy)); ctx.stroke();
    };
    axis(Math.cos(f.th), Math.sin(f.th), css("--axis-x"));
    axis(-Math.sin(f.th), Math.cos(f.th), css("--axis-y"));
  }

  slider.addEventListener("input", () => { stop(); show(Number(slider.value)); });
  parent.append(h("div", { class: "sim-view" }, canvas,
    h("div", { class: "row" }, button("▶ Play", play, "btn primary"), button("Pause", stop),
      button("⏮", () => { stop(); show(0); }, "btn", { "aria-label": "Rewind" }),
      button("Step", () => { stop(); show(index + 1); }), slider),
    info,
    h("div", { class: "legend" },
      h("span", { class: "key truth" }, "true path"), h("span", { class: "key estimate" }, "GPS fixes (noisy)"),
      h("span", { class: "key axis-x" }, "robot x axis (heading)"), h("span", { class: "key axis-y" }, "robot y axis"))));

  return {
    load(result) {
      stop();
      data = result;
      slider.max = Math.max(0, result.frames.length - 1);
      const w = result.world;
      canvas.height = Math.round(canvas.width * (w.height / w.width));
      show(0);
    },
    play,
  };
}
