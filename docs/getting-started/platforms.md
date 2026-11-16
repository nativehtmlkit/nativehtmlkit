# Linux and Windows

The UI library and the SDK are **the same on both platforms**: the same packages, API, examples and
behaviour, so every page in the [UI](../ui/index.md) and [SDK](../sdk/index.md) sections applies to
both. This page lists the few things that really differ. (The [CLI](../cli/index.md) is different:
shell scripts are written differently per system, so it has separate Linux and Windows sections.)

## Supported systems and runtimes

| | Linux | Windows |
|---|---|---|
| Desktop | KDE Plasma on Wayland | Interactive desktop session (also over RDP) |
| Python SDK and UI | Python 3.10+, x64, glibc 2.39 or newer (`manylinux_2_39_x86_64` wheel) | Python 3.10+, x64 |
| PowerShell SDK and UI | PowerShell 7.2+ | PowerShell 7.2+ **and** Windows PowerShell 5.1 |
| Native host | bundled in the package (`nativehtmlkit-host`) | bundled in the package (`nativehtmlkit-host.exe`) |

If `pip` finds no wheel on Linux, the distribution's glibc is older than 2.39; the source
distribution contains no host and cannot open windows. See [Platform requirements](requirements.md).

## What looks or behaves differently

| Topic | Linux | Windows |
|---|---|---|
| Window frame | KDE (KWin) decorations | Windows title bar; contents render identically |
| Native file dialogs | the desktop portal (`xdg-desktop-portal`) | the Windows common dialogs |
| Accessibility bridge | AT-SPI (Orca) | UI Automation (Narrator, NVDA) |
| Local connection between your program and the host | Unix domain socket | named pipe |
| Stopping an app from outside | `SIGTERM` to your script ends the host and backend | ending your script's process ends the host and backend (job object); there are no POSIX signals |
| Per-app folders (the `desktop.paths` host method; PowerShell: `Invoke-NativeHTMLKitRpc -Method desktop.paths`) | XDG folders (`~/.config`, `~/.local/share`, ...) | AppData folders (`%APPDATA%`, `%LOCALAPPDATA%`) |
| Live-bitmap shared files | the per-user runtime directory | `%TEMP%\nativehtmlkit-bitmaps\` (an empty folder may remain after the app exits) |
| File names your app creates | anything but `/` and NUL | not `< > : " / \` `?` `*`, the vertical bar, or control characters |

None of these change your code, except file names (validate them on Windows) and the
working-directory note below.

## Windows notes

- **Working directory of the backend.** On Windows the backend may start with an extended-length
  working directory (`\\?\C:\...`). Windows PowerShell 5.1's `Join-Path` rejects that form; resolve
  relative paths with `[IO.Path]::GetFullPath()` / `[IO.Path]::Combine()` (PowerShell) or
  `pathlib` (Python) instead. This is a known issue in Core 1.0.3.
- **Windows PowerShell 5.1.** Supported on Windows only. Scripts must avoid PowerShell 7 syntax
  (`?:`, `??`, `&&`, `||`), should be ASCII or UTF-8 **with BOM**, and must unroll arrays from
  `ConvertFrom-Json` (`$rows = ConvertFrom-Json $json | ForEach-Object { $_ }`). `$IsWindows` and
  `$IsLinux` do not exist in 5.1. Loops and runspaces are slower. Every PowerShell example on this
  site is tested on 5.1 as well as PowerShell 7. Details:
  [Windows PowerShell 5.1](../sdk/powershell/guides/windows-powershell-51.md).

## Linux notes

- A plain SSH session has no desktop. Run apps inside the KDE Plasma session, or use the host's
  headless test mode (`NATIVEHTMLKIT_TEST_MODE=1`) for automated tests; it behaves the same on both
  systems.
- Python wheels need glibc 2.39+ (for example Ubuntu 24.04 and newer, Debian 13).

## Screenshots on this site

The screenshots were captured on KDE Plasma 6.6 Wayland. On Windows the same programs look the same
apart from the window frame. The CLI section has separate Windows screenshots because its scripts
differ per system.
