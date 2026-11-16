# Documents and stale handles

## Windows and documents

A **window** is a native top-level window owned by the host. It shows at most one **document**: the HTML you loaded with `app.open_html(...)` / `window.load_html(...)` / `window.load_file(...)` in Python, or `Open-NativeHTMLKitHtml` / `Open-NativeHTMLKitFile` in PowerShell. Loading new HTML into the same window **atomically replaces** its document; unloading (`doc.unload()` / `Remove-NativeHTMLKitDocument`) leaves the window open and empty.

An inline HTML source is limited to 1 MiB. Relative stylesheet, image and font URLs resolve against an **asset root**: the folder of a loaded file, or the folder you pass as `asset_root` / `-AssetRoot`.

## Handles are generation-bound

Every object the SDK gives you — `Window`, `Document`, `Node`, live bitmap, event subscription — refers to one specific host object. The host gives each document a new identity (generation) when it is loaded, so a handle can never silently point at a different page.

A document handle becomes **stale** when:

- its window loaded another document (the *old* document handle is retired, the new one is live),
- the document was unloaded,
- its window closed, or
- the application shut down (`app.shutdown` retires every window and document handle at once).

Using a stale handle fails **locally, before anything is sent**:

| | Python | PowerShell |
|---|---|---|
| Stale window or document | `nativehtmlkit.StaleDocumentError` (a `StaleHandleError`) | `NativeHTMLKit.StaleObjectException` |
| App is shutting down (new window/document refused) | `ApplicationShutdownError` | — (handles are already retired) |
| The host itself reports a gone object | `RpcError` with `code == -32004` | `NativeHTMLKit.RpcException` with `Code -32004` |
| Operation no longer valid (invalid state, e.g. during shutdown) | `RpcError` with `code == -32008` | `NativeHTMLKit.RpcException` with `Code -32008` |

The UI libraries treat these errors as “the document is gone” and dispose themselves quietly instead of reporting a corrupted UI.

**Practical rule:** after replacing a document, re-register event handlers on the *new* document object, and never cache document handles in long-lived workers without handling the stale error. Handlers, nodes and bitmaps of the old document are released with it.

## Elements, ids and nodes

Most commands address an element by its HTML `id` (`doc.set_text("status", "…")`, `Set-NativeHTMLKitDocumentText -Element status`). For elements without an id, `doc.query_nodes(selector)` / `Get-NativeHTMLKitNodes` return opaque **node references** that are bound to the same document generation; they become stale with it. `doc.query(selector)` returns only the ids of matching elements that have one.

Several changes can be applied as one host transaction with `doc.batch([...])` / `Invoke-NativeHTMLKitBatch`.

## Events and delegation

Event handlers are registered on the document: `doc.on("click", callback, element="save")` / `Register-NativeHTMLKitDocumentEvent -Type click -Element save`. The event object carries the `type`, the nearest identified target `element`, and `path` — the ids of identified elements on the event's route. A handler registered with an element id fires when that id is the target **or appears on the path**, so one handler on a list container can serve all its rows (delegation). Without `element`, the handler receives every event of that type.

- Events arrive **after native dispatch**. To stop a supported default action (for example a key's default editing), register it in advance with `doc.prevent_default(...)` / `Set-NativeHTMLKitPreventDefault`; a callback cannot cancel it afterwards.
- Control events carry the current `value` / `checked`; key events carry `key` and `code`.
- A document accepts at most **256** handlers.
- Programmatic changes are not user input: `set_value`, `set_checked` and `set_selected_values` fire **no** events, while `request_submit` runs validation and fires `invalid` / `submit`, and `replace_control_range` goes through the native editor and fires `input`.

## Live bitmaps

A live bitmap (`doc.create_bitmap(id, w, h)` / `New-NativeHTMLKitLiveBitmap`) is a bounded RGBA8 image surface for `<img src="ui4me-bitmap://ID">`, shared with the host through a private memory-mapped file. Presenting a frame waits until the host has taken it, so there is no unbounded frame queue. A bitmap belongs to its document and is released when the document is replaced, unloaded or its window closes. See [live bitmap charts](../sdk/python/guides/live-bitmaps.md) ([PowerShell](../sdk/powershell/guides/live-bitmaps.md)).

**Related:** [Update the page](../sdk/python/guides/updating-the-page.md) ([PowerShell](../sdk/powershell/guides/updating-the-page.md)) · [Handle events](../sdk/python/guides/events-and-callbacks.md) ([PowerShell](../sdk/powershell/guides/events-and-callbacks.md)) · [Threading and callbacks](threading.md)
