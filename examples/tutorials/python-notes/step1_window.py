"""Notes tutorial, step 1: open a native window and render a list from Python data.

Teaches: Application.start(), open_html(), building HTML from data with html.escape(), app.run().
Run:     python step1_window.py
Guide:   docs/tutorials/python-notes.md (step 1 of 4)
"""
import html

from nativehtmlkit import Application

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; background: #f4f6fb; color: #1d2433; }
  main { padding: 20px 24px; }
  h1 { font-size: 22px; margin: 0 0 12px; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { background: white; border: 1px solid #d5dbe8; border-radius: 8px; padding: 10px 12px; margin: 6px 0; }
  .done { color: #7a8396; text-decoration: line-through; }
</style></head>
<body><main>
  <h1>Notes</h1>
  <ul id="notes"></ul>
</main></body></html>"""

SAMPLE_NOTES = [
    {"id": 1, "text": "Read the NativeHTMLKit tutorial", "done": True},
    {"id": 2, "text": "Build a notes app", "done": False},
]


def render_note(note):
    css = "note done" if note["done"] else "note"
    return f'<li class="{css}" id="note-{note["id"]}">{html.escape(note["text"])}</li>'


def main():
    with Application.start(name="Notes") as app:
        window = app.open_html(PAGE, title="Notes", width=520, height=600)
        window.document.replace_html("notes", "".join(render_note(n) for n in SAMPLE_NOTES))
        app.run()


if __name__ == "__main__":
    main()
