# Distribute your app

**Goal:** give your app to other people so that they can run it with one command.

The SDK packages and the CLI archive contain the native host for each supported platform, so a NativeHTMLKit app needs no separate runtime install: the user installs your app and its normal package dependencies.

## Start from a generated project

Both SDKs generate a small, runnable project with the HTML, CSS and code in separate files:

```bash
nativehtmlkit-new my-app --name "My App"     # app.py, index.html, style.css, pyproject.toml, app.toml
cd my-app && python app.py
```

```powershell
New-NativeHTMLKitProject -Path ./my-app -Name 'My App'    # app.ps1, index.html, style.css, app.toml
pwsh -File ./my-app/app.ps1
```

Use `-WindowsPowerShell` to generate an `app.toml` that names `powershell.exe`. Both generated apps are run by this site's test harness against the released packages.

`app.toml` is optional. Day to day you run the script directly; a launcher or deployment can instead start the host explicitly with the manifest (`nativehtmlkit-python-host run --app app.toml`, `Start-NativeHTMLKitHost -Manifest ./app.toml`). Check the `[backend] program` line: the Python generator writes the absolute path of the interpreter that created the project.

## Python

- Declare the dependency: `dependencies = ["nativehtmlkit>=0.1.2"]` (and `nativehtmlkit_ui>=0.1.1` if you use the UI library) in `pyproject.toml`. pip then picks the wheel for the user's platform, which includes the host.
- Users on Linux need glibc 2.39 or newer for the released wheel; on older systems pip finds no compatible wheel. Do not ship the source distribution as a fallback: it contains no host.
- Ship HTML, CSS, images and fonts as package data and locate them relative to your module (`Path(__file__).parent`), as the generated `app.py` does.
- Give your app a stable identity: `Application.start(name=..., app_id="org.example.MyApp")`. The default id is derived from the script path, which changes when users install the app elsewhere.
- `instance="single"` (the default) forwards a second launch to the running app; use `"multiple"` for tools that may run several times at once.

## PowerShell

- Publish a module or script whose manifest requires `NativeHTMLKit` (and `NativeHTMLKit.UI` if used), for example `RequiredModules = @(@{ ModuleName = 'NativeHTMLKit'; ModuleVersion = '0.1.2' })`. `Install-Module` then installs the SDK, which contains the hosts for Linux x64 and Windows x64.
- Users start the app with `pwsh -File app.ps1` (or `powershell.exe -File app.ps1`). `Start-NativeHTMLKitScript` must find the script file, so do not paste the code into an interactive prompt.
- Set `-AppId 'org.example.MyApp'` on `Start-NativeHTMLKitScript` for a stable identity, and `-Instance multiple` if needed.

## CLI scripts

Ship your script together with the instruction to install the CLI archive (or vendor the archive's folder next to your script and call it with an explicit path). Keep `nativehtmlkit`, `nhk` and `nativehtmlkit-host` in the same folder. Verify release archives with the published `SHA256SUMS`.

## Before you ship

- Run your app once on each target desktop with a real user session (KDE Plasma Wayland, Windows).
- Add a headless smoke test to your CI: run the app with `NATIVEHTMLKIT_TEST_MODE=1`, check that it reaches *ready*, then stop it. This site's [`scripts/test-examples.py`](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/scripts/test-examples.py) is a complete, standard-library-only example.
- Include the licence notices: the packages carry the host's `LICENSE`, `THIRD_PARTY_NOTICES.md` and `licenses/` files; keep them when you repackage.
