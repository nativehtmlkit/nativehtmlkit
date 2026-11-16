"""NativeHTMLKit Python SDK gallery: a real local native host (interactive desktop required).

Run: uv run --with nativehtmlkit examples/python-sdk/gallery.py
This does not use the UI library. For release qualification, exercise every button.
"""
from nativehtmlkit import Application

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
body{background:#171f31;color:#ecf2ff;font:14px sans-serif;margin:22px}
main{max-width:820px} h1{font-size:26px} p{line-height:1.55;color:#bac8df}
section{padding:16px;background:#25304a;border:1px solid #3c4b69;border-radius:10px;margin:12px 0}
button{background:#3574c6;color:white;border:0;border-radius:6px;padding:9px 14px;margin:4px;cursor:pointer}
input,select{background:#141e30;color:white;padding:8px;border:1px solid #647496;border-radius:5px}
dialog{background:#243450;color:white;border:1px solid #6581aa;border-radius:10px;padding:22px}
</style></head><body><main>
<h1>NativeHTMLKit · Python SDK</h1><p>Each button calls the public Python SDK. No browser or JavaScript.</p>
<section><h2>Events and DOM</h2><button id="add">Increment</button><button id="reset">Reset</button>
<strong id="counter">0</strong><p id="status">Click an action to see the result.</p>
<label>Name <input id="name" placeholder="Type here"></label><button id="read-name">Read input</button>
<label><input type="checkbox" id="enabled"> Enabled</label><button id="read-check">Read checkbox</button>
<button id="change-style">Change element attribute</button>
</section>
<section><h2>Native lifecycle</h2><button id="new-window">Open second window</button>
<button id="show-dialog">HTML dialog</button><button id="show-popover">Popover</button>
<button id="choose-file">Native file picker</button><button id="choose-folder">Native folder picker</button>
<p id="file-result">No file selected.</p></section>
<section><h2>System services and diagnostics</h2>
<button id="write-clipboard">Copy text to clipboard</button><button id="read-clipboard">Read clipboard</button>
<button id="diagnostics">Read diagnostic summary</button><button id="capabilities">List host capabilities</button>
<p>Clipboard permission and support vary by desktop session.</p></section>
<section><h2>Live bitmap</h2><button id="draw">Draw a new frame</button>
<img id="preview" width="160" height="90" src="ui4me-bitmap://gallery-preview" alt="RGBA bitmap preview" style="display:block;background:#0a1020;margin:12px 0">
<p>Each frame is 160 × 90 raw RGBA8 pixels and is delivered through a bounded local resource.</p></section>
<dialog id="about"><h2>A real HTML dialog</h2><p>This is opened by Document.show_dialog().</p><button id="close-dialog">Close</button></dialog>
<div id="tips" popover style="background:#2d4562;color:white;padding:14px;border-radius:7px">Popover anchored to document context. <button id="hide-popover">Dismiss</button></div>
</main></body></html>"""


def main():
    with Application.start(name="NativeHTMLKit SDK Demo", instance="multiple") as app:
        window = app.open_html(HTML, title="NativeHTMLKit · Python SDK gallery", width=860, height=760)
        doc = window.document
        counter = 0
        frames = 0
        bitmap = doc.create_bitmap("gallery-preview", 160, 90)

        def display(text):
            doc.set_text("status", text)

        def add(_event):
            nonlocal counter
            counter += 1
            doc.set_text("counter", str(counter))
            display(f"Button event received. Counter = {counter}")

        def reset(_event):
            nonlocal counter
            counter = 0
            doc.set_text("counter", "0")
            display("Counter reset")

        def new_window(_event):
            child = app.open_html('<main style="padding:28px;font:15px sans-serif"><h1>Second native window</h1><p>A second window from the same app.</p><button id="close">Close me</button></main>', title="NativeHTMLKit · Second window", width=420, height=260)
            child.document.on("click", lambda e: child.request_close(), element="close")
            display("Opened an additional native window")

        def pick_file(_event):
            display("Native file dialog opened; cancel to test cancellation.")
            # Non-blocking request keeps the SDK event callback available to other events.
            future = window.open_files(multiple=False, title="Select a file", wait=False)
            def completed(done):
                try:
                    result = done.result()
                    doc.set_text("file-result", str(result) if result else "Cancelled; no file selected")
                except Exception as exc:
                    doc.set_text("file-result", f"File dialog: {type(exc).__name__}")
            future.add_done_callback(completed)

        def choose_folder(_event):
            future = window.choose_folder(title="Choose a folder", wait=False)
            def completed(done):
                try:
                    value = done.result()
                    doc.set_text("file-result", str(value) if value else "Folder selection cancelled")
                except Exception as exc:
                    doc.set_text("file-result", f"Folder dialog: {type(exc).__name__}")
            future.add_done_callback(completed)

        def clipboard_action(read: bool):
            try:
                if read:
                    value = app.clipboard_text()
                    display(f"Clipboard contents: {value[:80]}")
                else:
                    app.set_clipboard_text("Copied from NativeHTMLKit SDK gallery")
                    display("Wrote demo string to native clipboard")
            except Exception as exc:
                display(f"Clipboard unavailable: {type(exc).__name__}")

        def diagnostic_action(kind: str):
            try:
                data = doc.diagnostics() if kind == "document" else app.capabilities()
                display(f"{kind} returned {len(data)} top-level field(s)")
            except Exception as exc:
                display(f"{kind} failed: {type(exc).__name__}")

        def draw(_event):
            nonlocal frames
            frames += 1
            # 160x90 straight-alpha, tightly packed RGBA8. Only one frame queued.
            rgba = bytearray(160 * 90 * 4)
            for y in range(90):
                for x in range(160):
                    i = (y * 160 + x) * 4
                    rgba[i:i+4] = bytes(((x + frames*17) % 256, (2*y) % 256, 175, 255))
            bitmap.present(rgba)
            display(f"Bitmap frame {frames} presented")

        doc.on("click", add, element="add")
        doc.on("click", reset, element="reset")
        doc.on("click", lambda e: display(f"Input value: {doc.get_value('name')}"), element="read-name")
        doc.on("click", lambda e: display(f"Checked: {doc.get_checked('enabled')}"), element="read-check")
        doc.on("click", new_window, element="new-window")
        doc.on("click", lambda e: doc.show_dialog("about"), element="show-dialog")
        doc.on("click", lambda e: doc.close_dialog("about"), element="close-dialog")
        doc.on("click", pick_file, element="choose-file")
        doc.on("click", draw, element="draw")
        doc.on("click", choose_folder, element="choose-folder")
        doc.on("click", lambda e: doc.show_popover("tips"), element="show-popover")
        doc.on("click", lambda e: doc.hide_popover("tips"), element="hide-popover")
        doc.on("click", lambda e: doc.set_attribute("status", "title", "Attribute mutation succeeded"), element="change-style")
        doc.on("click", lambda e: clipboard_action(False), element="write-clipboard")
        doc.on("click", lambda e: clipboard_action(True), element="read-clipboard")
        doc.on("click", lambda e: diagnostic_action("document"), element="diagnostics")
        doc.on("click", lambda e: diagnostic_action("capabilities"), element="capabilities")
        try:
            app.run()
        finally:
            bitmap.close()


if __name__ == "__main__":
    main()
