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
    # ⛔ The digit group was `\b\d+\.\d+\.\d+\b`, and a `v` prefix DESTROYS that leading
    # `\b` — `v` and `0` are both word chars, so there is no boundary between them.
    # Measured 2026-08-20 with an A/B control: one plan, changing only `v0.285.0` ->
    # `0.285.0`, flipped landing from `main` to `pr`. It also missed this repo's own
    # commit style (`chore(ravenclaude-core): v0.284.0`).
    #
    # ⛔ This is the EXPENSIVE direction of error. The comment on `layout-allowlist-edit`
    # below states the deliberate bias: "firing wrongly costs a needless draft PR", i.e.
    # over-fire on purpose. Missing a version bump does the opposite — it lets a plan
    # carrying a stale engineering pre-commitment land canonically in `main`, inverting
    # tiebreak F3. `(?<![\w.])` keeps the old anti-substring protection (no matching the
    # tail of `1.2.3.4`) while allowing an optional `v`.
    "version-bump-target": re.compile(
        r"\bbump\b[^\n]{0,40}(?<![\w.])v?\d+\.\d+\.\d+\b"
        r"|\bversion\b[^\n]{0,20}(?<![\w.])v?\d+\.\d+\.\d+\b"
        r"|(?<![\w.])v?\d+\.\d+\.\d+\b[^\n]{0,20}\bbump\b",
        re.IGNORECASE,
    ),
    "reserved-gate-slot": re.compile(r"\bGate\s+\d+\b", re.IGNORECASE),
    # NOTE: "layout-allowlist-edit" is NOT a bare regex — see _layout_edit_fires below.
    "layout-allowlist-edit": None,
    "named-pr-or-branch-target": re.compile(
        r"\b(?:branch|PR)\b[^\n]{0,30}\b(?:feat/|fix/|chore/|forge/)[\w./-]+", re.IGNORECASE
    ),
}

# --- layout-allowlist-edit: a MENTION is not a PRE-COMMITMENT --------------
# This signal used to be `re.compile(r"\.repo-layout\.json|allowed_globs")` — a bare
# substring match on the filename. So a plan stating the OPPOSITE of a pre-commitment
# ("`.repo-layout.json` needs **no edit** — settled by probe") fired it and was forced
# to a draft PR. That is this repo's own recorded "source-scan gates match PROSE"
# defect, sitting in the router that enforces tiebreak F3 — and F3 exists precisely so
# a PURE DESIGN/ANALYSIS plan lands on main. Any analysis plan that merely *discussed*
# the layout file was denied that path.
#
# The fix is scoped PER LINE (a natural window — plans state a commitment in one
# sentence) and requires all three of:
#   1. the token,  2. an edit VERB,  3. NO negation on that line.
#
# ⛔ DIRECTION OF ERROR IS DELIBERATE. Firing wrongly costs a needless draft PR;
# NOT firing wrongly lets a stale pre-commitment sit canonically in main, which is the
# harm F3 was written to prevent. So when in doubt this must fire — never widen the
# negation list to "clean up" a noisy PR verdict.
_LAYOUT_TOKEN = re.compile(r"\.repo-layout\.json|allowed_globs", re.IGNORECASE)
_LAYOUT_EDIT_VERB = re.compile(
    r"\b(?:add(?:s|ing|ed)?|edit(?:s|ing|ed)?|modif\w+|updat\w+|extend\w*|amend\w*"
    r"|append\w*|register\w*|declar\w+|widen\w*|new\s+(?:glob|entry|allow-?list))\b",
    re.IGNORECASE,
)
# Negation/absence words that flip a same-line edit mention into "we are NOT editing it".
_LAYOUT_NEGATION = re.compile(
    r"\b(?:no|not|none|never|without|un(?:changed|modified|touched|edited)|zero"
    r"|skip(?:s|ped)?|avoid\w*|already|needn'?t|doesn'?t|don'?t|isn'?t|aren'?t)\b",
    re.IGNORECASE,
)


def _layout_edit_fires(plan_text: str) -> bool:
    """True only for a line that commits to EDITING the layout allow-list.

    A line that merely names `.repo-layout.json` — or explicitly says no edit is
    needed — is not a pre-commitment and must not force a draft PR.
    """
    for line in plan_text.splitlines():
        if not _LAYOUT_TOKEN.search(line):
            continue
        if not _LAYOUT_EDIT_VERB.search(line):
            continue
        if _LAYOUT_NEGATION.search(line):
            continue
        return True
    return False


_SIGNAL_PREDICATES = {"layout-allowlist-edit": _layout_edit_fires}


def landing_verdict(plan_text: str) -> dict:
    """main vs pr, with the signals that fired (deterministic)."""
    hits = []
    for name, rx in _ENG_SIGNALS.items():
        pred = _SIGNAL_PREDICATES.get(name)
        fired = pred(plan_text) if pred is not None else bool(rx.search(plan_text))
        if fired:
            hits.append(name)
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
    # Regression: the v-PREFIXED bump. Every fixture above writes a bare `1.2.3`, which is
    # why nine of them passed while the detector was blind to this repo's own `v0.284.0`
    # convention. A control that only ever uses the shape that works is not a control.
    (
        "Ship one hook. Bump `plugin.json` to v0.285.0 so the version-keyed cache refreshes.",
        "small",
        True,
        "clean",
        ("use_local", "pr"),
    ),
    # Counter-fixture: a version-shaped string that is NOT a pre-commitment must still
    # land on main, so the widened regex cannot be "fixed" by matching everything.
    (
        "A design memo. Mentions that Python 3.11.2 is installed. No code, no bump target.",
        "small",
        True,
        "clean",
        ("use_local", "main"),
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
    # --- layout-allowlist-edit: mention vs pre-commitment ------------------
    # BOTH halves are required. The negative halves alone would pass on a signal
    # that never fires at all; the positive half above (fixture 5) is what proves
    # the tightened matcher did not simply go blind.
    #
    # NEGATIVE 1 — the exact sentence that exposed the defect. A plan stating the
    # OPPOSITE of a pre-commitment was forced to a draft PR, inverting tiebreak F3.
    (
        "`.repo-layout.json` needs no edit — settled by a bidirectional probe.",
        "small",
        True,
        "clean",
        ("use_local", "main"),
    ),
    # NEGATIVE 2 — a bare mention with no edit verb at all is analysis, not a commitment.
    (
        "A design memo weighing how allowed_globs coverage shapes the options.",
        "small",
        True,
        "clean",
        ("use_local", "main"),
    ),
    # POSITIVE — an unambiguous commitment must still reach a draft PR.
    (
        "We will add plugins/example/** to the allowed_globs list.",
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
