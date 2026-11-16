# Python SDK in five minutes

## 1. Install

```bash
python -m pip install nativehtmlkit      # or: uv add nativehtmlkit
nativehtmlkit-python doctor              # optional: check the bundled host on this desktop
```

You need Python 3.10+ on Linux (KDE Plasma, Wayland; glibc 2.39+) or Windows x64. See [requirements](requirements.md).

## 2. Write `hello.py`

<!-- include: examples/getting-started/hello.py -->
```python title="examples/getting-started/hello.py"
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
```
<!-- /include -->

## 3. Run it

```bash
python hello.py
```

A native window opens. Click the button: the host sends a `click` event to your callback, which replaces the paragraph's text with `set_text()`. Close the window to end the program.

<!-- screenshot: getting-started-hello-python -->

## What just happened

- `Application.start()` started the native host, and the host ran `hello.py` **again** as its backend. In the first run the call never returns (the process waits for the host and exits with its status); in the second run it returns the connected `Application`. Code before `start()` runs twice, so keep work inside `main()` after it.
- `open_html()` created a window and loaded the page. Element ids (`greet`, `status`) are how Python addresses parts of the page.
- `document.on("click", callback, element="greet")` subscribes to clicks on that element or anything inside it.
- `set_text()` changes text safely: the text is never parsed as HTML.
- `app.run()` tells the host the app is ready and waits until the user closes the window.

Prefer not to have the script re-executed? Run a function in a managed backend instead: `nativehtmlkit-python run module:main` calls `main(app)` with a connected application.

## Next steps

- Tutorial: [build a notes app with persistence](../tutorials/python-notes.md).
- How-to: [handle events](../how-to/handle-events.md), [update the page](../how-to/update-the-page.md), [forms](../how-to/forms.md).
- Start a new project with files laid out for you: `nativehtmlkit-new my-app` (see [Distribute your app](../how-to/distribute.md)).
- Exact API: [Python SDK reference](https://github.com/nativehtmlkit/nativehtmlkit-python/blob/main/docs/API.md).
