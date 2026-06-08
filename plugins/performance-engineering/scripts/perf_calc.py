#!/usr/bin/env python3
"""Performance / capacity calculator — performance-engineering plugin.

Stdlib only (Python 3.8+). Removes arithmetic error from three recurring
performance-engineering decisions: solving Little's law for whichever term you
lack, sizing the concurrency/instance count a target RPS demands at a measured
per-request latency, and reducing a list of latency samples to the percentiles
that actually gate a release. It is a *calculator, not a data source* — the
user supplies every input; outputs are decision-support, not a guarantee that
the system will hold the number.

Subcommands:
  littles-law   solve L = lambda * W for the one term you omit (give the other
                two). L = concurrency (in-flight requests), lambda = arrival
                rate (req/s), W = mean residence time (seconds).
  capacity      target RPS + per-request latency + headroom -> the required
                concurrency (Little's law) and the instance count, sized below
                the knee with explicit failover/growth headroom.
  percentiles   a list of latency samples -> p50/p90/p95/p99 (+ min/max/mean)
                via nearest-rank, so the tail is read off the data, not a mean.

Method references: Little's law (L = lambda * W). Percentiles use the
nearest-rank method (no interpolation) so a reported percentile is always an
observed sample. Verify the conventions against your tool before quoting.

Examples:
  perf_calc.py littles-law --lam 5000 --w 0.04
  perf_calc.py littles-law --l 200 --lam 5000
  perf_calc.py capacity --target-rps 5000 --latency-ms 40 --per-instance 50 --headroom 0.3
  perf_calc.py percentiles --samples 12,18,21,40,55,90,120,400
"""
from __future__ import annotations

import argparse
import math
import sys


def littles_law(
    lam: float | None,
    w: float | None,
    el: float | None,
) -> dict:
    """Solve L = lambda * W for the single omitted term.

    Exactly one of --l / --lam / --w must be left out; the other two are given.
    L = concurrency (in-flight), lambda = arrival rate (req/s), W = mean
    residence time (seconds).
    """
    given = [x is not None for x in (el, lam, w)]
    if sum(given) != 2:
        raise ValueError(
            "supply exactly two of --l, --lam, --w; the third is computed"
        )
    if lam is None:
        if w is None or w <= 0:
            raise ValueError("--w must be positive to solve for --lam")
        if el is None or el < 0:
            raise ValueError("--l must be non-negative")
        lam = el / w
        solved = "lambda_req_per_s"
    elif w is None:
        if lam <= 0:
            raise ValueError("--lam must be positive to solve for --w")
        if el is None or el < 0:
            raise ValueError("--l must be non-negative")
        w = el / lam
        solved = "w_seconds"
    else:  # el is None
        if lam < 0 or w < 0:
            raise ValueError("--lam and --w must be non-negative")
        el = lam * w
        solved = "l_concurrency"
    return {
        "solved_for": solved,
        "l_concurrency": el,
        "lambda_req_per_s": lam,
        "w_seconds": w,
        "note": "L = lambda * W (Little's law). W is mean residence time, "
        "not just service time — it includes queueing.",
    }


def capacity(
    target_rps: float,
    latency_ms: float,
    per_instance: float | None,
    headroom: float,
) -> dict:
    """Required concurrency + instance count for a target RPS.

    Concurrency comes straight from Little's law (L = lambda * W) at the target
    arrival rate and the measured per-request latency. Headroom is applied as a
    de-rate on per-instance capacity (size below the knee), so the instance
    count survives a node loss and growth.
    """
    if target_rps <= 0:
        raise ValueError("--target-rps must be positive")
    if latency_ms <= 0:
        raise ValueError("--latency-ms must be positive")
    if not 0 <= headroom < 1:
        raise ValueError("--headroom must be a fraction in [0, 1)")

    w_seconds = latency_ms / 1000.0
    required_concurrency = target_rps * w_seconds

    result = {
        "target_rps": target_rps,
        "latency_ms": latency_ms,
        "w_seconds": w_seconds,
        "required_concurrency": required_concurrency,
        "headroom_fraction": headroom,
    }

    if per_instance is not None:
        if per_instance <= 0:
            raise ValueError("--per-instance must be positive")
        # De-rate the measured per-instance ceiling by the headroom fraction so
        # we plan below the knee, then size the fleet against the de-rated rate.
        usable_per_instance = per_instance * (1 - headroom)
        instances = math.ceil(target_rps / usable_per_instance)
        result.update(
            {
                "per_instance_max_rps": per_instance,
                "usable_per_instance_rps": usable_per_instance,
                "required_instances": instances,
                "planned_capacity_rps": instances * usable_per_instance,
                "verdict": _capacity_verdict(headroom),
            }
        )
    else:
        result["note"] = (
            "supply --per-instance (measured saturation RPS per instance) to "
            "get an instance count; without it only the Little's-law "
            "concurrency is computed."
        )
    return result


