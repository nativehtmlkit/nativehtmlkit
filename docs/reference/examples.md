# Examples and verification

Every example on this site is a complete program kept in the repository that owns its API, listed
in that repository's `examples/catalog.toml`, and copied onto the site with its full source by
`scripts/import-docs.py`. Python and PowerShell examples share catalogue ids, so each Python example
page links to its PowerShell twin and back.

| Section | Examples | Verified by |
|---|---|---|
| [CLI on Linux](../cli/linux/examples/index.md) and [Windows](../cli/windows/examples/index.md) | bash and PowerShell scripts for every command and option | `scripts/test-examples.sh` (bash) and `scripts/test-examples.ps1` (PowerShell 7 and Windows PowerShell 5.1) in nativehtmlkit-cli |
| [Python SDK](../python/sdk/examples/index.md) | 21 apps | `tests/integration` (start-up and behaviour checks for every catalogue entry) in nativehtmlkit-python, Linux and Windows |
| [PowerShell SDK](../powershell/sdk/examples/index.md) | 20 apps | `tests/Examples.Tests.ps1` in nativehtmlkit-powershell, PowerShell 7 (Linux, Windows) and Windows PowerShell 5.1 |
| [Python UI](../python/ui/examples/index.md) and [PowerShell UI](../powershell/ui/examples/index.md) | 16 apps in each language | `qualification/examples/run_examples.py` in nativehtmlkit_ui, Linux and Windows PowerShell 5.1 |

## How examples are tested

Each harness runs every example through its normal entry point against the **released** packages
(Core 1.0.3, CLI 0.1.2, Python and PowerShell SDK 0.1.2, UI 0.1.1) with the host in headless test
mode. It waits until the app is ready, drives a short scenario through public document commands
(typing into fields, submitting forms, opening dialogs, reading the page back), requests an orderly
quit and checks the exit status, stderr, files written and leftover processes. CLI scripts run with
`--timeout` (exit status 124) plus their options and error paths. Every harness fails when a
catalogued example is missing or an example is not catalogued.

**Not covered headlessly:** real pointer and keyboard input, the clipboard, native file dialogs,
pixels on screen and screen readers. The screenshots on the example pages are real captures: each
example was started unchanged on KDE Plasma 6.6 Wayland and its window captured.
