# Reference

The landing site **teaches**; it does not keep a competing handwritten copy of API signatures. The exact, complete API of each package is documented in the repository that implements it, next to the source and released with it. Always check the documentation of the version you installed.

## API references by repository

| Repository | Front door | API reference | Examples | All docs |
|---|---|---|---|---|
| Core (native host, wire protocol) | [README](https://github.com/nativehtmlkit/nativehtmlkit-core/blob/main/README.md) | [Protocol v1](https://github.com/nativehtmlkit/nativehtmlkit-core/blob/main/protocol/README.md) · [Architecture](https://github.com/nativehtmlkit/nativehtmlkit-core/blob/main/docs/ARCHITECTURE.md) | — | [docs/](https://github.com/nativehtmlkit/nativehtmlkit-core/tree/main/docs) |
| CLI (`nativehtmlkit`, `nhk`) | [README](https://github.com/nativehtmlkit/nativehtmlkit-cli/blob/main/README.md) | [Command reference](https://github.com/nativehtmlkit/nativehtmlkit-cli/blob/main/docs/REFERENCE.md) | [examples](https://github.com/nativehtmlkit/nativehtmlkit-cli/blob/main/examples/README.md) | [docs/](https://github.com/nativehtmlkit/nativehtmlkit-cli/tree/main/docs) |
| Python SDK (`nativehtmlkit`) | [README](https://github.com/nativehtmlkit/nativehtmlkit-python/blob/main/README.md) | [API](https://github.com/nativehtmlkit/nativehtmlkit-python/blob/main/docs/API.md) | [examples](https://github.com/nativehtmlkit/nativehtmlkit-python/blob/main/examples/README.md) | [docs/](https://github.com/nativehtmlkit/nativehtmlkit-python/tree/main/docs) |
| PowerShell SDK (`NativeHTMLKit`) | [README](https://github.com/nativehtmlkit/nativehtmlkit-powershell/blob/main/README.md) | [API](https://github.com/nativehtmlkit/nativehtmlkit-powershell/blob/main/docs/API.md) | [examples](https://github.com/nativehtmlkit/nativehtmlkit-powershell/blob/main/examples/README.md) | [docs/](https://github.com/nativehtmlkit/nativehtmlkit-powershell/tree/main/docs) |
| UI library (`nativehtmlkit_ui`, `NativeHTMLKit.UI`) | [README](https://github.com/nativehtmlkit/nativehtmlkit_ui/blob/main/README.md) | [API](https://github.com/nativehtmlkit/nativehtmlkit_ui/blob/main/docs/API.md) | [examples](https://github.com/nativehtmlkit/nativehtmlkit_ui/blob/main/examples/README.md) | [docs/](https://github.com/nativehtmlkit/nativehtmlkit_ui/tree/main/docs) |

In PowerShell, `Get-Help <command> -Full` shows the installed module's own help; in Python, `help(nativehtmlkit.Document)` shows the installed docstrings.

## On this site

- [Capability matrix](../capabilities/matrix.md) — which feature is available in which entry point and release.
- [Limitations](../capabilities/limitations.md) — known issues, platform floors and what is out of scope.
- [Glossary](glossary.md) — the terms used across the documentation.
- [FAQ](faq.md) — short answers to common questions.
- [Examples on GitHub](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/README.md) — the runnable galleries, tutorials and how-to apps used on this site.

## Released versions documented here

Core 1.0.3 (wire protocol v1, stable) · CLI 0.1.2 · Python SDK 0.1.2 · PowerShell SDK 0.1.2 · UI 0.1.1 (Python and PowerShell, early release).
