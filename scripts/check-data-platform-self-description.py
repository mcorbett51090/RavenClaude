#!/usr/bin/env python3
"""check-data-platform-self-description.py — data-platform's own inventory vs its own docs.

The `data-platform` plugin's CLAUDE.md §5 Capability Grounding Protocol exists to stop an
*agent* from miscounting its own capabilities. A 2026-09-03 FORGE gap-analysis pass (run
`dashboard-top1pct`, P0-2) found the exact same failure mode in the plugin's own
*scaffolding*: CLAUDE.md said "14 skills" when 15 existed on disk, best-practices/README.md
said "31 rules" when 33 existed, CHANGELOG.md's top entry was two minor versions behind
plugin.json, and templates/CLAUDE.md's stated count had drifted too. Each was fixed once by
hand; this script exists so the *next* drift is caught mechanically instead of needing a
human (or another FORGE pass) to notice it a second time.

Scope: this script is DELIBERATELY data-platform-only, not a marketplace-wide gate — every
other plugin has its own doc-drift risk shape (different section names, different template
taxonomies) and a generic version would either need per-plugin config (defeating the point
of a tripwire) or false-positive across plugins with legitimately different structures. If
this pattern proves valuable, generalizing it is a separate, deliberate follow-up — not
something to fold in here silently.

Checks:
  1. skills count       — `find skills -name SKILL.md` vs CLAUDE.md's "the N skills in this
                           plugin" sentence (§5, Capability Grounding Protocol).
  2. best-practices count — `ls best-practices/*.md` (excluding README.md) vs
                           best-practices/README.md's "_N rules._" line.
  3. templates count    — `ls templates` (top-level entries) vs CLAUDE.md's "N templates on
                           disk" sentence (§9).
  4. CHANGELOG freshness — CHANGELOG.md's top `## [X.Y.Z]` entry vs
                           .claude-plugin/plugin.json's `version` field.
  5. Cube-version consistency (red-team RT-8) — every `>=X.Y.Z` Cube-version-floor string
                           across the five files P0-1 edited must be byte-identical, so the
                           *next* Cube version boundary doesn't silently repeat P0-1's own
                           defect (a floor stated in one place and left stale everywhere
                           else) on a slower clock.
  6. Stack-case coverage matrix (P1-11) — every data row of CLAUDE.md §9a's Case A/B/C/D/E
                           table must have every cell non-empty (✅/⚠/N/A-with-reason all
                           count; a bare empty cell does not). Catches the exact failure mode
                           the matrix exists to prevent: an asymmetry going unnoticed because
                           a cell was silently left blank rather than marked explicitly.

Usage:
    check-data-platform-self-description.py [--root <path-to-data-platform-plugin-dir>]

Exit 0 if every check passes; prints each drifted check and exits 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SKILLS_SENTENCE = re.compile(r"the (\d+) skills in this plugin")
_TEMPLATES_SENTENCE = re.compile(r"(\d+) templates on disk")
_RULES_LINE = re.compile(r"_(\d+) rules\.")
_CHANGELOG_TOP_VERSION = re.compile(r"^## \[(\d+\.\d+\.\d+)\]")
_CUBE_VERSION_FLOOR = re.compile(r">=(\d+\.\d+\.\d+)")

_CUBE_VERSION_FILES = (
    "templates/cube-schema-starter.yml",
    "templates/cube-nextjs-dashboard-starter/README.md",
    "templates/cube-astro-dashboard-starter/README.md",
    "skills/cube-schema-scaffolding/SKILL.md",
    "agents/dashboard-builder.md",
)


def _fail(problems: list[str], msg: str) -> None:
    problems.append(msg)


def _extract_one(text: str, pattern: re.Pattern[str], label: str, problems: list[str]) -> str | None:
    m = pattern.search(text)
    if not m:
        _fail(problems, f"{label}: pattern not found — has the sentence been reworded?")
        return None
    return m.group(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default="plugins/data-platform",
        help="path to the data-platform plugin directory (or a fixture root shaped the same way)",
    )
    args = ap.parse_args()
    root = Path(args.root)
    problems: list[str] = []

    if not root.is_dir():
        print(f"check-data-platform-self-description: root not found: {root}", file=sys.stderr)
        return 2

    claude_md = root / "CLAUDE.md"
    claude_text = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""

    # 1. Skills count
    actual_skills = len(list((root / "skills").glob("*/SKILL.md"))) if (root / "skills").is_dir() else 0
    stated_skills = _extract_one(claude_text, _SKILLS_SENTENCE, "CLAUDE.md skills sentence", problems)
    if stated_skills is not None and int(stated_skills) != actual_skills:
        _fail(
            problems,
            f"skills count drift: CLAUDE.md says {stated_skills}, "
            f"filesystem has {actual_skills} (skills/*/SKILL.md)",
        )

    # 2. best-practices count
    bp_dir = root / "best-practices"
    actual_rules = (
        len([p for p in bp_dir.glob("*.md") if p.name.lower() != "readme.md"]) if bp_dir.is_dir() else 0
    )
    bp_readme = bp_dir / "README.md"
    bp_text = bp_readme.read_text(encoding="utf-8") if bp_readme.exists() else ""
    stated_rules = _extract_one(bp_text, _RULES_LINE, "best-practices/README.md rules count", problems)
    if stated_rules is not None and int(stated_rules) != actual_rules:
        _fail(
            problems,
            f"best-practices count drift: README.md says {stated_rules}, "
            f"filesystem has {actual_rules} (best-practices/*.md excluding README.md)",
        )

    # 3. Templates count
    templates_dir = root / "templates"
    actual_templates = len(list(templates_dir.iterdir())) if templates_dir.is_dir() else 0
    stated_templates = _extract_one(claude_text, _TEMPLATES_SENTENCE, "CLAUDE.md templates sentence", problems)
    if stated_templates is not None and int(stated_templates) != actual_templates:
        _fail(
            problems,
            f"templates count drift: CLAUDE.md says {stated_templates}, "
            f"filesystem has {actual_templates} top-level entries under templates/",
        )

    # 4. CHANGELOG freshness vs plugin.json version
    plugin_json = root / ".claude-plugin" / "plugin.json"
    changelog = root / "CHANGELOG.md"
    if plugin_json.exists() and changelog.exists():
        try:
            declared_version = json.loads(plugin_json.read_text(encoding="utf-8"))["version"]
        except (json.JSONDecodeError, KeyError) as exc:
            _fail(problems, f"plugin.json unreadable/missing version: {exc}")
            declared_version = None
        changelog_text = changelog.read_text(encoding="utf-8")
        top_version = None
        for line in changelog_text.splitlines():
            m = _CHANGELOG_TOP_VERSION.match(line)
            if m:
                top_version = m.group(1)
                break
        if top_version is None:
            _fail(problems, "CHANGELOG.md: no '## [X.Y.Z]' entry found")
        elif declared_version is not None and top_version != declared_version:
            _fail(
                problems,
                f"CHANGELOG drift: top entry is [{top_version}], "
                f"plugin.json version is {declared_version}",
            )
    elif changelog.exists() != plugin_json.exists():
        # A fixture that only ships one of the two is a malformed fixture, not a pass.
        _fail(problems, "CHANGELOG.md and .claude-plugin/plugin.json must both exist to check freshness")

    # 5. Cube-version-floor consistency across the five P0-1 files (red-team RT-8)
    found_versions: dict[str, str] = {}
    for rel in _CUBE_VERSION_FILES:
        p = root / rel
        if not p.exists():
            continue  # a fixture testing only some checks need not carry every file
        text = p.read_text(encoding="utf-8")
        m = _CUBE_VERSION_FLOOR.search(text)
        if m:
            found_versions[rel] = m.group(1)
    if found_versions:
        distinct = set(found_versions.values())
        if len(distinct) > 1:
            detail = ", ".join(f"{rel}={v}" for rel, v in sorted(found_versions.items()))
            _fail(problems, f"Cube-version-floor drift: not all files agree ({detail})")

    # 6. Stack-case coverage matrix (P1-11): every data-row cell must be non-empty.
    if claude_md.exists():
        section_match = re.search(
            r"^## 9a\. Stack-case coverage matrix.*?(?=^## \d|\Z)", claude_text, re.DOTALL | re.MULTILINE
        )
        if section_match is None:
            _fail(problems, "CLAUDE.md: '## 9a. Stack-case coverage matrix' section not found")
        else:
            section = section_match.group(0)
            table_rows = [line for line in section.splitlines() if line.strip().startswith("|")]
            # Skip the header row and the `|---|---|...` separator row.
            data_rows = [
                row for row in table_rows[2:] if row.strip() and not re.fullmatch(r"\|[\s:|-]+\|", row.strip())
            ]
            if not data_rows:
                _fail(problems, "CLAUDE.md §9a: no data rows found in the coverage matrix table")
            for row in data_rows:
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                for idx, cell in enumerate(cells):
                    if not cell:
                        _fail(
                            problems,
                            f"CLAUDE.md §9a: empty cell in column {idx + 1} of row: {row.strip()[:80]}",
                        )

    if problems:
        print("check-data-platform-self-description: FAILED", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("check-data-platform-self-description: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