def _capacity_verdict(headroom: float) -> str:
    if headroom == 0:
        return "no headroom — planning to the knee; one node loss tips it over"
    if headroom < 0.2:
        return "thin headroom — covers minor bursts, not a node loss + growth"
    if headroom <= 0.4:
        return "healthy headroom — typical failover + growth band"
    return "generous headroom — confirm the over-provision is intentional"


def percentiles(samples: list[float]) -> dict:
    """p50/p90/p95/p99 (+ min/max/mean) via nearest-rank.

    Nearest-rank means every reported percentile is an actual observed sample —
    no interpolation invents a value between two measurements. Report the tail,
    never the mean, as the release gate.
    """
    if not samples:
        raise ValueError("--samples must contain at least one value")
    if any(s < 0 for s in samples):
        raise ValueError("latency samples must be non-negative")
    ordered = sorted(samples)
    n = len(ordered)

    def nearest_rank(p: float) -> float:
        # rank = ceil(p/100 * n), clamped into [1, n]; index is rank-1.
        rank = math.ceil((p / 100.0) * n)
        rank = max(1, min(rank, n))
        return ordered[rank - 1]

    return {
        "count": n,
        "min": ordered[0],
        "max": ordered[-1],
        "mean": sum(ordered) / n,
        "p50": nearest_rank(50),
        "p90": nearest_rank(90),
        "p95": nearest_rank(95),
        "p99": nearest_rank(99),
        "note": "nearest-rank (no interpolation) — each percentile is an "
        "observed sample. Gate releases on p95/p99, never the mean.",
    }


def _print(d: dict, indent: int = 0) -> None:
    pad = "  " * indent
    for k, v in d.items():
        if isinstance(v, list):
            print(f"{pad}{k}:")
            for item in v:
                if isinstance(item, dict):
                    print(f"{pad}  -")
                    _print(item, indent + 2)
                else:
                    print(f"{pad}  - {item}")
        elif isinstance(v, dict):
            print(f"{pad}{k}:")
            _print(v, indent + 1)
        elif isinstance(v, float):
            print(f"{pad}{k}: {v:.4g}")
        else:
            print(f"{pad}{k}: {v}")


def _parse_samples(raw: str) -> list[float]:
    parts = [p.strip() for p in raw.replace(",", " ").split()]
    return [float(p) for p in parts if p]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="perf_calc.py",
        description="Performance / capacity calculator (decision-support only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ll = sub.add_parser(
        "littles-law",
        help="solve L = lambda * W for the omitted term (give the other two)",
    )
    ll.add_argument("--l", type=float, default=None, help="concurrency / in-flight requests")
    ll.add_argument("--lam", type=float, default=None, help="arrival rate lambda (req/s)")
    ll.add_argument("--w", type=float, default=None, help="mean residence time W (seconds)")

    cap = sub.add_parser(
        "capacity",
        help="target RPS + per-req latency + headroom -> concurrency + instances",
    )
    cap.add_argument("--target-rps", type=float, required=True, help="target arrival rate (req/s)")
    cap.add_argument("--latency-ms", type=float, required=True, help="per-request residence time (ms)")
    cap.add_argument(
        "--per-instance",
        type=float,
        default=None,
        help="measured saturation throughput per instance (req/s); omit for concurrency only",
    )
    cap.add_argument(
        "--headroom",
        type=float,
        default=0.3,
        help="failover/growth headroom as a fraction in [0,1) (default 0.3)",
    )

    pct = sub.add_parser(
        "percentiles",
        help="latency samples -> p50/p90/p95/p99 (+ min/max/mean), nearest-rank",
    )
    pct.add_argument(
        "--samples",
        type=str,
        required=True,
        help="comma- or space-separated latency samples, e.g. 12,18,21,40",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "littles-law":
            result = littles_law(args.lam, args.w, args.l)
        elif args.command == "capacity":
            result = capacity(args.target_rps, args.latency_ms, args.per_instance, args.headroom)
        elif args.command == "percentiles":
            result = percentiles(_parse_samples(args.samples))
        else:  # pragma: no cover - argparse enforces choices
            parser.error(f"unknown command {args.command}")
            return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
