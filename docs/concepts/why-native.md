# Why native instead of Electron or an embedded browser?

NativeHTMLKit targets local tools and small desktop applications where you want the familiar structure of HTML and CSS and the convenience of Python or PowerShell — without shipping a JavaScript engine, a browser process or a local web server.

## What you gain

- **One language for the logic.** Event handlers are ordinary Python functions or PowerShell scriptblocks. There is no front-end/back-end split, no bundler and no IPC layer for you to design.
- **Small, self-contained installs.** The SDK wheel or module bundles the native host; `pip install nativehtmlkit` or `Install-Module NativeHTMLKit` is the whole runtime. The CLI is a single archive.
- **No network surface.** There is no HTTP server and the renderer never fetches remote resources (see the [security model](security.md)).
- **Real native windows and services.** Native file and folder dialogs, clipboard, multiple windows, window state, desktop preferences, accessibility integration and live RGBA bitmaps are host features, not browser emulations.
- **Scripts become apps.** A PowerShell admin script or a shell pipeline can ask the user a question in a proper window (`nativehtmlkit select`, `form`) and continue with the answer.

## What you give up

- **A subset of the web platform.** The engine implements a large part of HTML and CSS layout, forms, dialogs and popovers, but it is not a complete browser. There are no JavaScript or browser APIs (`fetch`, `canvas`, web components, routing), no video/audio playback, and CSS support is defined by the engine's own profile and compatibility tests. Check the [capability matrix](../capabilities/matrix.md) and [styling guide](../python/sdk/guides/styling-and-layout.md) ([PowerShell](../powershell/sdk/guides/styling-and-layout.md)) instead of assuming Chrome behaviour.
- **No existing web component ecosystem.** React/Vue widgets, charting libraries in JavaScript and similar packages cannot run. Build charts with [live bitmaps](../python/sdk/guides/live-bitmaps.md) ([PowerShell](../powershell/sdk/guides/live-bitmaps.md)) or server-free HTML/CSS.
- **Platform scope.** The current targets are Linux with KDE Plasma on Wayland and Windows (x64). The Linux Python wheel needs glibc 2.39 or newer. See [limitations](../capabilities/limitations.md).
- **Young UI library.** `nativehtmlkit_ui` / `NativeHTMLKit.UI` 0.1.1 is an early release with a deliberately small component set.

## When to choose something else

- You need a complex single-page web application, existing JavaScript libraries, or exact browser rendering: use a browser-based stack.
- You need macOS today: it is not a target of the current releases.
- You need rich native widget toolkits (tree views with virtualization, docking, rich text editors): consider a native toolkit such as Qt.

If your app is a form, a dashboard, a picker, a settings dialog, a log viewer or a small utility written in Python or PowerShell, NativeHTMLKit is designed for exactly that. Start with [Getting started](../getting-started/index.md).
