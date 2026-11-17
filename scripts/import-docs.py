#!/usr/bin/env python3
"""Assemble the documentation site tree from the owning repositories.

The owning repositories are the single source of truth for product documentation. This script
copies their docs into the site's section directories, generates one page per example from each
repository's examples/catalog.toml (summary, run command, screenshot, full source), generates the
Python <-> PowerShell parity tables and section indexes, and writes the navigation into
zensical.toml between the "# BEGIN GENERATED NAV" / "# END GENERATED NAV" markers.

    python3 scripts/import-docs.py            # regenerate
    python3 scripts/import-docs.py --check    # fail if the committed tree differs from a fresh import

Sibling repositories are located next to this one (../nativehtmlkit-python etc.) or via
NHK_REPOS_DIR. Generated directories are listed in GENERATED and are replaced wholesale; never edit
files inside them (the banner on every page says where to edit).
Python standard library only (3.11+).
"""
from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path

LANDING = Path(__file__).resolve().parents[1]
REPOS = Path(os.environ.get("NHK_REPOS_DIR", LANDING.parent))
GH = "https://github.com/nativehtmlkit"
GENERATED = ["cli", "ui", "sdk", "python", "powershell", "reference/protocol", "reference/core"]
LANG = {"python": ("Python", "python", ".py"), "powershell": ("PowerShell", "powershell", ".ps1"),
        "linux": ("Linux", "bash", ".sh"), "windows": ("Windows", "powershell", ".ps1")}


