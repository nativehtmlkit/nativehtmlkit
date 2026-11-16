# Frequently asked questions

**Can I use JavaScript?**
No. There is no JavaScript engine. All logic runs in your Python or PowerShell program, which receives events and updates the page. See [why native](../concepts/why-native.md).

**Can a page load images or CSS from the internet?**
No. Network URLs are always denied. Use local files under the [asset root](glossary.md), registered `ui4me-res://` bundles or inline styles. Your program itself may use the network and then display the result.

**Why does my script run twice?**
The first run is the launcher that starts the native host; the host runs your script again as its backend. Keep side effects below `Application.start()` / `Start-NativeHTMLKitScript` or inside `main()`. See [lifecycle](../concepts/lifecycle.md).

**Why does a click handler wait while a file dialog is open (Python)?**
Events are delivered in order on one worker thread, and `open_files()` waits for the user by default. Use `wait=False` and a done-callback. See [file dialogs](../sdk/python/guides/file-dialogs.md) ([PowerShell](../sdk/powershell/guides/file-dialogs.md)).

**Why do clipboard or file-dialog calls fail in CI?**
In headless test mode (`NATIVEHTMLKIT_TEST_MODE=1`) there is no native event loop: clipboard and native dialogs fail with RPC error `-32001`. Catch the error and show a message, as the examples do.

**Can I simulate clicks in headless tests?**
There is no synthetic input. You can drive documented document operations — for example `request_submit` fires the form's `submit` event and `replace_control_range` fires `input` — and read the DOM back with `get_text`, `get_value` or `get_html`. Real input needs an interactive desktop.

**`pip install nativehtmlkit` fails or installs a package without the host on Linux.**
The released Linux wheel is `manylinux_2_39_x86_64`: it needs glibc 2.39 or newer. On older systems pip may fall back to the source package, which has no native host. Run `nativehtmlkit-python doctor` to check.

**Does it work with Windows PowerShell 5.1?**
Yes, on Windows, for both the SDK and the UI module. Linux needs PowerShell 7.2 or newer.

**Does it support macOS?**
Not in the current releases. Targets are Linux (KDE Plasma, Wayland) and Windows x64.

**Which entry point should I use?**
See [choosing an entry point](../getting-started/choose.md). In short: a shell pipeline → CLI; quick reactive forms → UI library; everything else (dialogs, multiple windows, bitmaps, full DOM control) → the SDK, optionally mixed with the UI library.

**Can I mix the UI library with SDK calls?**
Yes. The UI library is built on the public SDK; native dialogs, extra windows, clipboard and live bitmaps are SDK calls you make next to it.

**Are the screenshots on this site real?**
Images marked as illustrations or placeholders are not captures. Real screenshots are added only after interactive verification on a native desktop.

**How do I report a bug?**
Open an issue in the repository that owns the behaviour: rendering and native windows in [Core](https://github.com/nativehtmlkit/nativehtmlkit-core), commands in the [CLI](https://github.com/nativehtmlkit/nativehtmlkit-cli), language APIs in [Python](https://github.com/nativehtmlkit/nativehtmlkit-python) or [PowerShell](https://github.com/nativehtmlkit/nativehtmlkit-powershell), components in the [UI library](https://github.com/nativehtmlkit/nativehtmlkit_ui), and documentation in [this site's repository](https://github.com/nativehtmlkit/nativehtmlkit). Include the versions and, if possible, a diagnostic report (see [troubleshooting](../sdk/python/guides/diagnostics-and-troubleshooting.md) ([PowerShell](../sdk/powershell/guides/diagnostics-and-troubleshooting.md))).
