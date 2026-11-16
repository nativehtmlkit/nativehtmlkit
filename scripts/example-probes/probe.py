"""Headless probe for one Python example (used by scripts/test-examples.py; not an example itself).

Usage: python probe.py EXAMPLE.py [ARGS...]   with NHK_PROBE_SPEC=<spec.json> and
NATIVEHTMLKIT_TEST_MODE=1 in the environment.

The probe runs the example unchanged as ``__main__``. It wraps ``Application.run`` so that, once the
example has announced readiness, a scenario from the spec file runs against the live documents
through public document commands (``replace_control_range`` types into a control and fires a real
``input`` event, ``request_submit`` validates a form and fires real ``invalid``/``submit`` events,
``get_html`` reads the live DOM back). Then it asks the host for an orderly quit
(``Application.request_quit``) and writes a JSON report next to the spec.

Headless mode has no pointer input: a click handler cannot be exercised here. Only the window
bookkeeping dictionary of the SDK (``Application._windows``) is read privately, to enumerate windows.
"""
from __future__ import annotations

import json
import os
import re
import runpy
import sys
import threading
import time
import traceback

from nativehtmlkit import Application

SPEC = json.loads(open(os.environ["NHK_PROBE_SPEC"], encoding="utf-8").read())
REPORT = os.environ["NHK_PROBE_SPEC"] + ".report.json"
_original_run = Application.run


def _windows(app):
    def order(window):
        digits = re.sub(r"\D", "", window.id)
        return int(digits) if digits else 0
    return sorted((w for w in list(app._windows.values()) if w.document is not None and not w.closed), key=order)


def _document(app, step):
    windows = _windows(app)
    index = step.get("window", 0)
    if index >= len(windows):
        raise AssertionError(f"window {index} does not exist ({len(windows)} open)")
    return windows[index].document


def _target(document, target):
    if "id" in target:
        return target["id"]
    ids = document.query(target["selector"])["ids"]
    index = target.get("index", 0)
    if index >= len(ids):
        raise AssertionError(f"selector {target['selector']!r} matched {len(ids)} element(s) with an id")
    return ids[index]


def _html(app, step):
    if step.get("window", "any") == "any":
        return "\n".join(w.document.command("get_html")["html"] for w in _windows(app))
    return _document(app, step).command("get_html")["html"]


def _poll(step, check):
    deadline = time.monotonic() + step.get("timeout_ms", 5000) / 1000
    while True:
        ok, detail = check()
        if ok or time.monotonic() > deadline:
            return ok, detail
        time.sleep(0.05)


def _run_step(app, step):
    if "wait" in step:
        time.sleep(step["wait"] / 1000)
        return True, "waited"
    if "type" in step:
        document = _document(app, step)
        element = _target(document, step["target"])
        current = document.get_value(element)
        units = len(current.encode("utf-16-le")) // 2
        document.replace_control_range(element, step["type"], start=0, end=units, selection_mode="end")
        time.sleep(0.1)  # like a person: let input handlers run before the next action
        return True, f"typed into {element}"
    if "submit" in step:
        document = _document(app, step)
        form = _target(document, step["submit"])
        submitter = _target(document, step["submitter"]) if "submitter" in step else None
        result = document.request_submit(form, submitter=submitter)
        expected = step.get("submitted", True)
        return result.get("submitted") == expected, f"request_submit {form}: {result}"
    if "command" in step:
        document = _document(app, step)
        fields = dict(step.get("fields", {}))
        if "target" in step:
            fields["element"] = _target(document, step["target"])
        return True, f"{step['command']}: {document.command(step['command'], **fields)}"
    if "close_window" in step:
        _windows(app)[step["close_window"]].request_close()
        return True, f"request_close window {step['close_window']}"
    if "expect_command" in step:
        spec = step["expect_command"]

        def check():
            document = _document(app, step)
            fields = dict(spec.get("fields", {}))
            if "target" in spec:
                fields["element"] = _target(document, spec["target"])
            text = json.dumps(document.command(spec["command"], **fields))
            return all(n in text for n in spec["contains"]), f"{spec['command']}: {text[:300]}"
        return _poll(step, check)
    if "expect" in step:
        return _poll(step, lambda: (step["expect"] in _html(app, step), f"expect {step['expect']!r}"))
    if "expect_not" in step:
        return _poll(step, lambda: (step["expect_not"] not in _html(app, step), f"expect_not {step['expect_not']!r}"))
    if "expect_windows" in step:
        return _poll(step, lambda: (len(_windows(app)) == step["expect_windows"],
                                    f"windows={len(_windows(app))}"))
    if "expect_style" in step:
        spec = step["expect_style"]

        def check():
            document = _document(app, step)
            element = _target(document, spec["target"])
            style = document.computed_style([spec["property"]], element)
            text = json.dumps(style)
            return spec["contains"] in text, f"computed {spec['property']} of {element}: {text}"
        return _poll(step, check)
    raise ValueError(f"unknown probe step {step}")


def _scenario(app):
    report = {"ok": True, "steps": [], "error": None}
    try:
        time.sleep(SPEC.get("settle_ms", 800) / 1000)
        for step in SPEC.get("steps", []):
            ok, detail = _run_step(app, step)
            report["steps"].append({"step": step, "ok": bool(ok), "detail": str(detail)[:400]})
            if not ok:
                report["ok"] = False
                break
        report["windows"] = [{"id": w.id, "html_bytes": len(w.document.command("get_html")["html"])}
                             for w in _windows(app)]
    except BaseException as error:  # the report must always be written
        report["ok"] = False
        report["error"] = "".join(traceback.format_exception(error))[-2000:]
    finally:
        with open(REPORT, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=1)
        try:
            app.request_quit()
        except Exception:
            pass


def run(self):
    self.ready()
    threading.Thread(target=_scenario, args=(self,), name="nhk-example-probe", daemon=True).start()
    return _original_run(self)


Application.run = run
example = os.path.abspath(sys.argv[1])
sys.argv = [example, *sys.argv[2:]]
sys.path.insert(0, os.path.dirname(example))
runpy.run_path(example, run_name="__main__")
