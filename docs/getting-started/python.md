# Python — your first native window

## Install

```bash
uv add nativehtmlkit
# alternatively: python -m pip install nativehtmlkit
nativehtmlkit-python doctor
```

Requires Python 3.10+, a GUI desktop and a wheel for your OS. **Linux released wheel glibc floor: 2.39.** If installation cannot find a compatible wheel, do not fall back to the host-less source package and expect a GUI to work.

## Save `hello.py`

```python
from nativehtmlkit import Application

def main():
    with Application.start(name="First NativeHTMLKit app") as app:
        window = app.open_html('<main style="padding:24px"><h1>Hello</h1><button id="go">Click me</button><p id="status">Ready</p></main>')
        window.document.on("click", lambda event: window.document.set_text("status", "Hello from Python!"), element="go")
        app.run()

if __name__ == "__main__":
    main()
```

```bash
python hello.py
```

Click the button: the host sends the event to Python, which updates the displayed document. `Application.start()` may execute the script twice (supervisor and backend); avoid top-level side effects before it. The alternate `python -m nativehtmlkit run module:main` accepts a backend `main(app)` instead.

**Next:** [Interactive Python SDK gallery](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/python-sdk/gallery.py) or [Python UI state tutorial](python-ui.md). Exact API: [Python SDK](https://github.com/nativehtmlkit/nativehtmlkit-python/blob/main/docs/API.md).
