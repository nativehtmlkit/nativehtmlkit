# NativeHTMLKit examples

Runnable source examples for every entry point, used by the documentation at https://nativehtmlkit.github.io/nativehtmlkit/ . Each file starts with a comment that says what it teaches and how to run it.

| Folder | What is inside |
|---|---|
| [`getting-started/`](getting-started/) | The first window of each entry point (`hello.py`, `hello_ui.py`, `hello.ps1`, `hello-ui.ps1`, `hello-cli.sh`) |
| [`tutorials/python-notes/`](tutorials/python-notes/) | Python SDK tutorial: notes app with persistence, in four steps |
| [`tutorials/python-ui-expenses/`](tutorials/python-ui-expenses/) | Python UI tutorial: expense tracker with computed totals, in three steps |
| [`tutorials/powershell-process-dashboard/`](tutorials/powershell-process-dashboard/) | PowerShell SDK tutorial: live process dashboard, in three steps |
| [`tutorials/powershell-ui-settings/`](tutorials/powershell-ui-settings/) | PowerShell UI tutorial: settings editor, in two steps |
| [`tutorials/cli-branch-picker/`](tutorials/cli-branch-picker/) | CLI tutorial: Git branch picker in Bash, in two steps |
| [`howto/python/`](howto/python/) | Python SDK recipes: events, page updates, forms, windows, dialogs, clipboard, background work, live chart, styling |
| [`howto/python-ui/`](howto/python-ui/) | Python UI recipes: theming, background progress |
| [`howto/powershell/`](howto/powershell/) | PowerShell recipes: forms, CSV viewer with a file dialog, background task, live chart |
| [`python-sdk/gallery.py`](python-sdk/gallery.py), [`python-ui/gallery.py`](python-ui/gallery.py), [`powershell-sdk/gallery.ps1`](powershell-sdk/gallery.ps1), [`powershell-ui/gallery.ps1`](powershell-ui/gallery.ps1) | Capability galleries: one window with a button for each SDK or UI feature, for manual exploration |

## Run an example

```bash
python -m pip install nativehtmlkit nativehtmlkit_ui      # Python SDK 0.1.2 and UI 0.1.1
python examples/tutorials/python-notes/notes.py
```

```powershell
Install-Module NativeHTMLKit, NativeHTMLKit.UI -Scope CurrentUser
pwsh -File examples/tutorials/powershell-process-dashboard/dashboard.ps1
```

```bash
# CLI 0.1.2 from https://github.com/nativehtmlkit/nativehtmlkit-cli/releases on PATH
bash examples/tutorials/cli-branch-picker/git-pick.sh
```

Examples open real windows, so run them in an interactive desktop session (KDE Plasma on Wayland, or Windows). PowerShell examples also run on Windows PowerShell 5.1 (`powershell.exe -File ...`).

## How the examples are verified

[`scripts/test-examples.py`](../scripts/test-examples.py) runs every example against the released packages with the host in headless test mode: it waits for the app to be ready, types into fields and submits forms through public document commands, reads the page back, requests a clean quit, and checks the exit status, stderr and leftover processes. CLI scripts are run with the headless CLI and `--timeout`. Click-only actions, the clipboard and native file dialogs need a real desktop and are checked interactively. Details: [Examples and verification](../docs/reference/examples.md).

## What to try in the galleries

- Buttons update status and state; text fields, selections and checkboxes change bound text.
- Closing a dialog or a second window leaves the main window running.
- The file picker returns to the app without freezing it; cancelling is reported.
- The live bitmap changes with each frame.
