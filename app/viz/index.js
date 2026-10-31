// Visualization registry. lesson.json refers to components by name:
//   { "id": "v1", "component": "tracer", "props": {...}, "notice": "...",
//     "predictFirst": { "question": "...", "reveal": "..." } }
// Each component is render(el, props, gate). When gate (the predict-first box)
// is given, the component shows its code/inputs, puts the gate right after
// them, hides only its interactive part, and returns an unlock() function.
import { renderTracer } from "./tracer.js";
import { renderNmeaFields, renderXorChecksum } from "./nmea.js";

export const VIZ = {
  tracer: renderTracer,
  "nmea-fields": renderNmeaFields,
  "xor-checksum": renderXorChecksum,
};
