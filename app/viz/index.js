// Visualization registry. lesson.json refers to components by name:
//   { "id": "v1", "component": "tracer", "props": {...}, "notice": "...",
//     "predictFirst": { "question": "...", "choices": [...], "answer": 1 } }
import { renderTracer } from "./tracer.js";
import { renderNmeaFields, renderXorChecksum } from "./nmea.js";

export const VIZ = {
  tracer: renderTracer,
  "nmea-fields": renderNmeaFields,
  "xor-checksum": renderXorChecksum,
};
