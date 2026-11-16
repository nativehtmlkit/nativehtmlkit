"""Project list with HTML dialogs: a confirmation dialog and a dialog that contains a form.

Teaches: show_dialog() (modal), close_dialog(element, return_value), reacting to the dialog's
"close" event and reading its return value with the "get_dialog" command (Escape closes a modal
dialog with an empty return value), and a <form> inside a dialog.
Run:     python dialogs.py
Guide:   docs/how-to/html-dialogs.md
"""
import html

from nativehtmlkit import Application

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; padding: 20px; background: #f3f5f9; color: #1c2330; }
  li { margin: 6px 0; }
  button { padding: 6px 12px; margin-right: 6px; }
  dialog { border: 1px solid #9aa6bf; border-radius: 10px; padding: 20px; background: white; }
  dialog input { width: 260px; padding: 6px; }
  .danger { background: #c0392b; color: white; border: 0; border-radius: 5px; }
  #status { color: #5a6578; }
</style></head>
<body>
  <h1 id="heading">Projects</h1>
  <ul id="projects"></ul>
  <button id="rename">Rename list...</button>
  <button id="clear" class="danger">Delete all...</button>
  <p id="status" role="status"></p>

  <dialog id="confirm" aria-labelledby="confirm-title">
    <h2 id="confirm-title">Delete all projects?</h2>
    <p>This cannot be undone.</p>
    <button id="confirm-delete" class="danger">Delete</button>
    <button id="confirm-cancel">Cancel</button>
  </dialog>

  <dialog id="rename-dialog" aria-labelledby="rename-title">
    <h2 id="rename-title">Rename the list</h2>
    <form id="rename-form">
      <input id="new-name" required maxlength="60" aria-label="New name">
      <button id="rename-save">Save</button>
      <button id="rename-cancel" type="button">Cancel</button>
    </form>
  </dialog>
</body></html>"""


def main():
    with Application.start(name="Dialogs") as app:
        window = app.open_html(PAGE, title="Projects", width=560, height=520)
        doc = window.document
        projects = ["Website refresh", "Mobile app", "Data migration"]

        def render():
            doc.replace_html("projects", "".join(f"<li>{html.escape(p)}</li>" for p in projects) or "<li>No projects</li>")

        def confirm_closed(_event):
            # Every way of closing ends here: our buttons, or Escape (empty return value).
            choice = doc.command("get_dialog", element="confirm")["return_value"]
            if choice == "delete":
                projects.clear()
                render()
                doc.set_text("status", "All projects deleted")
            else:
                doc.set_text("status", "Nothing was deleted")

        def open_rename(_event):
            doc.set_value("new-name", doc.get_text("heading"))
            doc.show_dialog("rename-dialog")
            doc.focus("new-name")

        def rename_submitted(_event):
            doc.set_text("heading", doc.get_value("new-name").strip())  # set_text: the name is not HTML
            doc.close_dialog("rename-dialog", "saved")
            doc.set_text("status", "List renamed")

        doc.on("click", lambda _e: doc.show_dialog("confirm"), element="clear")
        doc.on("click", lambda _e: doc.close_dialog("confirm", "delete"), element="confirm-delete")
        doc.on("click", lambda _e: doc.close_dialog("confirm", "cancel"), element="confirm-cancel")
        doc.on("close", confirm_closed, element="confirm")
        doc.on("click", open_rename, element="rename")
        doc.on("submit", rename_submitted, element="rename-form")
        doc.on("click", lambda _e: doc.close_dialog("rename-dialog", "cancel"), element="rename-cancel")
        render()
        app.run()


if __name__ == "__main__":
    main()
