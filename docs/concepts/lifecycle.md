# Process and lifecycle model

A NativeHTMLKit application is **two cooperating processes**: the native host, which owns the windows, and your script, which owns the logic. The SDK hides most of this, but knowing the model explains several rules you will meet in every tutorial.

```mermaid
sequenceDiagram
  participant L as Launcher run (python app.py / pwsh -File app.ps1)
  participant H as Native host
  participant B as Backend run (same script, second time)
  L->>H: start host with a private manifest
  H->>B: start the same script again, with endpoint + token
  B->>H: authenticate, create windows, load documents
  B->>H: app.ready
  Note over H,B: events flow to the backend, commands flow to the host
  H->>B: app.shutdown (last window closed or quit accepted)
  B-->>H: backend exits
  H-->>L: host exits; the launcher exits with the host's status
```

## Your script runs twice

When you run `python app.py`, `Application.start()` notices that it was not started by a host. It writes a private temporary manifest, starts the bundled host and waits; it **never returns** in that first run — the process ends with the host's exit status. The host then runs the *same command again* as its supervised backend. In that second run `Application.start()` connects to the host and returns the `Application`.

PowerShell works the same way: `Start-NativeHTMLKitScript` in a script run with `pwsh -File app.ps1` (or `powershell.exe -File app.ps1` on Windows) starts the host, which re-runs the script with the same PowerShell edition and arguments; the call returns the connected application only in the backend run. Script arguments are forwarded to the backend run.

Consequences:

- **Everything above `Application.start()` / `Start-NativeHTMLKitScript` runs twice.** Keep imports, constants and function definitions there; put side effects (reading files, creating folders, network calls) below the call or inside `main()`.
- Python examples use `if __name__ == "__main__": main()` and keep work inside `main()`.
- `Application.start()` must run from a script file or `python -m package.module`; it refuses an interactive interpreter, `python -c` and standard input, because it could not re-run them. Command-line arguments are passed to the backend run unchanged.
- A Python backend started with `python -m nativehtmlkit run module:main` (or by a host manifest) only connects; it is not relaunched.

## Starting up: `ready`

After connecting, the backend creates at least one window, loads its document and registers event handlers, then announces **ready**:

- Python: `app.run()` sends ready and then waits for shutdown (or call `app.ready()` yourself earlier).
- PowerShell: `Set-NativeHTMLKitReady -Application $app` (the UI library's `Start-NHKUi` does this for you unless you pass `-NoReady`), then `Wait-NativeHTMLKit -Application $app -UntilShutdown`.

The backend must authenticate and become ready before the manifest's startup deadline (`startup_timeout_ms` / `-StartupTimeoutMilliseconds`, default 30 seconds), otherwise the host gives up.

## Single or multiple instances

`instance="single"` (Python) / `-Instance single` (PowerShell) is the default: launching the same app again forwards the launch to the running instance instead of opening a second copy. The identity is the `app_id` / `-AppId` (a reverse-DNS name such as `org.example.Notes`); without one, a stable identity is derived from the script path. Use `"multiple"` for tools where several copies make sense.

## Closing windows and quitting

Closing is a negotiation, because a window may have unsaved work:

1. The user closes a window (or your code calls `window.request_close()` / `Close-NativeHTMLKitWindow`).
2. If you installed a **before-close policy** (`window.on_before_close(callback)` / `Set-NativeHTMLKitBeforeClose`), the host asks it; returning false keeps the window open. In PowerShell the scriptblock's *last output* decides (`$true` allows).
3. The window emits `close_requested` and then `closed` window events, and its handles become stale.

Quitting the whole application is negotiated the same way: `app.request_quit()` / `Request-NativeHTMLKitQuit` asks the **before-quit policy** (`app.on_before_quit(callback)` / `Set-NativeHTMLKitBeforeQuit`).

When the **last window** closes, or a quit is accepted, the host sends `app.shutdown`. In Core 1.0.x there is **no `closed` window event for that last window** — `app.shutdown` follows `close_requested` directly, and it implies that every window is closed. The SDKs therefore retire all window and document handles when shutdown arrives.

## Shutting down

- Python: `app.run()` delivers the events that arrived before `app.shutdown` (for up to two seconds), runs `app.on_shutdown(...)` callbacks in the thread that called `run()`, and returns normally. It raises `DisconnectedError` if the host disappeared instead of shutting down in order. Leaving the `with Application.start(...)` block closes the connection.
- PowerShell: `Wait-NativeHTMLKit -UntilShutdown` returns after shutdown (or after your own `Close-NativeHTMLKit`) and throws `NativeHTMLKit.DisconnectedException` if the host vanished first. Put `Close-NativeHTMLKit` (and `Stop-NHKUi`) in a `finally` block.

After `app.shutdown`, the backend has the manifest's shutdown timeout (`shutdown_timeout_ms`, default 5 seconds) to finish and exit.

## Exit status and teardown

The launcher exits with the host's status. If the Python launcher is interrupted by a signal it stops the host (bounded) and returns the conventional `128 + signal` status, for example **143** for SIGTERM and **130** for Ctrl+C. The host supervises the backend, and the launcher keeps the host tied to its own lifetime (on Windows through a job object, on Linux by watching the launcher process), so stopping the launcher does not leave orphaned host or backend processes.

## Headless test mode

Set `NATIVEHTMLKIT_TEST_MODE=1` before running a Python or PowerShell app, and the SDK starts the host with `--headless` (the CLI uses `NATIVEHTMLKIT_CLI_TEST_HEADLESS=1`). The host then runs the complete protocol and lifecycle — documents are parsed, styled and laid out, commands and queries work, events produced by document operations (for example `request_submit` firing `submit`, or `replace_control_range` firing `input`) are delivered — but **no window is shown** and:

- there is no user input: nothing clicks or types for you;
- the clipboard and native file dialogs are unavailable (the calls fail with RPC error `-32001`), as is opening external targets;
- desktop preferences report no observed values.

Headless mode is meant for continuous integration and automated checks that an app starts, renders, reaches ready and shuts down cleanly. It never proves real input, focus or accessibility behaviour; those need an interactive desktop.

**Related:** [Threading and callbacks](threading.md) · [Documents and stale handles](documents-and-handles.md) · [Troubleshooting](../how-to/troubleshooting.md)
