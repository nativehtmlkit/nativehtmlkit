# Tutorials

Each tutorial builds one small but complete application, step by step. Every step is a runnable file in [`examples/tutorials/`](https://github.com/nativehtmlkit/nativehtmlkit/tree/main/examples/tutorials); the code shown here is copied from those files and tested against the released packages (see [Examples and verification](../reference/examples.md)).

| Tutorial | Entry point | You will learn |
|---|---|---|
| [Notes app with persistence](python-notes.md) | Python SDK | forms and `submit`, delegated clicks, re-rendering escaped HTML, live filtering, saving JSON safely |
| [Expense tracker with computed totals](python-ui-expenses.md) | Python UI | `state()` and `computed()`, two-way inputs, validation, lists, saving state on change |
| [Live process dashboard](powershell-process-dashboard.md) | PowerShell SDK | tables from objects, `input`/`change`/`submit` events, background refresh with `Start-NativeHTMLKitTask`, clipboard |
| [Settings editor](powershell-ui-settings.md) | PowerShell UI | states bound to inputs, computed validation and "unsaved changes", saving and reverting a JSON file |
| [Git branch picker](cli-branch-picker.md) | CLI | `nativehtmlkit select` in a Bash script, exit statuses, multi-select, timeouts |

Before you start, finish the matching [getting-started page](../getting-started/index.md) so the package is installed and a first window works on your desktop.

!!! tip "Run every step"
    Each step is a complete program. Run it, try it, then read the explanation. Closing the window ends the program.
