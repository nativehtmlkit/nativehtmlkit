# The smallest NativeHTMLKit app (home page sample). Run: python five_lines.py
from nativehtmlkit import Application

with Application.start(name="Hello") as app:
    window = app.open_html('<h1 id="title">Hello</h1><button id="go">Click me</button>')
    window.document.on("click", lambda e: window.document.set_text("title", "Clicked!"), element="go")
    app.run()
