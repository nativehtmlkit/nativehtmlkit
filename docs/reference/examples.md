# Examples and verification

All code on this site lives in [`examples/`](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/README.md) and is copied into the pages by `scripts/sync-snippets.py`, so what you read is what was tested.

## What is tested, and how

[`scripts/test-examples.py`](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/scripts/test-examples.py) runs every Python and PowerShell example through its normal entry point (`Application.start()`, `Start-NativeHTMLKitScript`) against the **released** packages (Python SDK 0.1.2, UI 0.1.1, PowerShell SDK 0.1.2, PowerShell UI 0.1.1, each bundling Core 1.0.3), with the host in headless test mode (`NATIVEHTMLKIT_TEST_MODE=1`). For each example it:

1. waits until the app announced *ready*;
2. runs a short scenario through public document commands: typing into fields (`replace_control_range`, which fires real `input` events), submitting forms (`request_submit`, which validates and fires real `invalid`/`submit` events), opening and closing HTML dialogs, closing windows, and reading the live page back (`get_html`, `get_computed_style`, `get_accessibility_tree`);
3. requests an orderly quit and checks the exit status, that stderr has no traceback or callback failure, that files the app should write were written, and that no process of the run is left behind.

CLI scripts run with the released CLI 0.1.2 and `NATIVEHTMLKIT_CLI_TEST_HEADLESS=1`; the headless window never decides, so the scripts are checked with `--timeout` (exit status 124), their other options and their error paths. All `.ps1` files are also checked for Windows PowerShell 5.1 compatibility (parser, PowerShell 7-only syntax, ASCII-only source).

```bash
python3 scripts/test-examples.py --python VENV/bin/python --pwsh pwsh \
    --psmodulepath DIR_WITH_THE_TWO_MODULES --cli DIR_WITH_nativehtmlkit
python3 scripts/test-examples.py --list          # show every case
python3 scripts/test-examples.py --only notes    # run a subset
```

**Not covered by the automated run:** real pointer and keyboard input (so click-only paths, such as a button that copies to the clipboard, are exercised only on a desktop), the clipboard, native file dialogs, rendering pixels on screen, and screen-reader behaviour. These are checked interactively on the target desktops before screenshots are published.

## Example index

| Example | Entry point | Shows |
|---|---|---|
| `getting-started/hello.py`, `hello_ui.py`, `hello.ps1`, `hello-ui.ps1`, `hello-cli.sh`, `five_lines.py` | all | the first window of each entry point |
| `tutorials/python-notes/` (4 steps) | Python SDK | forms, delegated clicks, filtering, JSON persistence |
| `tutorials/python-ui-expenses/` (3 steps) | Python UI | state, computed totals, validation, persistence |
| `tutorials/powershell-process-dashboard/` (3 steps) | PowerShell SDK | tables, events, background refresh tasks, clipboard |
| `tutorials/powershell-ui-settings/` (2 steps) | PowerShell UI | bound settings form, validation, save and revert |
| `tutorials/cli-branch-picker/` (2 steps) | CLI | `select` in Bash, exit statuses, `--multi`, `--timeout` |
| `howto/python/event_inspector.py` | Python SDK | every event and its fields |
| `howto/python/status_board.py` | Python SDK | text, classes, attributes, `batch`, `query` |
| `howto/python/signup_form.py`, `howto/powershell/signup-form.ps1` | SDKs | form validation and custom validity |
| `howto/python/log_windows.py` | Python SDK | several windows, window events, close policy |
| `howto/python/file_preview.py`, `howto/powershell/csv-viewer.ps1` | SDKs | native open/save dialogs |
| `howto/python/dialogs.py` | Python SDK | HTML `<dialog>` with return values and a form |
| `howto/python/clipboard_tool.py` | Python SDK | clipboard with capability check |
| `howto/python/prime_counter.py`, `howto/python-ui/word_counter.py`, `howto/powershell/file-hash.ps1` | all three | background work, progress, cancellation |
| `howto/python/live_chart.py`, `howto/powershell/live-chart.ps1` | SDKs | live RGBA bitmaps |
| `howto/python/theme_switcher.py`, `howto/python/css_support.py` | Python SDK | CSS variables, colour scheme, the CSS profile |
| `howto/python-ui/theme_preview.py` | Python UI | themes, densities, design tokens |
| `python-sdk/gallery.py`, `python-ui/gallery.py`, `powershell-sdk/gallery.ps1`, `powershell-ui/gallery.ps1` | all | capability galleries for manual exploration |

The harness also generates a project with `nativehtmlkit-new` and with `New-NativeHTMLKitProject` and runs it.
