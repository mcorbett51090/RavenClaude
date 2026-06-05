#!/usr/bin/env python3
"""gamedev_budget.py — frame- and memory-budget calculator for game runtime work.

A *calculator, not a data source*: every input is supplied by the user; outputs
are decision-support, not a profile of the actual game. It removes arithmetic
error from three recurring runtime decisions and pairs with
``knowledge/gamedev-runtime-performance-decision-trees.md``:

  frame-budget   target FPS -> per-frame ms budget; classify a measured/percentile
                 frame time as under / at-risk / over budget, and report the
                 implied headroom.
  cpu-gpu        given measured CPU (main+render thread) ms and GPU ms for a
                 frame, report which side is the bottleneck and by how much
                 (the "is the GPU idle?" question, quantified).
  memory-budget  given a platform memory budget and a per-category breakdown,
                 report total vs budget, the dominant category, and per-category
                 share — the input to the memory-budget decision tree.

stdlib only (Python 3.8+). No third-party deps, no network, no file writes.

Examples:
  gamedev_budget.py frame-budget --fps 60 --frame-ms 18.5
  gamedev_budget.py frame-budget --fps 60 --frame-ms 18.5 --percentile p99
  gamedev_budget.py cpu-gpu --cpu-ms 19.0 --gpu-ms 8.0
  gamedev_budget.py memory-budget --budget-mb 2048 \\
      --category textures=900 --category meshes=350 --category audio=180 \\
      --category code=420 --category other=120
"""

from __future__ import annotations

import argparse
import sys

# Frame is "at risk" when within this fraction of the budget (e.g. >= 90%).
_AT_RISK_FRACTION = 0.90
# CPU/GPU are "balanced" when within this fraction of each other.
_BALANCED_FRACTION = 0.10


def _fmt(value: float, places: int = 2) -> str:
    """Format a float without trailing-zero noise."""
    return f"{value:.{places}f}".rstrip("0").rstrip(".")


def frame_budget(fps: float, frame_ms: float, percentile: str) -> tuple[str, list[str]]:
    """Classify a frame time against the per-frame ms budget for a target FPS."""
    if fps <= 0:
        raise ValueError("--fps must be positive")
    if frame_ms < 0:
        raise ValueError("--frame-ms must be non-negative")

    budget_ms = 1000.0 / fps
    headroom_ms = budget_ms - frame_ms
    used_fraction = frame_ms / budget_ms if budget_ms else 0.0

    if frame_ms > budget_ms:
        verdict = "OVER BUDGET"
        over_by = frame_ms - budget_ms
        note = (
            f"{percentile} frame time exceeds the budget by {_fmt(over_by)} ms "
            f"({_fmt(used_fraction * 100, 1)}% of budget). A frame is dropped — "
            "traverse the 'frame is over budget' tree: profile the CPU/GPU split "
            "and percentile before optimizing."
        )
    elif used_fraction >= _AT_RISK_FRACTION:
        verdict = "AT RISK"
        note = (
            f"{percentile} frame time is at {_fmt(used_fraction * 100, 1)}% of "
            f"the {_fmt(budget_ms)} ms budget — under budget but no safety margin. "
            "A small regression will start dropping frames."
        )
    else:
        verdict = "UNDER BUDGET"
        note = (
            f"{percentile} frame time uses {_fmt(used_fraction * 100, 1)}% of the "
            f"{_fmt(budget_ms)} ms budget — {_fmt(headroom_ms)} ms headroom."
        )

    lines = [
        f"Target frame rate : {_fmt(fps)} FPS",
        f"Per-frame budget  : {_fmt(budget_ms)} ms",
        f"Measured ({percentile}) : {_fmt(frame_ms)} ms",
        f"Headroom          : {_fmt(headroom_ms)} ms",
        f"Verdict           : {verdict}",
        "",
        f"Note: {note}",
        "Reminder: read the 99th-percentile / max frame time, not the average — "
        "a hitch is a tail-latency event the mean launders away.",
    ]
    return verdict, lines


def cpu_gpu(cpu_ms: float, gpu_ms: float) -> tuple[str, list[str]]:
    """Report which side (CPU vs GPU) bounds a frame, and by how much."""
    if cpu_ms < 0 or gpu_ms < 0:
        raise ValueError("--cpu-ms and --gpu-ms must be non-negative")

    frame_ms = max(cpu_ms, gpu_ms)
    diff = abs(cpu_ms - gpu_ms)
    larger = max(cpu_ms, gpu_ms)
    rel = diff / larger if larger else 0.0

    if rel <= _BALANCED_FRACTION:
        verdict = "BALANCED"
        note = (
            "CPU and GPU times are within "
            f"{_fmt(_BALANCED_FRACTION * 100, 0)}% of each other — neither side "
            "is clearly the bottleneck; optimize whichever is cheaper to move."
        )
    elif cpu_ms > gpu_ms:
        verdict = "CPU-BOUND"
        note = (
            f"CPU exceeds GPU by {_fmt(diff)} ms; the GPU is idle ~{_fmt(diff)} ms "
            "per frame. Chase CPU/render-thread levers (draw-call batching, jobify "
            "the hot path, kill per-frame allocation) — NOT poly/texture (GPU) cuts."
        )
    else:
        verdict = "GPU-BOUND"
        note = (
            f"GPU exceeds CPU by {_fmt(diff)} ms. Chase GPU levers "
            "(overdraw/resolution if fill-bound, LODs/shaders if geometry-bound) — "
            "the CPU has headroom."
        )

    lines = [
        f"CPU (main+render) : {_fmt(cpu_ms)} ms",
        f"GPU               : {_fmt(gpu_ms)} ms",
        f"Frame time (~max) : {_fmt(frame_ms)} ms",
        f"Verdict           : {verdict}",
        "",
        f"Note: {note}",
    ]
    return verdict, lines


