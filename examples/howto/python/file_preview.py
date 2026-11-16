"""Text file preview: pick a file with the native open dialog, preview it, save a copy elsewhere.

Teaches: Window.open_files() and Window.save_file() with wait=False (the event worker stays free
while the dialog is open), file-type filters, handling cancel (an empty result), and showing
untrusted file content safely with set_text().
Run:     python file_preview.py [FILE]      (FILE is shown at start, without a dialog)
Guide:   docs/how-to/file-dialogs.md
"""
import shutil
import sys
from pathlib import Path

from nativehtmlkit import Application, RpcError

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 14px sans-serif; margin: 0; padding: 16px; background: #f4f6fa; color: #1d2433; }
  .bar { display: flex; gap: 8px; align-items: center; }
  button { padding: 6px 12px; }
  #name { font-weight: 600; }
  pre { background: white; border: 1px solid #d5dbe8; border-radius: 6px; padding: 10px; height: 360px;
        overflow: auto; white-space: pre-wrap; }
  #status { color: #5a6578; }
</style></head>
<body>
  <div class="bar"><button id="open">Open...</button><button id="save" disabled>Save a copy...</button>
    <span id="name">No file</span></div>
  <pre id="content"></pre>
  <p id="status" role="status">Choose a text file to preview its first 200 lines.</p>
</body></html>"""

FILTERS = [{"name": "Text files", "extensions": ["txt", "md", "log", "csv", "json", "py", "ps1"]},
           {"name": "All files", "extensions": ["*"]}]


def main():
    with Application.start(name="File preview") as app:
        window = app.open_html(PAGE, title="File preview", width=760, height=560)
        doc = window.document
        current = {"path": None}

        def show(path):
            path = Path(path)
            try:
                with path.open(encoding="utf-8", errors="replace") as stream:
                    lines = [line for _, line in zip(range(200), stream)]
            except OSError as error:
                doc.set_text("status", f"Cannot read {path.name}: {error.strerror}")
                return
            current["path"] = path
            doc.set_text("name", path.name)
            doc.set_text("content", "".join(lines))  # text content: never interpreted as HTML
            doc.set_text("status", f"{path.stat().st_size:,} bytes; showing {len(lines)} lines")
            doc.remove_attribute("save", "disabled")

        def opened(future):
            # Runs on a completion thread once the dialog closes; SDK calls are allowed here.
            try:
                result = future.result()  # {"cancelled": bool, "paths": [...]}
            except RpcError as error:  # for example: no native dialogs in headless mode
                doc.set_text("status", f"The file dialog is not available: {error}")
                return
            if result["cancelled"] or not result["paths"]:
                doc.set_text("status", "Cancelled")
            else:
                show(result["paths"][0])

        def saved(future):
            try:
                result = future.result()  # the same shape: one path unless cancelled
            except RpcError as error:
                doc.set_text("status", f"The save dialog is not available: {error}")
                return
            if result["cancelled"] or not result["paths"]:
                doc.set_text("status", "Cancelled")
                return
            target = Path(result["paths"][0])
            try:
                shutil.copyfile(current["path"], target)
            except OSError as error:
                doc.set_text("status", f"Not saved: {error.strerror}")
                return
            doc.set_text("status", f"Saved a copy as {target.name}")

        doc.on("click", lambda _e: window.open_files(title="Open a text file", filters=FILTERS, wait=False)
               .add_done_callback(opened), element="open")
        doc.on("click", lambda _e: window.save_file(title="Save a copy", file_name=current["path"].name, wait=False)
               .add_done_callback(saved), element="save")
        if len(sys.argv) > 1:
            show(sys.argv[1])
        app.run()


if __name__ == "__main__":
    main()
