"""Clipboard text tool: paste text, transform it, copy the result back.

Teaches: Application.clipboard_text() and set_clipboard_text(), checking Application.capabilities()
for clipboard support, handling a failing clipboard request (RpcError) without crashing, and a <form> whose submit
applies the selected transformation.
Run:     python clipboard_tool.py
Guide:   docs/how-to/clipboard.md
"""
import json

from nativehtmlkit import Application, RpcError

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 14px sans-serif; margin: 0; padding: 16px; background: #f4f6fa; color: #1d2433; }
  textarea { width: 100%; box-sizing: border-box; height: 140px; font: 13px monospace; padding: 8px; }
  .bar { display: flex; gap: 8px; align-items: center; margin: 8px 0; }
  button, select { padding: 6px 10px; }
  #status { color: #5a6578; min-height: 1.2em; }
</style></head>
<body>
  <form id="tool">
    <label for="input">Input</label>
    <textarea id="input" placeholder="Paste or type text here"></textarea>
    <div class="bar">
      <button id="paste" type="button">Paste from clipboard</button>
      <select id="transform" aria-label="Transformation">
        <option value="upper">UPPER CASE</option><option value="lower">lower case</option>
        <option value="sort">Sort lines</option><option value="unique">Remove duplicate lines</option>
        <option value="json">Pretty-print JSON</option>
      </select>
      <button id="apply">Transform</button>
    </div>
    <label for="output">Result</label>
    <textarea id="output" readonly></textarea>
    <div class="bar"><button id="copy" type="button">Copy result</button></div>
  </form>
  <p id="status" role="status"></p>
</body></html>"""


def transform(kind, text):
    lines = text.splitlines()
    if kind == "upper":
        return text.upper()
    if kind == "lower":
        return text.lower()
    if kind == "sort":
        return "\n".join(sorted(lines, key=str.casefold))
    if kind == "unique":
        return "\n".join(dict.fromkeys(lines))
    if kind == "json":
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    raise ValueError(kind)


def main():
    with Application.start(name="Clipboard tool") as app:
        window = app.open_html(PAGE, title="Clipboard tool", width=620, height=560)
        doc = window.document

        def apply(_event):
            try:
                result = transform(doc.get_value("transform"), doc.get_value("input"))
            except ValueError as error:  # json.JSONDecodeError is a ValueError
                doc.set_text("status", f"Cannot transform: {error}")
                return
            doc.set_value("output", result)
            doc.set_text("status", f"{len(result)} characters")

        def paste(_event):
            try:
                doc.set_value("input", app.clipboard_text())
                doc.set_text("status", "Pasted from the clipboard")
            except RpcError as error:  # for example code -32001 when this session has no clipboard
                doc.set_text("status", f"The clipboard is not available here ({error})")

        def copy(_event):
            try:
                app.set_clipboard_text(doc.get_value("output"))
                doc.set_text("status", "Copied the result to the clipboard")
            except RpcError as error:
                doc.set_text("status", f"The clipboard is not available here ({error})")

        # "available" is False when the host knows there is no clipboard (headless test mode) and
        # None on a desktop, where only the actual request can tell; so test for False explicitly.
        clipboard = app.capabilities().get("features", {}).get("clipboard_text", {})
        if clipboard.get("available") is False:
            for button in ("paste", "copy"):
                doc.set_attribute(button, "disabled", "")
            doc.set_text("status", "The clipboard is not available in this session; transformations still work.")

        doc.on("submit", apply, element="tool")
        doc.on("click", paste, element="paste")
        doc.on("click", copy, element="copy")
        app.run()


if __name__ == "__main__":
    main()