def memory_budget(
    budget_mb: float, categories: dict[str, float]
) -> tuple[str, list[str]]:
    """Report total vs budget and the dominant category from a breakdown."""
    if budget_mb <= 0:
        raise ValueError("--budget-mb must be positive")
    if not categories:
        raise ValueError("at least one --category NAME=MB is required")
    if any(mb < 0 for mb in categories.values()):
        raise ValueError("category values must be non-negative")

    total = sum(categories.values())
    used_fraction = total / budget_mb
    dominant = max(categories, key=lambda k: categories[k])

    if total > budget_mb:
        verdict = "OVER BUDGET"
        note = (
            f"Over the {_fmt(budget_mb)} MB budget by {_fmt(total - budget_mb)} MB. "
            f"'{dominant}' dominates — attack that category's lever "
            "(compress/stream/LOD) or tier the budget per device; see the "
            "memory-budget tree."
        )
    elif used_fraction >= _AT_RISK_FRACTION:
        verdict = "AT RISK"
        note = (
            f"At {_fmt(used_fraction * 100, 1)}% of budget — no margin for "
            f"content growth. '{dominant}' is the largest category."
        )
    else:
        verdict = "UNDER BUDGET"
        note = (
            f"Using {_fmt(used_fraction * 100, 1)}% of the {_fmt(budget_mb)} MB "
            f"budget; '{dominant}' is the largest category."
        )

    lines = [
        f"Memory budget : {_fmt(budget_mb)} MB",
        f"Total used    : {_fmt(total)} MB ({_fmt(used_fraction * 100, 1)}%)",
        f"Dominant      : {dominant} ({_fmt(categories[dominant])} MB)",
        f"Verdict       : {verdict}",
        "",
        "Breakdown:",
    ]
    for name in sorted(categories, key=lambda k: categories[k], reverse=True):
        mb = categories[name]
        share = mb / total * 100 if total else 0.0
        lines.append(f"  {name:<12} {_fmt(mb):>10} MB  ({_fmt(share, 1)}%)")
    lines.extend(["", f"Note: {note}"])
    return verdict, lines


def _parse_category(values: list[str]) -> dict[str, float]:
    """Parse repeated ``NAME=MB`` flags into a dict, last-wins on duplicates."""
    out: dict[str, float] = {}
    for raw in values:
        if "=" not in raw:
            raise ValueError(f"--category must be NAME=MB, got: {raw!r}")
        name, _, mb_str = raw.partition("=")
        name = name.strip()
        if not name:
            raise ValueError(f"--category name must be non-empty, got: {raw!r}")
        try:
            out[name] = float(mb_str)
        except ValueError as exc:
            raise ValueError(f"--category value must be a number, got: {raw!r}") from exc
    return out


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gamedev_budget.py",
        description="Frame- and memory-budget calculator (decision-support; "
        "you supply every input).",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    p_frame = sub.add_parser("frame-budget", help="FPS target -> ms budget; classify a frame time")
    p_frame.add_argument("--fps", type=float, required=True, help="target frame rate")
    p_frame.add_argument("--frame-ms", type=float, required=True, help="measured frame time (ms)")
    p_frame.add_argument(
        "--percentile",
        default="frame",
        help="label for the measured value (e.g. p99, max, avg) — display only",
    )

    p_cg = sub.add_parser("cpu-gpu", help="which side bounds the frame")
    p_cg.add_argument("--cpu-ms", type=float, required=True, help="CPU main+render thread time (ms)")
    p_cg.add_argument("--gpu-ms", type=float, required=True, help="GPU time (ms)")

    p_mem = sub.add_parser("memory-budget", help="total vs budget + dominant category")
    p_mem.add_argument("--budget-mb", type=float, required=True, help="platform memory budget (MB)")
    p_mem.add_argument(
        "--category",
        action="append",
        default=[],
        metavar="NAME=MB",
        help="per-category usage in MB; repeatable (e.g. --category textures=900)",
    )
    return parser


def main(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.mode == "frame-budget":
            _, lines = frame_budget(args.fps, args.frame_ms, args.percentile)
        elif args.mode == "cpu-gpu":
            _, lines = cpu_gpu(args.cpu_ms, args.gpu_ms)
        elif args.mode == "memory-budget":
            categories = _parse_category(args.category)
            _, lines = memory_budget(args.budget_mb, categories)
        else:  # pragma: no cover - argparse guards this
            parser.error(f"unknown mode: {args.mode}")
            return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print("\n".join(lines))
    print(
        "\n(Decision-support only — validate against the actual game's profile; "
        "this is a calculator, not a measurement.)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
