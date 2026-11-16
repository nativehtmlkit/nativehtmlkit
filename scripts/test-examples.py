#!/usr/bin/env python3
"""Run every example in examples/ against the real NativeHTMLKit host in headless test mode.

Python and PowerShell examples start through their normal entry point (``Application.start`` /
``Start-NativeHTMLKitScript``) under ``NATIVEHTMLKIT_TEST_MODE=1``. A probe (scripts/example-probes/)
waits for app ready, runs the case's scenario against the live DOM using public document commands,
then requests an orderly quit. A case PASSES when the scenario passed, the launcher exited 0, stderr
shows no traceback/callback failure, and no process carrying the case's marker survives.
CLI scripts run with ``NATIVEHTMLKIT_CLI_TEST_HEADLESS=1`` and must give the expected exit status.
PowerShell files are also checked for Windows PowerShell 5.1 compatibility (parser + rules).

Usage (released packages installed by you):
  python3 scripts/test-examples.py --python VENV/bin/python --pwsh pwsh \
      --psmodulepath DIR_WITH_NativeHTMLKit_AND_NativeHTMLKit.UI --cli DIR_WITH_nativehtmlkit
Options: --only SUBSTRING (repeatable), --list, --json REPORT.json, --keep (keep temp dirs).
Linux only (orphan detection reads /proc). Uses the Python standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples"
PROBES = Path(__file__).resolve().parent / "example-probes"
BAD_STDERR = re.compile(r"Traceback|callback failed|handler failed|document error|Exception|"
                        r"ParserError|is not recognized|CommandNotFound|\x1b\[31;1m|^Cannot ", re.I | re.M)


def T(selector=None, index=0, id=None):
    return {"id": id} if id else {"selector": selector, "index": index}


def seed(name, content):
    """Setup helper: write a file into the case's temporary directory and pass its path as argument."""
    def setup(tmp: Path):
        path = tmp / name
        path.write_text(content, encoding="utf-8")
        return [str(path)]
    return setup


def file_contains(name, *needles):
    def check(tmp: Path):
        path = tmp / name
        if not path.exists():
            return False, f"{name} was not written"
        text = path.read_text(encoding="utf-8")
        missing = [n for n in needles if n not in text]
        return not missing, f"{name} missing {missing}" if missing else f"{name} ok"
    return check


NOTES = json.dumps({"version": 1, "notes": [
    {"id": 1, "text": "Water the plants", "done": False},
    {"id": 2, "text": "Renew passport", "done": True}]})
EXPENSES = json.dumps({"version": 1, "expenses": [
    {"description": "Train ticket", "amount": "12.50", "category": "travel"},
    {"description": "Lunch", "amount": "8.20", "category": "food"}]})
SETTINGS = json.dumps({"DisplayName": "Ada", "Email": "ada@example.org", "Theme": "graphite",
                       "RefreshSeconds": 60, "Notifications": True})
GIT_REPO = ["git init -q", "git commit -q --allow-empty -m 'Initial commit'",
            "git branch fix/typo", "git switch -q -c feature/login",
            "git commit -q --allow-empty -m 'Use \"quoted\" words'", "git switch -q main"]
CSV = "name,stage,owner\nAtlas,build,ops\nBorealis,<test>,qa\n"

