# Live bitmap charts

**Goal:** show pixels you compute yourself (a chart, a plot, a preview) and update them many times per second.

A *live bitmap* is a fixed-size RGBA image that belongs to one document. You create it with an id, reference it from an `<img src="ui4me-bitmap://ID">`, and present complete frames.

| Step | Python | PowerShell |
|---|---|---|
| Create | `bitmap = document.create_bitmap("chart", width, height)` | `$bitmap = New-NativeHTMLKitLiveBitmap -Document $doc -Id chart -Width w -Height h` |
| Show | `<img src="ui4me-bitmap://chart" width="w" height="h" alt="...">` | same |
| Draw a frame | `bitmap.present(rgba_bytes)` (`try_present` does not block) | `Send-NativeHTMLKitLiveBitmap -Bitmap $bitmap -Pixels $bytes` |
| Release | `bitmap.close()` | `Remove-NativeHTMLKitLiveBitmap -Bitmap $bitmap` |

- A frame is exactly `width * height * 4` bytes of straight-alpha RGBA8, row by row from the top left. Sizes are limited (up to 4096 x 4096).
- `present` returns once the host has taken a snapshot of the frame, which naturally limits your frame rate to what the host can show.
- Bitmaps are released automatically when their document is replaced or the window closes. Presenting to a released bitmap raises a stale-handle error.
- Keep text labels in HTML next to the image: they stay sharp, selectable and readable by screen readers. Give the `<img>` a meaningful `alt`.

## Python: a scrolling line chart

<!-- include: examples/howto/python/live_chart.py -->
```python title="examples/howto/python/live_chart.py"
"""Live chart: draw a scrolling line chart into a live bitmap ten times per second.

Teaches: Document.create_bitmap() with <img src="ui4me-bitmap://ID">, building straight-alpha
RGBA8 frames in Python, LiveBitmap.present() from a worker thread, a "change" event to pause,
labels in HTML next to the image, and closing the bitmap when the app ends.
Run:     python live_chart.py
Guide:   docs/how-to/live-bitmap-charts.md
"""
import math
import random
import threading
import time
from collections import deque

from nativehtmlkit import Application

WIDTH, HEIGHT = 400, 160
BACKGROUND = bytes((16, 22, 32, 255))
GRID = bytes((40, 52, 70, 255))
LINE = bytes((90, 170, 255, 255))

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 14px sans-serif; margin: 0; padding: 16px; background: #0c1018; color: #dfe6f0; }
  img { display: block; border: 1px solid #2c3a50; border-radius: 6px; }
  .bar { display: flex; gap: 16px; align-items: center; margin-top: 10px; }
  #value { font: 600 22px monospace; }
</style></head>
<body>
  <h1>Requests per second</h1>
  <img id="chart" src="ui4me-bitmap://requests" width="400" height="160" alt="Line chart of requests per second">
  <div class="bar">
    <span id="value" aria-live="polite">-</span>
    <label><input type="checkbox" id="paused"> Pause</label>
    <span id="frames">0 frames</span>
  </div>
</body></html>"""


def base_frame():
    """Background with horizontal grid lines every 40 pixels."""
    frame = bytearray(BACKGROUND * (WIDTH * HEIGHT))
    for y in range(0, HEIGHT, 40):
        start = y * WIDTH * 4
        frame[start:start + WIDTH * 4] = GRID * WIDTH
    return bytes(frame)


def draw(base, samples, top):
    """Copy the background and draw the samples (newest on the right) as a connected line."""
    frame = bytearray(base)
    previous = None
    offset = WIDTH - len(samples)
    for i, value in enumerate(samples):
        x = offset + i
        y = HEIGHT - 1 - int(min(value, top) / top * (HEIGHT - 1))
        low, high = (y, y) if previous is None else (min(y, previous), max(y, previous))
        for row in range(low, high + 1):  # a vertical span joins this point to the previous one
            index = (row * WIDTH + x) * 4
            frame[index:index + 4] = LINE
        previous = y
    return frame


def main():
    with Application.start(name="Live chart") as app:
        window = app.open_html(PAGE, title="Live chart", width=460, height=320)
        doc = window.document
        bitmap = doc.create_bitmap("requests", WIDTH, HEIGHT)
        paused = threading.Event()
        stopped = threading.Event()
        samples = deque(maxlen=WIDTH)
        base = base_frame()

        def run():
            frames, t = 0, 0.0
            while not stopped.wait(0.1):
                if paused.is_set():
                    continue
                t += 0.1
                value = 120 + 60 * math.sin(t / 2) + 25 * math.sin(t * 1.7) + random.uniform(-10, 10)
                samples.append(max(0.0, value))
                try:
                    bitmap.present(draw(base, samples, top=250))
                    frames += 1
                    doc.batch([{"op": "set_text", "element": "value", "text": f"{value:.0f} req/s"},
                               {"op": "set_text", "element": "frames", "text": f"{frames} frames"}])
                except Exception:
                    return  # the window closed or the app is shutting down: stop drawing

        def toggle(event):
            if event.get("checked"):
                paused.set()
            else:
                paused.clear()

        doc.on("change", toggle, element="paused")
        threading.Thread(target=run, name="chart", daemon=True).start()
        try:
            app.run()
        finally:
            stopped.set()
            bitmap.close()


if __name__ == "__main__":
    main()
```
<!-- /include -->

<!-- screenshot: howto-live-chart -->

- The background with grid lines is computed once; each frame copies it and draws the line.
- Drawing and presenting run on a worker thread, ten frames per second; `stopped` ends the loop when the app shuts down.

## PowerShell: a chart driven by your own loop

Instead of `Wait-NativeHTMLKit -UntilShutdown`, this script pumps events for up to 250 ms at a time and draws a frame in between. Per-pixel loops are slow in PowerShell, so the chart is small and updated four times per second.

<!-- include: examples/howto/powershell/live-chart.ps1 -->
```powershell title="examples/howto/powershell/live-chart.ps1"
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
```
<!-- /include -->

- `(Get-NativeHTMLKitDiagnosticReport -Application $app).Connection.ShutdownRequested` becomes true when the host shuts the app down; the loop then ends and `finally` releases everything.
- To keep `-UntilShutdown`, schedule frames with background tasks instead (see [Background work](background-work.md)).

Bitmaps are not a video player: there is no audio and no codec. The UI libraries have no bitmap component; create the bitmap on the UI's document with the SDK.
