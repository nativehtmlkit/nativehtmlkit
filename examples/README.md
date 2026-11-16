# Run the capability galleries

The four scripts in this directory are **real source examples**, not compiled binary distributions. They were statically checked against the 16 November 2026 public SDK/UI source, but the documentation packaging environment did **not** run native GUI tests.

| Gallery | Command | Shows |
|---|---|---|
| Python SDK | `python examples/python-sdk/gallery.py` | Direct DOM, events, HTML dialog, second window, file picker, bitmap |
| PowerShell SDK | `pwsh -File examples/powershell-sdk/gallery.ps1` | Same host-level patterns through exported cmdlets |
| Python UI | `python examples/python-ui/gallery.py` | State, computed/text, layout, inputs, select, list, conditional regions |
| PowerShell UI | `pwsh -File examples/powershell-ui/gallery.ps1` | PowerShell equivalents using `Add-NHKUi*` and state |

## Prerequisites

Install `nativehtmlkit` from its compatible native wheel. For the UI examples also install the appropriate UI package from a qualified release (the UI v0.1.0 is currently a GitHub prerelease). For PowerShell install the `NativeHTMLKit` module and, for UI, `NativeHTMLKit.UI` from an available release. Run in an **interactive desktop session** with an OS-native host; a headless SSH session alone will not demonstrate GUI input.

## What a user should test

- Buttons update status and state.
- Text fields, selections and checkboxes affect bound display text.
- Closing a dialog or a second window does not terminate the parent incorrectly.
- File picker returns to the app without freezing the event loop.
- Live bitmap display changes and releases resources correctly.

The matrix may include features not worth illustrating visually (transport safety, diagnostic counters, process supervision). Those have linked references and verification runs rather than dummy buttons.
