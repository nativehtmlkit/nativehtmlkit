# Install and first steps

NativeHTMLKit shows native desktop windows whose content is plain HTML and CSS. Your program, written in Python or PowerShell (or a shell script using the CLI), owns the logic; a small native host process draws the window and sends you the user's events. There is no browser, no JavaScript and no local web server.

## Pick your path and install

Choose the layer you want to work with, then the language (or, for the CLI, your system). Each tab
has the complete install command and a quick check that it worked.

### UI library: reactive components (start here)

=== "Python"

    ```bash
    python -m pip install nativehtmlkit_ui        # also installs the nativehtmlkit SDK
    # or: uv add nativehtmlkit_ui
    python -m pip show nativehtmlkit nativehtmlkit_ui    # both installed, with versions
    ```

    Next: [Python UI library: getting started](../ui/python/getting-started.md)

=== "PowerShell"

    ```powershell
    Install-Module NativeHTMLKit.UI -Scope CurrentUser   # also installs the NativeHTMLKit SDK
    Get-Module NativeHTMLKit, NativeHTMLKit.UI -ListAvailable | Select-Object Name, Version
    ```

    Next: [PowerShell UI library: getting started](../ui/powershell/getting-started.md)

### SDK: your own HTML and CSS, full control

=== "Python"

    ```bash
    python -m pip install nativehtmlkit
    # or: uv add nativehtmlkit
    nativehtmlkit-python version        # SDK, protocol and bundled host versions
    ```

    Next: [Python SDK: getting started](../sdk/python/getting-started.md)

=== "PowerShell"

    ```powershell
    Install-Module NativeHTMLKit -Scope CurrentUser
    Get-NativeHTMLKitHostPath           # the bundled native host for this system
    ```

    Next: [PowerShell SDK: getting started](../sdk/powershell/getting-started.md)

### CLI: one question to the user from a shell script

=== "Linux"

    ```bash
    curl -fLO https://github.com/nativehtmlkit/nativehtmlkit-cli/releases/download/v0.1.2/nativehtmlkit-cli-v0.1.2-linux-x64.tar.gz
    tar -xzf nativehtmlkit-cli-v0.1.2-linux-x64.tar.gz
    cd nativehtmlkit-cli-v0.1.2-linux-x64
    ./nhk doctor
    ```

    Next: [CLI on Linux](../cli/linux/index.md) (checksums, putting it on `PATH`, first command)

=== "Windows"

    ```powershell
    Invoke-WebRequest -OutFile nativehtmlkit-cli-v0.1.2-windows-x64.zip `
        https://github.com/nativehtmlkit/nativehtmlkit-cli/releases/download/v0.1.2/nativehtmlkit-cli-v0.1.2-windows-x64.zip
    Expand-Archive .\nativehtmlkit-cli-v0.1.2-windows-x64.zip -DestinationPath "$env:LOCALAPPDATA\Programs"
    & "$env:LOCALAPPDATA\Programs\nativehtmlkit-cli-v0.1.2-windows-x64\nativehtmlkit.exe" doctor
    ```

    Next: [CLI on Windows](../cli/windows/index.md) (checksums, adding it to `PATH`, first command)

Not sure which to pick? Read [Choose an entry point](choose.md). Before installing, check the
[platform requirements](requirements.md) and the few [Linux and Windows differences](platforms.md).

## What happens when you run an app

1. You run your script normally (`python app.py`, `pwsh -File app.ps1`).
2. The SDK starts the bundled native host, and the host starts **your script a second time** as its *backend*, connected over a private local channel. That is why every example keeps its work *after* `Application.start()` / `Start-NativeHTMLKitScript`. See [Process and lifecycle](../concepts/lifecycle.md).
3. Your code opens windows, loads HTML, subscribes to events and announces that it is *ready*.
4. Events (clicks, typing, form submits) arrive in your callbacks; you change the page with document commands such as "set this element's text".
5. When the user closes the last window, the host shuts the application down and your script ends.

## After the first window

- Build a complete app: the tutorials in your section ([UI](../ui/index.md), [SDK](../sdk/index.md), [CLI](../cli/index.md)).
- Understand the model: [Concepts](../concepts/index.md).
- Look up exact APIs: [Reference](../reference/index.md) (each package documents its own API).

Every example on this site is a program in the repository that owns its API, run automatically against the released packages; see [Examples and verification](../reference/examples.md).
