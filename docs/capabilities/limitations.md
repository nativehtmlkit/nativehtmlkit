# Limitations and qualifications

- **UI version:** NativeHTMLKit UI 0.1.1 is an early (pre-1.0) release. Its 0.1.1 packages passed the real-input GUI suite at 100% scaling against Python SDK 0.1.2 / PowerShell SDK 0.1.2 / Core 1.0.3 on KDE Plasma Wayland (Python, PowerShell 7) and Windows Server 2022 (Python, PowerShell 7, Windows PowerShell 5.1). IME, 125/150% scaling and screen-reader checks were last run against UI 0.1.0 with SDK 0.1.0 / Core 1.0.2.
- **Python SDK Linux:** the currently released x64 wheel uses a **manylinux_2_39_x86_64** tag. Earlier glibc versions do not meet that wheel's compatibility floor.
- **PowerShell 5.1:** Windows only. Linux uses PowerShell 7.2+.
- **Accessibility:** Core 1.0.3 has a reported Linux Orca collapsed-select announcement issue (NHK-CROSS-0010). UI-specific screen-reader coverage remains incomplete.
- **UI reactive state:** Python `Computed` can race when multiple threads mutate dependencies concurrently. Avoid such concurrent patterns until fixed.
- **UI lifecycle:** repeated disposed UI windows can accumulate shutdown callbacks; limit repeated create/dispose loops until fixed.
- **Not included:** JavaScript/browser APIs, HTTP server, general-purpose plugin framework, UI modal wrapper, web-style routing, video/audio playback, and full Chrome-level HTML/CSS support.
- **Screenshots:** initial visual in this documentation is a placeholder illustration; do not treat it as a native test capture. Real screenshots require interactive native qualification and sanitization.

For precise component status see [the matrix](matrix.md) and linked repository qualifications. A feature appearing in source code is not automatic proof of support on all OS/runtime combinations.
