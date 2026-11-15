# NativeHTMLKit

**HTML & CSS. Native by design.**

NativeHTMLKit is a Rust-powered toolkit for building desktop user interfaces with
ordinary HTML and CSS — **without Chromium, WebKit, Electron, a JavaScript runtime,
or a local web server**.

Application logic belongs to the tool or language that creates the UI. The native
host owns desktop windows, layout, rendering, input, and accessibility.

> **Status:** New project home. We are migrating the existing engine and developing
> a first standalone CLI. The repositories below are initially placeholders, not
> released SDKs.

## Explore the ecosystem

| Component | Purpose | Repository |
| --- | --- | --- |
| **Core** | Native Rust host, HTML/CSS engine, and versioned protocol | [nativehtmlkit-core](https://github.com/nativehtmlkit/nativehtmlkit-core) |
| **CLI** | Native selection windows, viewers, and forms for shell pipelines | [nativehtmlkit-cli](https://github.com/nativehtmlkit/nativehtmlkit-cli) |
| **Python SDK** | Use the native UI with plain Python *(planned)* | Coming later |
| **PowerShell SDK** | Use the native UI with PowerShell *(planned)* | Coming later |
| **Documentation** | Developer guides and examples *(planned)* | Coming later |

### What the CLI will enable

```bash
# Intended usage — the CLI is not released yet.
printf 'alpha\nbeta\ngamma\n' | nhk select --multi
```

The CLI will support both `nativehtmlkit` (full executable name) and `nhk`
(convenient command alias).

## Getting started

The ecosystem is being established. For the existing engine implementation and
its historical releases, see [UI4ME Core](https://github.com/ui4me/ui4me-core).
New NativeHTMLKit Core artifacts will be documented when their migration and
platform qualification have completed.

**Target platforms:** Linux Wayland desktops and interactive Windows desktops.
Support beyond those platforms will be documented only after verification.
