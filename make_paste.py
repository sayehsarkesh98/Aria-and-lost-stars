#!/usr/bin/env python3
"""Generate paste/PASTE_<part>.md = server-free context header + the full part prompt (prompts/PART*.md).
Run from the pack root:  python3 tools/make_paste.py   (idempotent; regenerates every file)."""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = """# PASTE THIS FIRST — server-free context (read before the task prompt below)

The shared MCP server is NOT available (its domain is not reachable from the code sandbox). **The attached zip is the only source of truth.**
- Unzip it to /home/claude/pack (user upload is read-only; do NOT edit in /mnt/user-data/uploads). Then read, in this order: `00_START_HERE.md`, `STATE.md`, `HANDOFF.md`.
- File layout: game files are in `game/` (so "aria_v32_p2.html" below means `game/aria_v32_p2.html`), prompts in `prompts/`, reference sheets in `reference_images/`, scripts/tests in `tools/`, Aria skills copy in `skills_copy/` (use /mnt/skills/plugins/aria-* if present).
- IGNORE any instruction to call `resume_project` / `save_checkpoint` / `write_handoff` / `files_*` / `cfile` or to upload to the server. If such tools exist and fail, do not retry. Keep state ONLY in the zip: update `HANDOFF.md` (status board + your `## Part N` section) and `STATE.md`.
- When finished: put the new game file in `game/`, then run `bash tools/make_pack.sh P<N>done` from the pack root. It writes MANIFEST.sha256 and the new zip to /mnt/user-data/outputs; then call present_files on that zip (plus the new game html). The user carries the zip to the next account.
- If you run low on budget: reach a loadable state, save `game/aria_v32_pN_WIP.html`, write the remaining checklist into HANDOFF.md, and ship a `P<N>WIP` zip the same way.
- Final report to the user in Persian; never claim tests you did not run.

---

"""
os.makedirs(os.path.join(ROOT, 'paste'), exist_ok=True)
n = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'prompts', 'PART*.md')), key=lambda x: int(re.search(r'PART(\d+)_', x).group(1))):
    out = os.path.join(ROOT, 'paste', 'PASTE_' + os.path.basename(f))
    open(out, 'w', encoding='utf-8').write(HEADER + open(f, encoding='utf-8').read())
    n += 1
print('wrote', n, 'paste files')
