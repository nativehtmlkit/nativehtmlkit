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
GENERATED = ["cli", "python", "powershell", "reference/protocol", "reference/core"]
LANG = {"python": ("Python", "python", ".py"), "powershell": ("PowerShell", "powershell", ".ps1"),
        "linux": ("Linux", "bash", ".sh"), "windows": ("Windows", "powershell", ".ps1")}


# --------------------------------------------------------------------------- helpers
def title_of(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
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


class Site:
    def __init__(self, out: Path):
        self.out = out
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
        banner = f"<!-- GENERATED by scripts/import-docs.py from {repo}/{rel_src}; edit it there. -->\n"
        note = (f"\n\n---\n\n<small>Source: [{repo}/{rel_src}]({GH}/{repo}/blob/main/{rel_src}) · "
                f"edit the page there.</small>\n")
        dest_path.write_text(banner + text.rstrip() + note, encoding="utf-8")

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
        lines += ["", f'!!! info "{label} only"', f"    This example has no counterpart in the other language."]
    if twin and twin_label:
        lines += ["", f"*Same example in {twin_label}: [{ex['title']}]({twin})*"]
    lines += [""]
    shot = screenshot_for(repo, ex, lang)
    if shot:
        asset = Path(dest).parent / "img" / shot.name
        (site.out / asset).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shot, site.out / asset)
        lines += [f"![{ex['title']}](img/{shot.name})", "",
                  "*Real capture on KDE Plasma 6.6 Wayland with the released packages.*", ""]
    if ex.get("teaches"):
        lines += ["**What it teaches:** " + "; ".join(ex["teaches"]) + ".", ""]
    run = ex.get(run_key) or ex.get("run")
    if run:
        lines += ["## Run it", "", f"```{fence if lang in ('linux', 'windows') else ('bash' if lang == 'python' else 'powershell')}", run, "```", ""]
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
    base = f"{lang}/sdk"
    nav: list = [f"{base}/index.md"]
    docs = root / "docs"
    if (docs / "getting-started.md").exists():
        site.import_page(repo, docs / "getting-started.md", f"{base}/getting-started.md", docs, base)
        nav.append({"Getting started": f"{base}/getting-started.md"})
    if (docs / "tutorials").is_dir():
        nav.append({"Tutorials": site.import_tree(repo, docs / "tutorials", f"{base}/tutorials",
                                                  ["todo-app.md", "bulk-rename.md", "process-dashboard.md"],
                                                  "Tutorials", docs, base)})
    if (docs / "guides").is_dir():
        nav.append({"How-to guides": site.import_tree(repo, docs / "guides", f"{base}/guides", None,
                                                      "How-to guides", docs, base)})
    nav.append({"Examples": examples_section(site, repo, f"{base}/examples", lang, "file", "run",
                                             f"{other}/sdk/examples", other, "file", other_repo)})
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
    base = f"{lang}/ui"
    nav: list = [f"{base}/index.md"]
    if (src / "README.md").exists():
        site.import_page(repo, src / "README.md", f"{base}/overview.md", src, base)
        nav.append({"Overview": f"{base}/overview.md"})
    if (src / "getting-started.md").exists():
        site.import_page(repo, src / "getting-started.md", f"{base}/getting-started.md", src, base)
        nav.append({"Getting started": f"{base}/getting-started.md"})
    if (src / "tutorials").is_dir():
        nav.append({"Tutorials": site.import_tree(repo, src / "tutorials", f"{base}/tutorials",
                                                  ["expense-tracker.md", "settings-editor.md"], "Tutorials", src, base)})
    if (src / "guides").is_dir():
        nav.append({"How-to guides": site.import_tree(repo, src / "guides", f"{base}/guides", None,
                                                      "How-to guides", src, base)})
    nav.append({"Examples": examples_section(site, repo, f"{base}/examples", lang, lang, f"run_{lang}",
                                             f"{other}/ui/examples", other, other)})
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


CLI_ORDER = ["commands", "input-formats.md", "output-formats.md", "exit-codes-and-scripting.md",
             "environment-and-diagnostics.md", "css-and-forms.md", "recipes", "tutorial.md", "troubleshooting.md"]


