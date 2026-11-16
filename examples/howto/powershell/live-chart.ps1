# Live chart: a scrolling bar chart of this process's working set, drawn into a live bitmap (PowerShell).
#
# Teaches: New-NativeHTMLKitLiveBitmap with <img src="ui4me-bitmap://ID">, filling a byte[] RGBA8
#          frame, Send-NativeHTMLKitLiveBitmap, and an application loop that pumps events with
#          Wait-NativeHTMLKit -TimeoutMilliseconds between frames instead of -UntilShutdown.
# Run:     pwsh -File live-chart.ps1        (Windows PowerShell 5.1: powershell.exe -File live-chart.ps1)
# Guide:   docs/how-to/live-bitmap-charts.md
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'Live chart'

$width = 240; $height = 100
$page = @'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 14px sans-serif; margin: 0; padding: 16px; background: #0c1018; color: #dfe6f0; }
  img { display: block; border: 1px solid #2c3a50; border-radius: 6px; }
  p { margin: 8px 0; }
</style></head>
<body>
  <h1>Working set of this script</h1>
  <img src="ui4me-bitmap://memory" width="240" height="100" alt="Bar chart of the working set over time">
  <p><span id="value">-</span> <label><input type="checkbox" id="paused"> Pause</label></p>
  <p id="frames">0 frames</p>
</body></html>
'@

$samples = New-Object System.Collections.Generic.List[double]
$state = [pscustomobject]@{ Paused = $false; Frames = 0 }

function New-ChartFrame {
    $pixels = New-Object 'byte[]' ($width * $height * 4)
    for ($i = 0; $i -lt $pixels.Length; $i += 4) { $pixels[$i] = 16; $pixels[$i + 1] = 22; $pixels[$i + 2] = 32; $pixels[$i + 3] = 255 }
    $top = 1.0
    foreach ($value in $samples) { if ($value -gt $top) { $top = $value } }
    $offset = $width - $samples.Count
    for ($s = 0; $s -lt $samples.Count; $s++) {
        $bar = [int]([Math]::Round($samples[$s] / $top * ($height - 4)))
        $x = $offset + $s
        for ($y = $height - $bar; $y -lt $height; $y++) {
            $i = ($y * $width + $x) * 4
            $pixels[$i] = 90; $pixels[$i + 1] = 170; $pixels[$i + 2] = 255
        }
    }
    return ,$pixels
}

$bitmap = $null
try {
    $window = New-NativeHTMLKitWindow -Application $app -Title 'Live chart' -Width 300 -Height 300
    $doc = Open-NativeHTMLKitHtml -Window $window -Html $page
    $bitmap = New-NativeHTMLKitLiveBitmap -Document $doc -Id memory -Width $width -Height $height
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type change -Element paused -Callback {
        param($eventObject) $state.Paused = [bool]$eventObject.checked
    }
    Set-NativeHTMLKitReady -Application $app
    $clock = [Diagnostics.Stopwatch]::StartNew()
    # Our own loop: handle events for up to 250 ms, then draw the next frame. The diagnostic
    # report tells when the host has shut the application down (last window closed or quit).
    while ($true) {
        $null = Wait-NativeHTMLKit -Application $app -TimeoutMilliseconds 250
        if ((Get-NativeHTMLKitDiagnosticReport -Application $app).Connection.ShutdownRequested) { break }
        if ($state.Paused -or $clock.ElapsedMilliseconds -lt 250) { continue }
        $clock.Restart()
        $megabytes = [System.Diagnostics.Process]::GetCurrentProcess().WorkingSet64 / 1MB
        $samples.Add($megabytes)
        if ($samples.Count -gt $width) { $samples.RemoveAt(0) }
        $null = Send-NativeHTMLKitLiveBitmap -Bitmap $bitmap -Pixels (New-ChartFrame)
        $state.Frames++
        Set-NativeHTMLKitDocumentText -Document $doc -Element value -Text ("{0:N1} MB" -f $megabytes)
        Set-NativeHTMLKitDocumentText -Document $doc -Element frames -Text "$($state.Frames) frames"
    }
} finally {
    if ($null -ne $bitmap) { Remove-NativeHTMLKitLiveBitmap -Bitmap $bitmap -Quiet }
    Close-NativeHTMLKit -Application $app
}
