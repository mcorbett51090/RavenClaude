#!/usr/bin/env python3
"""block_planner.py — partition a large repo-review plan into safely-sized blocks.

/repo-review's Workflow-tool fan-out (repo-sweep.workflow.js) is bounded by the
Workflow tool's own hard cap of 1,000 agent() calls PER INVOCATION. A cold-cache
review of a plan with hundreds of batches can exceed that cap even at a
correctly-sized effort tier (see estimate_cost.py's own module docstring for
the real 2026-09-09 incident this guards against). block_planner.py answers the
question estimate_cost.py deliberately does NOT: when one invocation genuinely
cannot cover the whole plan, how should the plan be SPLIT across multiple
Workflow invocations that still add up to complete, non-overlapping coverage?

Mechanism (see repo-sweep.workflow.js's args.batchIds / args.finalizeBlock):
every block invocation shares the SAME args.runId (and therefore the same
findings dir); a "review-only" block reviews its own slice of batch ids and
returns; the single "finalize" block reviews its own (smaller) slice and THEN
runs Merge -> Verify -> Fix -> Report (-> further --converge iterations, if
requested) over the FULL shared findings dir — by the time it runs, every
review-only block must already have completed and written its shards.

This tool is deliberately self-tested only (`--self-test`), NOT a formal
scripts/audit-gates.sh gate — the same tier as this skill's sibling
forge-route.py/forge-worktree.sh-style helpers and dependency-sweep.py. It
reuses estimate_cost.py's cardinality formula (imported, not re-derived) so
the two can never silently drift apart the way this repo's SEVERITY_RANK
vocabulary once did across two independently-authored copies.

Stdlib-only. No model calls, no network.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Reuse estimate_cost.py's own cardinality formula + tier tables rather than
# re-deriving them — see the module docstring above for why.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimate_cost  # noqa: E402

# Leaves headroom under estimate_cost.WORKFLOW_AGENT_CALL_HARD_CAP (1000) for
# every block — a block is sized to THIS ceiling, never to the raw hard cap,
# so estimation noise (a slightly-off review_agents_per_batch assumption, an
# extra agent() the workflow issues that this planner doesn't model) has room
# to be wrong without tipping a single invocation over the real, unforgiving
# limit.
DEFAULT_SAFE_CEILING = 700

# The Map phase's own overhead per invocation (repo_map.py's agent() call +
# the best-effort estimate_cost.py agent() call) — every block invocation
# pays this once, review-only or finalize.
MAP_OVERHEAD = 3

# A conservative, DOCUMENTED-AS-HEURISTIC fixed reserve subtracted from the
# finalize block's capacity when the caller intends to pass args.converge to
# that block. Iteration>=2 of a --converge run (since the workflow's own
# targeted-re-review fix) costs one resolveBatchesForFiles() agent() call
# plus review_agents_per_batch_with_cache_checks() per batch a Fix pass
# actually touched -- a number that depends on how many files get fixed each
# pass and cannot be known in advance. This reserve is NOT a proof the
# finalize block will fit; it is a deliberately generous fixed buffer sized
# for "a handful of re-reviewed batches across a few more iterations", named
# honestly rather than modeled precisely.
CONVERGE_RESERVE = 150


class BlockPlanError(Exception):
    """Raised when the plan cannot be safely partitioned (see message)."""


def _review_agents_per_batch_with_cache_checks(tier: str, cross_model_flag: bool) -> float:
    """The exact per-batch cost estimate_cost.py's `estimate()` uses, at the
    cold-cache default (cache_hit_rate=0.0) — the correct assumption for a
    first-ever sweep of a given scope, same as estimate_cost.py's own
    default. Delegates to estimate_cost.py's own resolver functions so this
    can never independently drift from what the real workflow actually
    dispatches.
    """
    dims = estimate_cost.TIER_DIMENSIONS[tier]
    cross_model_active = estimate_cost.resolve_cross_model(tier, cross_model_flag)
    _label, review_agents_per_batch = estimate_cost.compute_models_per_dimension_label(
        tier, cross_model_active, dims
    )
    return review_agents_per_batch * 2.0


def plan_blocks(
    plan: dict[str, Any],
    tier: str,
    cross_model: bool = False,
    safe_ceiling: int = DEFAULT_SAFE_CEILING,
    verify_cap: int | None = None,
    fix_cap: int | None = None,
    overhead: int = 6,
    converge: bool = False,
) -> dict[str, Any]:
    if tier in estimate_cost.REFUSED_TIERS:
        raise BlockPlanError(
            f"block_planner refuses effort tier {tier!r} — same floor as estimate_cost.py "
            "(minimum high; low/medium are refused for a whole-repo sweep)."
        )
    if tier not in estimate_cost.TIER_DIMENSIONS:
        raise BlockPlanError(
            f"unknown effort tier: {tier!r} (expected one of {estimate_cost.VALID_TIERS})"
        )

    v_max = estimate_cost.TIER_VERIFY_CAP_DEFAULT[tier] if verify_cap is None else verify_cap
    k_max = estimate_cost.TIER_FIX_CAP_DEFAULT[tier] if fix_cap is None else fix_cap
    o = overhead
    converge_reserve = CONVERGE_RESERVE if converge else 0

    r = _review_agents_per_batch_with_cache_checks(tier, cross_model)

    batches = plan.get("batches", [])
    batch_ids = [b["id"] for b in batches]
    total_batches = len(batch_ids)

    # A review-only block pays ONLY r * block_size + MAP_OVERHEAD (it never
    # reaches Merge/Verify/Fix). The finalize block ALSO reserves v_max +
    # k_max + o (+ converge_reserve if a converge loop will run inside it),
    # since it runs the full pipeline over its own slice plus every
    # already-reviewed batch's still-valid shard.
    non_finalize_capacity = _capacity(safe_ceiling - MAP_OVERHEAD, r, total_batches)
    finalize_reserved = MAP_OVERHEAD + v_max + k_max + o + converge_reserve
    finalize_available = safe_ceiling - finalize_reserved

    # _capacity() floors its result at 1 (a block always covers at least one
    # batch once it exists), so it can never itself signal "nothing fits at
    # all" -- that check has to happen against the raw available budget,
    # before clamping, or an impossibly small safe_ceiling would silently
    # produce a 1-batch finalize block instead of raising.
    if r > 0 and finalize_available < r:
        raise BlockPlanError(
            f"safe_ceiling={safe_ceiling} leaves no room for even a 1-batch finalize block once "
            f"verify_cap={v_max} + fix_cap={k_max} + overhead={o} + map_overhead={MAP_OVERHEAD}"
            f"{f' + converge_reserve={converge_reserve}' if converge_reserve else ''} are reserved "
            f"(available={finalize_available}, per-batch cost={r}). "
            "Raise --safe-ceiling, or lower --verify-cap/--fix-cap."
        )

    finalize_capacity = _capacity(finalize_available, r, total_batches)

    if total_batches <= finalize_capacity:
        # Fits in one shot at this tier — no blocks needed. The caller should
        # invoke repo-sweep.workflow.js normally (no args.batchIds /
        # args.finalizeBlock at all), which stays the well-tested single-shot
        # path this skill already runs against real repos.
        return {
            "schema_version": 1,
            "needs_blocks": False,
            "total_batches": total_batches,
            "effort_tier": tier,
            "cross_model": cross_model,
            "safe_ceiling": safe_ceiling,
            "non_finalize_capacity": non_finalize_capacity,
            "finalize_capacity": finalize_capacity,
            "blocks": [],
        }

    # Reserve the LAST slice (in the plan's own risk-ranked order) for the
    # finalize block, sized to finalize_capacity; everything before it is
    # split into review-only blocks sized to non_finalize_capacity. This
    # keeps the highest-risk batches in block-1 (reviewed first), and the
    # finalize block's slice is whatever is left over — never larger than
    # finalize_capacity by construction.
    finalize_slice = batch_ids[-finalize_capacity:]
    remaining = batch_ids[: total_batches - len(finalize_slice)]

    blocks: list[dict[str, Any]] = []
    idx = 1
    pos = 0
    while pos < len(remaining):
        chunk = remaining[pos : pos + non_finalize_capacity]
        blocks.append(
            {
                "block_id": f"block-{idx}",
                "role": "review-only",
                "batch_ids": chunk,
                "status": "pending",
            }
        )
        pos += non_finalize_capacity
        idx += 1
    blocks.append(
        {
            "block_id": f"block-{idx}",
            "role": "finalize",
            "batch_ids": finalize_slice,
            "status": "pending",
        }
    )

    # Coverage-completeness invariant: every batch id in the plan appears in
    # EXACTLY one block — no gaps, no duplicates. A violation here is a bug
    # in this function, not a caller error, so it raises rather than
    # returning a silently-incomplete manifest.
    all_ids_in_blocks = [bid for b in blocks for bid in b["batch_ids"]]
    if sorted(all_ids_in_blocks) != sorted(batch_ids):
        raise BlockPlanError("internal error: block partition does not cover the plan's batch_ids")
    if len(all_ids_in_blocks) != len(set(all_ids_in_blocks)):
        raise BlockPlanError(
            "internal error: block partition assigned a batch id to more than one block"
        )
    if blocks[-1]["role"] != "finalize":
        raise BlockPlanError("internal error: the last block must be the finalize block")

    return {
        "schema_version": 1,
        "needs_blocks": True,
        "total_batches": total_batches,
        "effort_tier": tier,
        "cross_model": cross_model,
        "safe_ceiling": safe_ceiling,
        "non_finalize_capacity": non_finalize_capacity,
        "finalize_capacity": finalize_capacity,
        "blocks": blocks,
    }


def _capacity(available: float, per_batch_cost: float, cap: int) -> int:
    if per_batch_cost <= 0:
        return cap
    return max(1, min(cap, int(available // per_batch_cost)))


def build_manifest(
    plan_path: str,
    plan: dict[str, Any],
    tier: str,
    cross_model: bool,
    safe_ceiling: int,
    verify_cap: int | None,
    fix_cap: int | None,
    overhead: int,
    converge: bool,
    run_id: str | None,
) -> dict[str, Any]:
    result = plan_blocks(
        plan,
        tier=tier,
        cross_model=cross_model,
        safe_ceiling=safe_ceiling,
        verify_cap=verify_cap,
        fix_cap=fix_cap,
        overhead=overhead,
        converge=converge,
    )
    resolved_run_id = run_id or f"repo-sweep-blocks-{_stamp()}"
    return {
        "schema_version": 1,
        "created_at": _now_iso(),
        "plan_path": plan_path,
        "run_id": resolved_run_id,
        "converge_reserved": converge,
        **result,
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", help="path to a review-plan.json produced by repo_map.py")
    parser.add_argument(
        "--effort-tier", choices=list(estimate_cost.VALID_TIERS), help="high|xhigh|max|ultra"
    )
    parser.add_argument(
        "--cross-model", action="store_true", help="mirrors estimate_cost.py's flag"
    )
    parser.add_argument(
        "--safe-ceiling",
        type=int,
        default=DEFAULT_SAFE_CEILING,
        help=f"per-invocation agent-call budget to plan against (default {DEFAULT_SAFE_CEILING}, "
        f"well under the Workflow tool's real {estimate_cost.WORKFLOW_AGENT_CALL_HARD_CAP}-call cap)",
    )
    parser.add_argument("--verify-cap", type=int, default=None)
    parser.add_argument("--fix-cap", type=int, default=None)
    parser.add_argument("--overhead", type=int, default=6)
    parser.add_argument(
        "--converge",
        action="store_true",
        help="reserve extra headroom in the finalize block for a --converge loop (heuristic, see "
        "CONVERGE_RESERVE)",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="run_id every block invocation must share; generated if omitted",
    )
    parser.add_argument("--out", default=None, help="write the manifest JSON here; default: stdout")
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if not args.plan or not args.effort_tier:
        parser.error("--plan and --effort-tier are required (or pass --self-test)")

    try:
        with open(args.plan, encoding="utf-8") as f:
            plan = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: failed to read plan {args.plan!r}: {exc}", file=sys.stderr)
        return 2

    try:
        manifest = build_manifest(
            plan_path=args.plan,
            plan=plan,
            tier=args.effort_tier,
            cross_model=args.cross_model,
            safe_ceiling=args.safe_ceiling,
            verify_cap=args.verify_cap,
            fix_cap=args.fix_cap,
            overhead=args.overhead,
            converge=args.converge,
            run_id=args.run_id,
        )
    except BlockPlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(manifest, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _make_plan(n: int) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "batches": [{"id": f"b{i:03d}", "files": [f"f{i}.py"]} for i in range(n)],
    }


def run_self_test() -> int:
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "ok" if cond else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            failures.append(name)

    # --- 1: low/medium refused ---
    for tier in ("low", "medium"):
        try:
            plan_blocks(_make_plan(10), tier=tier)
            check(f"tier={tier} is refused", False)
        except BlockPlanError:
            check(f"tier={tier} is refused", True)

    # --- 2: a small plan needs no blocks ---
    small = plan_blocks(_make_plan(5), tier="high")
    check(
        "small plan (5 batches, high tier): needs_blocks is False and blocks is empty",
        small["needs_blocks"] is False and small["blocks"] == [],
        str(small),
    )

    # --- 3: a huge plan needs blocks, and the partition is complete + non-overlapping ---
    huge_plan = _make_plan(500)
    huge = plan_blocks(huge_plan, tier="xhigh", safe_ceiling=700)
    check("huge plan (500 batches, xhigh): needs_blocks is True", huge["needs_blocks"] is True)
    all_ids = [bid for b in huge["blocks"] for bid in b["batch_ids"]]
    plan_ids = [b["id"] for b in huge_plan["batches"]]
    check(
        "huge plan: block partition covers every batch id exactly once (no gaps, no dupes)",
        sorted(all_ids) == sorted(plan_ids) and len(all_ids) == len(set(all_ids)),
        f"len(all_ids)={len(all_ids)} len(plan_ids)={len(plan_ids)}",
    )
    check(
        "huge plan: exactly ONE finalize block, and it is the LAST block",
        sum(1 for b in huge["blocks"] for x in [b] if x["role"] == "finalize") == 1
        and huge["blocks"][-1]["role"] == "finalize",
        str([b["role"] for b in huge["blocks"]]),
    )
    check(
        "huge plan: every review-only block respects non_finalize_capacity",
        all(
            len(b["batch_ids"]) <= huge["non_finalize_capacity"]
            for b in huge["blocks"]
            if b["role"] == "review-only"
        ),
    )
    check(
        "huge plan: the finalize block respects finalize_capacity",
        len(huge["blocks"][-1]["batch_ids"]) <= huge["finalize_capacity"],
    )
    check(
        "huge plan: the highest-risk (earliest-in-plan) batches land in block-1",
        huge["blocks"][0]["batch_ids"][0] == plan_ids[0],
    )

    # --- 4: determinism — two runs, byte-identical manifest (modulo run_id/created_at) ---
    m1 = build_manifest(
        "plan.json", huge_plan, "xhigh", False, 700, None, None, 6, False, run_id="fixed-run-id"
    )
    m2 = build_manifest(
        "plan.json", huge_plan, "xhigh", False, 700, None, None, 6, False, run_id="fixed-run-id"
    )
    m1_stable = {k: v for k, v in m1.items() if k != "created_at"}
    m2_stable = {k: v for k, v in m2.items() if k != "created_at"}
    check(
        "determinism: two runs with the same run_id produce identical blocks",
        json.dumps(m1_stable, sort_keys=True) == json.dumps(m2_stable, sort_keys=True),
    )

    # --- 5: converge=True reserves more (finalize_capacity shrinks or stays equal) ---
    no_converge = plan_blocks(huge_plan, tier="xhigh", safe_ceiling=700, converge=False)
    with_converge = plan_blocks(huge_plan, tier="xhigh", safe_ceiling=700, converge=True)
    check(
        "converge=True never INCREASES finalize_capacity vs converge=False",
        with_converge["finalize_capacity"] <= no_converge["finalize_capacity"],
        f"converge={with_converge['finalize_capacity']} no_converge={no_converge['finalize_capacity']}",
    )

    # --- 6: an impossibly small safe_ceiling raises cleanly ---
    try:
        plan_blocks(huge_plan, tier="ultra", safe_ceiling=1)
        check("an impossibly small safe_ceiling raises BlockPlanError", False)
    except BlockPlanError:
        check("an impossibly small safe_ceiling raises BlockPlanError", True)

    # --- 7: a run_id is auto-generated when omitted, and differs run to run ---
    auto1 = build_manifest(
        "plan.json", _make_plan(5), "high", False, 700, None, None, 6, False, None
    )
    check(
        "run_id is auto-generated when omitted",
        isinstance(auto1["run_id"], str) and auto1["run_id"].startswith("repo-sweep-blocks-"),
        auto1["run_id"],
    )

    # --- 8: CLI round-trip — valid JSON, exit 0, run_id honored ---
    import subprocess
    import tempfile

    this_file = str(Path(__file__).resolve())
    with tempfile.TemporaryDirectory() as tmp:
        plan_path = Path(tmp) / "plan.json"
        plan_path.write_text(json.dumps(_make_plan(500)), encoding="utf-8")
        out_path = Path(tmp) / "manifest.json"
        proc = subprocess.run(
            [
                sys.executable,
                this_file,
                "--plan",
                str(plan_path),
                "--effort-tier",
                "xhigh",
                "--run-id",
                "cli-test-run",
                "--out",
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )
        cli_ok = proc.returncode == 0
        manifest_ok = False
        if cli_ok and out_path.exists():
            try:
                parsed = json.loads(out_path.read_text(encoding="utf-8"))
                manifest_ok = (
                    parsed.get("run_id") == "cli-test-run" and parsed.get("needs_blocks") is True
                )
            except json.JSONDecodeError:
                manifest_ok = False
        check(
            "CLI: exits 0 and writes a valid manifest honoring --run-id",
            cli_ok and manifest_ok,
            f"returncode={proc.returncode} stderr={proc.stderr!r}",
        )

        # --- 8b: CLI-level low/medium refusal exits 2 ---
        proc_bad = subprocess.run(
            [sys.executable, this_file, "--plan", str(plan_path), "--effort-tier", "low"],
            capture_output=True,
            text=True,
        )
        check(
            "CLI: --effort-tier low exits 2 with a stderr message",
            proc_bad.returncode == 2 and len(proc_bad.stderr.strip()) > 0,
            f"returncode={proc_bad.returncode}",
        )

    if failures:
        print(f"\n{len(failures)} FAILED: {len(failures)} failing")
        return 1
    print("\nALL PASS: 0 failing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