# Each case: id, kind, path (relative to examples/), args/setup, steps, after (post checks).
CASES = [
    # ---- galleries --------------------------------------------------------------------------
    {"id": "gallery-python-sdk", "kind": "python", "path": "python-sdk/gallery.py",
     "steps": [{"expect": "NativeHTMLKit · Python SDK"}, {"expect": "ui4me-bitmap://gallery-preview"}]},
    {"id": "gallery-python-ui", "kind": "python", "path": "python-ui/gallery.py",
     "steps": [{"expect": "Developer clicked 0 times"},
               {"type": "Grace", "target": T("input")}, {"expect": "Grace clicked 0 times"}]},
    {"id": "gallery-powershell-sdk", "kind": "powershell", "path": "powershell-sdk/gallery.ps1",
     "steps": [{"expect": "NativeHTMLKit PowerShell SDK"}]},
    {"id": "gallery-powershell-ui", "kind": "powershell", "path": "powershell-ui/gallery.ps1",
     "steps": [{"expect": "Developer clicked 0 times"},
               {"type": "Grace", "target": T("input")}, {"expect": "Grace clicked 0 times"}]},
    # ---- tutorial: Python notes ------------------------------------------------------------
    {"id": "notes-step1", "kind": "python", "path": "tutorials/python-notes/step1_window.py",
     "steps": [{"expect": "Build a notes app"}, {"expect": 'class="note done"'}]},
    {"id": "notes-step2", "kind": "python", "path": "tutorials/python-notes/step2_add.py",
     "steps": [{"submit": T(id="add-form"), "submitted": False},
               {"type": "Call <Mum> & Dad", "target": T(id="new-note")}, {"submit": T(id="add-form")},
               {"expect": "<li>Call &lt;Mum&gt; &amp; Dad</li>"}, {"expect": "1 notes"}]},
    {"id": "notes-step3", "kind": "python", "path": "tutorials/python-notes/step3_actions.py",
     "steps": [{"expect": "0 notes, 0 open"}, {"type": "First", "target": T(id="new-note")},
               {"submit": T(id="add-form")}, {"expect": 'id="delete-1"'}, {"expect": "1 notes, 1 open"}]},
    {"id": "notes-final", "kind": "python", "path": "tutorials/python-notes/notes.py",
     "setup": seed("notes.json", NOTES),
     "steps": [{"expect": "Water the plants"}, {"expect": "2 notes, 1 open"},
               {"submit": T(id="add-form"), "submitted": False},
               {"type": "<b>Buy</b> milk & bread", "target": T(id="new-note")}, {"submit": T(id="add-form")},
               {"expect": "&lt;b&gt;Buy&lt;/b&gt; milk &amp; bread"}, {"expect": "3 notes, 2 open"},
               {"type": "passport", "target": T(id="filter")}, {"expect_not": "Water the plants"},
               {"expect": "Renew passport"}],
     "after": file_contains("notes.json", '"<b>Buy</b> milk & bread"', '"id": 3')},
    # ---- tutorial: Python UI expenses -------------------------------------------------------
    {"id": "expenses-step1", "kind": "python", "path": "tutorials/python-ui-expenses/step1_layout.py",
     "steps": [{"expect": "Preview: (no description) - 0 (food)"},
               {"type": "Coffee", "target": T("input", 0)}, {"type": "3.5", "target": T("input", 1)},
               {"expect": "Preview: Coffee - 3.5 (food)"}]},
    {"id": "expenses-step2", "kind": "python", "path": "tutorials/python-ui-expenses/step2_add.py",
     "steps": [{"submit": T("form")}, {"expect": "Enter a description."},
               {"type": "Coffee & cake", "target": T("input", 0)}, {"type": "0", "target": T("input", 1)},
               {"submit": T("form")}, {"expect": "Enter an amount greater than 0"},
               {"type": "4.5", "target": T("input", 1)}, {"submit": T("form")},
               {"expect": "<li>Coffee &amp; cake - Food - 4.50</li>"}]},
    {"id": "expenses-final", "kind": "python", "path": "tutorials/python-ui-expenses/expenses.py",
     "setup": seed("expenses.json", EXPENSES),
     "steps": [{"expect": "Total 20.70"}, {"expect": "Travel: 12.50"}, {"expect": "2 entries"},
               {"type": "Bus", "target": T("input", 0)}, {"type": "2.25", "target": T("input", 1)},
               {"submit": T("form")}, {"expect": "Total 22.95"}, {"expect": "Food: 10.45"},
               {"expect": "<li>Bus - Food - 2.25</li>"}],
     "after": file_contains("expenses.json", '"description": "Bus"', '"amount": "2.25"')},
    # ---- tutorial: PowerShell process dashboard --------------------------------------------
    {"id": "dashboard-step1", "kind": "powershell", "path": "tutorials/powershell-process-dashboard/step1-snapshot.ps1",
     "steps": [{"expect": "Top processes by memory"}, {"expect": '<td class="num">'}]},
    {"id": "dashboard-step2", "kind": "powershell", "path": "tutorials/powershell-process-dashboard/step2-filter.ps1",
     "steps": [{"expect": "Showing 25 of"}, {"type": "pwsh", "target": T(id="filter")}, {"expect": "<td>pwsh</td>"},
               {"type": "no-such-[process]", "target": T(id="filter")}, {"expect": "Showing 0 of"},
               {"submit": T(id="view-form")}, {"expect": "Showing 0 of"}]},
    {"id": "dashboard-final", "kind": "powershell", "path": "tutorials/powershell-process-dashboard/dashboard.ps1",
     "args": ["-RefreshSeconds", "1"],
     "steps": [{"expect": "(refresh #1)"}, {"expect": "MB in total"}, {"type": "pwsh", "target": T(id="filter")},
               {"expect": "<td>pwsh</td>"}, {"expect": "(refresh #2)", "timeout_ms": 8000},
               {"type": "no-such-[process]", "target": T(id="filter")}, {"expect": "Showing 0 of"}]},
    # ---- tutorial: PowerShell UI settings editor ------------------------------------------
    {"id": "settings-step1", "kind": "powershell", "path": "tutorials/powershell-ui-settings/step1-form.ps1",
     "steps": [{"expect": "Ada &lt;ada@example.org&gt;, cobalt theme, with e-mail notifications"},
               {"type": "Grace", "target": T("input", 0)}, {"expect": "Grace &lt;ada@example.org&gt;"}]},
    {"id": "settings-final", "kind": "powershell", "path": "tutorials/powershell-ui-settings/settings.ps1",
     "setup": seed("settings.json", SETTINGS),
     "steps": [{"expect": 'value="Ada"'}, {"expect": "nhk-theme-graphite"}, {"expect": "All changes saved"},
               {"type": "ada-at-example", "target": T("input", 1)}, {"expect": "The e-mail address looks invalid."},
               {"expect": "Unsaved changes"}, {"type": "ada@example.org", "target": T("input", 1)},
               {"expect_not": "looks invalid"}, {"expect": "All changes saved"},
               {"type": "2", "target": T("input", 2)}, {"expect": "Refresh interval must be a whole number"}]},
    # ---- tutorial: CLI branch picker (headless CLI: the window never decides, so --timeout -> 124)
    {"id": "branch-picker-step1", "kind": "cli", "path": "tutorials/cli-branch-picker/step1-pick.sh",
     "git_repo": GIT_REPO,
     "runs": [{"args": ["--timeout", "2"], "exit": 124, "stderr": ["No choice made in time"]}]},
    {"id": "branch-picker-final", "kind": "cli", "path": "tutorials/cli-branch-picker/git-pick.sh",
     "git_repo": GIT_REPO,
     "runs": [{"args": ["--print"], "exit": 0, "stdout": ["branch\tupdated\tlast commit", "feature/login\t",
                                                         "Use 'quoted' words"]},
              {"args": ["--timeout", "2"], "exit": 124, "stderr": ["no choice made in time; nothing changed"],
               "after": "git branch --show-current", "after_equals": "main"},
              {"args": ["--delete-merged", "--timeout", "2"], "exit": 124,
               "after": "git branch --list --format='%(refname:short)' | sort | tr '\\n' ' '",
               "after_equals": "feature/login fix/typo main"},
              {"args": ["--bogus"], "exit": 64, "stderr": ["unknown option"]},
              {"args": ["--help"], "exit": 0, "stdout": ["git-pick: choose a local Git branch"]}]},
    {"id": "branch-picker-outside-git", "kind": "cli", "path": "tutorials/cli-branch-picker/git-pick.sh",
     "runs": [{"args": [], "exit": 1, "stderr": ["not inside a Git repository"]}]},
    {"id": "settings-save-functions", "kind": "pwsh-check", "path": "tutorials/powershell-ui-settings/settings.ps1",
     "check": "settings-save-check.ps1"},
    # ---- generated starter projects (nativehtmlkit-new / New-NativeHTMLKitProject) -----------
    {"id": "scaffold-python", "kind": "python", "path": "(generated by nativehtmlkit-new)", "scaffold": "python",
     "steps": [{"expect": "Scaffolded"}]},
    {"id": "scaffold-powershell", "kind": "powershell", "path": "(generated by New-NativeHTMLKitProject)",
     "scaffold": "powershell", "steps": [{"expect": "Scaffolded"}]},
    # ---- how-to examples: Python SDK --------------------------------------------------------
    {"id": "howto-signup-form", "kind": "python", "path": "howto/python/signup_form.py",
     "steps": [{"submit": T(id="signup"), "submitted": False}, {"expect": "E-mail: Please fill out this field."},
               {"type": "ada@example.org", "target": T(id="email")}, {"type": "correct horse", "target": T(id="password")},
               {"type": "correct horsE", "target": T(id="confirm")},
               {"command": "set_checked", "target": T(id="terms"), "fields": {"checked": True}},
               {"submit": T(id="signup"), "submitted": False}, {"expect": "Repeat password: The passwords do not match."},
               {"type": "correct horse", "target": T(id="confirm")}, {"submit": T(id="signup")},
               {"expect": "Welcome, ada@example.org! Plan: free."},
               {"expect_command": {"command": "get_accessibility_tree", "contains": ['"name": "E-mail"', '"name": "Repeat password"']}}]},
    {"id": "howto-event-inspector", "kind": "python", "path": "howto/python/event_inspector.py",
     "steps": [{"type": "abc", "target": T(id="name")}, {"expect": "input: element='name'"},
               {"expect": "value='abc'"}]},
    {"id": "howto-status-board", "kind": "python", "path": "howto/python/status_board.py",
     "steps": [{"command": "set_selected_values", "target": T(id="service"), "fields": {"values": ["mail"]}},
               {"command": "set_selected_values", "target": T(id="state"), "fields": {"values": ["down"]}},
               {"type": "<i>relay</i> restarting", "target": T(id="note")}, {"submit": T(id="update")},
               {"expect": 'class="service down" id="svc-mail"'}, {"expect": "&lt;i&gt;relay&lt;/i&gt; restarting"},
               {"expect": 'id="h-1"'}]},
    {"id": "howto-log-windows", "kind": "python", "path": "howto/python/log_windows.py",
     "steps": [{"submit": T(id="open-form")}, {"expect_windows": 2}, {"expect": "Log: web #1"},
               {"command": "set_selected_values", "target": T(id="source"), "fields": {"values": ["mail"]}},
               {"submit": T(id="open-form")}, {"expect_windows": 3}, {"expect": "delivered &lt;alerts@example.org&gt;"},
               {"close_window": 1}, {"expect_windows": 2}, {"expect_not": "web #1", "window": 0},
               {"expect": "<li>mail #2</li>", "window": 0}]},
    {"id": "howto-file-preview", "kind": "python", "path": "howto/python/file_preview.py",
     "setup": seed("sample.txt", "first line\n<script>not html</script>\n"),
     "steps": [{"expect": "sample.txt"}, {"expect": "&lt;script&gt;not html&lt;/script&gt;"}, {"expect": "showing 2 lines"}]},
    {"id": "howto-dialogs", "kind": "python", "path": "howto/python/dialogs.py",
     "steps": [{"expect": "<li>Mobile app</li>"}, {"command": "show_dialog", "target": T(id="confirm"), "fields": {"modal": True}},
               {"command": "close_dialog", "target": T(id="confirm"), "fields": {"return_value": "cancel"}},
               {"expect": "Nothing was deleted"}, {"command": "show_dialog", "target": T(id="confirm"), "fields": {"modal": True}},
               {"command": "close_dialog", "target": T(id="confirm"), "fields": {"return_value": "delete"}},
               {"expect": "<li>No projects</li>"}, {"command": "show_dialog", "target": T(id="rename-dialog"), "fields": {"modal": True}},
               {"type": "Q3 <plans>", "target": T(id="new-name")}, {"submit": T(id="rename-form")},
               {"expect": "Q3 &lt;plans&gt;</h1>"}, {"expect": "List renamed"}]},
    {"id": "howto-clipboard-tool", "kind": "python", "path": "howto/python/clipboard_tool.py",
     "steps": [{"expect": "The clipboard is not available in this session"},
               {"type": "pear\nApple\npear\nbanana", "target": T(id="input")},
               {"command": "set_selected_values", "target": T(id="transform"), "fields": {"values": ["unique"]}},
               {"submit": T(id="tool")}, {"expect": "17 characters"},
               {"command": "set_selected_values", "target": T(id="transform"), "fields": {"values": ["json"]}},
               {"submit": T(id="tool")}, {"expect": "Cannot transform: Expecting value"}]},
    {"id": "howto-prime-counter", "kind": "python", "path": "howto/python/prime_counter.py",
     "steps": [{"type": "1000000", "target": T(id="limit")}, {"submit": T(id="job")},
               {"expect": "Done: 78,498 primes up to 1,000,000", "timeout_ms": 20000}, {"expect": "width: 100%"}]},
    {"id": "howto-live-chart", "kind": "python", "path": "howto/python/live_chart.py",
     "steps": [{"expect": "ui4me-bitmap://requests"}, {"expect": " req/s"}, {"expect": "frames</span>"}]},
    {"id": "howto-theme-switcher", "kind": "python", "path": "howto/python/theme_switcher.py",
     "steps": [{"expect": "rgb(47, 111, 208)"},
               {"command": "set_selected_values", "target": T(id="scheme"), "fields": {"values": ["dark"]}},
               {"command": "set_selected_values", "target": T(id="accent"), "fields": {"values": ["#1f8a4c"]}},
               {"submit": T(id="appearance")}, {"expect": "rgb(31, 138, 76)"},
               {"expect_style": {"target": T(id="panel"), "property": "background-color", "contains": "rgb(25, 33, 46)"}}]},
    {"id": "howto-css-support", "kind": "python", "path": "howto/python/css_support.py",
     "steps": [{"expect": "ui4me-desktop-1.0"}, {"expect": "css.display.grid"},
               {"type": "color-mix", "target": T(id="filter")}, {"expect_not": "css.display.grid"},
               {"expect": "css.function.color-mix"}]},
    # ---- how-to examples: Python UI ---------------------------------------------------------
    {"id": "howto-theme-preview", "kind": "python", "path": "howto/python-ui/theme_preview.py",
     "args": ["daylight", "comfortable", "#8a2be2"],
     "steps": [{"expect": "nhk-theme-daylight nhk-density-comfortable"}, {"expect": "--nhk-accent: #8a2be2"},
               {"expect_style": {"target": T("button.nhk-primary"), "property": "background-color",
                                 "contains": "rgb(138, 43, 226)"}}]},
    {"id": "howto-theme-preview-default", "kind": "python", "path": "howto/python-ui/theme_preview.py",
     "steps": [{"expect": "nhk-theme-cobalt nhk-density-compact"}]},
    {"id": "howto-word-counter", "kind": "python", "path": "howto/python-ui/word_counter.py",
     "setup": seed("words.txt", "the cat and the hat\nThe end\n"),
     "steps": [{"expect": "Source: words.txt"}, {"submit": T("form")},
               {"expect": "Done: 7 words, 5 different, 2 lines."}, {"expect": "<li>the: 3</li>"}]},
    # ---- how-to examples: PowerShell ---------------------------------------------------------
    {"id": "howto-ps-signup-form", "kind": "powershell", "path": "howto/powershell/signup-form.ps1",
     "steps": [{"submit": T(id="signup"), "submitted": False}, {"expect": "email: Please fill out this field."},
               {"type": "ada@example.org", "target": T(id="email")}, {"type": "correct horse", "target": T(id="password")},
               {"type": "correct horsE", "target": T(id="confirm")}, {"submit": T(id="signup"), "submitted": False},
               {"expect": "confirm: The passwords do not match."}, {"type": "correct horse", "target": T(id="confirm")},
               {"submit": T(id="signup")}, {"expect": "Welcome, ada@example.org! Plan: free."}]},
    {"id": "howto-ps-csv-viewer", "kind": "powershell", "path": "howto/powershell/csv-viewer.ps1",
     "setup": seed("stages.csv", CSV),
     "steps": [{"expect": "<th>stage</th>"}, {"expect": "<td>&lt;test&gt;</td>"}, {"expect": "2 rows, 3 columns"}]},
    {"id": "howto-ps-file-hash", "kind": "powershell", "path": "howto/powershell/file-hash.ps1",
     "setup": seed("hello.txt", "hello\n"),
     "steps": [{"submit": T(id="job")}, {"expect": "5891B5B522D5DF086D0FF0B110FBD9D21BB4FC7163AF34D08286A2E846F6BE03"},
               {"expect": "Done in"}, {"type": "/no/such/file", "target": T(id="path")}, {"submit": T(id="job")},
               {"expect": "That file does not exist."}]},
    {"id": "howto-ps-live-chart", "kind": "powershell", "path": "howto/powershell/live-chart.ps1", "start_after_pumps": 12,
     "steps": [{"expect": "ui4me-bitmap://memory"}, {"expect": " MB</span>"}, {"expect_not": ">0 frames<"}]},
]


