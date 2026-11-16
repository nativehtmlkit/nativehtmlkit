# Python UI in five minutes

`nativehtmlkit_ui` is a small reactive component library built on the public Python SDK. You describe the window with `ui.heading()`, `ui.input()`, `ui.button()` and friends; values that change are `state()` objects, and anything bound to them updates by itself. UI 0.1.1 is an early release.

## 1. Install

```bash
python -m pip install nativehtmlkit_ui    # installs the nativehtmlkit SDK as a dependency
```

## 2. Write `hello_ui.py`

<!-- include: examples/getting-started/hello_ui.py -->
```python title="examples/getting-started/hello_ui.py"
"""Hello, NativeHTMLKit UI: a reactive counter with nativehtmlkit_ui.

Teaches: state(), a text bound to a lambda, buttons, ui.mount(app), ui.dispose().
Run:     python hello_ui.py
Guide:   docs/getting-started/python-ui.md
"""
from nativehtmlkit import Application
from nativehtmlkit_ui import UI, state


def main():
    with Application.start(name="Counter") as app:
        count = state(0)
        ui = UI(title="Counter", theme="cobalt", density="regular", width=420, height=300)
        with ui.column():
            ui.heading("Counter", level=1)
            ui.text(lambda: f"Count: {count.value}")  # re-rendered whenever count changes
            with ui.row():
                ui.button("+1", on_click=lambda _e: count.set(count.value + 1))
                ui.button("Reset", variant="secondary", on_click=lambda _e: count.set(0))
        try:
            ui.mount(app)  # build the tree first, then mount it into a window
            app.run()
        finally:
            ui.dispose()


if __name__ == "__main__":
    main()
```
<!-- /include -->

## 3. Run it

```bash
python hello_ui.py
```

<!-- screenshot: getting-started-hello-python-ui -->

## What just happened

- `state(0)` is an observable value. `count.set(...)` changes it; reading `count.value` inside a lambda passed to `ui.text()` makes that text depend on it.
- The `with ui.column():` / `with ui.row():` blocks build a tree. Build the whole tree **before** `ui.mount(app)`; after mounting, change state instead of adding components.
- `ui.mount(app)` opens the window through the SDK; `app.run()` is the same event loop as in the [SDK quick start](python.md).
- `ui.dispose()` releases bindings and the UI's owner thread.

Themes: `cobalt` (default), `graphite`, `daylight`; densities: `compact`, `regular`, `comfortable`. See [Theme the UI library](../how-to/theming-ui.md).

## Next steps

- Tutorial: [an expense tracker with computed totals](../tutorials/python-ui-expenses.md).
- Need a file dialog, a second window or a bitmap? Use the SDK next to the UI: `ui.window` and `ui.document` are ordinary SDK objects after `mount`.
- Exact API: [UI reference](https://github.com/nativehtmlkit/nativehtmlkit_ui/blob/main/docs/API.md).
