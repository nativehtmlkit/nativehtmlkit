# NativeHTMLKit

**Native desktop windows from HTML and CSS, driven by Python, PowerShell or a shell script.** No browser engine, no JavaScript, no local web server: a small Rust host renders your page and sends your program the user's events over a private local connection.

![The Python UI component gallery running on KDE Plasma 6.6 Wayland](assets/python-ui-linux.png)

*Real capture: the Python UI gallery on KDE Plasma 6.6 Wayland (Core 1.0.3, Python SDK 0.1.2, UI 0.1.1). See [Screenshots and media](demos/screenshots.md) for every example.*

## Start here

<div class="grid cards" markdown>

- **[Getting started](getting-started/index.md)**: install one package and open your first window in five minutes, in Python, PowerShell or Bash.
- **[Tutorials](tutorials/index.md)**: build complete apps step by step: a notes app, an expense tracker, a process dashboard, a settings editor, a Git branch picker.
- **[How-to guides](how-to/index.md)**: recipes for events, forms, dialogs, multiple windows, background work, live charts, styling, distribution and troubleshooting.
- **[Concepts](concepts/index.md)**: how the host, your script and the page fit together, and why.
- **[Reference](reference/index.md)**: where each package documents its exact API, plus the capability matrix, limitations, glossary and FAQ.

</div>

## A complete app in a few lines

<!-- include: examples/getting-started/five_lines.py -->
```python title="examples/getting-started/five_lines.py"
# The smallest NativeHTMLKit app (home page sample). Run: python five_lines.py
from nativehtmlkit import Application

with Application.start(name="Hello") as app:
    window = app.open_html('<h1 id="title">Hello</h1><button id="go">Click me</button>')
    window.document.on("click", lambda e: window.document.set_text("title", "Clicked!"), element="go")
    app.run()
```
<!-- /include -->

The [quick start](getting-started/python.md) explains each line (including why the script runs twice) and the [same app in PowerShell](getting-started/powershell.md) uses `Start-NativeHTMLKitScript`.

## Entry points

| Entry point | Package | For |
|---|---|---|
| Python SDK | [`nativehtmlkit`](https://pypi.org/project/nativehtmlkit/) 0.1.2 | Full control of windows, documents, events, dialogs, clipboard and live bitmaps |
| Python UI | [`nativehtmlkit_ui`](https://pypi.org/project/nativehtmlkit_ui/) 0.1.1 | Reactive state and compact components, built on the Python SDK |
| PowerShell SDK | [`NativeHTMLKit`](https://www.powershellgallery.com/packages/NativeHTMLKit) 0.1.2 | The same features as cmdlets, plus background tasks |
| PowerShell UI | [`NativeHTMLKit.UI`](https://www.powershellgallery.com/packages/NativeHTMLKit.UI) 0.1.1 | Reactive components for PowerShell |
| CLI | [`nativehtmlkit` / `nhk`](https://github.com/nativehtmlkit/nativehtmlkit-cli/releases) 0.1.2 | Select rows, view text or fill a form from any shell |

All of them bundle the native host, Core 1.0.3 (wire protocol v1, stable). Target desktops are KDE Plasma on Wayland (Linux) and Windows; see [platform requirements](getting-started/requirements.md) and the [capability matrix](capabilities/matrix.md).

## Tested examples

Every code sample on this site is a file in [`examples/`](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/README.md), and a committed harness runs each one against the released packages in the host's headless test mode before the documentation is published. See [Examples and verification](reference/examples.md).

## What it is not

NativeHTMLKit is not a web browser, not a web UI framework and not a plugin platform. It runs no JavaScript, loads nothing from the network, and implements a documented CSS profile rather than the whole web platform. If you need arbitrary web content, a browser-based toolkit is the better fit; see [Why native?](concepts/why-native.md).
