#!/usr/bin/env python3
"""estimate_cost.py — pre-flight, zero-model-call cost estimator for /repo-review.

Reads a review-plan.json (produced by repo_map.py) and an effort tier, and
prints how many agent calls a full /repo-review run would cost BEFORE
launching anything, so a user (or the Workflow script) can decide whether to
proceed, narrow scope, or pick a cheaper tier.

Stdlib-only. No model calls.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# The effort-tier ladder (hardcoded — this is the shipped design).
#
# tier    | dimensions (D) | models-per-dimension (M) default | cross-model
# low     | REFUSED        | -                                 | -
# medium  | REFUSED        | -                                 | -
# high    | 4              | 1                                 | no
# xhigh   | 8              | 2 (opt-in via --cross-model, else 1) | yes, opt-in
# max     | 8              | 2 (default ON)                    | yes, default on
# ultra   | 8              | 2                                  | yes, always
#
# D=8 at xhigh/max/ultra: the original 7 (correctness, security, concurrency,
# resource-leaks, error-handling, performance, dead-code-simplification) plus
# ci-cd-actions-security (GitHub Actions / CI-gate specific findings, distinct
# from the generic `security` dimension). dead-code-simplification is still
# the only dimension pinned to models-per-dimension=1 regardless of tier.
# ---------------------------------------------------------------------------

REFUSED_TIERS = ("low", "medium")

# dimensions per tier
TIER_DIMENSIONS: dict[str, int] = {
    "high": 4,
    "xhigh": 8,
    "max": 8,
    "ultra": 8,
}

# default verify/fix caps per tier (overridable via CLI)
TIER_VERIFY_CAP_DEFAULT: dict[str, int] = {
    "high": 60,
    "xhigh": 120,
    "max": 160,
    "ultra": 160,
}

TIER_FIX_CAP_DEFAULT: dict[str, int] = {
    "high": 40,
    "xhigh": 60,
    "max": 80,
    "ultra": 80,
}

VALID_TIERS = ("low", "medium", "high", "xhigh", "max", "ultra")


class TierError(Exception):
    """Raised when the effort tier is refused (low/medium)."""


def resolve_cross_model(tier: str, cross_model_flag: bool) -> bool:
    """Whether cross-model (M=2) is active for this tier/flag combination."""
    if tier == "high":
        return False
    if tier == "xhigh":
        return bool(cross_model_flag)
    if tier in ("max", "ultra"):
        # default ON for max, always on for ultra; --cross-model cannot
        # disable it (there is no --no-cross-model per the spec), so the
        # flag is simply irrelevant here — it's already on.
        return True
    raise TierError(f"unknown tier: {tier}")


def compute_models_per_dimension_label(tier: str, cross_model: bool, dimensions: int) -> tuple[str, int]:
    """Return (human label, review_agents_per_batch) per the dead-code-simplification nuance.

    dead-code-simplification always effectively runs at models-per-dimension=1
    regardless of tier, even under cross-model. For high (D=4, M=1) this
    nuance is moot since M is already 1.
    """
    if tier == "high":
        m = 1
        review_agents_per_batch = dimensions * m
        label = f"{dimensions} dims x {m} model"
        return label, review_agents_per_batch

    # xhigh / max / ultra: D=8, dead-code-simplification is always 1 model.
    m = 2 if cross_model else 1
    if m == 1:
        review_agents_per_batch = dimensions * 1
        label = f"{dimensions} dims x 1 model"
        return label, review_agents_per_batch

    # m == 2: (D-1)*M + 1*1
    review_agents_per_batch = (dimensions - 1) * m + 1 * 1
    label = f"{dimensions - 1} dims x {m} models + dead-code-simplification x 1 model"
    return label, review_agents_per_batch


def load_plan(plan_path: str) -> dict[str, Any]:
    with open(plan_path, encoding="utf-8") as f:
        return json.load(f)


def estimate(
    plan: dict[str, Any],
    tier: str,
    cross_model_flag: bool,
    agent_budget: int,
    verify_cap: int | None,
    fix_cap: int | None,
    overhead: int,
) -> dict[str, Any]:
    if tier in REFUSED_TIERS:
        raise TierError(
            f"--scope repo needs at least `high` effort — `{tier}` is refused for a full "
            "repo review. Pick --effort-tier high, xhigh, max, or ultra."
        )
    if tier not in TIER_DIMENSIONS:
        raise TierError(f"unknown effort tier: {tier!r} (expected one of {VALID_TIERS})")

    dimensions = TIER_DIMENSIONS[tier]
    cross_model = resolve_cross_model(tier, cross_model_flag)
    label, review_agents_per_batch = compute_models_per_dimension_label(tier, cross_model, dimensions)

    v_max = TIER_VERIFY_CAP_DEFAULT[tier] if verify_cap is None else verify_cap
    k_max = TIER_FIX_CAP_DEFAULT[tier] if fix_cap is None else fix_cap
    o = overhead

    batches_planned = int(plan["coverage"]["batches_planned"])

    numerator = agent_budget - v_max - k_max - o
    b = math.floor(numerator / review_agents_per_batch) if review_agents_per_batch > 0 else 0
    b = max(b, 0)

    full_coverage = b >= batches_planned
    batches_affordable = batches_planned if full_coverage else min(b, batches_planned)
    batches_affordable = max(batches_affordable, 0)

    review_agents = batches_affordable * review_agents_per_batch
    total_agents = review_agents + v_max + k_max + o
    waves_at_16_concurrency = math.ceil(total_agents / 16) if total_agents > 0 else 0

    return {
        "effort_tier": tier,
        "cross_model": cross_model,
        "dimensions": dimensions,
        "models_per_dimension_effective": label,
        "review_agents_per_batch": review_agents_per_batch,
        "agent_budget": agent_budget,
        "verify_cap": v_max,
        "fix_cap": k_max,
        "overhead": o,
        "batches_needed": batches_planned,
        "batches_affordable": batches_affordable,
        "full_coverage": full_coverage,
        "review_agents": review_agents,
        "total_agents": total_agents,
        "waves_at_16_concurrency": waves_at_16_concurrency,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pre-flight, zero-model-call cost estimator for /repo-review."
    )
    parser.add_argument("--plan", help="path to review-plan.json")
    parser.add_argument(
        "--effort-tier",
        choices=list(VALID_TIERS),
        help="effort tier: low|medium (refused) | high|xhigh|max|ultra",
    )
    parser.add_argument(
        "--cross-model",
        action="store_true",
        help="opt in to cross-model (M=2) for xhigh; ignored/always-on for max/ultra",
    )
    parser.add_argument("--agent-budget", type=int, default=900, help="A_max (default 900)")
    parser.add_argument(
        "--verify-cap", type=int, default=None, help="V_max override (tier-specific default otherwise)"
    )
    parser.add_argument(
        "--fix-cap", type=int, default=None, help="K_max override (tier-specific default otherwise)"
    )
    parser.add_argument("--overhead", type=int, default=6, help="O, fixed overhead cost (default 6)")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test suite")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if not args.plan or not args.effort_tier:
        parser.error("--plan and --effort-tier are required (or pass --self-test)")

    try:
        plan = load_plan(args.plan)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: failed to read plan {args.plan!r}: {exc}", file=sys.stderr)
        return 2

    try:
        result = estimate(
            plan=plan,
            tier=args.effort_tier,
            cross_model_flag=args.cross_model,
            agent_budget=args.agent_budget,
            verify_cap=args.verify_cap,
            fix_cap=args.fix_cap,
            overhead=args.overhead,
        )
    except TierError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _make_plan(batches_planned: int) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "commit": "deadbeef",
        "totals": {},
        "excluded": {},
        "batches": [],
        "coverage": {
            "batches_planned": batches_planned,
            "batches_budgeted": batches_planned,
            "files_covered": batches_planned * 45,
            "files_deferred": 0,
            "deferred_reason": None,
            "top_deferred_dirs": [],
        },
    }


EXPECTED_OUTPUT_KEYS = {
    "effort_tier",
    "cross_model",
    "dimensions",
    "models_per_dimension_effective",
    "review_agents_per_batch",
    "agent_budget",
    "verify_cap",
    "fix_cap",
    "overhead",
    "batches_needed",
    "batches_affordable",
    "full_coverage",
    "review_agents",
    "total_agents",
    "waves_at_16_concurrency",
}


def run_self_test() -> int:
    import subprocess

    results: list[tuple[str, bool, str]] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        results.append((name, cond, detail))
        status = "[ok]" if cond else "[FAIL]"
        print(f"{status} {name}" + (f" — {detail}" if detail and not cond else ""))

    this_file = str(Path(__file__).resolve())

    with tempfile.TemporaryDirectory() as tmpdir:
        plan10_path = Path(tmpdir) / "plan10.json"
        plan10_path.write_text(json.dumps(_make_plan(10)), encoding="utf-8")

        plan_many_path = Path(tmpdir) / "plan_many.json"
        plan_many_path.write_text(json.dumps(_make_plan(500)), encoding="utf-8")

        # --- Assertion 1: low/medium tiers exit 2, non-empty stderr, no stdout JSON ---
        for tier in ("low", "medium"):
            proc = subprocess.run(
                [sys.executable, this_file, "--plan", str(plan10_path), "--effort-tier", tier],
                capture_output=True,
                text=True,
            )
            exit_ok = proc.returncode == 2
            stderr_ok = len(proc.stderr.strip()) > 0
            stdout_no_json = True
            if proc.stdout.strip():
                try:
                    json.loads(proc.stdout)
                    stdout_no_json = False
                except json.JSONDecodeError:
                    stdout_no_json = True
            check(
                f"tier={tier} exits 2 with non-empty stderr, no stdout JSON",
                exit_ok and stderr_ok and stdout_no_json,
                f"returncode={proc.returncode} stderr={proc.stderr!r} stdout={proc.stdout!r}",
            )

        # --- Assertion 2: high tier, 10 batches, default budgets -> full_coverage, rapb=4 ---
        result_high = estimate(
            plan=_make_plan(10),
            tier="high",
            cross_model_flag=False,
            agent_budget=900,
            verify_cap=None,
            fix_cap=None,
            overhead=6,
        )
        check(
            "high tier: full_coverage true and review_agents_per_batch == 4",
            result_high["full_coverage"] is True and result_high["review_agents_per_batch"] == 4,
            str(result_high),
        )

        # --- Assertion 3: xhigh + --cross-model on 10-batch plan -> rapb=15, full_coverage ---
        # D=8 now (the original 7 plus ci-cd-actions-security); formula is
        # (D-1)*M + 1 for the dead-code-simplification single-model carve-out:
        # (8-1)*2 + 1 = 15.
        result_xhigh_cm = estimate(
            plan=_make_plan(10),
            tier="xhigh",
            cross_model_flag=True,
            agent_budget=900,
            verify_cap=None,
            fix_cap=None,
            overhead=6,
        )
        check(
            "xhigh + cross-model: review_agents_per_batch == 15 and full_coverage true",
            result_xhigh_cm["review_agents_per_batch"] == 15 and result_xhigh_cm["full_coverage"] is True,
            str(result_xhigh_cm),
        )

        # --- Assertion 4: xhigh WITHOUT --cross-model -> rapb=8 (D*1) ---
        result_xhigh_nocm = estimate(
            plan=_make_plan(10),
            tier="xhigh",
            cross_model_flag=False,
            agent_budget=900,
            verify_cap=None,
            fix_cap=None,
            overhead=6,
        )
        check(
            "xhigh without cross-model: review_agents_per_batch == 8",
            result_xhigh_nocm["review_agents_per_batch"] == 8,
            str(result_xhigh_nocm),
        )

        # --- Assertion 5: tiny --agent-budget on a plan needing many batches ---
        result_tiny = estimate(
            plan=_make_plan(500),
            tier="high",
            cross_model_flag=False,
            agent_budget=20,
            verify_cap=None,
            fix_cap=None,
            overhead=6,
        )
        check(
            "tiny agent-budget: full_coverage false, 0 <= batches_affordable < batches_planned",
            (
                result_tiny["full_coverage"] is False
                and result_tiny["batches_affordable"] < result_tiny["batches_needed"]
                and result_tiny["batches_affordable"] >= 0
            ),
            str(result_tiny),
        )

        # --- Assertion 6: waves_at_16_concurrency hand-computed cases ---
        # Construct a scenario with total_agents == 32 and == 33 by controlling
        # review_agents_per_batch=4 (high tier), batches_affordable, verify/fix/overhead.
        # total_agents = review_agents + verify_cap + fix_cap + overhead
        # Pick verify_cap=0, fix_cap=0, overhead=0, review_agents_per_batch=4 (high tier)
        # batches_affordable * 4 = 32 -> batches_affordable = 8 -> batches_planned=8, budget large enough
        result_32 = estimate(
            plan=_make_plan(8),
            tier="high",
            cross_model_flag=False,
            agent_budget=900,
            verify_cap=0,
            fix_cap=0,
            overhead=0,
        )
        check(
            "waves_at_16_concurrency: total_agents=32 -> waves=2",
            result_32["total_agents"] == 32 and result_32["waves_at_16_concurrency"] == 2,
            str(result_32),
        )

        # total_agents == 33: batches_affordable*4 + overhead = 33 -> overhead=1, batches=8
        result_33 = estimate(
            plan=_make_plan(8),
            tier="high",
            cross_model_flag=False,
            agent_budget=900,
            verify_cap=0,
            fix_cap=0,
            overhead=1,
        )
        check(
            "waves_at_16_concurrency: total_agents=33 -> waves=3",
            result_33["total_agents"] == 33 and result_33["waves_at_16_concurrency"] == 3,
            str(result_33),
        )

        # --- Assertion 7: output is valid JSON, round-trips, all keys present ---
        proc = subprocess.run(
            [
                sys.executable,
                this_file,
                "--plan",
                str(plan10_path),
                "--effort-tier",
                "xhigh",
                "--cross-model",
            ],
            capture_output=True,
            text=True,
        )
        json_ok = False
        keys_ok = False
        detail = f"returncode={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}"
        if proc.returncode == 0:
            try:
                parsed = json.loads(proc.stdout)
                json_ok = True
                keys_ok = EXPECTED_OUTPUT_KEYS.issubset(set(parsed.keys()))
                detail = f"keys={sorted(parsed.keys())}"
            except json.JSONDecodeError as exc:
                detail = f"JSONDecodeError: {exc}; stdout={proc.stdout!r}"
        check(
            "CLI output is valid JSON round-tripping via json.loads with all Output keys present",
            json_ok and keys_ok,
            detail,
        )

    failing = [name for name, ok, _ in results if not ok]
    if failing:
        print(f"{len(failing)} FAILED: {len(failing)} failing")
        return 1
    print(f"ALL PASS: 0 failing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
