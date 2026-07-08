#!/usr/bin/env python3
"""forge-route.py — deterministic routing for the /forge gated-planning pipeline.

Two independent, MODEL-FREE verdicts (rule-derivable judgment belongs in a script,
not a free-form model call — the same principle behind thing-decide.py):

1. EXECUTION routing (Ultraplan-cloud vs local) — the repo's existing rubric
   (`docs/research/2026-06-02-data-viz-agent/build-plan.md` §routing): three signals
   → use_local | consider_ultraplan | lean_ultraplan. Privacy-sensitive work never
   leans cloud.

2. LANDING routing (commit straight to main vs a forge/<slug> draft PR) — tiebreak
   F3: a pure design/analysis plan lands on main (AGENTS.md docs-to-main rule); a plan
   carrying an ENGINEERING PRE-COMMITMENT (a concrete version-bump target, a reserved
   `Gate N` slot, a `.repo-layout.json`/allowed_globs edit, a named PR/branch target)
   lands via a draft PR, so a stale pre-commitment can't sit canonically in main.

CI never needs a model: `--self-test` runs built-in fixtures (known input → expected
verdict) and exits non-zero on any mismatch. This makes forge-route.py a registered
"canonical route" in the accuracy-near-guarantee sense (a real pass/fail you can cite).

Usage:
    forge-route.py --plan <path> [--size small|medium|large]
                   [--research-done] [--privacy clean|sensitive]
    forge-route.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --- LANDING: engineering-pre-commitment signals (F3). A hit → draft PR, else main. ---
_ENG_SIGNALS = {
    "version-bump-target": re.compile(
        r"\bbump\b[^\n]{0,40}\b\d+\.\d+\.\d+\b|\bversion\b[^\n]{0,20}\b\d+\.\d+\.\d+\b|\b\d+\.\d+\.\d+\b[^\n]{0,20}\bbump\b",
        re.IGNORECASE,
    ),
    "reserved-gate-slot": re.compile(r"\bGate\s+\d+\b", re.IGNORECASE),
    "layout-allowlist-edit": re.compile(r"\.repo-layout\.json|allowed_globs", re.IGNORECASE),
    "named-pr-or-branch-target": re.compile(
        r"\b(?:branch|PR)\b[^\n]{0,30}\b(?:feat/|fix/|chore/|forge/)[\w./-]+", re.IGNORECASE
    ),
}


def landing_verdict(plan_text: str) -> dict:
    """main vs pr, with the signals that fired (deterministic)."""
    hits = [name for name, rx in _ENG_SIGNALS.items() if rx.search(plan_text)]
    return {
        "landing": "pr" if hits else "main",
        "engineering_signals": hits,
        "reason": (
            f"engineering pre-commitment(s) {hits} → draft PR so a stale plan can't sit in main"
            if hits
            else "pure design/analysis plan → commit straight to main (AGENTS.md docs rule)"
        ),
    }


# --- EXECUTION: Ultraplan-vs-local rubric (three signals). ---
def execution_verdict(size: str, research_done: bool, privacy: str) -> dict:
    """use_local | consider_ultraplan | lean_ultraplan (+ confidence + reasons)."""
    reasons = []
    # Privacy is a hard cap: sensitive work never leaves for the cloud. Fail CLOSED —
    # whitelist the known-safe value ("clean") rather than blacklisting "sensitive", so
    # any typo / casing / unknown label is treated as sensitive and stays local.
    if str(privacy).strip().lower() != "clean":
        reasons.append(
            f"privacy={privacy!r} is not 'clean' → cloud Ultraplan is off the table (hard cap)"
        )
        return {"execution": "use_local", "confidence": 0.9, "reasons": reasons}

    score = {"small": 0, "medium": 1, "large": 2}.get(size, 1)
    reasons.append(f"size/scope={size} (weight {score})")
    if not research_done:
        score += 1
        reasons.append("web research not yet done → Ultraplan's cloud-research advantage applies")
    else:
        reasons.append(
            "research already done → one Ultraplan advantage neutralized (not against it)"
        )

    if score >= 3:
        verdict, conf = "lean_ultraplan", 0.72
    elif score == 2:
        verdict, conf = "consider_ultraplan", 0.6
    else:
        verdict, conf = "use_local", 0.7
    return {"execution": verdict, "confidence": conf, "reasons": reasons}


def route(plan_text: str, size: str, research_done: bool, privacy: str) -> dict:
    ev = execution_verdict(size, research_done, privacy)
    lv = landing_verdict(plan_text)
    # A reject is the pipeline's job (unmitigated blocker / incoherent scope) — not this script's.
    return {"schema_version": 1, **ev, **lv}


_FIXTURES = [
    # (plan_text, size, research_done, privacy) -> (execution, landing)
    (
        "Build 4 plugins. bump ravenclaude-core to 0.120.0 and add Gate 53.",
        "large",
        False,
        "clean",
        ("lean_ultraplan", "pr"),
    ),
    (
        "A short design memo weighing two approaches. No code, no version changes.",
        "small",
        True,
        "clean",
        ("use_local", "main"),
    ),
    (
        "Medium refactor across two skills; research still needed.",
        "medium",
        False,
        "clean",
        ("consider_ultraplan", "main"),
    ),
    (
        "Large client-confidential build. bump to 1.2.3.",
        "large",
        False,
        "sensitive",
        ("use_local", "pr"),
    ),
    (
        "Add a knowledge doc. Edit .repo-layout.json allowed_globs for the new dir.",
        "small",
        True,
        "clean",
        ("use_local", "pr"),
    ),
    # Lowercase mid-sentence 'gate N' must still fire the reserved-gate-slot signal
    # (regression guard for the missing re.IGNORECASE — Finding 10).
    (
        "A short memo, but we reserve gate 53 for the follow-up work.",
        "small",
        True,
        "clean",
        ("use_local", "pr"),
    ),
]


def self_test() -> int:
    fails = []
    for text, size, rd, priv, (exp_exec, exp_land) in _FIXTURES:
        got = route(text, size, rd, priv)
        if got["execution"] != exp_exec or got["landing"] != exp_land:
            fails.append((text[:40], (exp_exec, exp_land), (got["execution"], got["landing"])))
    if fails:
        for t, exp, got in fails:
            print(f"FAIL: {t!r} expected {exp} got {got}", file=sys.stderr)
        print(f"forge-route self-test: {len(fails)} FAILED", file=sys.stderr)
        return 1
    print(f"forge-route self-test: {len(_FIXTURES)} fixtures OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic routing for /forge.")
    ap.add_argument("--plan", help="path to the synthesized plan.md")
    ap.add_argument("--size", choices=["small", "medium", "large"], default="medium")
    ap.add_argument("--research-done", action="store_true")
    ap.add_argument("--privacy", choices=["clean", "sensitive"], default="clean")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.plan:
        ap.error("--plan is required (or use --self-test)")
    text = Path(a.plan).read_text(encoding="utf-8", errors="replace")
    print(json.dumps(route(text, a.size, a.research_done, a.privacy), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
