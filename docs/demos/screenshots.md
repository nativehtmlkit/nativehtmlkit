# Screenshots and media

Every image on this site is a **real capture** of the example it shows, taken on **KDE Plasma 6.6 Wayland** (1280×800, 100% scaling) with the released packages: Core 1.0.3, Python SDK 0.1.2, PowerShell SDK 0.1.2 on PowerShell 7.7, UI 0.1.1 and CLI 0.1.2. Each window was opened by its example script, as a user would, and captured with KDE Spectacle (active window only). Nothing was retouched.

Windows looks the same apart from the window frame; Windows captures are not published yet.

## Galleries

| Python SDK | Python UI |
|---|---|
| ![Python SDK gallery](../assets/python-sdk-linux.png) | ![Python UI gallery](../assets/python-ui-linux.png) |
| **PowerShell SDK** | **PowerShell UI** |
| ![PowerShell SDK gallery](../assets/powershell-sdk-linux.png) | ![PowerShell UI gallery](../assets/powershell-ui-linux.png) |

## Getting started

**Hello cli** (`getting-started-hello-cli`)

![getting-started-hello-cli](../assets/screenshots/getting-started-hello-cli.png)

**Hello powershell** (`getting-started-hello-powershell`)

![getting-started-hello-powershell](../assets/screenshots/getting-started-hello-powershell.png)

**Hello powershell ui** (`getting-started-hello-powershell-ui`)

![getting-started-hello-powershell-ui](../assets/screenshots/getting-started-hello-powershell-ui.png)

**Hello python** (`getting-started-hello-python`)

![getting-started-hello-python](../assets/screenshots/getting-started-hello-python.png)

**Hello python ui** (`getting-started-hello-python-ui`)

![getting-started-hello-python-ui](../assets/screenshots/getting-started-hello-python-ui.png)

## Tutorials

**Cli branch picker** (`tutorial-cli-branch-picker`)

![tutorial-cli-branch-picker](../assets/screenshots/tutorial-cli-branch-picker.png)

**Powershell process dashboard** (`tutorial-powershell-process-dashboard`)

![tutorial-powershell-process-dashboard](../assets/screenshots/tutorial-powershell-process-dashboard.png)

**Powershell ui settings** (`tutorial-powershell-ui-settings`)

![tutorial-powershell-ui-settings](../assets/screenshots/tutorial-powershell-ui-settings.png)

**Python notes** (`tutorial-python-notes`)

![tutorial-python-notes](../assets/screenshots/tutorial-python-notes.png)

**Python ui expenses** (`tutorial-python-ui-expenses`)

![tutorial-python-ui-expenses](../assets/screenshots/tutorial-python-ui-expenses.png)

## How-to guides

**Clipboard tool** (`howto-clipboard-tool`)

![howto-clipboard-tool](../assets/screenshots/howto-clipboard-tool.png)

**Css support** (`howto-css-support`)

![howto-css-support](../assets/screenshots/howto-css-support.png)

**Dialogs** (`howto-dialogs`)

![howto-dialogs](../assets/screenshots/howto-dialogs.png)

**Event inspector** (`howto-event-inspector`)

![howto-event-inspector](../assets/screenshots/howto-event-inspector.png)

**File preview** (`howto-file-preview`)

![howto-file-preview](../assets/screenshots/howto-file-preview.png)

**Live chart** (`howto-live-chart`)

![howto-live-chart](../assets/screenshots/howto-live-chart.png)

**Log windows** (`howto-log-windows`)

![howto-log-windows](../assets/screenshots/howto-log-windows.png)

**Prime counter** (`howto-prime-counter`)

![howto-prime-counter](../assets/screenshots/howto-prime-counter.png)

**Signup form** (`howto-signup-form`)

![howto-signup-form](../assets/screenshots/howto-signup-form.png)

**Status board** (`howto-status-board`)

![howto-status-board](../assets/screenshots/howto-status-board.png)

**Theme preview** (`howto-theme-preview`)

![howto-theme-preview](../assets/screenshots/howto-theme-preview.png)

## Capturing a new screenshot

1. Install the **exact released** packages on the target desktop (KDE Plasma Wayland or Windows) and note the OS, runtime and package versions.
2. Run the example the page documents, for example `python examples/tutorials/python-notes/notes.py`, from a neutral working directory so no personal paths appear in the window.
3. Exercise the controls the page describes. Never present a capture of a broken state as working.
4. Capture only the application window (KDE: `spectacle -b -n -a -o shot.png`; Windows: Win+Shift+S, window mode). Remove personal data, host names, user names, tokens and file paths.
5. Save it as `docs/assets/screenshots/<example-id>.png` and reference it with a caption that states the platform and versions. Record provenance in `assets/README.md`.

Keep motion clips short and optional: every page must make sense without them and with reduced motion enabled.
