"""Notes: a small persistent notes app built with the NativeHTMLKit Python SDK (tutorial final code).

Teaches: a form with validation and the "submit" event, a delegated "click" handler, a live
"input" filter, re-rendering escaped HTML from a Python model, and saving the model to a JSON file
with an atomic replace.
Run:     python notes.py [NOTES_FILE]
         (default file: .nativehtmlkit-notes.json in your home directory)
Guide:   docs/tutorials/python-notes.md (step 4 of 4)
"""
import html
import json
import os
import sys
import tempfile
from pathlib import Path

from nativehtmlkit import Application

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; background: #f4f6fb; color: #1d2433; }
  main { padding: 20px 24px; }
  h1 { font-size: 22px; margin: 0 0 12px; }
  form { display: flex; gap: 8px; margin-bottom: 12px; }
  input { padding: 8px; border: 1px solid #9aa6bf; border-radius: 6px; }
  #new-note { flex: 1; }
  #filter { width: 100%; box-sizing: border-box; margin-bottom: 8px; }
  button { padding: 8px 14px; border: 0; border-radius: 6px; background: #2f6fd0; color: white; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { display: flex; align-items: center; gap: 8px; background: white; border: 1px solid #d5dbe8;
       border-radius: 8px; padding: 8px 12px; margin: 6px 0; }
  li .text { flex: 1; }
  li.done .text { color: #7a8396; text-decoration: line-through; }
  li.empty { color: #7a8396; justify-content: center; }
  li button { padding: 4px 10px; background: #e3e8f3; color: #1d2433; }
  li button.danger { background: #f6dede; color: #8a1f1f; }
  #status { color: #8a1f1f; min-height: 1.2em; }
</style></head>
<body><main>
  <h1>Notes</h1>
  <form id="add-form">
    <input id="new-note" name="text" required maxlength="200" placeholder="What do you need to remember?"
           aria-label="New note">
    <button id="add">Add</button>
  </form>
  <input id="filter" type="search" placeholder="Filter notes" aria-label="Filter notes">
  <ul id="notes"></ul>
  <p id="summary"></p>
  <p id="status" role="status"></p>
</main></body></html>"""


class NoteStore:
    """Loads and saves the notes list as JSON. A save never leaves a half-written file."""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        return [{"id": int(n["id"]), "text": str(n["text"]), "done": bool(n["done"])}
                for n in data.get("notes", [])]

    def save(self, notes: list) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".notes-", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump({"version": 1, "notes": notes}, stream, indent=2)
            os.replace(temporary, self.path)
        except BaseException:
            os.unlink(temporary)
            raise


def render_note(note):
    css = "done" if note["done"] else ""
    label = "Undo" if note["done"] else "Done"
    return (f'<li class="{css}" id="note-{note["id"]}">'
            f'<span class="text">{html.escape(note["text"])}</span>'
            f'<button id="done-{note["id"]}">{label}</button>'
            f'<button id="delete-{note["id"]}" class="danger">Delete</button></li>')


def main():
    # Application.start() runs this script twice; everything with side effects comes after it.
    with Application.start(name="Notes") as app:
        path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".nativehtmlkit-notes.json"
        store = NoteStore(path)
        window = app.open_html(PAGE, title="Notes", width=520, height=640)
        doc = window.document
        try:
            notes = store.load()
        except (OSError, ValueError, KeyError, TypeError) as error:
            notes = []
            doc.set_text("status", f"Could not read {path.name}: {error}")

        def refresh():
            needle = doc.get_value("filter").strip().casefold()
            shown = [n for n in notes if needle in n["text"].casefold()]
            empty = '<li class="empty">No matching notes.</li>' if notes else '<li class="empty">No notes yet.</li>'
            doc.replace_html("notes", "".join(render_note(n) for n in shown) or empty)
            remaining = sum(1 for n in notes if not n["done"])
            doc.set_text("summary", f"{len(notes)} notes, {remaining} open")

        def save():
            try:
                store.save(notes)
                doc.set_text("status", "")
            except OSError as error:
                doc.set_text("status", f"Not saved: {error.strerror}")

        def add_note(_event):
            text = doc.get_value("new-note").strip()
            if not text:
                return
            next_id = max((n["id"] for n in notes), default=0) + 1
            notes.append({"id": next_id, "text": text, "done": False})
            save()
            refresh()
            doc.set_value("new-note", "")
            doc.focus("new-note")

        def list_clicked(event):
            action, _, note_id = (event.get("element") or "").partition("-")
            note = next((n for n in notes if str(n["id"]) == note_id), None)
            if note is None:
                return
            if action == "done":
                note["done"] = not note["done"]
            elif action == "delete":
                notes.remove(note)
            else:
                return
            save()
            refresh()

        doc.on("submit", add_note, element="add-form")
        doc.on("click", list_clicked, element="notes")
        doc.on("input", lambda _event: refresh(), element="filter")
        refresh()
        doc.focus("new-note")
        app.run()


if __name__ == "__main__":
    main()