def load_cases():
    return list(CASES)


def marker_processes(marker: str) -> list[str]:
    found = []
    needle = f"NHK_EXAMPLE_MARKER={marker}".encode()
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            if needle in (proc / "environ").read_bytes():
                found.append(proc.name + " " + (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")[:160])
        except OSError:
            continue
    return found


def run_app_case(case, args, tmp: Path):
    marker = uuid.uuid4().hex
    spec = tmp / "spec.json"
    spec.write_text(json.dumps({"steps": case.get("steps", []), "settle_ms": case.get("settle_ms", 800),
                                "start_after_pumps": case.get("start_after_pumps", 1)}), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not k.startswith("UI4ME_")}
    env.update(NATIVEHTMLKIT_TEST_MODE="1", NHK_PROBE_SPEC=str(spec), NHK_EXAMPLE_MARKER=marker,
               NATIVEHTMLKIT_DIAGNOSTICS_DIR=str(tmp / "diagnostics"))
    example = str(EX / case["path"])
    if case.get("scaffold") == "python":
        bindir = Path(args.python).parent
        subprocess.run([str(bindir / "nativehtmlkit-new"), str(tmp / "app"), "--name", "Scaffolded"], check=True,
                       capture_output=True, env=env)
        example = str(tmp / "app" / "app.py")
    elif case.get("scaffold") == "powershell":
        subprocess.run([args.pwsh, "-NoProfile", "-NonInteractive", "-Command",
                        f"New-NativeHTMLKitProject -Path '{tmp / 'app'}' -Name Scaffolded | Out-Null"], check=True,
                       capture_output=True, env={**env, "PSModulePath": args.psmodulepath + os.pathsep + env.get("PSModulePath", "")})
        example = str(tmp / "app" / "app.ps1")
    extra = list(case.get("args", []))
    if "setup" in case:
        extra = case["setup"](tmp) + extra
    if case["kind"] == "python":
        command = [args.python, str(PROBES / "probe.py"), example, *extra]
    else:
        env["PSModulePath"] = args.psmodulepath + os.pathsep + env.get("PSModulePath", "")
        command = [args.pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(PROBES / "probe.ps1"), example, *extra]
    started = time.monotonic()
    try:
        proc = subprocess.run(command, cwd=tmp, env=env, capture_output=True, text=True,
                              timeout=case.get("timeout", 90), start_new_session=True)
        code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as error:
        code, out, err = "timeout", error.stdout or "", (error.stderr or "") if isinstance(error.stderr, str) else ""
    elapsed = time.monotonic() - started
    problems = []
    report_file = Path(str(spec) + ".report.json")
    report = json.loads(report_file.read_text(encoding="utf-8")) if report_file.exists() else None
    if report is None:
        problems.append("probe wrote no report (example never reached the event loop)")
    elif not report.get("ok"):
        failed = [s for s in report.get("steps", []) if not s.get("ok")]
        done = len(report.get("steps", [])) - (1 if failed else 0)
        problems.append(f"scenario failed at step {done + 1}: " + json.dumps(failed or report.get("error"))[:1500])
    if code != 0:
        problems.append(f"exit status {code}")
    if BAD_STDERR.search(err or ""):
        problems.append("stderr: " + err[-1500:])
    if "after" in case:
        ok, detail = case["after"](tmp)
        if not ok:
            problems.append(detail)
    leftovers = []
    for _ in range(50):
        leftovers = marker_processes(marker)
        if not leftovers:
            break
        time.sleep(0.1)
    if leftovers:
        problems.append(f"orphan processes: {leftovers}")
    steps = len(report.get("steps", [])) if report else 0
    return problems, f"{elapsed:.1f}s, {steps} scenario step(s)"


def run_cli_case(case, args, tmp: Path):
    marker = uuid.uuid4().hex
    env = {k: v for k, v in os.environ.items() if not k.startswith("UI4ME_")}
    env.update(NATIVEHTMLKIT_CLI_TEST_HEADLESS="1", NHK_EXAMPLE_MARKER=marker,
               PATH=args.cli + os.pathsep + env.get("PATH", ""), GIT_CONFIG_GLOBAL=str(tmp / "gitconfig"),
               GIT_CONFIG_NOSYSTEM="1")
    (tmp / "gitconfig").write_text("[user]\n\tname = Example\n\temail = example@example.org\n[init]\n\tdefaultBranch = main\n")
    cwd = tmp
    if case.get("git_repo"):
        cwd = tmp / "repo"
        cwd.mkdir()
        for command in case["git_repo"]:
            subprocess.run(command, cwd=cwd, env=env, check=True, capture_output=True, shell=True)
    problems = []
    for check in case["runs"]:
        command = ["bash", str(EX / case["path"]), *check.get("args", [])]
        proc = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=60,
                              input=check.get("stdin"), start_new_session=True)
        if proc.returncode != check["exit"]:
            problems.append(f"{check.get('args')}: exit {proc.returncode}, expected {check['exit']}; stderr {proc.stderr[-600:]}")
        for needle in check.get("stdout", []):
            if needle not in proc.stdout:
                problems.append(f"{check.get('args')}: stdout lacks {needle!r}: {proc.stdout[-400:]}")
        for needle in check.get("stderr", []):
            if needle not in proc.stderr:
                problems.append(f"{check.get('args')}: stderr lacks {needle!r}: {proc.stderr[-400:]}")
        if "after" in check:
            got = subprocess.run(check["after"], cwd=cwd, env=env, capture_output=True, text=True, shell=True).stdout.strip()
            if got != check["after_equals"]:
                problems.append(f"{check['after']!r} gave {got!r}, expected {check['after_equals']!r}")
    time.sleep(0.3)
    if marker_processes(marker):
        problems.append(f"orphan processes: {marker_processes(marker)}")
    return problems, f"{len(case['runs'])} invocation(s)"


PS51_RULES = r'''
param([string[]]$Paths)
$bad = 0
foreach ($path in $Paths) {
    $bytes = [IO.File]::ReadAllBytes($path)
    if (@($bytes | Where-Object { $_ -gt 127 }).Count -gt 0) { "$path : non-ASCII bytes (Windows PowerShell 5.1 reads BOM-less files as ANSI)"; $bad++ }
    $tokens = $null; $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors)
    foreach ($e in $errors) { "$path : parse error $($e.Message)"; $bad++ }
    $seven = $ast.FindAll({ param($n) $n.GetType().Name -in @('TernaryExpressionAst', 'PipelineChainAst') }, $true)
    foreach ($n in $seven) { "$path : line $($n.Extent.StartLineNumber) uses $($n.GetType().Name) (PowerShell 7 only)"; $bad++ }
    foreach ($t in $tokens) {
        if ($t.Kind -in @('QuestionQuestion', 'QuestionQuestionEquals', 'QuestionDot', 'QuestionLBracket', 'AndAnd', 'OrOr')) {
            "$path : line $($t.Extent.StartLineNumber) uses '$($t.Text)' (PowerShell 7 only)"; $bad++
        }
    }
    $commands = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.CommandAst] }, $true)
    foreach ($c in $commands) {
        $text = $c.Extent.Text
        if ($text -match '-AsHashtable\b|-Parallel\b|\$IsWindows|\$IsLinux|\$IsMacOS|\bGet-Error\b|\bTest-Json\b') {
            "$path : line $($c.Extent.StartLineNumber) uses a PowerShell 7-only parameter or command"; $bad++
        }
    }
}
if ($bad) { exit 1 } else { 'OK' }
'''


def check_ps51(args, files):
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "ps51.ps1"
        script.write_text(PS51_RULES, encoding="ascii")
        proc = subprocess.run([args.pwsh, "-NoProfile", "-NonInteractive", "-File", str(script), *map(str, files)],
                              capture_output=True, text=True, timeout=120)
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--pwsh", default=shutil.which("pwsh") or "pwsh")
    parser.add_argument("--psmodulepath", default="")
    parser.add_argument("--cli", default="", help="directory containing the released nativehtmlkit binary")
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()
    cases = load_cases()
    if args.only:
        cases = [c for c in cases if any(o in c["id"] or o in c["path"] for o in args.only)]
    if args.list:
        for c in cases:
            print(f"{c['id']:40} {c['kind']:10} examples/{c['path']}")
        return 0
    covered = {c["path"] for c in load_cases() if c["kind"] != "pwsh-check"}
    uncovered = [str(p.relative_to(EX)) for p in sorted(EX.rglob("*")) if p.suffix in (".py", ".ps1", ".sh")
                 and str(p.relative_to(EX)) not in covered]
    results = []
    for case in cases:
        tmp = Path(tempfile.mkdtemp(prefix="nhk-example-"))
        try:
            if case["kind"] == "cli":
                if not args.cli:
                    results.append((case, "SKIP", "no --cli directory"))
                    continue
                problems, info = run_cli_case(case, args, tmp)
            elif case["kind"] == "pwsh-check":
                proc = subprocess.run([args.pwsh, "-NoProfile", "-NonInteractive", "-File", str(PROBES / case["check"]),
                                       str(EX / case["path"]), str(tmp)], capture_output=True, text=True, timeout=120)
                ok = proc.returncode == 0 and proc.stdout.strip().endswith("OK")
                problems, info = ([] if ok else [(proc.stdout + proc.stderr)[-800:]]), "function check"
            elif case["kind"] == "powershell" and not args.psmodulepath:
                results.append((case, "SKIP", "no --psmodulepath"))
                continue
            else:
                problems, info = run_app_case(case, args, tmp)
            results.append((case, "FAIL" if problems else "PASS", "; ".join(problems) if problems else info))
        finally:
            if not args.keep:
                shutil.rmtree(tmp, ignore_errors=True)
        case_result = results[-1]
        print(f"{case_result[1]:4}  {case['id']:40} {case_result[2]}", flush=True)
    if not args.only:
        ps_files = sorted(EX.rglob("*.ps1"))
        ok, detail = check_ps51(args, ps_files)
        results.append(({"id": "ps51-compatibility", "path": f"{len(ps_files)} .ps1 files"}, "PASS" if ok else "FAIL", detail))
        print(f"{results[-1][1]:4}  {'ps51-compatibility':40} {detail}")
        if uncovered:
            results.append(({"id": "coverage", "path": ""}, "FAIL", "examples without a case: " + ", ".join(uncovered)))
            print(f"FAIL  {'coverage':40} {results[-1][2]}")
    counts = {k: sum(1 for r in results if r[1] == k) for k in ("PASS", "FAIL", "SKIP")}
    print(f"\n{counts['PASS']} passed, {counts['FAIL']} failed, {counts['SKIP']} skipped")
    if args.json:
        Path(args.json).write_text(json.dumps([{"id": c["id"], "path": c["path"], "result": r, "detail": d}
                                               for c, r, d in results], indent=1), encoding="utf-8")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
