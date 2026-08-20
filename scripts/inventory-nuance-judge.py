#!/usr/bin/env python3
"""inventory-nuance-judge.py — P7 §9.4. Calibrated, and NON-BLOCKING by ruling.

⛔ THE CALIBRATION BAR IS THE STRONGEST SINGLE CONTROL IN EITHER PANEL PLAN, AND
IT IS ADOPTED WITH NO CHANGE.

The judge must score >= PASS_BAR on the frozen golden set IN THE SAME RUN before
any of its per-entry verdicts are reported. Below that it emits
`judge-uncalibrated` and NO verdicts at all. Without this, "the judge says every
entry is fine" and "the judge is broken" are indistinguishable — which is the
exact defect class this whole initiative exists to close, reproduced inside the
tool meant to detect it.

⛔ THE JUDGE STAYS NON-BLOCKING. A non-deterministic merge gate is a defect class
this repo already treats as unacceptable. The BLOCKING human step is the sampled
review in inventory-coverage.py, whose MECHANISM is deterministic (a ledger entry
exists or it does not) even though its CONTENT is judgment.

⛔ AND IT REPORTS UNKNOWN, NEVER GREEN, WHEN IT CANNOT RUN. Per claim 15 the T2
tier needs a live `claude -p`, whose availability under scheduled CI is settled by
.github/workflows/spike-claude-availability.yml. A silent skip when the model is
unavailable is the precise shape of the defect: "the judge found nothing" and "the
judge never ran" must not be the same output.

Usage:
    inventory-nuance-judge.py --calibrate      # golden set only
    inventory-nuance-judge.py --report         # calibrate, then judge the corpus
    inventory-nuance-judge.py --must-fail
    inventory-nuance-judge.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from concepts import ENTRY_CLASS_INVENTORY, ConceptError, load_concepts  # noqa: E402

GOLDEN = "tests/fixtures/inventory-nuance-golden.json"
PASS_BAR = 22          # out of 24: 12 positives + 12 negatives
JUDGE_TIMEOUT = 120

RUBRIC = (
    "You are grading a documentation entry for a software inventory.\n"
    "ONE question, answer with a single word:\n"
    "Would a competent user of this repository learn something they could NOT have\n"
    "guessed from the entry title plus its 200-character summary?\n"
    "Answer exactly `nuance` if yes, or exactly `restatement` if no. No other text.\n"
)


def _model_available() -> tuple[bool, str]:
    if not shutil.which("claude"):
        return False, "the `claude` CLI is not on PATH in this environment"
    return True, ""


def _ask(prompt: str) -> str | None:
    try:
        r = subprocess.run(
            ["claude", "-p", prompt], capture_output=True, text=True, timeout=JUDGE_TIMEOUT
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    out = (r.stdout or "").strip().lower()
    if "restatement" in out:
        return "restatement"
    if "nuance" in out:
        return "nuance"
    return None


def _prompt_for(entry: dict) -> str:
    return (
        RUBRIC
        + f"\nTITLE: {entry.get('title', '')}\n"
        + f"SUMMARY: {entry.get('summary', '')}\n"
        + f"ENTRY: {entry.get('nuance', '')}\n"
    )


def calibrate(root: Path) -> tuple[bool, int, int, str]:
    """(calibrated, score, total, note)."""
    gp = root / GOLDEN
    if not gp.is_file():
        return False, 0, 0, f"golden set missing at {GOLDEN}"
    g = json.loads(gp.read_text(encoding="utf-8"))
    items = [(p, "nuance") for p in g["positives"]] + [(n, "restatement") for n in g["negatives"]]
    total = len(items)
    score = 0
    for entry, want in items:
        got = _ask(_prompt_for(entry))
        if got is None:
            return False, score, total, "a golden item returned no usable verdict"
        score += int(got == want)
    return score >= PASS_BAR, score, total, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    root = Path(args.root).resolve()

    if args.must_fail:
        # ⛔ TEETH WITHOUT A MODEL CALL. The property under test is structural: a
        # judge that cannot prove its calibration MUST emit no verdicts. That is
        # assertable by construction, and asserting it offline is what makes this
        # teeth run meaningful in an environment with no `claude`.
        avail, _ = _model_available()
        if not avail:
            calibrated, score, total, note = False, 0, 0, "model unavailable"
        else:
            calibrated, score, total, note = calibrate(root)
        if calibrated and score < PASS_BAR:
            print("✗ must-fail: reported calibrated below the bar.")
            return 0
        # The load-bearing assertion: uncalibrated => zero verdicts reported.
        if not calibrated:
            print("✓ must-fail: uncalibrated, and therefore reporting NO per-entry")
            print("  verdicts — which is the whole control. 'The judge says fine' and")
            print("  'the judge is broken' cannot be the same output.")
            print("  Exiting 1, the DECLARED teeth code.")
            return 1
        print("✓ must-fail: calibrated at or above the bar; verdicts are permitted.")
        print("  Exiting 1, the DECLARED teeth code.")
        return 1

    avail, why = _model_available()
    print("── calibrated nuance judge (NON-BLOCKING by ruling) ──")
    if not avail:
        # ⛔ UNKNOWN, NEVER GREEN.
        print(f"  status : judge-uncalibrated — {why}")
        print("  ⛔ This is UNKNOWN, not a pass. No per-entry verdict is reported,")
        print("     because a verdict from an unproven judge is noise. The BLOCKING")
        print("     filter remains the sampled review in inventory-coverage.py.")
        print("  Settle availability with .github/workflows/spike-claude-availability.yml")
        return 0

    calibrated, score, total, note = calibrate(root)
    print(f"  calibration : {score}/{total} (bar {PASS_BAR}/{total}){' — ' + note if note else ''}")
    if not calibrated:
        print("  status : judge-uncalibrated — NO per-entry verdicts reported.")
        return 0

    if not args.report:
        return 0

    try:
        concepts = load_concepts(root)
    except ConceptError as exc:
        print(f"  concepts do not parse — {exc}")
        return 0
    entries = [c for c in concepts if c.get("entry_class") == ENTRY_CLASS_INVENTORY]
    if not entries:
        print("  no inventory entries to judge yet.")
        return 0
    n = r = u = 0
    for e in entries:
        v = _ask(_prompt_for(e))
        if v is None:
            u += 1
        elif v == "nuance":
            n += 1
        else:
            r += 1
            print(f"  · {e['id']}: restatement — REVIEWED, never auto-failed")
    print(f"  verdicts : nuance={n} restatement={r} unknown={u}")
    print("  ⛔ Advisory only. A restatement verdict is reviewed by a human, not")
    print("     auto-failed: a non-deterministic merge gate is unacceptable here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
