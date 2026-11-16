# Limitations and qualifications

- **UI version:** NativeHTMLKit UI 0.1.0 is a GitHub prerelease; its qualification occurred principally against earlier SDK and Core versions. Revalidate against the exact released current stack before claiming full production support.
- **Python SDK Linux:** the currently released x64 wheel uses a **manylinux_2_39_x86_64** tag. Earlier glibc versions do not meet that wheel's compatibility floor.
- **PowerShell 5.1:** Windows only. Linux uses PowerShell 7.2+.
- **Accessibility:** Core 1.0.3 has a reported Linux Orca collapsed-select announcement issue (NHK-CROSS-0010). UI-specific screen-reader coverage remains incomplete.
- **UI reactive state:** Python `Computed` can race when multiple threads mutate dependencies concurrently. Avoid such concurrent patterns until fixed.
- **UI lifecycle:** repeated disposed UI windows can accumulate shutdown callbacks; limit repeated create/dispose loops until fixed.
- **Not included:** JavaScript/browser APIs, HTTP server, general-purpose plugin framework, UI modal wrapper, web-style routing, video/audio playback, and full Chrome-level HTML/CSS support.
- **Screenshots:** initial visual in this documentation is a placeholder illustration; do not treat it as a native test capture. Real screenshots require interactive native qualification and sanitization.

For precise component status see [the matrix](matrix.md) and linked repository qualifications. A feature appearing in source code is not automatic proof of support on all OS/runtime combinations.
