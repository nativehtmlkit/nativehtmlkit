"""CSS support explorer: ask the running host which CSS features its renderer profile enables.

Teaches: the low-level Document.command("css_profile") operation, rendering a large table from data
with escaping, and a live "input" filter. Use it before relying on a CSS feature: the renderer
implements a documented desktop profile, not every browser feature.
Run:     python css_support.py
Guide:   docs/how-to/styling.md
"""
import html
from collections import Counter

from nativehtmlkit import Application

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 14px sans-serif; margin: 0; padding: 16px; background: #f4f6fa; color: #1d2433; }
  input { width: 100%; box-sizing: border-box; padding: 8px; margin: 8px 0; }
  table { border-collapse: collapse; width: 100%; }
  td, th { text-align: left; padding: 4px 8px; border-bottom: 1px solid #dde3ee; }
  td.state { font-weight: 600; }
  tr.on td.state { color: #1d6b34; }
  tr.off td.state, tr.unavailable td.state { color: #8a1f1f; }
  tr.filtered td.state { color: #7a5300; }
</style></head>
<body>
  <h1>CSS profile <span id="version"></span></h1>
  <p id="summary"></p>
  <input id="filter" type="search" placeholder="Filter, for example grid or color-mix" aria-label="Filter features">
  <table><thead><tr><th>Feature</th><th>State</th></tr></thead><tbody id="rows"></tbody></table>
</body></html>"""


def main():
    with Application.start(name="CSS support") as app:
        window = app.open_html(PAGE, title="CSS support", width=640, height=720)
        doc = window.document
        profile = doc.command("css_profile")
        features = sorted(profile["features"], key=lambda f: f["id"])
        counts = Counter(f["state"] for f in features)
        doc.set_text("version", profile.get("version", ""))
        doc.set_text("summary", ", ".join(f"{count} {state}" for state, count in counts.most_common()))

        def render(_event=None):
            needle = doc.get_value("filter").strip().lower()
            rows = [f'<tr class="{html.escape(f["state"])}"><td>{html.escape(f["id"])}</td>'
                    f'<td class="state">{html.escape(f["state"])}</td></tr>'
                    for f in features if needle in f["id"].lower()]
            doc.replace_html("rows", "".join(rows) or '<tr><td colspan="2">No matching feature</td></tr>')

        doc.on("input", render, element="filter")
        render()
        app.run()


if __name__ == "__main__":
    main()
