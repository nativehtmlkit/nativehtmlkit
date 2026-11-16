"""Notes tutorial, step 3: mark notes done and delete them.

Teaches: keeping the data model in Python and re-rendering the list from it, one delegated "click"
handler for many buttons (event["element"] is the id of the clicked element), stable element ids.
Run:     python step3_actions.py
Guide:   docs/tutorials/python-notes.md (step 3 of 4)
"""
import html

from nativehtmlkit import Application

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; background: #f4f6fb; color: #1d2433; }
  main { padding: 20px 24px; }
  h1 { font-size: 22px; margin: 0 0 12px; }
  form { display: flex; gap: 8px; margin-bottom: 12px; }
  input { flex: 1; padding: 8px; border: 1px solid #9aa6bf; border-radius: 6px; }
  button { padding: 8px 14px; border: 0; border-radius: 6px; background: #2f6fd0; color: white; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { display: flex; align-items: center; gap: 8px; background: white; border: 1px solid #d5dbe8;
       border-radius: 8px; padding: 8px 12px; margin: 6px 0; }
  li .text { flex: 1; }
  li.done .text { color: #7a8396; text-decoration: line-through; }
  li button { padding: 4px 10px; background: #e3e8f3; color: #1d2433; }
  li button.danger { background: #f6dede; color: #8a1f1f; }
</style></head>
<body><main>
  <h1>Notes</h1>
  <form id="add-form">
    <input id="new-note" name="text" required maxlength="200" placeholder="What do you need to remember?"
           aria-label="New note">
    <button id="add">Add</button>
  </form>
  <ul id="notes"></ul>
  <p id="summary"></p>
</main></body></html>"""


def render_note(note):
    css = "done" if note["done"] else ""
    label = "Undo" if note["done"] else "Done"
    return (f'<li class="{css}" id="note-{note["id"]}">'
            f'<span class="text">{html.escape(note["text"])}</span>'
            f'<button id="done-{note["id"]}">{label}</button>'
            f'<button id="delete-{note["id"]}" class="danger">Delete</button></li>')


def main():
    with Application.start(name="Notes") as app:
        window = app.open_html(PAGE, title="Notes", width=520, height=600)
        doc = window.document
        notes = []

        def refresh():
            doc.replace_html("notes", "".join(render_note(n) for n in notes))
            remaining = sum(1 for n in notes if not n["done"])
            doc.set_text("summary", f"{len(notes)} notes, {remaining} open")

        def add_note(_event):
            text = doc.get_value("new-note").strip()
            if not text:
                return
            next_id = max((n["id"] for n in notes), default=0) + 1
            notes.append({"id": next_id, "text": text, "done": False})
            refresh()
            doc.set_value("new-note", "")
            doc.focus("new-note")

        def list_clicked(event):
            # One handler for every button in the list: "done-3" or "delete-3".
            action, _, note_id = (event.get("element") or "").partition("-")
            note = next((n for n in notes if str(n["id"]) == note_id), None)
            if note is None:
                return
            if action == "done":
                note["done"] = not note["done"]
            elif action == "delete":
                notes.remove(note)
            refresh()

        doc.on("submit", add_note, element="add-form")
        doc.on("click", list_clicked, element="notes")
        refresh()
        app.run()


if __name__ == "__main__":
    main()
