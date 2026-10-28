// CodeMirror 5 wrapper: syntax highlighting, line numbers, 4-space indent,
// error-line marking, and an optional paste guard for No Hands checkpoints.
/* global CodeMirror */

const PASTE_LIMIT = 80;

export function createEditor(parent, { value = "", mode = "python", readOnly = false,
  onChange = null, noPaste = false, onRun = null, onSubmit = null, minLines = 6 } = {}) {
  const cm = CodeMirror(parent, {
    value,
    mode,
    readOnly,
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    matchBrackets: true,
    viewportMargin: Infinity,
    extraKeys: {
      Tab: (ed) => (ed.somethingSelected() ? ed.indentSelection("add") : ed.replaceSelection("    ", "end")),
      "Shift-Tab": (ed) => ed.indentSelection("subtract"),
      "Ctrl-Enter": () => onRun && onRun(),
      "Cmd-Enter": () => onRun && onRun(),
      "Shift-Ctrl-Enter": () => onSubmit && onSubmit(),
      "Shift-Cmd-Enter": () => onSubmit && onSubmit(),
      Esc: (ed) => ed.getInputField().blur(), // keyboard users can always leave the editor
    },
  });
  cm.getWrapperElement().classList.add(readOnly ? "cm-readonly" : "cm-editable");
  const lines = Math.max(minLines, value.split("\n").length);
  cm.getWrapperElement().style.minHeight = `${Math.min(lines, 30) * 1.5 + 1}em`;
  if (onChange) cm.on("change", () => onChange(cm.getValue()));
  if (noPaste) {
    cm.on("beforeChange", (_, change) => {
      if (change.origin === "paste" && change.text.join("\n").length > PASTE_LIMIT) {
        change.cancel();
        parent.dispatchEvent(new CustomEvent("paste-blocked", { bubbles: true }));
      }
    });
  }
  let marked = null;
  cm.markError = (lineno) => {
    if (marked !== null) cm.removeLineClass(marked, "background", "cm-error-line");
    marked = null;
    if (lineno && lineno > 0 && lineno <= cm.lineCount()) {
      marked = lineno - 1;
      cm.addLineClass(marked, "background", "cm-error-line");
    }
  };
  setTimeout(() => cm.refresh(), 0);
  return cm;
}
