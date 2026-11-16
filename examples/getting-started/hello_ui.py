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
