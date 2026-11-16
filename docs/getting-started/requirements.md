# Platform requirements

The released packages documented here are **Core 1.0.3**, **CLI 0.1.2**, **Python SDK 0.1.2**, **PowerShell SDK 0.1.2** and **UI 0.1.1** (Python and PowerShell, early release). Each SDK package and the CLI archive bundle the matching Core host, so you never install Core separately.

## Desktops

| Desktop | Status |
|---|---|
| Linux, KDE Plasma on Wayland | Target desktop for all entry points |
| Windows (x64), interactive desktop session | Target desktop for all entry points |
| Other Linux desktops, macOS | Not targeted by these releases |

A window needs an interactive desktop session. A plain SSH session, a service account or a CI runner can still run apps in the host's **headless test mode** (`NATIVEHTMLKIT_TEST_MODE=1` for the SDKs, `NATIVEHTMLKIT_CLI_TEST_HEADLESS=1` for the CLI): the whole protocol runs without a window, but there is no user input, no clipboard and no native file dialog. See [Troubleshooting](../python/sdk/guides/diagnostics-and-troubleshooting.md) ([PowerShell](../powershell/sdk/guides/diagnostics-and-troubleshooting.md)).

## Runtimes

| Entry point | Linux | Windows |
|---|---|---|
| Python SDK `nativehtmlkit` | Python 3.10+; x64 wheel tagged `manylinux_2_39_x86_64` (glibc 2.39 or newer) | Python 3.10+; x64 wheel |
| Python UI `nativehtmlkit_ui` | as the Python SDK (pure-Python wheel) | as the Python SDK |
| PowerShell SDK `NativeHTMLKit` | PowerShell 7.2+ | PowerShell 7.2+ and Windows PowerShell 5.1 |
| PowerShell UI `NativeHTMLKit.UI` | PowerShell 7.2+ | PowerShell 7.2+ and Windows PowerShell 5.1 |
| CLI `nativehtmlkit` / `nhk` | x64 release archive | x64 release archive |

If `pip` cannot find a compatible wheel on Linux, your distribution's glibc is probably older than 2.39. Do not fall back to the source distribution and expect a window: it contains no native host.

## Check an installation

```bash
nativehtmlkit-python doctor      # Python: the host's environment report
nativehtmlkit-python version     # Python: SDK, protocol and bundled host versions as JSON
nativehtmlkit doctor             # CLI: which host it found and its version
```

```powershell
Get-Module NativeHTMLKit -ListAvailable | Select-Object Name, Version
Get-NativeHTMLKitHostPath        # the bundled host for this platform
```

For per-feature availability see the [capability matrix](../capabilities/matrix.md) and the [limitations](../capabilities/limitations.md).
