# Why native instead of Electron or an embedded browser?

NativeHTMLKit targets local application development where you want familiar HTML/CSS structure and standard scripting languages without shipping a JavaScript engine, browser process or local web server. Its Rust Core host owns desktop integration and rendering; a Python or PowerShell program owns the logic.

This simplifies some deployment paths but introduces real tradeoffs: the supported HTML/CSS subset is not every browser API, the renderer has its own behavior and compatibility tests, platform-specific input and accessibility need dedicated qualification, and you cannot run arbitrary web JavaScript components. For complex web applications, a browser-based framework may be more appropriate.

Start with [the first window](../getting-started/python.md), then inspect [the capability matrix](../capabilities/matrix.md) instead of assuming the full modern web platform exists.
