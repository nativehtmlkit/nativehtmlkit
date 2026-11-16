# HTML dialogs

**Goal:** ask for confirmation or a small piece of input in an in-window `<dialog>`, without a native message box.

- `show_dialog(id)` shows a `<dialog>` modally by default (the rest of the page becomes inert and focus moves into the dialog); `show_dialog(id, modal=False)` shows it non-modally. PowerShell: `Show-NativeHTMLKitHtmlDialog -Element id [-Modal $false]`.
- `close_dialog(id, return_value)` closes it and sets its return value. PowerShell: `Show-NativeHTMLKitHtmlDialog -Element id -Close -ReturnValue ...`.
- When a dialog closes, for any reason, it fires a `close` event. Read the return value with the `get_dialog` document command (`{"open", "modal", "return_value"}`). Escape closes a modal dialog with an empty return value, so treat anything except your "yes" value as "no".
- The `<form method="dialog">` shortcut of browsers is not used here: give the dialog's buttons ids and call `close_dialog` from their click handlers, or handle a form's `submit` inside the dialog yourself.
- Popovers work the same way: `show_popover`, `hide_popover`, `toggle_popover` (PowerShell `Show-NativeHTMLKitPopover -Action show|hide|toggle`).

## Example

<!-- include: examples/howto/python/dialogs.py -->
```python title="examples/howto/python/dialogs.py"
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
```
<!-- /include -->

<!-- screenshot: howto-dialogs -->

- One `close` handler decides for the confirmation dialog, whichever way it was closed.
- The rename dialog contains a form; Enter in the field submits it, and `required` stops an empty name.
- The new name is set with `set_text`, so it is never parsed as HTML.

## PowerShell

The [PowerShell SDK gallery](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/powershell-sdk/gallery.ps1) opens and closes a dialog and a popover with `Show-NativeHTMLKitHtmlDialog` and `Show-NativeHTMLKitPopover`. Read the return value with `Invoke-NativeHTMLKitDocumentCommand -Operation get_dialog -Parameters @{ element = 'confirm' }`.

The UI libraries have no dialog component; use these SDK calls on the UI's document.