def cli_section(site: Site) -> list:
    repo = "nativehtmlkit-cli"
    docs = REPOS / repo / "docs"
    nav: list = ["cli/index.md"]
    for os_name in ("linux", "windows"):
        src = docs / os_name
        if not src.is_dir():
            continue
        base = f"cli/{os_name}"
        sub: list = []
        if (src / "index.md").exists():
            site.import_page(repo, src / "index.md", f"{base}/index.md", docs, "cli")
            sub.append(f"{base}/index.md")
        for item in CLI_ORDER + sorted(p.name for p in src.iterdir() if p.name not in CLI_ORDER and p.name != "index.md"):
            path = src / item
            if path.is_dir():
                pages = site.import_tree(repo, path, f"{base}/{item}", ["select.md", "view.md", "form.md", "doctor.md"],
                                         item.capitalize(), docs, "cli")
                sub.append({item.capitalize(): pages})
            elif path.suffix == ".md" and path.exists():
                site.import_page(repo, path, f"{base}/{item}", docs, "cli")
                sub.append({title_of(path): f"{base}/{item}"})
        twin = "windows" if os_name == "linux" else "linux"
        sub.append({"Examples": examples_section(site, repo, f"{base}/examples", os_name, os_name, f"run_{os_name}",
                                                 f"cli/{twin}/examples", twin, twin)})
        nav.append({LANG[os_name][0]: sub})
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
def parity_table(lang: str) -> str:
    other = "powershell" if lang == "python" else "python"
    names = {"python": "Python", "powershell": "PowerShell"}
    out = [f"## {names[lang]} ↔ {names[other]}", "",
           f"Everything in this section has a {names[other]} twin wherever the languages allow. "
           f"Language-specific items are marked.", ""]
    for kind, base, keyl, keyo, repo_l, repo_o in [
        ("SDK examples", "sdk/examples", "file", "file",
         f"nativehtmlkit-{'python' if lang == 'python' else 'powershell'}",
         f"nativehtmlkit-{'python' if other == 'python' else 'powershell'}"),
        ("UI examples", "ui/examples", lang, other, "nativehtmlkit_ui", "nativehtmlkit_ui")]:
        mine = {e["id"]: e for e in load_catalog(repo_l) if e.get(keyl)}
        theirs = {e["id"]: e for e in load_catalog(repo_o) if e.get(keyo)}
        ids = list(mine) + [i for i in theirs if i not in mine]
        if not ids:
            continue
        out += [f"### {kind}", "", f"| | {names[lang]} | {names[other]} |", "|---|---|---|"]
        for i in ids:
            a = f"[{mine[i]['title']}]({base}/{i}.md)" if i in mine else "—"
            b = f"[{theirs[i]['title']}](../{other}/{base}/{i}.md)" if i in theirs else "—"
            out.append(f"| `{i}` | {a} | {b} |")
        out.append("")
    return "\n".join(out)


def language_index(site: Site, lang: str) -> None:
    name = "Python" if lang == "python" else "PowerShell"
    run = ("Python 3.10+ on Linux (glibc 2.39+) and Windows x64" if lang == "python"
           else "PowerShell 7.2+ on Linux and Windows, Windows PowerShell 5.1 on Windows")
    site.write(f"{lang}/index.md", f"""# {name}

Build native desktop windows from HTML and CSS with {name}. {run}.

<div class="grid cards" markdown>

-   **[{name} SDK](sdk/index.md)**

    Plain HTML and CSS plus {name}: open windows, load pages, react to events, update the page,
    use native dialogs, the clipboard and live bitmaps. Full control, no extra layer.

    [Getting started](sdk/getting-started.md) · [Tutorials](sdk/tutorials/index.md) · [Guides](sdk/guides/index.md) · [Examples](sdk/examples/index.md) · [API](sdk/reference/index.md)

-   **[{name} UI library](ui/index.md)**

    Reactive state and ready-made components (layouts, buttons, inputs, lists, themes) on top of the
    SDK. Less HTML to write; use the SDK directly for anything it does not wrap.

    [Getting started](ui/getting-started.md) · [Tutorials](ui/tutorials/index.md) · [Guides](ui/guides/index.md) · [Examples](ui/examples/index.md) · [API](ui/reference.md)

</div>

{parity_table(lang)}
""")
    for part, title, blurb in [
        ("sdk", f"{name} SDK", f"The {name} SDK drives a native window with your own HTML and CSS."),
        ("ui", f"{name} UI library", f"The {name} UI library adds reactive state and components on top of the SDK.")]:
        links = [("Getting started", f"getting-started.md"), ("Tutorials", "tutorials/index.md"),
                 ("How-to guides", "guides/index.md"), ("Examples", "examples/index.md"),
                 ("API reference", "reference/index.md" if part == "sdk" else "reference.md")]
        body = [f"# {title}", "", blurb, ""]
        for label, href in links:
            if (site.out / f"{lang}/{part}/{href}").exists():
                body.append(f"- **[{label}]({href})**")
        site.write(f"{lang}/{part}/index.md", "\n".join(body) + "\n")


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
    language_index(site, "python")
    language_index(site, "powershell")
    core = core_pages(site)
    site.finalize()
    nav = [
        {"Home": "index.md"},
        {"Get started": ["getting-started/index.md", {"Choose an entry point": "getting-started/choose.md"},
                         {"Platform requirements": "getting-started/requirements.md"}]},
        {"CLI": cli},
        {"Python": ["python/index.md", {"SDK": py_sdk}, {"UI library": py_ui}]},
        {"PowerShell": ["powershell/index.md", {"SDK": ps_sdk}, {"UI library": ps_ui}]},
        {"Concepts": ["concepts/index.md", {"Architecture": "concepts/architecture.md"},
                      {"Process and lifecycle": "concepts/lifecycle.md"},
                      {"Threading and callbacks": "concepts/threading.md"},
                      {"Documents and stale handles": "concepts/documents-and-handles.md"},
                      {"Security model": "concepts/security.md"}, {"Accessibility": "concepts/accessibility.md"},
                      {"Why native?": "concepts/why-native.md"}]},
        {"Reference": ["reference/index.md", {"Capability matrix": "capabilities/matrix.md"},
                       {"Limitations": "capabilities/limitations.md"}, *core,
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