# --------------------------------------------------------------------------- helpers
def title_of(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip().replace("`", "")
    return path.stem.replace("-", " ").capitalize()


def ordered(directory: Path, explicit: list[str] | None = None) -> list[Path]:
    """Markdown files of a directory: explicit order first, then README link order, then name."""
    files = sorted(p for p in directory.glob("*.md") if p.name not in ("README.md", "index.md"))
    order: list[str] = list(explicit or [])
    readme = directory / "README.md"
    if readme.exists():
        order += [m.group(1) for m in re.finditer(r"\]\(\.?/?([\w.-]+\.md)\)", readme.read_text(encoding="utf-8"))]
    rank = {name: i for i, name in reversed(list(enumerate(order)))}
    return sorted(files, key=lambda p: (rank.get(p.name, 10_000), p.name))


PROGRAM = re.compile(r"\]\((https://github\.com/nativehtmlkit/([\w.-]+)/blob/main/(examples/[^)#\s]+?\.(?:py|ps1|sh)))\)")


def program_shots() -> dict:
    """(repo, 'examples/<path>') -> screenshot file, from the catalogues and prog-<path>.png captures."""
    shots: dict = {}
    for repo, keys in [("nativehtmlkit-python", [("file", "python")]),
                       ("nativehtmlkit-powershell", [("file", "powershell")]),
                       ("nativehtmlkit_ui", [("python", "python"), ("powershell", "powershell")]),
                       ("nativehtmlkit-cli", [("linux", "linux"), ("windows", "windows")]),
                       ("nativehtmlkit-core", [])]:
        for ex in load_catalog(repo):
            for key, lang in keys:
                if ex.get(key):
                    shot = screenshot_for(repo, ex, lang)
                    if shot:
                        shots[(repo, "examples/" + ex[key])] = shot
        folder = REPOS / repo / "docs" / "images" / "examples"
        for img in folder.glob("prog-*.png") if folder.is_dir() else []:
            stem = img.stem[len("prog-"):].replace("__", "/")
            for ext in (".py", ".ps1", ".sh"):
                if (REPOS / repo / "examples" / (stem + ext)).exists():
                    shots[(repo, "examples/" + stem + ext)] = img
    return shots


class Site:
    def __init__(self, out: Path):
        self.out = out
        self.shots = program_shots()
        self.hello: dict = {}   # getting-started page -> screenshot of the catalogue "hello" example
        self.pages: dict[str, tuple[Path, str]] = {}   # site rel path -> (source file, repo)
        self.nav: list = []

    # --- copying with link rewriting (two passes: register every page, then write with links resolved)
    def import_page(self, repo: str, src: Path, dest: str, src_root: Path | None = None, site_root: str | None = None) -> None:
        self.pages[dest] = (src, repo)

    def finalize(self) -> None:
        by_source = {src.resolve(): dest for dest, (src, _) in self.pages.items()}
        for dest, (src, repo) in self.pages.items():
            self._write_page(repo, src, dest, by_source)

    def _write_page(self, repo: str, src: Path, dest: str, by_source: dict) -> None:
        text = src.read_text(encoding="utf-8")
        repo_root = (REPOS / repo).resolve()
        rel_src = src.resolve().relative_to(repo_root).as_posix()
        dest_path = self.out / dest
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        def site_rel(target: str) -> str:
            return os.path.relpath(target, Path(dest).parent).replace(os.sep, "/")

        def fix(match: re.Match) -> str:
            label, target = match.group(1), match.group(2)
            if re.match(r"^[a-z]+:|^#|^/", target):
                return match.group(0)
            path_part, _, anchor = target.partition("#")
            if not path_part:
                return match.group(0)
            resolved = (src.parent / path_part).resolve()
            frag = "#" + anchor if anchor else ""
            if resolved in by_source:
                return f"[{label}]({site_rel(by_source[resolved])}{frag})"
            if resolved.is_dir() and (resolved / "README.md").resolve() in by_source:
                return f"[{label}]({site_rel(by_source[(resolved / 'README.md').resolve()])}{frag})"
            try:
                rel_repo = resolved.relative_to(repo_root)
            except ValueError:
                return match.group(0)
            if resolved.suffix.lower() in (".png", ".svg", ".jpg", ".jpeg", ".gif") and resolved.exists():
                asset = Path("_media") / repo / rel_repo
                (self.out / asset).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(resolved, self.out / asset)
                return f"[{label}]({site_rel(asset.as_posix())})"
            kind = "tree" if resolved.is_dir() else "blob"
            return f"[{label}]({GH}/{repo}/{kind}/main/{rel_repo.as_posix()}{frag})"

        parts = re.split(r"(^\s*```.*?^\s*```[^\n]*$)", text, flags=re.M | re.S)
        for i in range(0, len(parts), 2):
            parts[i] = re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", fix, parts[i])
        text = "".join(parts)
        text = self._add_screenshots(text, dest)
        banner = f"<!-- GENERATED by scripts/import-docs.py from {repo}/{rel_src}; edit it there. -->\n"
        note = (f"\n\n---\n\n<small>Source: [{repo}/{rel_src}]({GH}/{repo}/blob/main/{rel_src}) · "
                f"edit the page there.</small>\n")
        dest_path.write_text(banner + text.rstrip() + note, encoding="utf-8")

    def _add_screenshots(self, text: str, dest: str) -> str:
        """After each paragraph that links an example program with a capture, show the capture (once per page)."""
        out, pending, seen, in_code = [], [], set(), False
        for line in text.split("\n"):
            if line.lstrip().startswith("```"):
                in_code = not in_code
            if not in_code and not line.strip() and pending:
                for img in pending:
                    asset = Path("_media") / img.relative_to(REPOS)
                    (self.out / asset).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, self.out / asset)
                    rel = os.path.relpath(asset, Path(dest).parent).replace(os.sep, "/")
                    out += ["", f"![Screenshot: {img.stem}]({rel})", "", caption(img)]
                pending = []
            out.append(line)
            if not in_code:
                for m in PROGRAM.finditer(line):
                    img = self.shots.get((m.group(2), m.group(3)))
                    if img and img not in seen:
                        seen.add(img)
                        pending.append(img)
        if not seen and dest in self.hello:
            # Pages that write the first program inline: show it after the first full program block.
            lines, out2, in_code, block, done = out, [], False, 0, False
            for line in lines:
                out2.append(line)
                if line.lstrip().startswith("```"):
                    if in_code and block >= 8 and not done:
                        img = self.hello[dest]
                        asset = Path("_media") / img.relative_to(REPOS)
                        (self.out / asset).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(img, self.out / asset)
                        rel = os.path.relpath(asset, Path(dest).parent).replace(os.sep, "/")
                        out2 += ["", f"![Screenshot: {img.stem}]({rel})", "",
                                 "*Real capture on KDE Plasma 6.6 Wayland with the released packages.*"]
                        done = True
                    in_code, block = not in_code, 0
                elif in_code:
                    block += 1
            out = out2
        if pending:
            out.append("")
            for img in pending:
                asset = Path("_media") / img.relative_to(REPOS)
                (self.out / asset).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(img, self.out / asset)
                out += [f"![Screenshot: {img.stem}]({os.path.relpath(asset, Path(dest).parent)})", ""]
        return "\n".join(out)

    def import_tree(self, repo: str, src_dir: Path, site_dir: str, explicit: list[str] | None = None,
                    index_title: str | None = None, src_root: Path | None = None, site_root: str | None = None) -> list:
        """Import every page of a directory; return its nav entries (index first)."""
        src_root = src_root or src_dir
        site_root = site_root or site_dir
        entries: list = []
        index_src = next((src_dir / n for n in ("index.md", "README.md") if (src_dir / n).exists()), None)
        if index_src:
            self.import_page(repo, index_src, f"{site_dir}/index.md", src_root, site_root)
            entries.append(f"{site_dir}/index.md")
        elif index_title:
            self.write(f"{site_dir}/index.md", f"# {index_title}\n\n" + "\n".join(
                f"- [{title_of(p)}]({p.name})" for p in ordered(src_dir, explicit)) + "\n")
            entries.append(f"{site_dir}/index.md")
        for page in ordered(src_dir, explicit):
            dest = f"{site_dir}/{page.name}"
            self.import_page(repo, page, dest, src_root, site_root)
            entries.append({title_of(page): dest})
        return entries

    def write(self, dest: str, text: str) -> None:
        path = self.out / dest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<!-- GENERATED by scripts/import-docs.py; edit the generator or the owning repository. -->\n"
                        + text, encoding="utf-8")


