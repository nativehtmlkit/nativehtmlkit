# NativeHTMLKit

**Native desktop windows from HTML and CSS, driven by a shell script, Python or PowerShell.** No browser engine, no JavaScript, no local web server: a small Rust host renders your page and sends your program the user's events over a private local connection.

## Choose what you build with

<div class="grid cards" markdown>

-   **[Command line (CLI)](cli/index.md)**

    One executable for shell scripts: pick rows, view text or fill in a form in a native window and
    get the answer on stdout. Every command and option with examples.

    [Linux](cli/linux/index.md) · [Windows](cli/windows/index.md) · [Reference](cli/reference/index.md)

-   **[Python](python/index.md)**

    Python 3.10+ on Linux and Windows.

    [SDK: HTML/CSS + Python](python/sdk/index.md) · [UI library](python/ui/index.md)

-   **[PowerShell](powershell/index.md)**

    PowerShell 7 on Linux and Windows, Windows PowerShell 5.1 on Windows.

    [SDK: HTML/CSS + PowerShell](powershell/sdk/index.md) · [UI library](powershell/ui/index.md)

</div>

Each section has the same shape: **getting started**, step-by-step **tutorials**, task **guides**, complete **examples** with screenshots and source, and the full **API reference**. Python and PowerShell mirror each other one to one, so you can switch languages without relearning the structure.

Not sure which to pick? [Choose an entry point](getting-started/choose.md) · [Platform requirements](getting-started/requirements.md)

## What it looks like

![The Python UI component gallery running on KDE Plasma 6.6 Wayland](assets/python-ui-linux.png)

*Real capture: the Python UI gallery on KDE Plasma 6.6 Wayland (Core 1.0.3, Python SDK 0.1.2, UI 0.1.1).*

## A complete app in a few lines

=== "Python"

    ```python
    from nativehtmlkit import Application

    with Application.start(name="Hello") as app:
        window = app.open_html('<h1 id="title">Hello</h1><button id="go">Click me</button>')
        window.document.on("click", lambda e: window.document.set_text("title", "Clicked!"), element="go")
        app.run()
    ```

=== "PowerShell"

    ```powershell
    Import-Module NativeHTMLKit
    $app = Start-NativeHTMLKitScript -Name 'Hello'
    try {
        $window = New-NativeHTMLKitWindow -Application $app -Title 'Hello'
        $doc = Open-NativeHTMLKitHtml -Window $window -Html '<h1 id="title">Hello</h1><button id="go">Click me</button>'
        $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element go -Callback {
            Set-NativeHTMLKitDocumentText -Document $doc -Element title -Text 'Clicked!'
        }
        Set-NativeHTMLKitReady -Application $app
        Wait-NativeHTMLKit -Application $app -UntilShutdown
    } finally { Close-NativeHTMLKit -Application $app }
    ```

=== "Linux shell"

    ```bash
    printf '%s\n' apple banana cherry | nativehtmlkit select --multi --title "Pick fruit"
    ```

=== "Windows PowerShell"

    ```powershell
    'apple', 'banana', 'cherry' | nativehtmlkit select --multi --title 'Pick fruit'
    ```

## Packages

| Entry point | Package | For |
|---|---|---|
| CLI | [`nativehtmlkit` / `nhk`](https://github.com/nativehtmlkit/nativehtmlkit-cli/releases) 0.1.2 | Select rows, view text or fill a form from any shell |
| Python SDK | [`nativehtmlkit`](https://pypi.org/project/nativehtmlkit/) 0.1.2 | Windows, documents, events, dialogs, clipboard and live bitmaps |
| Python UI | [`nativehtmlkit_ui`](https://pypi.org/project/nativehtmlkit_ui/) 0.1.1 | Reactive state and compact components on the Python SDK |
| PowerShell SDK | [`NativeHTMLKit`](https://www.powershellgallery.com/packages/NativeHTMLKit) 0.1.2 | The same features as cmdlets, plus background tasks |
| PowerShell UI | [`NativeHTMLKit.UI`](https://www.powershellgallery.com/packages/NativeHTMLKit.UI) 0.1.1 | Reactive components on the PowerShell SDK |

All of them bundle the native host, Core 1.0.3 (wire protocol v1, stable). Target desktops are KDE Plasma on Wayland (Linux) and Windows; see the [capability matrix](capabilities/matrix.md) and [limitations](capabilities/limitations.md). Every example on this site is run against the released packages before it is published.

## What it is not

NativeHTMLKit is not a web browser, not a web UI framework and not a plugin platform. It runs no JavaScript, loads nothing from the network, and implements a documented [HTML and CSS profile](reference/core/html-css-support.md) rather than the whole web platform. See [Why native?](concepts/why-native.md) and [Concepts](concepts/index.md).
