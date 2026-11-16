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
