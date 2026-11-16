# Choose an entry point

All entry points use the same native host and the same HTML/CSS renderer. They differ in who writes the page and how much control you get.

| Your job | Best entry point | Why |
|---|---|---|
| A Python program needs a window, and you are happy to write HTML | [Python SDK](python.md) | Full control: windows, documents, events, dialogs, clipboard, live bitmaps |
| A Python tool needs a form-like window quickly | [Python UI](python-ui.md) | Reactive `state()`/`computed()`, inputs, lists and layout without writing HTML |
| A PowerShell admin script needs a dashboard or a dialog | [PowerShell SDK](powershell.md) | The same features as cmdlets, plus background tasks in isolated runspaces |
| A PowerShell script needs a settings form or a small reactive UI | [PowerShell UI](powershell-ui.md) | `Add-NHKUi*` components bound to `New-NHKUiState` values |
| A shell pipeline needs the user to pick rows or fill a form | [CLI](cli.md) | One command, stdin in, stdout out, exit status tells what happened |

## How they relate

- The **UI libraries** are small layers built only on the public SDK of the same language. They do not wrap everything: native file dialogs, HTML `<dialog>`, clipboard, extra windows and live bitmaps are used through the SDK, next to the UI library, in the same app.
- The **CLI** is a standalone program. It does not need Python or PowerShell, and scripts cannot subscribe to individual events; a window ends with one result.
- You can start with the UI library and drop down to the SDK at any time: `ui.document` (Python) and the document of the window returned by `Start-NHKUi` (PowerShell) are ordinary SDK objects.

## Rules of thumb

- Prefer the **SDK** when the page is your own HTML/CSS design, when you show tables or logs, or when you need dialogs, several windows or bitmaps.
- Prefer the **UI library** for settings, forms and small tools where state should drive the page automatically. It is an early (0.1.1) release; check its [limitations](../capabilities/limitations.md).
- Prefer the **CLI** when the rest of the program is a shell script and you need a single decision from the user.

Feature-by-feature availability is in the [capability matrix](../capabilities/matrix.md).
