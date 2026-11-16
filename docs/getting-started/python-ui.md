# Python UI — state and controls

The optional `nativehtmlkit_ui` layer is a small reactive UI library built exclusively on the public Python SDK. **UI v0.1.1 is an early (pre-1.0) release, installable with `uv add nativehtmlkit_ui` or `pip install nativehtmlkit_ui`.**

```python
from nativehtmlkit import Application
from nativehtmlkit_ui import UI, state

with Application.start(name="Counter") as app:
    count = state(0)
    ui = UI(title="Counter", theme="cobalt", density="compact")
    with ui.column():
        ui.heading("Native counter")
        ui.text(lambda: f"Count: {count.value}")
        ui.button("+1", on_click=lambda e: count.set(count.value + 1))
    ui.mount(app)
    app.run()
```

The UI library binds state changes to SDK document updates. Build layouts before `ui.mount(app)`; use `ui.post()` to deliver worker-thread results to the owning UI thread. There is a known concurrent computed-state issue: see [limitations](../capabilities/limitations.md).

For a complete gallery with inputs, conditional regions, select and text lists use [Python UI gallery](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/python-ui/gallery.py). For native dialogs use the SDK outside the managed component tree.
