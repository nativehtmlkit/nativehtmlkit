# Limitations and qualifications

This page lists what the released packages (Core 1.0.3, CLI 0.1.2, Python SDK 0.1.2, PowerShell SDK 0.1.2, UI 0.1.1) do not do, or do only with qualifications. For per-feature availability see [the matrix](matrix.md). A feature appearing in source code is not automatic proof of support on every OS/runtime combination.

## Platforms and runtimes

- **Targets:** Linux with KDE Plasma on Wayland, and Windows x64. macOS is not a target of the current releases.
- **Python SDK on Linux:** the released x64 wheel uses a **manylinux_2_39_x86_64** tag. Systems with glibc older than 2.39 do not meet that wheel's compatibility floor; the source package has no native host.
- **PowerShell:** Windows PowerShell 5.1 is Windows only. Linux uses PowerShell 7.2+.

## UI library

- **Version:** NativeHTMLKit UI 0.1.1 is an early (pre-1.0) release with a deliberately small component set. Its 0.1.1 packages passed the real-input GUI suite at 100% scaling against Python SDK 0.1.2 / PowerShell SDK 0.1.2 / Core 1.0.3 on KDE Plasma Wayland (Python, PowerShell 7) and Windows Server 2022 (Python, PowerShell 7, Windows PowerShell 5.1). IME, 125/150% scaling and screen-reader checks were last run against UI 0.1.0 with SDK 0.1.0 / Core 1.0.2.
- **Fixed tree:** components are declared before mounting; afterwards only bound state changes the page. Lists are text-only (`text_list` / `Add-NHKUiTextList`).
- **Reactive state:** Python `Computed` can race when multiple threads mutate its dependencies concurrently. Avoid such concurrent patterns until fixed; update related state from one thread.
- **Lifecycle:** repeatedly creating and disposing UI windows can accumulate shutdown callbacks; limit repeated create/dispose loops until fixed.
- **No modal wrapper:** HTML dialogs, native file dialogs, extra windows, clipboard and live bitmaps are SDK calls made next to the UI library.

## Accessibility

- Core 1.0.3 has a reported Linux Orca collapsed-select announcement issue (NHK-CROSS-0010).
- UI-specific screen-reader coverage remains incomplete. See [accessibility basics](../how-to/accessibility.md).

## Headless test mode

With `NATIVEHTMLKIT_TEST_MODE=1` (SDKs) or `NATIVEHTMLKIT_CLI_TEST_HEADLESS=1` (CLI) the host runs the protocol without a window. In that mode:

- there is **no synthetic user input** — only document operations you call (for example `request_submit`, which fires `submit`, or `replace_control_range`, which fires `input`) produce events; `set_value`, `set_checked` and `set_selected_values` fire none;
- the **clipboard** and **native file/folder dialogs** are unavailable and fail with RPC error `-32001`;
- opening external targets and revealing files are unavailable;
- desktop preferences report no observed values.

Headless runs prove startup, rendering, DOM state, readiness and clean shutdown — not real input, focus, IME or screen-reader behaviour.

## Not included

JavaScript and browser APIs, network resource loading, an HTTP server, a general-purpose plugin framework, a UI modal wrapper, web-style routing, video/audio playback, and full Chrome-level HTML/CSS support.

## Screenshots

The initial visual in this documentation is a **placeholder illustration**; do not treat it as a native test capture. Real screenshots require interactive native qualification and sanitization.
