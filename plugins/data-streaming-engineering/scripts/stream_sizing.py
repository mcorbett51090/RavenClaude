#!/usr/bin/env python3
"""stream_sizing.py — streaming capacity sizing calculator (stdlib only, Python 3.8+).

Removes arithmetic error from three recurring streaming-sizing decisions. It is a
*calculator, not a data source*: the user supplies every input; outputs are
decision-support, not a guarantee. Re-verify broker/cluster limits against the
vendor before provisioning ([verify-at-use]).

Modes:
  partitions      Minimum partition count for a throughput target, from per-partition
                  consumer throughput and a headroom factor. Reports the parallelism
                  ceiling (one consumer per partition) and a skew warning.
  poll-budget     Whether a consumer's per-poll work fits inside max.poll.interval.ms.
                  Guards the rebalance-storm failure mode (handler slower than the
                  poll-interval deadline). Suggests a safe max.poll.records.
  watermark       Translate an observed event-time lateness distribution into a
                  watermark bound (p99) and the latency cost it implies, plus the
                  allowed-lateness grace for the tail.

Usage:
  stream_sizing.py partitions  --target-msgs-per-sec 40000 --per-consumer-msgs-per-sec 5000 \\
                               [--headroom 1.5] [--max-skew-share 0.6]
  stream_sizing.py poll-budget --per-record-ms 30 --max-poll-records 500 \\
                               [--max-poll-interval-ms 300000] [--margin 0.7]
  stream_sizing.py watermark   --p50-lateness-ms 1500 --p99-lateness-ms 90000 \\
                               [--max-lateness-ms 600000]

All outputs are illustrative; validate against your cluster's measured numbers.
"""
from __future__ import annotations

import argparse
import sys


