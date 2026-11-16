# Which entry point should I use?

| Your job | Best entry point | Why |
|---|---|---|
| Existing Python app needs a window | Python SDK | Direct window/document control, small dependency surface |
| Python app needs compact UI controls | Python UI | State bindings, buttons, inputs, layouts, cards |
| PowerShell administrative script needs desktop input | PowerShell SDK | Native window lifecycle and OS dialog cmdlets |
| PowerShell script needs a reactive dashboard | PowerShell UI | Declarative controls and state based on the public SDK |
| Bash/terminal pipeline needs user selection | Native CLI | Standalone binary, stdin/stdout/exit-status contract |

The Python/PowerShell UI libraries are deliberately small, and do not replace SDK access for native dialogs, clipboard, live image surfaces or advanced document operations. Check availability and target OS in [the matrix](../capabilities/matrix.md).
