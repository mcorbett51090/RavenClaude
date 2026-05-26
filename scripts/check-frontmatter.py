#!/usr/bin/env python3
"""check-frontmatter.py — validate every skill/agent SKILL.md/agent frontmatter.

A skill or agent whose YAML frontmatter does not parse under a STRICT YAML parser
silently fails to load in strict hosts (e.g. GitHub Copilot), even though Claude
Code's lenient loader tolerates it. The classic offender is an unquoted scalar
containing a colon-space, e.g.

    description: Foo — explaining the bar: the baz   # ScannerError

This gate parses the frontmatter of every `plugins/*/skills/*/SKILL.md` and
`plugins/*/agents/*.md` with `yaml.safe_load` and requires a mapping with a
non-empty string `description`. It prints each offender and exits non-zero if any
fail, so a malformed front-matter can never ship again.

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


def _violations(root: Path) -> list[tuple[str, str]]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return [("<environment>", "pyyaml not available to validate frontmatter")]

    patterns = ["plugins/*/skills/*/SKILL.md", "plugins/*/agents/*.md"]
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
        elif not isinstance(data.get("description"), str) or not data["description"].strip():
            bad.append((rel, "missing or non-string 'description'"))
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
    print("Frontmatter OK — every skill/agent frontmatter parses as strict YAML with a description.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
