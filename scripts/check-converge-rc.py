#!/usr/bin/env python3
"""check-converge-rc.py — bidirectional audit gate for P4 of the Convergence
Engine: the `rc converge` front-door verb + the report-renderer hardening.

The DEFAULT run proves the user-facing surface:
  - `rc converge derive --kind code` prints a schema-shaped rubric;
  - `rc converge verdict --rubric R --scorecard S` prints the deterministic
    terminate() verdict JSON and exit-codes it (0 = stop reached, 1 = continue);
  - `rc converge report <completed-scorecard>` renders the constrained report and
    its body contains NO over-claim word;
  - `rc converge report <scorecard-without-verdict>` fails with a FRIENDLY message
    (exit 2), not a traceback — a report needs a terminate() verdict;
  - the over-claim screen is WORD-BOUNDARY based: an honest "not a claim of
    perfection" disclaimer is allowed, but a real "the artifact is perfect"
    over-claim in a rendered field is rejected;
  - `rc converge` with no/!bad subcommand exits nonzero with usage.

BIDIRECTIONAL TEETH (--must-fail-overclaim): strip the word-boundary screen from
render_report (make it a no-op) and assert a report carrying "the artifact is
perfect" THEN renders clean — proving the screen is what blocks it. Exit 0 iff
the over-claim leaks (gate has teeth).

Stdlib-only. Exit 0 = all held. Exit 1 = a failure / teeth absent.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RC = os.path.join(REPO_ROOT, "plugins", "ravenclaude-core", "bin", "rc")
SCRIPTS = os.path.join(
    REPO_ROOT, "plugins", "ravenclaude-core", "skills", "refine-to-rubric", "scripts"
)


class _Fail(Exception):
    pass


def _check(cond, msg):
    if not cond:
        raise _Fail(msg)
    print(f"  ✓ {msg}")


def _load_loop():
    spec = importlib.util.spec_from_file_location("loop", os.path.join(SCRIPTS, "loop.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rc(args):
    p = subprocess.run(["bash", RC] + args, capture_output=True, text=True, check=False)
    return p.returncode, p.stdout, p.stderr


def _completed_scorecard(loop):
    rubric = {
        "schema_version": "1.0.0", "artifact_kind": "code",
        "dimensions": [
            {"id": "tests-pass", "title": "T", "weight": 50, "source": "library",
             "verified": True, "hard_gate": True, "objective_signal": "lint-cmd"},
            {"id": "correctness", "title": "C", "weight": 50, "source": "library",
             "verified": True, "hard_gate": False, "objective_signal": ""},
        ],
    }
    cscores = {1: 0.5, 2: 0.95, 3: 0.96}

    def ev(idx):
        g = idx >= 1
        return {"judge_needed": g, "hard_gates": {"tests-pass": g},
                "scores": {"tests-pass": 1.0 if g else 0.0},
                "judge_dimensions": ["correctness"] if g else []}

    def judge(idx):
        c = cscores.get(idx, 0.96)
        f = [{"dimension": "correctness", "severity": "high", "note": "gap"}] if c < 0.6 else []
        return {"scores": {"correctness": c}, "findings": f}

    return loop.run_loop(rubric, ev, judge, lambda i: None,
                         config={"iteration_cap": 10, "model_call_budget": 50,
                                 "score_floor": 0.85, "epsilon": 0.01, "plateau_patience": 2})


def run_default():
    loop = _load_loop()
    _check(os.path.isfile(RC), "bin/rc exists")

    # derive
    rc, out, err = _rc(["converge", "derive", "--kind", "code"])
    _check(rc == 0, f"rc converge derive exits 0 (rc={rc}; err={err.strip()[:80]})")
    rub = json.loads(out)
    _check(len(rub["dimensions"]) >= 2 and rub["artifact_kind"] == "code",
           "rc converge derive prints a schema-shaped rubric for the kind")

    with tempfile.TemporaryDirectory() as td:
        rpath = os.path.join(td, "r.json")
        spath = os.path.join(td, "s.json")
        cpath = os.path.join(td, "completed.json")
        nopath = os.path.join(td, "noverdict.json")
        json.dump(rub, open(rpath, "w"))

        # a converged scorecard (verdict present) + a no-verdict scorecard
        completed = _completed_scorecard(loop)
        json.dump(completed, open(cpath, "w"))
        noverdict = {k: v for k, v in completed.items() if k != "verdict"}
        json.dump(noverdict, open(nopath, "w"))
        # verdict subcommand needs rubric + scorecard
        json.dump(completed, open(spath, "w"))

        # verdict
        rc, out, err = _rc(["converge", "verdict", "--rubric", rpath, "--scorecard", spath])
        _check(rc in (0, 1), f"rc converge verdict exit-codes the stop decision (rc={rc})")
        v = json.loads(out)
        _check(v["status"] in ("rubric-pass", "capped", "plateaued", "budget-exhausted"),
               f"rc converge verdict prints an honest verdict status ({v['status']})")

        # report (completed) → renders, no over-claim word
        rc, out, err = _rc(["converge", "report", cpath])
        _check(rc == 0, f"rc converge report exits 0 on a completed scorecard (rc={rc})")
        low = out.lower()
        for w in ("perfect", "flawless"):
            _check(w not in low, f"rendered report body contains no over-claim word '{w}'")
        _check("verdict" in low and "residual" in low, "report shows the verdict + residual gaps")

        # report (no verdict) → friendly error, exit 2, no traceback
        rc, out, err = _rc(["converge", "report", nopath])
        _check(rc == 2, f"rc converge report on a verdict-less scorecard exits 2 (rc={rc})")
        _check("Traceback" not in err and "verdict" in err.lower(),
               "verdict-less report fails FRIENDLY (no Python traceback)")

    # word-boundary screen: an honest 'perfection' disclaimer renders; a real
    # 'perfect' over-claim in a rendered field is rejected.
    honest = {"verdict": {"status": "rubric-pass", "best_index": 0, "best_score": 1.0,
                          "reason": "ok", "residual_gaps": ["this is not a claim of perfection"]},
              "iterations": [{"index": 0, "model_calls": 0}]}
    rep = loop.render_report(honest)
    _check("perfection" in rep.lower(), "honest 'not a claim of perfection' disclaimer is allowed (word-boundary screen)")

    overclaim = {"verdict": {"status": "rubric-pass", "best_index": 0, "best_score": 1.0,
                            "reason": "ok", "residual_gaps": ["the artifact is now perfect"]},
                 "iterations": [{"index": 0, "model_calls": 0}]}
    raised = False
    try:
        loop.render_report(overclaim)
    except AssertionError:
        raised = True
    _check(raised, "a real 'perfect' over-claim in a rendered field is rejected")

    # bad/empty subcommand → nonzero + usage
    rc, out, err = _rc(["converge", "bogus-subcommand"])
    _check(rc != 0 and "converge" in err.lower(), "rc converge with a bad subcommand exits nonzero with usage")

    return True


def run_must_fail_overclaim():
    """Strip the word-boundary over-claim screen → a report with 'the artifact is
    perfect' renders clean. If it does, the screen is the real protection (teeth)."""
    loop = _load_loop()
    overclaim = {"verdict": {"status": "rubric-pass", "best_index": 0, "best_score": 1.0,
                            "reason": "ok", "residual_gaps": ["the artifact is now perfect"]},
                 "iterations": [{"index": 0, "model_calls": 0}]}

    # sanity: intact screen rejects it
    try:
        loop.render_report(overclaim)
        print("  ✗ intact screen already let an over-claim through — broken", file=sys.stderr)
        return False
    except AssertionError:
        pass

    # mutant: make the banned-word regex match nothing
    import re as _re
    loop._BANNED_RE = _re.compile(r"(?!x)x")  # matches nothing
    try:
        rep = loop.render_report(overclaim)
    except AssertionError:
        print("  ✗ mutant still rejected — teeth not demonstrated", file=sys.stderr)
        return False
    if "perfect" in rep.lower():
        print("  ✓ mutant (no over-claim screen) WRONGLY renders 'perfect' — gate has teeth")
        return True
    print("  ✗ mutant did not leak the over-claim — teeth not demonstrated", file=sys.stderr)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail-overclaim", action="store_true")
    args = ap.parse_args(argv)
    try:
        ok = run_must_fail_overclaim() if args.must_fail_overclaim else run_default()
    except _Fail as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
