# NativeHTMLKit capability galleries

This repository builds the documentation site https://nativehtmlkit.github.io/ . It keeps only four
**capability galleries**: one window per entry point with a button for each feature, for manual
exploration.

| Gallery | Run |
|---|---|
| [Python SDK](python-sdk/gallery.py) | `uv run --with nativehtmlkit examples/python-sdk/gallery.py` |
| [Python UI](python-ui/gallery.py) | `uv run --with nativehtmlkit_ui examples/python-ui/gallery.py` |
| [PowerShell SDK](powershell-sdk/gallery.ps1) | `pwsh -File examples/powershell-sdk/gallery.ps1` |
| [PowerShell UI](powershell-ui/gallery.ps1) | `pwsh -File examples/powershell-ui/gallery.ps1` |

All other examples, tutorials and guides live in the repository that owns the API, each with an
`examples/catalog.toml`, and are published on the site with a screenshot and full source:

| Entry point | Examples |
|---|---|
| CLI (Linux and Windows) | https://github.com/nativehtmlkit/nativehtmlkit-cli/tree/main/examples |
| Python SDK | https://github.com/nativehtmlkit/nativehtmlkit-python/tree/main/examples |
| PowerShell SDK | https://github.com/nativehtmlkit/nativehtmlkit-powershell/tree/main/examples |
| Python and PowerShell UI | https://github.com/nativehtmlkit/nativehtmlkit_ui/tree/main/examples |

`scripts/test-examples.py` runs the galleries against the released packages in the host's headless
test mode; each owning repository runs its own examples the same way.
