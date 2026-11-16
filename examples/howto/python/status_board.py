"""Status board: change parts of a live page without reloading it.

Teaches: set_text() for untrusted text, set_attribute(), add_class()/remove_class(),
batch() to apply several changes as one transaction, query() to find elements by CSS selector,
remove(), and insert_html() with escaped values.
Run:     python status_board.py
Guide:   docs/how-to/update-the-page.md
"""
import html
import itertools
import time

from nativehtmlkit import Application

SERVICES = {"api": "Public API", "web": "Web shop", "mail": "Mail relay"}
STATES = ("ok", "degraded", "down")

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; background: #f3f5f9; color: #1c2330; }
  main { padding: 20px; max-width: 640px; }
  .service { display: flex; justify-content: space-between; align-items: center; background: white;
             border: 1px solid #d6dce8; border-radius: 8px; padding: 10px 14px; margin: 6px 0; }
  .pill { border-radius: 999px; padding: 2px 10px; font-size: 13px; background: #dfe6f1; }
  .ok .pill { background: #d5f0dc; color: #1d6b34; }
  .degraded .pill { background: #fbecc8; color: #7a5300; }
  .down .pill { background: #f8d6d6; color: #8a1f1f; }
  .note { color: #5a6578; font-size: 13px; }
  form { display: flex; gap: 8px; flex-wrap: wrap; margin: 14px 0; }
  input, select, button { padding: 6px 8px; }
  #history li { font-size: 13px; color: #5a6578; }
</style></head>
<body><main>
  <h1>Service status</h1>
  <div id="services">%(services)s</div>
  <form id="update">
    <select id="service" aria-label="Service">%(service_options)s</select>
    <select id="state" aria-label="Status">%(state_options)s</select>
    <input id="note" placeholder="Note (optional)" aria-label="Note" maxlength="120">
    <button id="apply">Update</button>
    <button id="clear" type="button">Clear history</button>
  </form>
  <h2>History</h2>
  <ul id="history"></ul>
</main></body></html>"""


def build_page():
    services = "".join(
        f'<div class="service ok" id="svc-{key}"><div><strong>{html.escape(name)}</strong>'
        f'<div class="note" id="note-{key}"></div></div><span class="pill" id="pill-{key}">ok</span></div>'
        for key, name in SERVICES.items())
    return PAGE % {
        "services": services,
        "service_options": "".join(f'<option value="{k}">{html.escape(v)}</option>' for k, v in SERVICES.items()),
        "state_options": "".join(f"<option>{s}</option>" for s in STATES),
    }


def main():
    with Application.start(name="Status board") as app:
        window = app.open_html(build_page(), title="Status board", width=700, height=640)
        doc = window.document
        entry_ids = itertools.count(1)

        def update(_event):
            key, state = doc.get_value("service"), doc.get_value("state")
            note = doc.get_value("note").strip()
            # One atomic transaction: the page never shows a half-updated row.
            operations = [{"op": "remove_class", "element": f"svc-{key}", "name": s} for s in STATES]
            operations += [
                {"op": "add_class", "element": f"svc-{key}", "name": state},
                {"op": "set_text", "element": f"pill-{key}", "text": state},
                {"op": "set_text", "element": f"note-{key}", "text": note},  # text, never parsed as HTML
                {"op": "set_attribute", "element": f"svc-{key}", "name": "title",
                 "value": f"Changed {time.strftime('%H:%M:%S')}"},
            ]
            doc.batch(operations)
            entry = f"{time.strftime('%H:%M:%S')} {SERVICES[key]}: {state}" + (f" ({note})" if note else "")
            doc.insert_html("history", f'<li id="h-{next(entry_ids)}">{html.escape(entry)}</li>', position="afterbegin")
            doc.set_value("note", "")

        def clear(_event):
            for element in doc.query("#history li")["ids"]:
                doc.remove(element)

        doc.on("submit", update, element="update")
        doc.on("click", clear, element="clear")
        app.run()


if __name__ == "__main__":
    main()
