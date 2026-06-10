#!/usr/bin/env python3
"""search_relevance_engineering_calc.py — a zero-dependency Search & Relevance Engineering decision calculator.

Removes arithmetic error from 3 recurring search & relevance engineering decisions:

  relevance     NDCG@k from graded judgments, plus DCG/IDCG and precision@k.

  latency-budgetPer-stage latency vs the p95 budget, with headroom.

  index-sizing  Primary + replica storage and shard-count guidance.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No query/user PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No query/user PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_relevance(a):
    import math
    parts = [p.strip() for p in a.graded.split(",") if p.strip() != ""]
    if not parts:
        print("error: --graded must be a comma-separated list of grades (e.g. 3,2,0,1)", file=sys.stderr)
        return 2
    try:
        grades = [float(p) for p in parts]
    except ValueError:
        print("error: --graded must be numeric grades, comma-separated", file=sys.stderr)
        return 2
    if any(g < 0 for g in grades):
        print("error: relevance grades must be >= 0", file=sys.stderr)
        return 2
    k = len(grades)
    # DCG = sum(rel_i / log2(i+1)) with rank i starting at 1
    dcg = sum(rel / math.log2(i + 1) for i, rel in enumerate(grades, start=1))
    ideal = sorted(grades, reverse=True)
    idcg = sum(rel / math.log2(i + 1) for i, rel in enumerate(ideal, start=1))
    ndcg = (dcg / idcg) if idcg > 0 else 0.0
    rel_count = sum(1 for g in grades if g >= a.relevant_threshold)
    precision = rel_count / k
    print("=== Relevance: NDCG@k (CLAUDE.md S3 #1) ===")
    print(f"  Graded results (rank order): {grades}")
    print(f"  k                   : {k}")
    print(f"  DCG@{k}              : {dcg:.4f}  (Sum rel_i / log2(i+1), rank i from 1)")
    print(f"  IDCG@{k}             : {idcg:.4f}  (ideal relevance-sorted order)")
    print(f"  >> NDCG@{k}          : {ndcg:.4f}  (DCG / IDCG)")
    print(f"  >> Precision@{k}     : {_pct(precision)}  (grade >= {a.relevant_threshold:g})")
    if ndcg < 0.8:
        print("  >> Ranking leaves relevance on the table — relevant docs not ranked high enough (S3 #1)")
    else:
        print("  >> Ranking near-ideal on this query; confirm offline win transfers online (S3 #6)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_latency_budget(a):
    stages = {"parse": a.parse_ms, "match": a.match_ms, "fetch": a.fetch_ms, "rescore": a.rescore_ms}
    for n, v in stages.items():
        if v < 0:
            print(f"error: {n} latency must be >= 0", file=sys.stderr)
            return 2
    if a.budget_ms <= 0:
        print("error: --budget-ms > 0", file=sys.stderr)
        return 2
    total = sum(stages.values())
    headroom = a.budget_ms - total
    print("=== Latency budget (CLAUDE.md S3 #4) ===")
    for n, v in stages.items():
        share = (v / total) if total > 0 else 0
        print(f"  {n:<8}: {v:>8.1f} ms  ({_pct(share)})")
    print(f"  {'TOTAL':<8}: {total:>8.1f} ms")
    print(f"  Budget  : {a.budget_ms:>8.1f} ms (p95)")
    worst = max(stages, key=stages.get)
    if headroom >= 0:
        print(f"  >> WITHIN budget — headroom {headroom:.1f} ms for relevance work (S3 #4)")
    else:
        print(f"  >> OVER budget by {abs(headroom):.1f} ms — slowest stage '{worst}'; trim it (S3 #4)")
    print("  NOTE: relevance levers (rescore/expansion) cost latency — tune inside the budget (S3 #4 #5).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_index_sizing(a):
    if a.docs < 0 or a.avg_doc_kb < 0 or a.replicas < 0:
        print("error: --docs, --avg-doc-kb, --replicas must be >= 0", file=sys.stderr)
        return 2
    if a.shard_gb <= 0:
        print("error: --shard-gb > 0", file=sys.stderr)
        return 2
    primary_gb = (a.docs * a.avg_doc_kb) / (1024.0 * 1024.0)
    total_gb = primary_gb * (1 + a.replicas)
    import math
    shards = max(1, math.ceil(primary_gb / a.shard_gb)) if primary_gb > 0 else 1
    print("=== Index sizing (CLAUDE.md S3 #7) ===")
    print(f"  Documents           : {a.docs:,.0f}")
    print(f"  Avg doc size        : {a.avg_doc_kb:g} KB")
    print(f"  Replicas            : {a.replicas:g}")
    print(f"  >> Primary storage  : {primary_gb:,.2f} GB")
    print(f"  >> Total w/ replicas: {total_gb:,.2f} GB  (primary x (1 + replicas))")
    print(f"  >> Suggested primary shards: {shards}  (target {a.shard_gb:g} GB/shard)")
    print("  NOTE: shape mappings/shards for the actual query patterns (S3 #7); targets are [unverified] (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='search_relevance_engineering_calc.py',
        description="Search & Relevance Engineering decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('relevance', help='graded relevance for top-k (comma-separated) -> DCG, IDCG, NDCG + precision@k')
    sp.add_argument('--graded', type=str, required=True, help='graded relevance of the top-k results, comma-separated (e.g. 3,2,0,1)')
    sp.add_argument('--relevant-threshold', type=float, default=1.0, help='grade >= this counts as relevant for precision@k')
    sp.set_defaults(func=cmd_relevance)

    sp = sub.add_parser('latency-budget', help='per-stage latencies -> total + headroom vs budget')
    sp.add_argument('--parse-ms', type=float, required=True, help='query parse latency (ms)')
    sp.add_argument('--match-ms', type=float, required=True, help='match/retrieve latency (ms)')
    sp.add_argument('--fetch-ms', type=float, required=True, help='fetch/hydrate latency (ms)')
    sp.add_argument('--rescore-ms', type=float, required=True, help='rescore/rank latency (ms)')
    sp.add_argument('--budget-ms', type=float, required=True, help='p95 latency budget (ms)')
    sp.set_defaults(func=cmd_latency_budget)

    sp = sub.add_parser('index-sizing', help='docs, avg doc size, replicas -> storage + shard guidance')
    sp.add_argument('--docs', type=float, required=True, help='number of documents')
    sp.add_argument('--avg-doc-kb', type=float, required=True, help='average indexed doc size (KB)')
    sp.add_argument('--replicas', type=float, required=True, help='replica copies per primary')
    sp.add_argument('--shard-gb', type=float, default=30.0, help='target primary shard size (GB)')
    sp.set_defaults(func=cmd_index_sizing)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
