#!/usr/bin/env python3
"""check-data-platform-skill-reachability.py — every skill must be reachable from an agent.

FORGE dashboard-top1pct P1-6 (2026-09-03): a dispatched subagent loads its own
`agents/*.md`, not the plugin's `CLAUDE.md` skill table — so a skill listed in
CLAUDE.md §8 but never mentioned by any `agents/*.md` is shipped, indexed, and
structurally invisible at runtime. Confirmed this session with a positive control
(`cube-schema-scaffolding` returns a hit in `agents/dashboard-builder.md`, proving
the probe itself works) before trusting the negative result for the five skills
that had zero hits.

Scope: deliberately `plugins/data-platform/`-scoped, not marketplace-wide — every
other plugin has its own agent/skill topology and this reachability shape (an
`agents/*.md` reference OR an `invoked_by:` frontmatter escape for the legitimate
cross-plugin-consumed case) is not a universal contract worth imposing elsewhere
without the same grounding pass.

A skill is "reachable" if EITHER:
  1. Its own directory name (e.g. "dbt-project-scaffolding") is mentioned as
     plain text in at least one `agents/*.md` file in this plugin — the simple,
     robust proxy for "an agent's own file tells a dispatched subagent to read
     this skill", OR
  2. Its `SKILL.md` frontmatter carries a non-empty `invoked_by:` field, naming
     the external (cross-plugin) agent that is its primary consumer — the
     legitimate case where a skill's real audience is another plugin's agent,
     not this plugin's own.

Deliberate deviation from plan.md's original wording ("make CLAUDE.md §8's table
the single source the script reads"): this gate reads `agents/*.md` and each
skill's own frontmatter DIRECTLY rather than parsing CLAUDE.md §8's prose table.
The P0-2 phase of this same FORGE run found that plugin's own doc tables drift
from reality routinely (stale skill/template/rule counts) — trusting a prose
table as the reachability source of truth would make this gate only as reliable
as the table it reads, reintroducing exactly the class of defect P0-2 fixed.
Reading the actual `agents/*.md` files (what a dispatched subagent truly loads)
and each skill's own frontmatter is the doc-independent, harder-to-drift check.

Usage:
    check-data-platform-skill-reachability.py [--root <path-to-data-platform-plugin-dir>]

Exit 0 if every skill is reachable; prints each unreachable skill and exits 1
otherwise. Includes a positive-control assertion: `cube-schema-scaffolding` (a
skill this plugin's own history confirms IS referenced) must register as
reachable, or the probe itself is broken and the whole result is untrustworthy.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_FM = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
_INVOKED_BY = re.compile(r"^invoked_by:\s*(.+)$", re.MULTILINE)

# The plugin's own history (this session) — a skill this reachability probe
# must NEVER report as unreachable, or the probe itself is broken and every
# other verdict in this run is untrustworthy.
_POSITIVE_CONTROL_SKILL = "cube-schema-scaffolding"


def _skill_dirs(root: Path) -> list[Path]:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(p.parent for p in skills_dir.glob("*/SKILL.md"))


def _agents_text(root: Path) -> str:
    agents_dir = root / "agents"
    if not agents_dir.is_dir():
        return ""
    parts = []
    for p in sorted(agents_dir.glob("*.md")):
        parts.append(p.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _invoked_by(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    m = _FM.match(text)
    if not m:
        return None
    fm = m.group(1)
    im = _INVOKED_BY.search(fm)
    if not im:
        return None
    value = im.group(1).strip()
    return value or None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default="plugins/data-platform",
        help="path to the data-platform plugin directory (or a fixture root shaped the same way)",
    )
    args = ap.parse_args()
    root = Path(args.root)

    if not root.is_dir():
        print(f"check-data-platform-skill-reachability: root not found: {root}", file=sys.stderr)
        return 2

    agents_text = _agents_text(root)
    skill_dirs = _skill_dirs(root)

    unreachable: list[str] = []
    control_ok = False

    for skill_dir in skill_dirs:
        name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        reachable = name in agents_text or bool(_invoked_by(skill_md))
        if name == _POSITIVE_CONTROL_SKILL:
            control_ok = reachable
        if not reachable:
            unreachable.append(name)

    problems: list[str] = []
    if not skill_dirs:
        problems.append("no skills found under skills/*/SKILL.md — is --root correct?")
    elif not control_ok:
        problems.append(
            f"POSITIVE CONTROL FAILED: '{_POSITIVE_CONTROL_SKILL}' registered as unreachable — "
            "the probe itself is broken; every other verdict in this run is untrustworthy."
        )
    if unreachable:
        problems.append(
            "unreachable skill(s) — no agents/*.md reference and no invoked_by: frontmatter: "
            + ", ".join(sorted(unreachable))
        )

    if problems:
        print("check-data-platform-skill-reachability: FAILED", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"check-data-platform-skill-reachability: OK ({len(skill_dirs)} skills, all reachable)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
