# NativeHTMLKit PowerShell SDK gallery. Run: pwsh -File examples/powershell-sdk/gallery.ps1
# Must be run in an interactive GUI desktop session with the SDK installed.
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'NativeHTMLKit PowerShell SDK Gallery'
$bitmap = $null
try {
    $html = @'
<!doctype html><html><head><meta charset="utf-8"><style>
body{background:#171f31;color:#e9f1ff;font:14px sans-serif;padding:20px}
section{background:#243451;border-radius:9px;padding:14px;margin:10px 0}
button{background:#3574c6;border:0;color:white;border-radius:6px;padding:9px;margin:4px}
input{background:#0d1828;color:white;padding:8px}
dialog{background:#243451;color:white;padding:20px}
</style></head><body>
<h1>NativeHTMLKit PowerShell SDK</h1><p>No browser or JavaScript: every action is an exported cmdlet.</p>
<section><h2>Document events</h2><button id="add">Increment</button>
<strong id="count">0</strong><p id="status">Ready</p>
<input id="name" placeholder="Enter name"><button id="read">Read input</button>
<button id="change-style">Set native DOM attribute</button></section>
<section><h2>Desktop integration</h2><button id="second">Second window</button>
<button id="modal">HTML dialog</button><button id="popover">Popover</button><button id="pick">Native file picker</button>
<button id="folder">Native folder picker</button></section>
<section><h2>Desktop services and diagnostics</h2>
<button id="copy">Write clipboard</button><button id="paste">Read clipboard</button>
<button id="diagnostics">Document diagnostics</button><button id="capabilities">Host capabilities</button></section>
<section><h2>Live bitmap</h2><button id="draw">Present bitmap</button>
<img src="ui4me-bitmap://ps-preview" width="160" height="90" alt="RGBA preview"></section>
<dialog id="about"><h2>HTML dialog</h2><p>Rendered by the native host.</p><button id="close-modal">Close</button></dialog>
<div id="tips" popover style="background:#2d4562;color:white;padding:14px">Native popover. <button id="hide-popover">Dismiss</button></div>
</body></html>
'@
    $window = New-NativeHTMLKitWindow -Application $app -Title 'PowerShell SDK gallery' -Width 900 -Height 720
    $doc = Open-NativeHTMLKitHtml -Window $window -Html $html
    $counter = [pscustomobject]@{ Value = 0; Frames = 0 }
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element add -Callback ({
        param($eventObject)
        $counter.Value = [int]$counter.Value + 1
        Set-NativeHTMLKitDocumentText -Document $doc -Element count -Text ([string]$counter.Value)
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element read -Callback ({
        param($eventObject)
        $value = Get-NativeHTMLKitValue -Document $doc -Element name
        Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text "Entered: $value"
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element second -Callback ({
        param($eventObject)
        $w = New-NativeHTMLKitWindow -Application $app -Title 'Second window' -Width 410 -Height 240
        $null = Open-NativeHTMLKitHtml -Window $w -Html '<main style="padding:30px"><h2>Second native window</h2><p>Close this window to return.</p></main>'
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element modal -Callback ({
        param($eventObject) Show-NativeHTMLKitHtmlDialog -Document $doc -Element about
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element 'close-modal' -Callback ({
        param($eventObject) Show-NativeHTMLKitHtmlDialog -Document $doc -Element about -Close
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element pick -Callback ({
        param($eventObject)
        try {
            $result = Show-NativeHTMLKitFileDialog -Window $window -Kind OpenFiles -Title 'Select a file'
            $message = if ($null -eq $result) { 'File selection cancelled' } else { "File result: $result" }
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text $message
        } catch {
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ("Dialog error: " + $_.Exception.GetType().Name)
        }
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element 'change-style' -Callback ({
        param($eventObject)
        Set-NativeHTMLKitDocumentAttribute -Document $doc -Element status -Name title -Value 'Native attribute updated'
        Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Updated native title attribute'
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element popover -Callback ({
        param($eventObject) Show-NativeHTMLKitPopover -Document $doc -Element tips -Action show
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element 'hide-popover' -Callback ({
        param($eventObject) Show-NativeHTMLKitPopover -Document $doc -Element tips -Action hide
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element folder -Callback ({
        param($eventObject)
        try {
            $result = Show-NativeHTMLKitFileDialog -Window $window -Kind ChooseFolder -Title 'Choose a folder'
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text "Folder result: $result"
        } catch {
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ('Folder dialog: ' + $_.Exception.GetType().Name)
        }
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element copy -Callback ({
        param($eventObject)
        try {
            Set-NativeHTMLKitClipboard -Application $app -Text 'Copied from NativeHTMLKit PowerShell gallery'
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Wrote to native clipboard'
        } catch { Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Clipboard unsupported in this session' }
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element paste -Callback ({
        param($eventObject)
        try {
            $value = Get-NativeHTMLKitClipboard -Application $app
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ("Clipboard: " + [string]$value)
        } catch { Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Clipboard unsupported in this session' }
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element diagnostics -Callback ({
        param($eventObject)
        try {
            $data = Get-NativeHTMLKitDiagnostics -Document $doc
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ('Document diagnostics: ' + ([string]($data | ConvertTo-Json -Compress -Depth 2)))
        } catch { Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Diagnostics returned an error' }
    }.GetNewClosure())
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element capabilities -Callback ({
        param($eventObject)
        try {
            $data = Get-NativeHTMLKitCapabilities -Application $app
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ('Host capabilities: ' + [string]($data | ConvertTo-Json -Compress -Depth 2))
        } catch { Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Capabilities returned an error' }
    }.GetNewClosure())
    $bitmap = New-NativeHTMLKitLiveBitmap -Document $doc -Id 'ps-preview' -Width 160 -Height 90
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element draw -Callback ({
        param($eventObject)
        $counter.Frames = [int]$counter.Frames + 1
        $pixels = New-Object 'byte[]' (160 * 90 * 4)
        for ($i=0; $i -lt $pixels.Length; $i+=4) {
            $pixels[$i] = [byte](($i / 4 + $counter.Frames * 31) % 256)
            $pixels[$i+1] = 110; $pixels[$i+2] = 185; $pixels[$i+3] = 255
        }
        $null = Send-NativeHTMLKitLiveBitmap -Bitmap $bitmap -Pixels $pixels
        Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text "Bitmap frame $($counter.Frames)"
    }.GetNewClosure())
    Set-NativeHTMLKitReady -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    if ($null -ne $bitmap) { Remove-NativeHTMLKitLiveBitmap -Bitmap $bitmap -Quiet }
    Close-NativeHTMLKit -Application $app
}
