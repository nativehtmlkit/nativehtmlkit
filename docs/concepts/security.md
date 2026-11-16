# Security model

NativeHTMLKit is a local desktop toolkit. Its security model is about keeping the host channel private, keeping untrusted text from becoming markup, and keeping the renderer away from the network and from arbitrary files.

## A private, authenticated channel

- The host creates a random token for each launch and gives the backend the endpoint and token through environment variables (`UI4ME_ENDPOINT`, `UI4ME_TOKEN`). The backend must authenticate with `host.hello` before anything else.
- The endpoint is local only: a Unix-domain socket on Linux, a named pipe on Windows. On Linux the host's runtime files are created private to the user (directories `0700`, files `0600`).
- The SDKs **remove the connection variables from their own environment** right after connecting, so programs your app starts do not inherit the secret and can launch their own NativeHTMLKit apps.
- The launcher's temporary manifest (which names the program, script, arguments and working directory) lives in a private temporary folder — mode `0700` on Linux; on Windows the per-user temporary folder's permissions apply — and is removed when the launcher ends.

## No JavaScript, no network

There is no JavaScript engine, so `<script>` content and `on…` attributes do nothing. The resource loader **always denies network URLs** (`http:`, `https:`, `ftp:`, `ws:` …) as well as `javascript:` and `blob:` URLs for stylesheets, images and fonts. Pages can use:

- local files **inside the document's asset root** (the folder of a loaded file, or the `asset_root` / `-AssetRoot` you pass) — paths outside every allowed root are refused before they are opened,
- `ui4me-res://` bundles you register from code, and `ui4me-bitmap://` live bitmaps.

Activating a link is reported to your program as a `link_activated` event; what happens next is your code's decision (for example `open_external`).

## Trusted and untrusted content

The one rule you must follow: **markup APIs take trusted HTML only.**

| Safe for any text (never parsed as HTML) | Trusted markup only |
|---|---|
| `doc.set_text`, `Set-NativeHTMLKitDocumentText`, `doc.set_value`, `Set-NativeHTMLKitDocumentValue`, `doc.set_attribute`, UI `text`/`heading`/`badge`/`alert`/`text_list` and their PowerShell equivalents | `doc.replace_html`, `doc.insert_html`, `Set-NativeHTMLKitDocumentHtml`, `open_html` / `Open-NativeHTMLKitHtml`, UI `raw_html` / `Add-NHKUiHtml` |

When you build HTML from data — file names, process names, user input, log lines — escape every value first: `html.escape(value)` in Python, `[System.Net.WebUtility]::HtmlEncode($value)` in PowerShell. Every tutorial and example on this site does this. The UI libraries escape all bound text and list items and reject unsafe attribute names (`on…`); generated element ids cannot be overridden.

## Desktop services

- `open_external` / `Open-NativeHTMLKitExternal` accepts only `http`, `https`, `mailto` and `file` URIs or absolute local paths. On Windows, local targets whose file type would be *executed* rather than opened (executables, scripts, shortcuts) are refused. Revealing a file requires a bounded absolute local path. Both are unavailable in headless mode.
- Clipboard access is explicit (`clipboard_text` / `set_clipboard_text`, `Get-/Set-NativeHTMLKitClipboard`). Clipboard editing commands are deferred and report completion through events.

## The CLI

`nativehtmlkit select` and `view` treat their stdin data as **untrusted**: it is escaped before display and bounded (UTF-8, up to 8 MiB, 2,000 rows and 32 columns in the 0.1.x line). The HTML passed to `nativehtmlkit form --html` and CSS passed with `--css` are **trusted developer input** — never feed them user-supplied content. Results are written to stdout only on success (exit 0). See the [CLI reference](https://github.com/nativehtmlkit/nativehtmlkit-cli/blob/main/docs/REFERENCE.md).

## What this model does not cover

NativeHTMLKit runs with the permissions of the user who starts it; it is not a sandbox for untrusted *code*. Your Python or PowerShell program can do anything that user can. Treat example scripts like any other script you run.

**Related:** [Architecture](architecture.md) · [Update the page](../how-to/update-the-page.md) · [Distribute your app](../how-to/distribute.md)