# --------------------------------------------------------------------------- examples
def caption(img: Path) -> str:
    where = "Windows Server 2022" if img.name.startswith("windows-") else "KDE Plasma 6.6 Wayland"
    return f"*Real capture on {where} with the released packages.*"


def load_catalog(repo: str) -> list[dict]:
    path = REPOS / repo / "examples" / "catalog.toml"
    if not path.exists():
        return []
    return tomllib.loads(path.read_text(encoding="utf-8")).get("example", [])


def screenshot_for(repo: str, ex: dict, lang: str | None) -> Path | None:
    key = ex.get(f"screenshot_{lang}") if lang else None
    key = key or ex.get("screenshot")
    if key:
        p = REPOS / repo / key
        return p if p.exists() else None
    stem = ex["id"]
    folder = REPOS / repo / "docs" / "images" / "examples"
    file_key = lang if lang in ex else "file"
    fval = ex.get(file_key, "")
    if fval and "/" in fval and file_key == "file":   # SDK apps in their own folder: name/app.py
        fstem = fval.split("/")[0]
    else:
        fstem = Path(fval).stem if fval else stem
    short = {"python": "py", "powershell": "ps", "linux": "linux", "windows": "windows"}.get(lang or "", "")
    sdk = {"nativehtmlkit-python": "py-sdk", "nativehtmlkit-powershell": "ps-sdk"}.get(repo, "")
    cands = ([f"{lang}-{stem}.png", f"ui-{short}-{fstem}.png"] if lang else []) + \
            ([f"{sdk}-{fstem}.png", f"{sdk}-{stem}.png"] if sdk else []) + [f"{stem}.png"]
    for cand in cands:
        if (folder / cand).exists():
            return folder / cand
    return None


def example_page(site: Site, repo: str, ex: dict, lang: str, file_key: str, run_key: str, dest: str,
                 twin: str | None, twin_label: str | None) -> None:
    label, fence, _ = LANG[lang]
    rel = ex[file_key]
    src = REPOS / repo / "examples" / rel
    code = src.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip()
    lines = [f"# {ex['title']}", "", ex.get("summary", "")]
    if ex.get("language_specific"):
        other_name = {"linux": "on Windows", "windows": "on Linux"}.get(lang, "in the other language")
        lines += ["", f'!!! info "{label} only"', f"    This example has no counterpart {other_name}."]
    if twin and twin_label:
        lines += ["", f"*Same example in {twin_label}: [{ex['title']}]({twin})*"]
    lines += [""]
    shot = screenshot_for(repo, ex, lang)
    if shot:
        asset = Path(dest).parent / "img" / shot.name
        (site.out / asset).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shot, site.out / asset)
        lines += [f"![{ex['title']}](img/{shot.name})", "", caption(shot), ""]
    if ex.get("teaches"):
        lines += ["**What it teaches:** " + "; ".join(ex["teaches"]) + ".", ""]
    run = ex.get(run_key) or ex.get("run")
    if run:
        setup = []
        if lang == "python":  # in a uv project that has the package (see getting started)
            package = "nativehtmlkit_ui" if repo == "nativehtmlkit_ui" else "nativehtmlkit"
            setup = [f"uv init --app myapp && cd myapp    # once: a uv project for your app",
                     f"uv add {package}", "# save the example file(s) in the project folder, then:"]
        lines += ["## Run it", "", f"```{fence if lang in ('linux', 'windows') else ('bash' if lang == 'python' else 'powershell')}",
                  *setup, run, "```", ""]
    guide = ex.get("guide")
    if guide:
        target = Path(dest).parent.parent / "guides" / f"{guide}.md"
        if target.as_posix() in site.pages or (site.out / target).exists():
            lines += [f"Related guide: [{guide.replace('-', ' ')}](../guides/{guide}.md)", ""]
    lines += [f"## Source: `{rel}`", "",
              f"[View on GitHub]({GH}/{repo}/blob/main/examples/{rel})", "",
              f"```{fence}", code, "```", ""]
    site.write(dest, "\n".join(lines))


