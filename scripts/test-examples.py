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
Linux and Windows (Windows orphan detection compares host processes with a pre-case baseline). Uses the Python standard library only.
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
        path.write_bytes(content.encode("utf-8"))  # exact bytes: no CRLF translation on Windows
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



# Each case: id, kind, path (relative to examples/), args/setup, steps, after (post checks).
# Only the four galleries live here; every other example lives in its owning repository
# (catalogued in examples/catalog.toml there) and is verified by that repository's harness.
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
]


def load_cases():
    return list(CASES)


def _windows_session() -> int:
    import ctypes
    session = ctypes.c_ulong()
    ctypes.windll.kernel32.ProcessIdToSessionId(os.getpid(), ctypes.byref(session))
    return session.value


def _windows_hosts() -> list[str]:
    # Only hosts in this process's logon session: runs in other sessions (e.g. a desktop) are not ours.
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq nativehtmlkit-host.exe", "/FI", f"SESSION eq {_windows_session()}",
                          "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    return [line for line in out.splitlines() if "nativehtmlkit-host" in line]


WINDOWS_BASELINE: list[str] = []


def marker_processes(marker: str) -> list[str]:
    # Windows: other processes' environments are not readable; require that no host process
    # beyond those present before the case (WINDOWS_BASELINE) survives.
    if os.name == "nt":
        return [line for line in _windows_hosts() if line not in WINDOWS_BASELINE]
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
    if os.name == "nt":
        WINDOWS_BASELINE[:] = _windows_hosts()
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
    uncovered = [p.relative_to(EX).as_posix() for p in sorted(EX.rglob("*")) if p.suffix in (".py", ".ps1", ".sh")
                 and p.relative_to(EX).as_posix() not in covered]
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
