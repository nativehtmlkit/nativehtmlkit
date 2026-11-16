# Getting started

NativeHTMLKit shows native desktop windows whose content is plain HTML and CSS. Your program, written in Python or PowerShell (or a shell script using the CLI), owns the logic; a small native host process draws the window and sends you the user's events. There is no browser, no JavaScript and no local web server.

## Pick your path

| You write... | Start with | Install |
|---|---|---|
| Python, reactive components | [Python UI library](../ui/python/getting-started.md) | `pip install nativehtmlkit_ui` |
| PowerShell, reactive components | [PowerShell UI library](../ui/powershell/getting-started.md) | `Install-Module NativeHTMLKit.UI` |
| Python, full control of the page | [Python SDK](../sdk/python/getting-started.md) | `pip install nativehtmlkit` |
| PowerShell, full control of the page | [PowerShell SDK](../sdk/powershell/getting-started.md) | `Install-Module NativeHTMLKit` |
| Bash or another Linux shell | [CLI on Linux](../cli/linux/index.md) | download the release archive |
| PowerShell or cmd on Windows, one question to the user | [CLI on Windows](../cli/windows/index.md) | download the release archive |

Not sure? Read [Choose an entry point](choose.md). Before installing, check the [platform requirements](requirements.md).

## What happens when you run an app

1. You run your script normally (`python app.py`, `pwsh -File app.ps1`).
2. The SDK starts the bundled native host, and the host starts **your script a second time** as its *backend*, connected over a private local channel. That is why every example keeps its work *after* `Application.start()` / `Start-NativeHTMLKitScript`. See [Process and lifecycle](../concepts/lifecycle.md).
3. Your code opens windows, loads HTML, subscribes to events and announces that it is *ready*.
4. Events (clicks, typing, form submits) arrive in your callbacks; you change the page with document commands such as "set this element's text".
5. When the user closes the last window, the host shuts the application down and your script ends.

## After the first window

- Build a complete app: the tutorials in your section ([UI](../ui/index.md), [SDK](../sdk/index.md), [CLI](../cli/index.md)).
- Understand the model: [Concepts](../concepts/index.md).
- Look up exact APIs: [Reference](../reference/index.md) (each package documents its own API).

Every example on this site is a program in the repository that owns its API, run automatically against the released packages; see [Examples and verification](../reference/examples.md).