def examples_section(site: Site, repo: str, base: str, lang: str, file_key: str, run_key: str,
                     twin_base: str | None, twin_lang: str | None, twin_file_key: str | None,
                     twin_repo: str | None = None, intro: str = "") -> list:
    catalog = load_catalog(repo)
    twin_ids = {e["id"] for e in load_catalog(twin_repo or repo) if twin_file_key and e.get(twin_file_key)} if twin_base else set()
    entries = [f"{base}/index.md"]
    rows = []
    for ex in catalog:
        if not ex.get(file_key):
            continue
        dest = f"{base}/{ex['id']}.md"
        twin = None
        if twin_base and ex["id"] in twin_ids:
            twin = os.path.relpath(f"{twin_base}/{ex['id']}.md", base).replace(os.sep, "/")
        example_page(site, repo, ex, lang, file_key, run_key, dest, twin, LANG[twin_lang][0] if twin_lang else None)
        entries.append({ex["title"]: dest})
        shot = screenshot_for(repo, ex, lang)
        thumb = f"![]({'img/' + shot.name})" if shot else ""
        rows.append(f"| [{ex['title']}]({ex['id']}.md) | {ex.get('summary', '')} | {thumb} |")
    site.write(f"{base}/index.md", "\n".join([
        f"# {LANG[lang][0]} examples" if not intro else intro.splitlines()[0], "",
        *(intro.splitlines()[1:] if intro else []), "",
        "Every example is a complete program, verified against the real NativeHTMLKit host. Open one to see "
        "a screenshot, how to run it and its full source.", "",
        "| Example | What it does | |", "|---|---|---|", *rows, ""]))
    return entries


# --------------------------------------------------------------------------- sections
def sdk_section(site: Site, lang: str) -> list:
    repo = "nativehtmlkit-python" if lang == "python" else "nativehtmlkit-powershell"
    other = "powershell" if lang == "python" else "python"
    other_repo = "nativehtmlkit-powershell" if lang == "python" else "nativehtmlkit-python"
    root = REPOS / repo
    base = f"sdk/{lang}"
    nav: list = [f"{base}/index.md"]
    docs = root / "docs"
    if (docs / "getting-started.md").exists():
        site.import_page(repo, docs / "getting-started.md", f"{base}/getting-started.md", docs, base)
        hello = next((e for e in load_catalog(repo) if e["id"] == "hello"), None)
        shot = screenshot_for(repo, hello, lang) if hello else None
        if shot:
            site.hello[f"{base}/getting-started.md"] = shot
        nav.append({"Getting started": f"{base}/getting-started.md"})
    if (docs / "tutorials").is_dir():
        nav.append({"Tutorials": site.import_tree(repo, docs / "tutorials", f"{base}/tutorials",
                                                  ["todo-app.md", "bulk-rename.md", "process-dashboard.md"],
                                                  "Tutorials", docs, base)})
    if (docs / "guides").is_dir():
        nav.append({"How-to guides": site.import_tree(repo, docs / "guides", f"{base}/guides", None,
                                                      "How-to guides", docs, base)})
    nav.append({"Examples": examples_section(site, repo, f"{base}/examples", lang, "file", "run",
                                             f"sdk/{other}/examples", other, "file", other_repo)})
    ref: list = []
    if (docs / "API.md").exists():
        site.import_page(repo, docs / "API.md", f"{base}/reference/index.md", docs, base)
        ref.append(f"{base}/reference/index.md")
    for page in ordered(docs / "reference"):
        site.import_page(repo, page, f"{base}/reference/{page.name}", docs, base)
        ref.append({title_of(page): f"{base}/reference/{page.name}"})
    nav.append({"API reference": ref})
    if (docs / "ARCHITECTURE.md").exists():
        site.import_page(repo, docs / "ARCHITECTURE.md", f"{base}/architecture.md", docs, base)
        nav.append({"How it works": f"{base}/architecture.md"})
    # map remaining relative links (API.md etc. sit at docs/ root)
    return nav


