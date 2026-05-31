#!/usr/bin/env python3
"""check-frontmatter.py — validate every skill/agent SKILL.md/agent frontmatter.

A skill or agent whose YAML frontmatter does not parse under a STRICT YAML parser
silently fails to load in strict hosts (e.g. GitHub Copilot), even though Claude
Code's lenient loader tolerates it. The classic offender is an unquoted scalar
containing a colon-space, e.g.

    description: Foo — explaining the bar: the baz   # ScannerError

This gate parses the frontmatter of every `plugins/*/skills/*/SKILL.md`,
`plugins/*/agents/*.md`, and `plugins/*/commands/*.md` with `yaml.safe_load` and
requires a mapping with a non-empty string `description`. It prints each offender
and exits non-zero if any fail, so a malformed front-matter can never ship again.
(Commands were added 2026-05-31 when the marketplace began shipping 5+ per
plugin — their `description` is what the dashboard's Commands tab surfaces.)

Agents carry an additional contract: the scenario-authoring schema (AGENTS.md
step 7, docs/best-practices/agent-scenario-authoring.md). Every `agents/*.md`
must declare `audience`, `works_with`, a non-empty `scenarios` list whose items
each have `intent` / `trigger_phrase` / `outcome` / `difficulty`, and a non-empty
`quickstart`. The repo-guide generator surfaces these in per-agent cards and the
Overview use-case lookup table, so a missing block ships a blank card silently.

Usage:
    check-frontmatter.py [--root <dir>]
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

_FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

_SCENARIO_ITEM_KEYS = ("intent", "trigger_phrase", "outcome", "difficulty")


def _agent_scenario_violations(data: dict) -> list[str]:
    """Return the scenario-authoring-schema problems for one agent's frontmatter."""
    problems: list[str] = []

    for key in ("audience", "works_with"):
        if key not in data or data[key] in (None, "", [], {}):
            problems.append(f"missing or empty '{key}' (scenario-authoring schema)")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        problems.append("missing or empty 'scenarios' list (scenario-authoring schema)")
    else:
        for i, item in enumerate(scenarios):
            if not isinstance(item, dict):
                problems.append(f"scenarios[{i}] is not a mapping")
                continue
            for k in _SCENARIO_ITEM_KEYS:
                v = item.get(k)
                if not isinstance(v, str) or not v.strip():
                    problems.append(f"scenarios[{i}] missing or non-string '{k}'")

    quickstart = data.get("quickstart")
    if quickstart in (None, "", [], {}):
        problems.append("missing or empty 'quickstart' (scenario-authoring schema)")

    return problems


def _violations(root: Path) -> list[tuple[str, str]]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return [("<environment>", "pyyaml not available to validate frontmatter")]

    patterns = [
        "plugins/*/skills/*/SKILL.md",
        "plugins/*/agents/*.md",
        "plugins/*/commands/*.md",
    ]
    files = sorted({f for p in patterns for f in glob.glob(str(root / p))})
    bad: list[tuple[str, str]] = []
    for f in files:
        rel = str(Path(f).relative_to(root))
        text = Path(f).read_text(encoding="utf-8")
        m = _FM.match(text)
        if not m:
            bad.append((rel, "no YAML frontmatter (missing leading '---' block)"))
            continue
        try:
            data = yaml.safe_load(m.group(1))
        except Exception as exc:  # strict-YAML parse error — the load-failure bug
            bad.append((rel, f"{type(exc).__name__}: {str(exc).splitlines()[0]}"))
            continue
        if not isinstance(data, dict):
            bad.append((rel, "frontmatter is not a mapping"))
            continue
        if not isinstance(data.get("description"), str) or not data["description"].strip():
            bad.append((rel, "missing or non-string 'description'"))
        # Agents additionally carry the scenario-authoring schema.
        if Path(f).parent.name == "agents":
            for why in _agent_scenario_violations(data):
                bad.append((rel, why))
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repo root")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    bad = _violations(root)
    if bad:
        print("Frontmatter validation FAILED — these will not load in a strict YAML host:")
        for rel, why in bad:
            print(f"  ✗ {rel}\n      {why}")
        print("\nFix: quote the offending scalar (e.g. wrap description in double quotes).")
        return 1
    print(
        "Frontmatter OK — every skill/agent parses as strict YAML with a description, "
        "and every agent carries the scenario-authoring schema."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
