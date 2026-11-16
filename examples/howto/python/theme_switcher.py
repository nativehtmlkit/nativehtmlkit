"""Theme switcher: light/dark mode and accent colours with CSS custom properties.

Teaches: CSS custom properties (var()), @media (prefers-color-scheme) driven by the desktop or
overridden with Document.set_environment(), add_stylesheet() + replace_stylesheet() to swap one
small stylesheet at run time, and computed_style() to read back what the renderer resolved.
Run:     python theme_switcher.py
Guide:   docs/how-to/styling.md
"""
from nativehtmlkit import Application

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  :root { --bg: #f5f7fb; --panel: #ffffff; --text: #1b2230; --muted: #5d6879; --accent: #2f6fd0; }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #10151e; --panel: #19212e; --text: #e4e9f1; --muted: #9aa7ba; }
  }
  body { margin: 0; padding: 20px; font: 15px sans-serif; background: var(--bg); color: var(--text); }
  .panel { background: var(--panel); border-radius: 10px; padding: 16px; border: 1px solid color-mix(in srgb, var(--text) 15%, transparent); }
  .muted { color: var(--muted); }
  .accent { color: var(--accent); font-weight: 600; }
  button.primary { background: var(--accent); color: white; border: 0; border-radius: 6px; padding: 8px 14px; }
  form { display: grid; grid-template-columns: auto 1fr; gap: 8px 12px; align-items: center; margin-top: 12px; }
</style></head>
<body>
  <div class="panel" id="panel">
    <h1>Appearance</h1>
    <p class="muted">The page uses CSS variables; switching a theme changes a few of them.</p>
    <form id="appearance">
      <label for="scheme">Colour scheme</label>
      <select id="scheme"><option value="system">Follow the desktop</option><option value="light">Light</option><option value="dark">Dark</option></select>
      <label for="accent">Accent</label>
      <select id="accent"><option value="#2f6fd0">Blue</option><option value="#1f8a4c">Green</option><option value="#b4451f">Orange</option></select>
      <span></span><button class="primary" id="apply">Apply</button>
    </form>
    <p>Resolved accent: <span class="accent" id="resolved"></span></p>
  </div>
</body></html>"""


def main():
    with Application.start(name="Theme switcher") as app:
        window = app.open_html(PAGE, title="Theme switcher", width=520, height=420)
        doc = window.document
        # A separate, replaceable stylesheet for the run-time accent colour.
        accent_sheet = doc.add_stylesheet(":root { --accent: #2f6fd0; }")["sheet"]

        def show_resolved():
            style = doc.computed_style(["color"], "resolved")
            doc.set_text("resolved", style["properties"]["color"]["value"])

        def apply(_event):
            # "light"/"dark" override the desktop preference for this document; "system" follows it again.
            doc.set_environment(color_scheme=doc.get_value("scheme"))
            accent = doc.get_value("accent")
            if accent.startswith("#") and len(accent) == 7:  # only values from our own <select>
                doc.replace_stylesheet(accent_sheet, f":root {{ --accent: {accent}; }}")
            show_resolved()

        doc.on("submit", apply, element="appearance")
        show_resolved()
        app.run()


if __name__ == "__main__":
    main()
