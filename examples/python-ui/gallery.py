"""NativeHTMLKit Python UI gallery. Run: python examples/python-ui/gallery.py.

UI gallery includes only actual public components; SDK HTML dialogs are separate.
"""
from nativehtmlkit import Application
from nativehtmlkit_ui import UI, state, computed


def main():
    with Application.start(name="NativeHTMLKit UI Demo", instance="multiple") as app:
        count = state(0)
        name = state("Developer")
        show_events = state(True)
        enabled = state(False)
        theme = state("cobalt")
        recent = state(["Demo loaded"])
        message = computed(lambda: f"{name.value} clicked {count.value} times")
        ui = UI(title="NativeHTMLKit · Python UI", theme="cobalt", density="compact", width=900, height=720)

        def record(text):
            recent.set([text, *recent.value][:8])

        def increment(_):
            count.set(count.value + 1)
            record(f"Incremented to {count.value}")

        with ui.column():
            ui.heading("NativeHTMLKit UI component gallery", level=1)
            ui.text("Reactive state, compact layouts and public SDK access. No JS or browser.", muted=True)
            with ui.row():
                ui.badge(lambda: f"Count {count.value}")
                ui.badge(lambda: f"Theme selection {theme.value}")
            with ui.grid():
                with ui.card():
                    ui.heading("State and events", level=2)
                    ui.text(message)
                    with ui.row():
                        ui.button("Increment", on_click=increment)
                        ui.button("Reset", variant="secondary", on_click=lambda e: count.set(0))
                        ui.button("Disabled", disabled=True)
                with ui.card():
                    ui.heading("Inputs", level=2)
                    ui.input(name, label="Your name", placeholder="Enter a name")
                    ui.checkbox(enabled, label="Enable custom feature")
                    ui.select(theme, [("cobalt", "Cobalt"), ("olive", "Olive")], label="Preview choice")
                    ui.text(lambda: f"Enabled: {enabled.value}; selected: {theme.value}")
                with ui.card():
                    ui.heading("Conditional and list", level=2)
                    ui.checkbox(show_events, label="Show recent events")
                    with ui.when(show_events):
                        ui.text_list(recent)
            ui.alert(lambda: f"Live reactive value: {count.value}")
            ui.text("Native file dialogs, HTML dialogs, live bitmaps and secondary windows are SDK-level capabilities; see the SDK gallery.", muted=True)
        try:
            ui.mount(app)
            app.run()
        finally:
            ui.dispose()
            message.close()


if __name__ == "__main__":
    main()
