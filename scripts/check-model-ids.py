#!/usr/bin/env python3
"""Gate 134 — model-ID drift gate.

Fails the build if any governed, git-tracked code/config file references a
claude-* model id that is NOT one of the canonical `current` values in
plugins/ravenclaude-core/knowledge/model-catalog.json.

Design notes (from the FORGE red-team, run dashboard-process-hardening):
  - Repo-wide + git-derived governed list (NOT a hand-copied file list) — FM6
    Trigger B: a fixed list false-PASSes when a new seat file adds a stale id.
  - Token/word-boundary matching with exact set membership, NEVER substring —
    FM6 Trigger A: bare `claude-haiku-4-5` is a strict prefix of the canonical
    dated `claude-haiku-4-5-20251001`, so a substring test would false-FAIL the
    canonical id.
  - Carve-outs kept in ONE place (widening later = a one-line edit): the
    design-checkin-owned routing-quality tier tables, test fixtures (arbitrary
    model literals as test data), docs/CHANGELOG prose (historical), the
    illustrative claude-app-engineering narrative, and the catalog + this gate.

Usage: python3 scripts/check-model-ids.py   (exit 0 clean, 1 on drift)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "plugins" / "ravenclaude-core" / "knowledge" / "model-catalog.json"

# A claude model id token: family + numeric version, optional dated suffix.
# `claude-code` (product, no numeric version) is excluded by the required -[0-9].
MODEL_RE = re.compile(r"claude-[a-z]+-[0-9]+(?:-[0-9]+)?(?:-[0-9]{8})?")

# Governed file extensions — code + config where a stale id is a real bug.
GOVERNED_EXT = {".py", ".sh", ".json", ".yaml", ".yml", ".mjs", ".js"}

# Carve-outs (path substrings / exact rels). ONE place — see module docstring.
CARVE_SUBSTR = (
    "plugins/ravenclaude-core/knowledge/model-catalog.json",  # the source of truth
    "plugins/ravenclaude-core/scripts/thing-decide.py",  # design-checkin tier tables (C5)
    "rc-deep-research",  # design-checkin routing-quality table
    "adaptive-run-classifier",  # design-checkin
    "eval-adaptive-classifier",  # design-checkin adjacent
    "evaluate-dispatch",  # design-checkin
    "refine-to-rubric",  # judge-normalization subsystem: dated-id examples + judge default
    "scripts/check-",  # gate-verification harnesses embed fixture/expected model literals
    "scripts/audit-gates.sh",  # meta-gate runner: many synthetic thing.yaml fixtures
    "/hooks/tests/",  # test fixtures use arbitrary model literals
    "/tests/",  # ditto
    "plugins/claude-app-engineering/",  # illustrative routing-ladder narrative
    "/docs/",  # plans/research/follow-ups + historical prose
    "CHANGELOG.md",
)


def is_carved(rel: str) -> bool:
    return any(c in rel for c in CARVE_SUBSTR)


def scan_text(text: str, current: set) -> list:
    """Return the list of (token, kind) non-canonical model ids in `text`.
    Kind is 'STALE' if in the catalog `stale` list, else 'UNKNOWN'."""
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    stale = set(catalog["stale"])
    hits = []
    for m in MODEL_RE.finditer(text):
        tok = m.group(0)
        if tok in current:
            continue
        hits.append((tok, "STALE" if tok in stale else "UNKNOWN"))
    return hits


def self_test() -> int:
    """Prove the detector's teeth without touching the tree: a stale id is caught,
    and the dated-haiku canonical (a strict superset of the bare stale token) is NOT
    false-flagged by a substring match."""
    current = set(json.loads(CATALOG.read_text(encoding="utf-8"))["current"].values())
    bad = scan_text('model: "claude-sonnet-4-6"  # and claude-opus-4-7', current)
    good = scan_text(
        'a: claude-opus-4-8  b: claude-sonnet-5  c: claude-haiku-4-5-20251001  d: claude-fable-5',
        current,
    )
    ok_bad = {t for t, _ in bad} == {"claude-sonnet-4-6", "claude-opus-4-7"}
    ok_good = good == []
    if ok_bad and ok_good:
        print("check-model-ids --self-test: PASS (stale caught; canonical dated-haiku not flagged)")
        return 0
    print(f"check-model-ids --self-test: FAIL bad={bad!r} good={good!r}")
    return 1


def governed_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    for rel in out:
        if Path(rel).suffix not in GOVERNED_EXT:
            continue
        if is_carved(rel):
            continue
        yield rel


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    current = set(catalog["current"].values())
    stale = set(catalog["stale"])

    violations = []
    for rel in governed_files():
        p = ROOT / rel
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in MODEL_RE.finditer(line):
                tok = m.group(0)
                if tok in current:
                    continue  # canonical — fine
                kind = "STALE" if tok in stale else "UNKNOWN"
                violations.append((rel, i, tok, kind, line.strip()[:100]))

    if violations:
        print("Gate 134 FAILED — non-canonical model id(s) in governed files:")
        for rel, i, tok, kind, ctx in violations:
            print(f"  {rel}:{i}  [{kind}] {tok}")
            print(f"      {ctx}")
        print(
            f"\nCanonical ids (plugins/ravenclaude-core/knowledge/model-catalog.json): "
            f"{sorted(current)}"
        )
        print(
            "Replace each with its canonical form, or (if this is a deliberate "
            "model-quality change to a routing-tier table) add the path to CARVE_SUBSTR."
        )
        return 1
    print(f"Gate 134 OK — every governed claude-* id ∈ current {sorted(current)}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    sys.exit(main())
