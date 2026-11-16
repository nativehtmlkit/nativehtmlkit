# Glossary

**App id**
: A reverse-DNS identity such as `org.example.Notes` (`app_id=` in Python, `-AppId` in PowerShell). It identifies the application for single-instance forwarding. Without one, a stable id is derived from the script path.

**app.ready**
: The message a backend sends when startup is finished (at least one window exists). Python's `app.run()` sends it; PowerShell uses `Set-NativeHTMLKitReady` (or `Start-NHKUi`). It must arrive before the startup deadline.

**app.shutdown**
: The host's message that the application is ending: the last window closed or a quit was accepted. It implies that every window is closed — Core 1.0.x sends no `closed` event for the last window — and the SDKs retire all handles.

**Asset root**
: The folder that relative stylesheet, image and font URLs resolve against, and outside of which local resources are refused. By default the folder of a loaded HTML file; set it with `asset_root=` / `-AssetRoot`.

**Backend**
: Your Python or PowerShell process, started and supervised by the host, holding the application logic. See [lifecycle](../concepts/lifecycle.md).

**Before-close / before-quit policy**
: A callback the host asks before closing a window (`on_before_close`, `Set-NativeHTMLKitBeforeClose`) or quitting (`on_before_quit`, `Set-NativeHTMLKitBeforeQuit`). Returning false vetoes it.

**Delegation**
: Registering one event handler on a container id; it fires for events whose `path` contains that id. See [documents and handles](../concepts/documents-and-handles.md).

**Document**
: The HTML page shown in a window. Loading new HTML replaces it atomically and makes the previous document handle stale.

**Generation**
: The identity of one loaded document. Handles and node references belong to one generation.

**Headless / test mode**
: `NATIVEHTMLKIT_TEST_MODE=1` (SDKs) or `NATIVEHTMLKIT_CLI_TEST_HEADLESS=1` (CLI): the host runs the full protocol without showing windows. No user input, clipboard, native file dialogs or external opening.

**Host**
: The native Core executable `nativehtmlkit-host`, bundled with each SDK and the CLI. It owns windows, rendering, input and desktop services.

**Launcher**
: The first run of your script (`uv run app.py`, `pwsh -File app.ps1`). It starts the host, waits, and exits with the host's status; the host then runs the script again as the backend.

**Live bitmap**
: A bounded RGBA8 image surface that your code fills with pixels and presents to an `<img src="ui4me-bitmap://ID">`. Released with its document.

**Node reference**
: An opaque, generation-bound handle for an element that may have no `id`, returned by `query_nodes` / `Get-NativeHTMLKitNodes`.

**Owner thread / owner runspace**
: The thread (Python UI) or runspace (PowerShell, PowerShell UI) that is allowed to perform UI updates. See [threading](../concepts/threading.md).

**Protocol v1**
: The local JSON-RPC wire contract between backends/CLI and the host; stable since Core 1.0.3.

**Pump**
: In PowerShell, processing of host messages on your runspace by `Wait-NativeHTMLKit` and by every waiting SDK call.

**Stale handle**
: A window, document, node, bitmap or subscription whose host object no longer exists or was replaced. Using it raises `StaleDocumentError` (Python) or `NativeHTMLKit.StaleObjectException` (PowerShell).

**State / computed**
: The UI library's observable values (`state(...)`, `New-NHKUiState`) and derived values (`computed(...)`, `New-NHKUiComputed`) that bound components follow automatically.

**Supervisor**
: The host's role towards the backend: it starts it, watches it, and ends it on shutdown or failure.

**Task**
: In PowerShell, bounded background work started with `Start-NativeHTMLKitTask` in an isolated runspace; its completion callback runs on the owner runspace.

**ui4me-res://, ui4me-bitmap://**
: URL schemes for in-memory resource bundles registered from code (`register_resources`, `Register-NativeHTMLKitResources`) and for live bitmaps. The `ui4me-` spellings are the stable v1 names.
