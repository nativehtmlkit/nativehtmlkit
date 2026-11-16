# NativeHTMLKit agent skills

The five skills describe the **released, public** entrypoints and the differences between direct SDK and reactive UI. Each has a `SKILL.md` and an example reference.

| Skill | Canonical source | Use when |
|---|---|---|
| `nativehtmlkit-python` | [Python SDK](https://github.com/nativehtmlkit/nativehtmlkit-python/tree/main/skills/nativehtmlkit-python) | Direct Python windows/documents |
| `nativehtmlkit-powershell` | [PowerShell SDK](https://github.com/nativehtmlkit/nativehtmlkit-powershell/tree/main/NativeHTMLKit/skills/nativehtmlkit-powershell) | Native PowerShell scripts |
| `nativehtmlkit-cli` | [CLI](https://github.com/nativehtmlkit/nativehtmlkit-cli/tree/main/skills/nativehtmlkit-cli) | Shell selection, views, forms |
| `nativehtmlkit-ui-python` | [UI repository](https://github.com/nativehtmlkit/nativehtmlkit_ui/tree/main/skills/nativehtmlkit-ui-python) | Reactive Python UI components |
| `nativehtmlkit-ui-powershell` | [UI repository](https://github.com/nativehtmlkit/nativehtmlkit_ui/tree/main/skills/nativehtmlkit-ui-powershell) | Reactive PowerShell UI components |

From the landing repository:

```bash
python3 scripts/install-skills.py --list
python3 scripts/install-skills.py --agent claude --scope user        # preview
python3 scripts/install-skills.py --agent claude --scope user --apply
python3 scripts/install-skills.py --agent codex --scope project --project ~/myapp --apply
```

Supported presets: `claude`, `codex`, `opencode`, `cursor`, `copilot`, `gemini`. Installer can accept `--dest` to override directories. Agents still need the actual installed SDK or CLI; installing a skill does not install native binaries. Check current agent-tool behavior before relying on auto-discovery.
