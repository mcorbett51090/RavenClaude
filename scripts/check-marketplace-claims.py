#!/usr/bin/env python3
"""Guard against marketplace self-description drift.

Two checks, both surfaced by the 2026-05-23 whole-repo self-review:

  1. Required-file presence — every plugins/<p>/ must have README.md, CLAUDE.md,
     and .claude-plugin/plugin.json (AGENTS.md hard rule). Two flagship plugins
     had drifted out of compliance with no gate catching it.

  2. Skill-count accuracy — the "<N> skills" claim in each plugin's plugin.json
     description AND in its .claude-plugin/marketplace.json entry must equal the
     actual number of entries under plugins/<p>/skills/. Five plugins had stale
     counts (e.g. data-platform claimed 7, had 11) because nothing verified the prose.

Exit 0 if everything matches; exit 1 with a report otherwise. Runs in CI
(validate-marketplace.yml) and is exercised bidirectionally by audit-gates.sh.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
REQUIRED = ["README.md", "CLAUDE.md", ".claude-plugin/plugin.json"]
SKILLS_RE = re.compile(r"(\d+)\s+skills", re.IGNORECASE)

failures = []


def actual_skill_count(plugin_dir: Path) -> int:
    skills = plugin_dir / "skills"
    if not skills.is_dir():
        return 0
    # Count one per skill: flat "<name>.md" files OR "<name>/" dirs (SKILL.md layout).
    return sum(1 for e in skills.iterdir() if not e.name.startswith("."))


def first_skill_claim(text: str):
    m = SKILLS_RE.search(text or "")
    return int(m.group(1)) if m else None


def main() -> int:
    marketplace = json.loads(MARKETPLACE.read_text())
    mp_entries = {p["name"]: p for p in marketplace.get("plugins", [])}

    for plugin_dir in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        name = plugin_dir.name

        # Check 1 — required files
        for rel in REQUIRED:
            if not (plugin_dir / rel).is_file():
                failures.append(f"{name}: missing required file '{rel}'")

        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            continue  # already reported as missing

        # Check 2 — skill-count accuracy
        actual = actual_skill_count(plugin_dir)
        manifest = json.loads(manifest_path.read_text())

        pj_claim = first_skill_claim(manifest.get("description", ""))
        if pj_claim is not None and pj_claim != actual:
            failures.append(
                f"{name}: plugin.json says '{pj_claim} skills' but plugins/{name}/skills/ has {actual}"
            )

        mp = mp_entries.get(name)
        if mp:
            mp_claim = first_skill_claim(mp.get("description", ""))
            if mp_claim is not None and mp_claim != actual:
                failures.append(
                    f"{name}: marketplace.json says '{mp_claim} skills' but plugins/{name}/skills/ has {actual}"
                )

    if failures:
        print("Marketplace-claims check FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Marketplace-claims check passed: required files present, skill counts accurate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
