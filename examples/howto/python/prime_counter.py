"""Prime counter: run a long computation in a worker thread with progress and a Cancel button.

Teaches: keeping event callbacks short (they share one ordered event worker), starting a
threading.Thread for slow work, updating the page from that thread (SDK calls are thread-safe),
throttling progress updates, cooperative cancellation with threading.Event, and disabling controls
while a job runs.
Run:     python prime_counter.py
Guide:   docs/how-to/background-work.md
"""
import threading
import time

from nativehtmlkit import Application

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; padding: 20px; background: #f4f6fa; color: #1d2433; }
  form { display: flex; gap: 8px; align-items: center; }
  input { width: 140px; padding: 6px; }
  button { padding: 6px 12px; }
  .track { height: 12px; background: #dde3ee; border-radius: 6px; margin: 16px 0 8px; }
  #bar { height: 12px; width: 0%; background: #2f6fd0; border-radius: 6px; }
</style></head>
<body>
  <h1>Count primes</h1>
  <form id="job">
    <label for="limit">Up to</label>
    <input id="limit" type="number" min="10" max="50000000" step="1" value="2000000" required>
    <button id="start">Start</button>
    <button id="cancel" type="button" disabled>Cancel</button>
  </form>
  <div class="track"><div id="bar"></div></div>
  <p id="status" role="status">Ready.</p>
</body></html>"""


def count_primes(limit, cancelled, progress):
    """Sieve of Eratosthenes in chunks; calls progress(fraction) now and then."""
    sieve = bytearray([1]) * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    step = 0
    for n in range(2, int(limit ** 0.5) + 1):
        if cancelled.is_set():
            return None
        if sieve[n]:
            sieve[n * n::n] = bytes(len(range(n * n, limit + 1, n)))
        step += 1
        if step % 200 == 0:
            progress(n * n / limit)
    return sum(sieve)


def main():
    with Application.start(name="Prime counter") as app:
        window = app.open_html(PAGE, title="Prime counter", width=520, height=320)
        doc = window.document
        job = {"cancel": None, "running": False}

        def set_running(running):
            if running:
                doc.set_attribute("start", "disabled", "")
                doc.remove_attribute("cancel", "disabled")
            else:
                doc.remove_attribute("start", "disabled")
                doc.set_attribute("cancel", "disabled", "")

        def worker(limit, cancelled):
            started = time.monotonic()
            last = [0.0]

            def progress(fraction):
                now = time.monotonic()
                if now - last[0] > 0.1:  # at most ten page updates per second
                    last[0] = now
                    doc.set_attribute("bar", "style", f"width: {fraction * 100:.0f}%")
                    doc.set_text("status", f"Working... {fraction:.0%}")

            try:
                result = count_primes(limit, cancelled, progress)
                if result is None:
                    doc.set_text("status", "Cancelled.")
                else:
                    doc.set_attribute("bar", "style", "width: 100%")
                    doc.set_text("status", f"Done: {result:,} primes up to {limit:,} "
                                           f"in {time.monotonic() - started:.2f} s.")
                set_running(False)
            except Exception as error:  # StaleDocumentError when the window closed mid-job
                print(f"Prime job stopped: {type(error).__name__}")
            finally:
                job["running"] = False

        def start(_event):
            if job["running"]:
                return  # one job at a time
            job["running"] = True
            limit = int(doc.get_value("limit"))
            job["cancel"] = threading.Event()
            set_running(True)
            doc.set_text("status", "Starting...")
            # daemon=True: a running job never keeps the process alive after the window closed.
            threading.Thread(target=worker, args=(limit, job["cancel"]), daemon=True).start()

        def cancel(_event):
            if job["cancel"] is not None:
                job["cancel"].set()

        doc.on("submit", start, element="job")
        doc.on("click", cancel, element="cancel")
        app.run()


if __name__ == "__main__":
    main()