def ui_section(site: Site, lang: str) -> list:
    repo = "nativehtmlkit_ui"
    other = "powershell" if lang == "python" else "python"
    docs = REPOS / repo / "docs"
    src = docs / lang
    base = f"ui/{lang}"
    nav: list = [f"{base}/index.md"]
    if (src / "README.md").exists():
        site.import_page(repo, src / "README.md", f"{base}/overview.md", src, base)
        nav.append({"Overview": f"{base}/overview.md"})
    if (src / "getting-started.md").exists():
        site.import_page(repo, src / "getting-started.md", f"{base}/getting-started.md", src, base)
        hello = next((e for e in load_catalog(repo) if e["id"] == "hello"), None)
        shot = screenshot_for(repo, hello, lang) if hello else None
        if shot:
            site.hello[f"{base}/getting-started.md"] = shot
        nav.append({"Getting started": f"{base}/getting-started.md"})
    if (src / "tutorials").is_dir():
        nav.append({"Tutorials": site.import_tree(repo, src / "tutorials", f"{base}/tutorials",
                                                  ["expense-tracker.md", "settings-editor.md"], "Tutorials", src, base)})
    if (src / "guides").is_dir():
        nav.append({"How-to guides": site.import_tree(repo, src / "guides", f"{base}/guides", None,
                                                      "How-to guides", src, base)})
    nav.append({"Examples": examples_section(site, repo, f"{base}/examples", lang, lang, f"run_{lang}",
                                             f"ui/{other}/examples", other, other)})
    ref: list = []
    if (src / "reference.md").exists():
        site.import_page(repo, src / "reference.md", f"{base}/reference.md", src, base)
        ref.append({"API reference": f"{base}/reference.md"})
    if (docs / "css.md").exists():
        site.import_page(repo, docs / "css.md", f"{base}/css.md", docs, base)
        ref.append({"CSS and theming": f"{base}/css.md"})
    if (docs / "LIMITATIONS.md").exists():
        site.import_page(repo, docs / "LIMITATIONS.md", f"{base}/limitations.md", docs, base)
        ref.append({"Limitations": f"{base}/limitations.md"})
    nav += ref
    return nav


CLI_GUIDES = ["exit-codes-and-scripting.md", "css-and-forms.md", "environment-and-diagnostics.md", "troubleshooting.md"]
CLI_TUTORIALS = ["tutorial.md", "tutorial-branch-picker.md"]
CLI_COMMANDS = ["select.md", "view.md", "form.md", "doctor.md"]
CLI_FORMATS = ["input-formats.md", "output-formats.md"]


def cli_title(path: Path) -> str:
    """Navigation title without the redundant '(Linux)' / '(Windows)' suffix."""
    return re.sub(r"\s*\((Linux|Windows)\)$", "", title_of(path))


def cli_section(site: Site) -> list:
    """Each system has the same shape as a UI/SDK language section:
    Getting started (index) | Tutorials | How-to guides | Examples | Command reference."""
    repo = "nativehtmlkit-cli"
    docs = REPOS / repo / "docs"
    nav: list = ["cli/index.md"]
    for os_name in ("linux", "windows"):
        src = docs / os_name
        if not src.is_dir():
            continue
        base = f"cli/{os_name}"
        system = LANG[os_name][0]
        sub: list = []
        if (src / "index.md").exists():
            site.import_page(repo, src / "index.md", f"{base}/index.md", docs, "cli")
            sub.append(f"{base}/index.md")
        # Tutorials
        tut = [src / n for n in CLI_TUTORIALS if (src / n).exists()]
        if tut:
            for page in tut:
                site.import_page(repo, page, f"{base}/{page.name}", docs, "cli")
            site.write(f"{base}/tutorials/index.md", "\n".join(
                [f"# Tutorials ({system})", "", "Build a complete shell tool step by step.", ""]
                + [f"- [{cli_title(p)}](../{p.name})" for p in tut]) + "\n")
            sub.append({"Tutorials": [f"{base}/tutorials/index.md"] + [{cli_title(p): f"{base}/{p.name}"} for p in tut]})
        # How-to guides: recipes plus the scripting / styling / diagnostics pages
        guides: list = []
        rec = src / "recipes"
        if (rec / "index.md").exists():
            site.import_page(repo, rec / "index.md", f"{base}/recipes/index.md", docs, "cli")
            guides.append(f"{base}/recipes/index.md")
        for name in CLI_GUIDES:
            if (src / name).exists():
                site.import_page(repo, src / name, f"{base}/{name}", docs, "cli")
                guides.append({cli_title(src / name): f"{base}/{name}"})
        if rec.is_dir():
            for page in ordered(rec):
                site.import_page(repo, page, f"{base}/recipes/{page.name}", docs, "cli")
                guides.append({cli_title(page): f"{base}/recipes/{page.name}"})
        if guides:
            sub.append({"How-to guides": guides})
        # Examples
        twin = "windows" if os_name == "linux" else "linux"
        sub.append({"Examples": examples_section(site, repo, f"{base}/examples", os_name, os_name, f"run_{os_name}",
                                                 f"cli/{twin}/examples", twin, twin)})
        # Command reference: every command and format with examples for this system
        ref: list = [f"{base}/commands/index.md"]
        lines = [f"# Command reference ({system})", "",
                 f"Every command and option with a runnable {('bash' if os_name == 'linux' else 'PowerShell')} example. "
                 "The exact, system-independent rules are in the [reference for both systems](../../reference/index.md).", "",
                 "## Commands", ""]
        for name in CLI_COMMANDS:
            if (src / "commands" / name).exists():
                site.import_page(repo, src / "commands" / name, f"{base}/commands/{name}", docs, "cli")
                ref.append({cli_title(src / "commands" / name): f"{base}/commands/{name}"})
                lines.append(f"- [{cli_title(src / 'commands' / name)}]({name})")
        lines += ["", "## Formats", ""]
        for name in CLI_FORMATS:
            if (src / name).exists():
                site.import_page(repo, src / name, f"{base}/{name}", docs, "cli")
                ref.append({cli_title(src / name): f"{base}/{name}"})
                lines.append(f"- [{cli_title(src / name)}](../{name})")
        site.write(f"{base}/commands/index.md", "\n".join(lines) + "\n")
        sub.append({"Command reference": ref})
        nav.append({system: sub})
    ref = site.import_tree(repo, docs / "reference", "cli/reference", None, "CLI reference", docs, "cli")
    if (docs / "REFERENCE.md").exists():
        site.import_page(repo, docs / "REFERENCE.md", "cli/reference/index.md", docs, "cli")
    nav.append({"Reference (both systems)": ref})
    if (docs / "ARCHITECTURE.md").exists():
        site.import_page(repo, docs / "ARCHITECTURE.md", "cli/architecture.md", docs, "cli")
        nav.append({"How it works": "cli/architecture.md"})
    return nav


