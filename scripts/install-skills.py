#!/usr/bin/env python3
"""Copy NativeHTMLKit skills to a chosen agent's skill directory; dry-run by default."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILLS=ROOT/'skills'
PRESETS={
  'claude':('.claude/skills','.claude/skills'),
  'codex':('.agents/skills','.agents/skills'),
  'opencode':('.config/opencode/skills','.opencode/skills'),
  'cursor':('.cursor/skills','.cursor/skills'),
  'copilot':('.copilot/skills','.github/skills'),
  'gemini':('.gemini/skills','.gemini/skills'),
}

def main():
  p=argparse.ArgumentParser(description=__doc__)
  p.add_argument('--list',action='store_true')
  p.add_argument('--agent',choices=sorted(PRESETS))
  p.add_argument('--scope',choices=('user','project'),default='user')
  p.add_argument('--project',type=Path)
  p.add_argument('--dest',type=Path,help='Override destination skill root path')
  p.add_argument('--apply',action='store_true')
  p.add_argument('--overwrite',action='store_true',help='Replace an existing skill after explicit confirmation')
  args=p.parse_args()
  skills=sorted(d for d in SKILLS.iterdir() if d.is_dir() and (d/'SKILL.md').is_file())
  if args.list:
    for s in skills: print(s.name)
    return
  if not args.agent and not args.dest: p.error('Provide --agent or --dest (or --list)')
  if args.scope=='project' and not args.project and not args.dest:p.error('--project DIRECTORY is required for --scope project')
  if args.dest:root=args.dest.expanduser().resolve()
  elif args.scope=='user':root=Path.home()/PRESETS[args.agent][0]
  else:root=args.project.expanduser().resolve()/PRESETS[args.agent][1]
  for src in skills:
    dst=root/src.name
    verb='REPLACE' if dst.exists() else 'COPY'
    print(f'{verb}: {src} -> {dst}')
    if dst.exists() and not args.overwrite:
      print('  SKIP: destination exists (pass --overwrite to replace)')
      continue
    if not args.apply:continue
    if dst.is_symlink():p.error(f'refusing to replace symlink {dst}')
    if dst.exists():shutil.rmtree(dst)
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(src,dst)
  if not args.apply:print('Preview only; add --apply to copy. Skills do not install runtime packages.')

if __name__=='__main__':main()
