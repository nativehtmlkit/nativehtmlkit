"""Notes tutorial, step 2: add notes with a form.

Teaches: an HTML <form> with a required field, the "submit" event, reading a control with
get_value(), appending escaped HTML with insert_html(), clearing and focusing the field.
Run:     python step2_add.py
Guide:   docs/tutorials/python-notes.md (step 2 of 4)
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
  li { background: white; border: 1px solid #d5dbe8; border-radius: 8px; padding: 10px 12px; margin: 6px 0; }
</style></head>
<body><main>
  <h1>Notes</h1>
  <form id="add-form">
    <input id="new-note" name="text" required maxlength="200" placeholder="What do you need to remember?"
           aria-label="New note">
    <button id="add">Add</button>
  </form>
  <ul id="notes"></ul>
  <p id="summary">0 notes</p>
</main></body></html>"""


def main():
    with Application.start(name="Notes") as app:
        window = app.open_html(PAGE, title="Notes", width=520, height=600)
        doc = window.document
        notes = []

        def add_note(_event):
            # The form only submits when its "required" field is filled in.
            text = doc.get_value("new-note").strip()
            if not text:
                return
            notes.append(text)
            doc.insert_html("notes", f"<li>{html.escape(text)}</li>")  # never insert raw user text
            doc.set_text("summary", f"{len(notes)} notes")
            doc.set_value("new-note", "")
            doc.focus("new-note")

        doc.on("submit", add_note, element="add-form")
        doc.focus("new-note")
        app.run()


if __name__ == "__main__":
    main()