def core_pages(site: Site) -> list:
    repo = "nativehtmlkit-core"
    root = REPOS / repo
    nav: list = []
    for src, dest, title in [
        (root / "docs/guides/html-css-support.md", "reference/core/html-css-support.md", "HTML and CSS support"),
        (root / "docs/reference/html-css-profile.md", "reference/core/html-css-profile.md", "CSS profile (generated)"),
        (root / "docs/guides/events.md", "reference/core/events.md", "Events the host delivers"),
    ]:
        if src.exists():
            site.import_page(repo, src, dest, root, "reference/core")
            nav.append({title: dest})
    proto: list = []
    for src, dest, title in [
        (root / "protocol/README.md", "reference/protocol/index.md", None),
        (root / "protocol/SDK-AUTHORING.md", "reference/protocol/sdk-authoring.md", "Writing an SDK"),
        (root / "docs/tutorials/first-wire-client.md", "reference/protocol/first-client.md", "Tutorial: a first client"),
        (root / "protocol/reference/wire-tables.md", "reference/protocol/wire-tables.md", "Methods and messages"),
        (root / "protocol/reference/document-commands.md", "reference/protocol/document-commands.md", "Document commands"),
        (root / "protocol/COMPATIBILITY.md", "reference/protocol/compatibility.md", "Compatibility"),
    ]:
        if src.exists():
            site.import_page(repo, src, dest, root, "reference")
            proto.append(dest if title is None else {title: dest})
    if proto:
        nav.append({"Wire protocol (for client authors)": proto})
    return nav


# --------------------------------------------------------------------------- generated indexes
NAMES = {"python": "Python", "powershell": "PowerShell"}


def parity_table(part: str) -> str:
    """Python <-> PowerShell table for one layer ("ui" or "sdk"), links relative to <part>/index.md."""
    if part == "sdk":
        cats = {"python": ("nativehtmlkit-python", "file"), "powershell": ("nativehtmlkit-powershell", "file")}
    else:
        cats = {"python": ("nativehtmlkit_ui", "python"), "powershell": ("nativehtmlkit_ui", "powershell")}
    py = {e["id"]: e for e in load_catalog(cats["python"][0]) if e.get(cats["python"][1])}
    ps = {e["id"]: e for e in load_catalog(cats["powershell"][0]) if e.get(cats["powershell"][1])}
    ids = list(py) + [i for i in ps if i not in py]
    out = ["## Python ↔ PowerShell", "",
           "The two languages mirror each other: the same tutorials, guides and examples, with the same "
           "window and text. Language-specific items show —.", "",
           "| Example | Python | PowerShell |", "|---|---|---|"]
    for i in ids:
        title = (py.get(i) or ps.get(i))["title"]
        a = f"[Python](python/examples/{i}.md)" if i in py else "—"
        b = f"[PowerShell](powershell/examples/{i}.md)" if i in ps else "—"
        out.append(f"| {title} | {a} | {b} |")
    return "\n".join(out) + "\n"


