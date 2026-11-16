"""Hello, NativeHTMLKit: your first native window from Python.

Teaches: Application.start(), open_html(), a click handler, set_text(), app.run().
Run:     python hello.py
Guide:   docs/getting-started/python.md
"""
from nativehtmlkit import Application

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 16px sans-serif; margin: 0; padding: 32px; }
  button { padding: 8px 16px; }
</style></head>
<body>
  <h1>Hello from Python</h1>
  <button id="greet">Say hello</button>
  <p id="status">Not clicked yet.</p>
</body></html>"""


def main():
    # Application.start() starts the native host, which runs this script again as its backend.
    # Keep everything with side effects inside main(), after start().
    with Application.start(name="Hello") as app:
        window = app.open_html(PAGE, title="Hello", width=480, height=320)
        clicks = 0

        def greet(_event):
            nonlocal clicks
            clicks += 1
            window.document.set_text("status", f"Hello! You clicked {clicks} time(s).")

        window.document.on("click", greet, element="greet")
        app.run()  # announce "ready" and handle events until the window is closed


if __name__ == "__main__":
    main()
