#!/usr/bin/env python3
"""Copy verified example files into the documentation, so docs never drift from tested code.

In any Markdown file under docs/ (and README.md), a block

    <!-- include: examples/howto/python/signup_form.py -->
    ...anything...
    <!-- /include -->

is replaced by a fenced code block holding that file's exact content. The examples themselves are
verified by scripts/test-examples.py. Run without arguments to update, or with --check to fail
(exit 1) when a page is out of date. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(r"(<!-- include: (?P<path>[^ ]+) -->\n)(?P<body>.*?)(<!-- /include -->)", re.S)
LANGUAGES = {".py": "python", ".ps1": "powershell", ".sh": "bash", ".html": "html", ".css": "css", ".json": "json"}


def render(match: re.Match) -> str:
    rel = match.group("path")
    source = (ROOT / rel).resolve()
    if ROOT not in source.parents or not source.is_file():
        raise SystemExit(f"include target not found inside the repository: {rel}")
    text = source.read_text(encoding="utf-8").rstrip("\n")
    fence = "````" if "```" in text else "```"
    language = LANGUAGES.get(source.suffix, "text")
    return f"{match.group(1)}{fence}{language} title=\"{rel}\"\n{text}\n{fence}\n{match.group(4)}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    pages = sorted((ROOT / "docs").rglob("*.md")) + [ROOT / "README.md"]
    for page in pages:
        original = page.read_text(encoding="utf-8")
        updated = BLOCK.sub(render, original)
        if updated != original:
            stale.append(page.relative_to(ROOT))
            if not args.check:
                page.write_text(updated, encoding="utf-8")
    if args.check:
        if stale:
            print("Out-of-date example includes (run scripts/sync-snippets.py):", *stale, sep="\n  ", file=sys.stderr)
            return 1
        print("Example includes are current")
    else:
        print(f"Updated {len(stale)} page(s)" if stale else "Example includes were already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