LAYER = {
    "ui": ("UI library", "Reactive state and ready-made components (layouts, buttons, inputs, lists, "
           "themes) on top of the SDK. Start here unless you want to write all of the HTML yourself; "
           "use the SDK directly for anything the UI library does not wrap.", "reference.md"),
    "sdk": ("SDK", "Plain HTML and CSS driven from your program: open windows, load pages, react to "
            "events, update the page, use native dialogs, the clipboard and live bitmaps. Full control, "
            "no extra layer. The UI library is built on it.", "reference/index.md"),
}


def layer_index(site: Site, part: str) -> None:
    title, blurb, api = LAYER[part]
    cards = []
    for lang in ("python", "powershell"):
        run = ("Python 3.10+ with uv" if lang == "python"
               else "PowerShell 7.2+, or Windows PowerShell 5.1 on Windows")
        cards += [f"-   **[{NAMES[lang]}]({lang}/index.md)**", "",
                  f"    {run}. Same API on Linux (KDE Plasma Wayland) and Windows.", "",
                  f"    [Getting started]({lang}/getting-started.md) · [Tutorials]({lang}/tutorials/index.md) · "
                  f"[Guides]({lang}/guides/index.md) · [Examples]({lang}/examples/index.md) · [API]({lang}/{api})", ""]
    site.write(f"{part}/index.md", "\n".join([
        f"# {title}", "", blurb, "",
        "It works the same on Linux and Windows; the few real differences are listed in "
        "[Linux and Windows](../getting-started/platforms.md).", "",
        '<div class="grid cards" markdown>', "", *cards, "</div>", "", parity_table(part)]))
    for lang in ("python", "powershell"):
        body = [f"# {NAMES[lang]} {title}", "", blurb, ""]
        for label, href in [("Getting started", "getting-started.md"), ("Tutorials", "tutorials/index.md"),
                            ("How-to guides", "guides/index.md"), ("Examples", "examples/index.md"),
                            ("API reference", api)]:
            if f"{part}/{lang}/{href}" in site.pages or (site.out / f"{part}/{lang}/{href}").exists():
                body.append(f"- **[{label}]({href})**")
        other = "powershell" if lang == "python" else "python"
        body += ["", f"Same section in {NAMES[other]}: [{NAMES[other]} {title}](../{other}/index.md). "
                 "Differences between Linux and Windows: [Linux and Windows](../../getting-started/platforms.md)."]
        site.write(f"{part}/{lang}/index.md", "\n".join(body) + "\n")


def cli_index(site: Site) -> None:
    site.write("cli/index.md", """# Command-line tool

`nativehtmlkit` gives shell scripts a native window: pick rows from a list, view text, or fill in a
form, and get the answer on stdout with a meaningful exit status. One executable, no runtime to install.

<div class="grid cards" markdown>

-   **[Linux](linux/index.md)**

    bash/zsh on KDE Plasma Wayland: install, every command and option with examples, recipes,
    scripting with exit codes, a tutorial.

-   **[Windows](windows/index.md)**

    PowerShell 7 and Windows PowerShell 5.1 (cmd.exe notes): the same commands and recipes with
    Windows examples.

</div>

The [reference](reference/index.md) is the exact, system-independent specification of every
command, format, limit and exit code.
""")


def old_site_redirects(site: Site) -> None:
    """HTML stubs at the previous addresses (python/sdk/... -> sdk/python/... etc.)."""
    pages = [p.relative_to(site.out).as_posix() for p in site.out.rglob("*.md")
             if p.relative_to(site.out).parts[0] in ("ui", "sdk")]
    for page in pages:
        part, lang, rest = page.split("/", 2) if page.count("/") >= 2 else (*page.split("/"), "index.md")
        old = f"{lang}/{part}/{rest}" if lang in NAMES else None
        if not old:
            continue
        new_url = "/" + page[:-len("index.md")] if page.endswith("index.md") else "/" + page[:-3] + "/"
        target = site.out / (old[:-len("index.md")] if old.endswith("index.md") else old[:-3] + "/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{new_url}">'
                          f'<meta http-equiv="refresh" content="0; url={new_url}"><meta name="robots" content="noindex">'
                          f'<p>Moved to <a href="{new_url}">{new_url}</a>.</p>\n', encoding="utf-8")
    for lang in NAMES:
        t = site.out / lang / "index.html"
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=/ui/{lang}/">'
                     f'<p>Moved to <a href="/ui/{lang}/">/ui/{lang}/</a>.</p>\n', encoding="utf-8")


