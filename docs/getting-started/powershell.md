# PowerShell SDK in five minutes

## 1. Install

```powershell
Install-Module NativeHTMLKit -Scope CurrentUser
```

PowerShell 7.2+ on Linux (KDE Plasma, Wayland) or Windows; Windows PowerShell 5.1 also works on Windows. The module bundles the native host for Linux x64 and Windows x64. See [requirements](requirements.md).

## 2. Write `hello.ps1`

<!-- include: examples/getting-started/hello.ps1 -->
```powershell title="examples/getting-started/hello.ps1"
# Hello, NativeHTMLKit: your first native window from PowerShell.
#
# Teaches: Start-NativeHTMLKitScript, New-NativeHTMLKitWindow, Open-NativeHTMLKitHtml,
#          Register-NativeHTMLKitDocumentEvent, Set-NativeHTMLKitDocumentText, Wait-NativeHTMLKit.
# Run:     pwsh -File hello.ps1           (Windows PowerShell 5.1: powershell.exe -File hello.ps1)
# Guide:   docs/getting-started/powershell.md
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit -ErrorAction Stop
# Starts the native host, which runs this script again as its backend: keep side effects below.
$app = Start-NativeHTMLKitScript -Name 'Hello'

$page = @'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 16px sans-serif; margin: 0; padding: 32px; }
  button { padding: 8px 16px; }
</style></head>
<body>
  <h1>Hello from PowerShell</h1>
  <button id="greet">Say hello</button>
  <p id="status">Not clicked yet.</p>
</body></html>
'@

try {
    $window = New-NativeHTMLKitWindow -Application $app -Title 'Hello' -Width 480 -Height 320
    $doc = Open-NativeHTMLKitHtml -Window $window -Html $page
    $counter = [pscustomobject]@{ Clicks = 0 }
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element greet -Callback {
        param($eventObject)
        $counter.Clicks++
        Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text "Hello! You clicked $($counter.Clicks) time(s)."
    }
    Set-NativeHTMLKitReady -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown   # handle events until the window is closed
} finally {
    Close-NativeHTMLKit -Application $app
}
```
<!-- /include -->

## 3. Run it

```powershell
pwsh -File hello.ps1                 # PowerShell 7
powershell.exe -File .\hello.ps1     # Windows PowerShell 5.1
```

Run it as a script file: `Start-NativeHTMLKitScript` needs a `.ps1` path, because the host starts that file again as its backend.

<!-- screenshot: getting-started-hello-powershell -->

## What just happened

- `Start-NativeHTMLKitScript` started the native host; the host ran `hello.ps1` a second time, with the same PowerShell edition and arguments, and the call returned the connected application there. In the first run the script ends inside that call. Everything above it runs twice.
- `New-NativeHTMLKitWindow` and `Open-NativeHTMLKitHtml` created the window and its document.
- `Register-NativeHTMLKitDocumentEvent` subscribed a script block to clicks on `#greet`. Callbacks run later, inside `Wait-NativeHTMLKit`, on this same runspace. State that callbacks change is kept in an object (`$counter.Clicks`), because assigning a plain variable inside a script block only creates a local copy.
- `Set-NativeHTMLKitDocumentText` changes text safely; it is never parsed as HTML.
- `Set-NativeHTMLKitReady` announces startup is complete; `Wait-NativeHTMLKit -UntilShutdown` pumps events until the last window closes. `Close-NativeHTMLKit` in `finally` releases everything.

Short aliases exist for most commands (`New-NHKWindow`, `Open-NHKHtml`, `Wait-NHK`, ...). This site uses the full names.

## Next steps

- Tutorial: [a live process dashboard](../tutorials/powershell-process-dashboard.md).
- How-to: [handle events](../how-to/handle-events.md), [background work](../how-to/background-work.md), [file dialogs](../how-to/file-dialogs.md).
- Generate a project skeleton: `New-NativeHTMLKitProject -Path ./my-app` (see [Distribute your app](../how-to/distribute.md)).
- Exact API: [PowerShell SDK reference](https://github.com/nativehtmlkit/nativehtmlkit-powershell/blob/main/docs/API.md), or `Get-Help <command> -Full`.
