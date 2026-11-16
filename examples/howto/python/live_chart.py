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
