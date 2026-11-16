"""Word counter: count words in a large text file in a worker thread and show progress with UI state.

Teaches: starting background work from a UI event, setting State from a worker thread (bindings
marshal the page update onto the UI owner thread), throttled progress, a Cancel button, and
avoiding computed() values whose dependencies change on several threads at once (a known
limitation in nativehtmlkit_ui 0.1.1).
Run:     python word_counter.py [FILE]   (without FILE it generates sample text in memory)
Guide:   docs/how-to/background-work.md
"""
import re
import sys
import threading
import time
from collections import Counter
from contextlib import nullcontext
from pathlib import Path

from nativehtmlkit import Application
from nativehtmlkit_ui import UI, state

WORD = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?")


def sample_lines():
    words = "the quick brown fox jumps over the lazy dog while native windows render html".split()
    for i in range(200_000):
        yield " ".join(words[(i + j) % len(words)] for j in range(9))


def main():
    with Application.start(name="Word counter") as app:
        source = Path(sys.argv[1]) if len(sys.argv) > 1 else None
        progress = state("Press Count to start.")
        top_words = state([])
        running = state(False)
        cancel = threading.Event()

        def work():
            counts, lines, done, last = Counter(), 0, 0, 0.0
            try:
                opened = source.open(encoding="utf-8", errors="replace") if source else nullcontext(sample_lines())
                with opened as stream:
                    total = max(1, source.stat().st_size) if source else 200_000
                    for line in stream:
                        if cancel.is_set():
                            progress.set("Cancelled.")
                            return
                        counts.update(word.lower() for word in WORD.findall(line))
                        lines += 1
                        done += len(line.encode("utf-8")) if source else 1
                        if time.monotonic() - last > 0.2:  # at most five updates per second
                            last = time.monotonic()
                            progress.set(f"{done / total:.0%} - {lines:,} lines")
                progress.set(f"Done: {sum(counts.values()):,} words, {len(counts):,} different, {lines:,} lines.")
                top_words.set([f"{word}: {count:,}" for word, count in counts.most_common(10)])
            except OSError as error:
                progress.set(f"Cannot read the file: {error.strerror}")
            finally:
                running.set(False)

        def start(_event):
            if running.value:
                return
            cancel.clear()
            running.set(True)
            top_words.set([])
            progress.set("Starting...")
            threading.Thread(target=work, name="word-count", daemon=True).start()

        ui = UI(title="Word counter", theme="daylight", density="regular", width=560, height=520)
        with ui.column():
            ui.heading("Word counter", level=1)
            ui.text(f"Source: {source.name if source else 'generated sample text'}", muted=True)
            with ui.container("form") as form:
                with ui.row():
                    ui.element("button", css_class="nhk-button nhk-primary", attrs={"type": "submit"}, text="Count")
                    ui.button("Cancel", variant="secondary", on_click=lambda _e: cancel.set(),
                              disabled=lambda: not running.value)
            ui.on(form, "submit", start)
            ui.alert(progress)
            with ui.card():
                ui.heading("Most frequent words", level=2)
                ui.text_list(top_words)
        try:
            ui.mount(app)
            app.run()
        finally:
            cancel.set()
            ui.dispose()


if __name__ == "__main__":
    main()
