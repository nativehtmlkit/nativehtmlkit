# PowerShell — your first native window

## Install

```powershell
Install-Module NativeHTMLKit -Scope CurrentUser
Import-Module NativeHTMLKit
```

On Linux use PowerShell 7.2+ with KDE Wayland. Windows supports PowerShell 7.2+ and Windows PowerShell 5.1 in an interactive desktop session.

## Save `hello.ps1`

```powershell
Import-Module NativeHTMLKit -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'First NativeHTMLKit app'
try {
    $window = New-NativeHTMLKitWindow -Application $app -Title 'Hello'
    $doc = Open-NativeHTMLKitHtml -Window $window -Html '<button id="go">Click me</button><p id="status">Ready</p>'
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element go -Callback {
        Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Hello from PowerShell!'
    }
    Set-NativeHTMLKitReady -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally { Close-NativeHTMLKit -Application $app }
```

Run with `pwsh -File hello.ps1` or `powershell.exe -File hello.ps1` on Windows. The script is restarted under the native host: keep side effects below `Start-NativeHTMLKitScript`.

**Next:** [PowerShell SDK gallery](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/powershell-sdk/gallery.ps1) · [PowerShell UI](powershell-ui.md) · [SDK reference](https://github.com/nativehtmlkit/nativehtmlkit-powershell/blob/main/docs/API.md).