def size_partitions(
    target_mps: float,
    per_consumer_mps: float,
    headroom: float,
    max_skew_share: float,
) -> int:
    """Print a minimum partition count for a throughput target and return it."""
    if target_mps <= 0 or per_consumer_mps <= 0:
        print("error: throughput values must be positive", file=sys.stderr)
        return 2
    if headroom < 1.0:
        print("error: --headroom must be >= 1.0 (1.0 = no spare capacity)", file=sys.stderr)
        return 2

    effective_target = target_mps * headroom
    # Ceiling division without importing math.
    needed = int(-(-effective_target // per_consumer_mps))
    needed = max(needed, 1)

    print("=== Partition / parallelism sizing ===")
    print(f"  Target throughput:        {target_mps:,.0f} msg/s")
    print(f"  Headroom factor:          {headroom:.2f}x  -> design for {effective_target:,.0f} msg/s")
    print(f"  Per-consumer throughput:  {per_consumer_mps:,.0f} msg/s")
    print(f"  --> minimum partitions:   {needed}")
    print(f"      (parallelism ceiling is {needed} consumers; more than that sit idle)")
    print()
    print("  Notes:")
    print("   - Order is per-partition. Pick the partition KEY for the ordering you need;")
    print("     this count only spreads DISTINCT keys, it cannot split one hot key.")
    if max_skew_share > 0:
        hot_partition_load = effective_target * max_skew_share
        print(
            f"   - Skew check: if one key is ~{max_skew_share * 100:.0f}% of traffic, its single"
        )
        print(
            f"     partition carries ~{hot_partition_load:,.0f} msg/s alone"
            f" (vs {per_consumer_mps:,.0f} per consumer)."
        )
        if hot_partition_load > per_consumer_mps:
            print(
                "     WARNING: that exceeds one consumer's throughput — re-key at a finer"
            )
            print("     ordering granularity or salt the hot key (see partition-skew scenario).")
    print("   - Partition count is hard to change later; size for the busiest key, not the average.")
    return 0


def poll_budget(
    per_record_ms: float,
    max_poll_records: int,
    max_poll_interval_ms: float,
    margin: float,
) -> int:
    """Check that a poll batch is processable inside max.poll.interval.ms."""
    if per_record_ms <= 0 or max_poll_records <= 0:
        print("error: --per-record-ms and --max-poll-records must be positive", file=sys.stderr)
        return 2
    if not 0 < margin <= 1.0:
        print("error: --margin must be in (0, 1.0]", file=sys.stderr)
        return 2

    batch_ms = per_record_ms * max_poll_records
    budget_ms = max_poll_interval_ms * margin
    safe_records = int(budget_ms // per_record_ms)
    safe_records = max(safe_records, 1)

    print("=== Consumer poll-budget check ===")
    print(f"  Per-record processing time: {per_record_ms:,.1f} ms")
    print(f"  max.poll.records:           {max_poll_records}")
    print(f"  Worst-case batch time:      {batch_ms:,.0f} ms")
    print(f"  max.poll.interval.ms:       {max_poll_interval_ms:,.0f} ms")
    print(f"  Usable budget ({margin:.0%} margin):  {budget_ms:,.0f} ms")
    print()
    if batch_ms <= budget_ms:
        print("  OK: a full batch fits inside the poll interval with margin.")
    else:
        print("  RISK: a full batch can EXCEED the poll interval -> broker evicts the")
        print("        consumer -> rebalance storm (see consumer-lag-rebalance-storm scenario).")
        print(f"  --> lower max.poll.records to <= {safe_records}, AND/OR")
        print("      raise max.poll.interval.ms, AND/OR get slow I/O off the poll loop")
        print("      (batch/async the downstream call). Adding consumers does NOT fix this.")
    return 0


def watermark(p50_ms: float, p99_ms: float, max_ms: float) -> int:
    """Translate a lateness distribution into watermark + allowed-lateness guidance."""
    if p99_ms < p50_ms:
        print("error: --p99-lateness-ms must be >= --p50-lateness-ms", file=sys.stderr)
        return 2
    if max_ms < p99_ms:
        print("error: --max-lateness-ms must be >= --p99-lateness-ms", file=sys.stderr)
        return 2

    allowed_lateness_ms = max_ms - p99_ms

    print("=== Watermark / late-data sizing ===")
    print(f"  Observed lateness p50:  {p50_ms:,.0f} ms")
    print(f"  Observed lateness p99:  {p99_ms:,.0f} ms")
    print(f"  Observed max lateness:  {max_ms:,.0f} ms")
    print()
    print(f"  --> watermark bound (out-of-orderness): ~{p99_ms:,.0f} ms (size to p99)")
    print(f"      => adds ~{p99_ms / 1000:,.1f} s of window-close latency (the dial cost).")
    print(f"  --> allowedLateness grace for the tail:  ~{allowed_lateness_ms:,.0f} ms")
    print("      (window stays open this long past the watermark to absorb stragglers)")
    print()
    print("  Notes:")
    print("   - Window on EVENT-time, not processing-time.")
    print("   - Events later than watermark + allowedLateness -> route to a SIDE OUTPUT,")
    print("     never drop silently. Alarm on the side-output rate (completeness signal).")
    print("   - Make the sink idempotent (keyed upsert on window key) so late re-emissions")
    print("     CORRECT the window rather than double-count.")
    print("   - Too tight a watermark drops late data (low numbers); too loose taxes every")
    print("     window's latency and state. Set it from the measured distribution.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stream_sizing.py",
        description="Streaming capacity sizing calculator (decision-support; validate against your cluster).",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    p_part = sub.add_parser("partitions", help="minimum partitions for a throughput target")
    p_part.add_argument("--target-msgs-per-sec", type=float, required=True)
    p_part.add_argument("--per-consumer-msgs-per-sec", type=float, required=True)
    p_part.add_argument("--headroom", type=float, default=1.5)
    p_part.add_argument("--max-skew-share", type=float, default=0.6)

    p_poll = sub.add_parser("poll-budget", help="does a poll batch fit the poll interval?")
    p_poll.add_argument("--per-record-ms", type=float, required=True)
    p_poll.add_argument("--max-poll-records", type=int, default=500)
    p_poll.add_argument("--max-poll-interval-ms", type=float, default=300000.0)
    p_poll.add_argument("--margin", type=float, default=0.7)

    p_wm = sub.add_parser("watermark", help="lateness distribution -> watermark + grace")
    p_wm.add_argument("--p50-lateness-ms", type=float, required=True)
    p_wm.add_argument("--p99-lateness-ms", type=float, required=True)
    p_wm.add_argument("--max-lateness-ms", type=float, default=600000.0)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "partitions":
        return size_partitions(
            args.target_msgs_per_sec,
            args.per_consumer_msgs_per_sec,
            args.headroom,
            args.max_skew_share,
        )
    if args.mode == "poll-budget":
        return poll_budget(
            args.per_record_ms,
            args.max_poll_records,
            args.max_poll_interval_ms,
            args.margin,
        )
    if args.mode == "watermark":
        return watermark(
            args.p50_lateness_ms,
            args.p99_lateness_ms,
            args.max_lateness_ms,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