# --------------------------------------------------------------------------- nav + main
def nav_to_toml(nav: list, indent: int = 1) -> str:
    pad = "  " * indent
    lines = []
    for item in nav:
        if isinstance(item, str):
            lines.append(f'{pad}"{item}",')
        else:
            (title, value), = item.items()
            t = title.replace('"', '\\"')
            if isinstance(value, str):
                lines.append(f'{pad}{{ "{t}" = "{value}" }},')
            else:
                lines.append(f'{pad}{{ "{t}" = [')
                lines.append(nav_to_toml(value, indent + 1))
                lines.append(f"{pad}] }},")
    return "\n".join(lines)


def build(out: Path) -> str:
    site = Site(out)
    for d in GENERATED:
        shutil.rmtree(out / d, ignore_errors=True)
    shutil.rmtree(out / "_media", ignore_errors=True)
    cli = cli_section(site)
    cli_index(site)
    py_sdk, py_ui = sdk_section(site, "python"), ui_section(site, "python")
    ps_sdk, ps_ui = sdk_section(site, "powershell"), ui_section(site, "powershell")
    layer_index(site, "ui")
    layer_index(site, "sdk")
    core = core_pages(site)
    site.finalize()
    old_site_redirects(site)
    nav = [
        {"Home": ["index.md", {"Try the demo": "getting-started/demo.md"},
                  {"Install and first steps": "getting-started/index.md"},
                  {"Choose an entry point": "getting-started/choose.md"},
                  {"Platform requirements": "getting-started/requirements.md"},
                  {"Linux and Windows": "getting-started/platforms.md"}]},
        {"UI": ["ui/index.md", {"Python": py_ui}, {"PowerShell": ps_ui}]},
        {"SDK": ["sdk/index.md", {"Python": py_sdk}, {"PowerShell": ps_sdk}]},
        {"CLI": cli},
        {"Concepts": ["concepts/index.md", {"Architecture": "concepts/architecture.md"},
                      {"Process and lifecycle": "concepts/lifecycle.md"},
                      {"Threading and callbacks": "concepts/threading.md"},
                      {"Documents and stale handles": "concepts/documents-and-handles.md"},
                      {"Security model": "concepts/security.md"}, {"Accessibility": "concepts/accessibility.md"},
                      {"Why native?": "concepts/why-native.md"}]},
        {"Reference": ["reference/index.md", {"Capability matrix": "capabilities/matrix.md"},
                       {"Limitations": "capabilities/limitations.md"}, *core,
                       {"Examples and verification": "reference/examples.md"},
                       {"Glossary": "reference/glossary.md"}, {"FAQ": "reference/faq.md"},
                       {"Screenshots": "demos/screenshots.md"}]},
    ]
    return "nav = [\n" + nav_to_toml(nav) + "\n]"


def write_nav(toml_text: str, nav: str) -> str:
    begin, end = "# BEGIN GENERATED NAV", "# END GENERATED NAV"
    if begin in toml_text:
        pre, rest = toml_text.split(begin, 1)
        post = rest.split(end, 1)[1]
        return pre + begin + "\n" + nav + "\n" + end + post
    # first run: replace an existing nav = [...] block
    m = re.search(r"^nav = \[.*?^\]\n", toml_text, flags=re.M | re.S)
    block = begin + "\n" + nav + "\n" + end + "\n"
    return toml_text[:m.start()] + block + toml_text[m.end():] if m else toml_text + "\n" + block


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    docs = LANDING / "docs"
    toml_path = LANDING / "zensical.toml"
    if not args.check:
        nav = build(docs)
        toml_path.write_text(write_nav(toml_path.read_text(encoding="utf-8"), nav), encoding="utf-8")
        print(f"Imported docs into {', '.join(GENERATED)}; nav written to zensical.toml")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "docs"
        nav = build(out)
        problems = []
        for d in GENERATED + ["_media"]:
            a, b = docs / d, out / d
            fa = {p.relative_to(a) for p in a.rglob("*") if p.is_file()} if a.exists() else set()
            fb = {p.relative_to(b) for p in b.rglob("*") if p.is_file()} if b.exists() else set()
            problems += [f"{d}/{p}: missing or extra" for p in fa ^ fb]
            problems += [f"{d}/{p}: differs" for p in fa & fb if not filecmp.cmp(a / p, b / p, shallow=False)]
        if write_nav(toml_path.read_text(encoding="utf-8"), nav) != toml_path.read_text(encoding="utf-8"):
            problems.append("zensical.toml nav differs")
        if problems:
            print("Imported docs are stale; run scripts/import-docs.py:\n  " + "\n  ".join(problems[:30]))
            return 1
        print("Imported docs are current")
        return 0


if __name__ == "__main__":
    sys.exit(main())
