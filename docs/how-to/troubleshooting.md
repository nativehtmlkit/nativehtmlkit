# Troubleshooting and diagnostics

## First checks

| Symptom | Check |
|---|---|
| No window appears | Run `nativehtmlkit-python doctor` (Python), `nativehtmlkit doctor` (CLI) or `Get-NativeHTMLKitHostPath` (PowerShell). Are you in an interactive desktop session (not SSH, not a service)? |
| `pip install` finds no wheel (Linux) | The released wheel needs glibc 2.39+ (`ldd --version`). |
| "must run from a script file" | Run a saved file: `python app.py`, `pwsh -File app.ps1`. Interactive prompts, `python -c` and piped stdin are refused. |
| Something happens twice at start | Code before `Application.start()` / `Start-NativeHTMLKitScript` runs in both processes. Move it after the call. |
| A click does nothing | Is the element id right, and is the subscription on the document of *this* window? Was the document replaced (old subscriptions are gone)? Use the [event inspector](handle-events.md). |
| `StaleDocumentError` / `NativeHTMLKit.StaleObjectException` | The window was closed or the document replaced; see [Documents and stale handles](../concepts/documents-and-handles.md). |
| RPC error -32008 during shutdown | The application is shutting down; requests are refused. Usually harmless in late callbacks. |
| Clipboard or file dialog fails with -32001 | Not available in this session, for example in headless mode. Handle the error. |
| The window freezes while working | A callback is doing slow work; see [Background work](background-work.md). |
| A CSS rule has no effect | Check the feature with the [CSS support explorer](styling.md) and `explain`. |

## Diagnostics levels

All entry points share the levels `off`, `normal` (default: critical problems only), `debug` and `trace`:

```bash
NATIVEHTMLKIT_DIAGNOSTICS=debug python app.py
nativehtmlkit-python --diagnostics trace run my_app:main
nativehtmlkit --diagnostics debug select < items.txt
```

```powershell
$env:NATIVEHTMLKIT_DIAGNOSTICS = 'debug'; pwsh -File app.ps1
$app = Start-NativeHTMLKitScript -Name 'My App' -Diagnostics Trace
```

Records are structured JSON lines on stderr. `NATIVEHTMLKIT_DIAGNOSTICS_DIR=<folder>` additionally writes the SDKs' records to files in that folder.

## Counters and support bundles

- Python: `app.host_diagnostics()` returns the host's counters (for example `dropped_notifications`); `nativehtmlkit-python support bundle.zip` exports a redacted local support bundle.
- PowerShell: `Get-NativeHTMLKitDiagnosticReport -Application $app` returns session, queue-loss and callback-failure counters; `Export-NativeHTMLKitSupportBundle -Path bundle.zip -Application $app` writes a sanitized ZIP.
- Both bundles stay on your machine (nothing is uploaded) and leave out form values, tokens, file paths and raw output. Review them before you attach one to a bug report.

## Headless test mode

Set `NATIVEHTMLKIT_TEST_MODE=1` (SDKs) or `NATIVEHTMLKIT_CLI_TEST_HEADLESS=1` (CLI) to run the full protocol without a window, for CI and smoke tests. There is no pointer or keyboard input, no clipboard, no native file dialog and no external opening. Document commands still work, so a test can type into fields (`replace_control_range`), submit forms (`request_submit`) and read the page back (`get_html`); [`scripts/test-examples.py`](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/scripts/test-examples.py) does exactly that.

## Reporting a problem

Open an issue in the repository that owns the component (links in the [Reference](../reference/index.md)), with the versions (`nativehtmlkit-python version`, `Get-Module NativeHTMLKit`, `nativehtmlkit --version`), your OS and desktop, the smallest script that shows the problem, and diagnostics at `debug` level.
