#!/usr/bin/env python3
"""memory_engineering_calc.py — a zero-dependency agent-memory decision calculator.

Removes arithmetic error from 4 recurring memory-engineering decisions:

  cost-per-correct  THE SPINE. Cost per CORRECT answer for one or two systems.
                    Comparing raw cost across systems with different accuracy is
                    meaningless; the unit that survives the comparison is cost per
                    correct answer.

  amortize          Break-even query volume for a memory build, against an
                    EXPLICITLY NAMED baseline. There is no default baseline: the
                    answer is only interpretable once you say what you are
                    comparing against.

  store-growth      Footprint at 30 / 90 / 365 days, and the day a supplied cap
                    is reached. Nothing forgets by default.

  cache-economics   Monthly delta between a cache-breaking write pattern and a
                    stable-prefix design, plus the effective multiple COMPUTED
                    from your own inputs rather than quoted as a constant.

This is a CALCULATOR, not a data source — it does not fetch pricing, benchmarks or
live data, and it carries no vendor constants. Every priced fact is a required flag
with no default, because a priced fact moves and a calculator must not quietly
become a stale data source. Stdlib only (argparse); runs anywhere Python 3.8+ is
present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the client's
actual data; route every professional determination to the qualified authority.
No user data / memory-store contents belong in any input or output.
"""

from __future__ import annotations

import argparse
import math
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No user data / "
    "memory-store contents."
)

# The fastest-moving numbers deliberately do NOT live in this file. A .py is
# invisible to the only staleness sweep that exists (knowledge-health.py scans
# plugins/*/knowledge/**/*.md), so a constant baked in here would rot unwatched.
KNOWLEDGE_POINTER = (
    "see ../knowledge/memory-surfaces-2026.md (dated 2026-08-06) for current "
    "published multipliers and caps"
)

BASELINES = ("full-context-prefill", "lexical-retrieval", "stateless")

BASELINE_GLOSS = {
    "full-context-prefill": (
        "re-send the whole raw history every query (Paradigm I) — same job, "
        "zero construction cost"
    ),
    "lexical-retrieval": (
        "deterministic top-k over the history, e.g. BM25 (Paradigm II) — same "
        "job, cheap construction"
    ),
    "stateless": (
        "answer with no injected history at all — NOT the same job; it cannot "
        "answer memory-dependent queries"
    ),
}


def _money(x):
    return f"${x:,.2f}"


def _cost(x):
    return f"${x:,.6f}".rstrip("0").rstrip(".")


def _pct(x):
    return f"{x * 100:.1f}%"


def _box(title, lines):
    width = 74
    out = ["  +" + "-" * width + "+"]
    out.append("  | %-*s |" % (width - 2, title))
    out.append("  +" + "-" * width + "+")
    for ln in lines:
        out.append("  | %-*s |" % (width - 2, ln))
    out.append("  +" + "-" * width + "+")
    return "\n".join(out)


def cmd_cost_per_correct(a):
    # Guards first — no arithmetic before every denominator is proven non-zero.
    # cost-per-correct divides by (queries x accuracy), so BOTH factors are
    # guarded; the queries guard alone is not the fix.
    if a.queries_a <= 0:
        print("error: --queries-a > 0", file=sys.stderr)
        return 2
    if a.total_cost_a < 0:
        print("error: --total-cost-a >= 0", file=sys.stderr)
        return 2
    if not (0 < a.accuracy_a <= 1):
        print("error: 0 < --accuracy-a <= 1", file=sys.stderr)
        return 2

    b_flags = (a.total_cost_b, a.queries_b, a.accuracy_b)
    b_given = [f is not None for f in b_flags]
    if any(b_given) and not all(b_given):
        print(
            "error: --total-cost-b, --queries-b and --accuracy-b must all be "
            "supplied together",
            file=sys.stderr,
        )
        return 2
    have_b = all(b_given)
    if have_b:
        if a.queries_b <= 0:
            print("error: --queries-b > 0", file=sys.stderr)
            return 2
        if a.total_cost_b < 0:
            print("error: --total-cost-b >= 0", file=sys.stderr)
            return 2
        if not (0 < a.accuracy_b <= 1):
            print("error: 0 < --accuracy-b <= 1", file=sys.stderr)
            return 2

    name_a = a.system_name_a or "system A"
    correct_a = a.queries_a * a.accuracy_a
    cpc_a = a.total_cost_a / correct_a

    print("=== Cost per correct answer (CLAUDE.md S3 #8) ===")
    print("  Formula             : cost per correct = total cost / (queries x accuracy)")
    print(f"  {name_a:<20.20}: {_money(a.total_cost_a)} over {a.queries_a:,} queries "
          f"at {_pct(a.accuracy_a)}")
    print(f"    correct answers   : {correct_a:,.1f}")
    print(f"  >> {name_a:<17.17}: {_cost(cpc_a)} per correct answer")

    if have_b:
        name_b = a.system_name_b or "system B"
        correct_b = a.queries_b * a.accuracy_b
        cpc_b = a.total_cost_b / correct_b
        print(f"  {name_b:<20.20}: {_money(a.total_cost_b)} over {a.queries_b:,} "
              f"queries at {_pct(a.accuracy_b)}")
        print(f"    correct answers   : {correct_b:,.1f}")
        print(f"  >> {name_b:<17.17}: {_cost(cpc_b)} per correct answer")
        cheaper, dearer = (name_a, name_b) if cpc_a <= cpc_b else (name_b, name_a)
        lo, hi = (cpc_a, cpc_b) if cpc_a <= cpc_b else (cpc_b, cpc_a)
        ratio = hi / lo  # lo > 0: both costs are >= 0 and only a 0-cost system ties
        if lo > 0:
            print(f"  >> {cheaper} is {ratio:,.2f}x cheaper per correct answer "
                  f"than {dearer}")
        else:
            print(f"  >> {cheaper} costs nothing per correct answer; no ratio to report")
        raw_a = a.total_cost_a / a.queries_a
        raw_b = a.total_cost_b / a.queries_b
        raw_cheaper = name_a if raw_a <= raw_b else name_b
        if raw_cheaper != cheaper:
            print("  >> NOTE: the raw cost-per-query ranking DISAGREES with this one. "
                  "Cost per correct answer is the ranking that survives an accuracy "
                  "difference (S3 #8).")
    else:
        print("  NOTE: one system only. A cost-per-correct figure is a comparison "
              "unit — supply --total-cost-b/--queries-b/--accuracy-b, or read it "
              "against your own recorded baseline.")

    print(f"\n  {DISCLAIMER}")
    return 0


def cmd_amortize(a):
    # --baseline is required=True at the parser, so argparse owns its exit 2.
    if a.build_cost < 0:
        print("error: --build-cost >= 0", file=sys.stderr)
        return 2
    if a.per_query_cost_with < 0:
        print("error: --per-query-cost-with >= 0", file=sys.stderr)
        return 2
    if a.per_query_cost_without < 0:
        print("error: --per-query-cost-without >= 0", file=sys.stderr)
        return 2
    if a.queries_per_month is not None and a.queries_per_month <= 0:
        print("error: --queries-per-month > 0", file=sys.stderr)
        return 2

    print("=== Amortization vs a named baseline (CLAUDE.md S3 #1) ===")

    # The stateless warning is a PRECONDITION on interpreting the number, so it
    # prints BEFORE the result, never after it.
    if a.baseline == "stateless":
        print(
            _box(
                "FUNCTIONAL NON-EQUIVALENCE - read this before the number",
                [
                    "baseline=stateless answers with no injected history at all.",
                    "It is NOT the same job: it cannot answer a memory-dependent",
                    "query at any accuracy. A break-even against it compares a",
                    "working system to one that does not do the task, so the",
                    "figure below is a cost fact, not a decision.",
                    "",
                    "For a decision, re-run against full-context-prefill or",
                    "lexical-retrieval, or use the cost-per-correct mode, which",
                    "carries accuracy explicitly.",
                ],
            )
        )

    print(f"  Baseline            : {a.baseline}")
    print(f"    ({BASELINE_GLOSS[a.baseline]})")
    print(f"  Build cost          : {_money(a.build_cost)}")
    print(f"  Per query WITH      : {_cost(a.per_query_cost_with)}")
    print(f"  Per query WITHOUT   : {_cost(a.per_query_cost_without)}")
    print("  Formula             : n* = build cost / (per-query without - per-query with)")

    delta = a.per_query_cost_without - a.per_query_cost_with
    print(f"  Per-query saving    : {_cost(delta)}")

    if delta <= 0:
        print(f"  >> NEVER AMORTIZES at baseline={a.baseline}")
        print("     The memory path costs the same or more per query than the "
              "baseline, so no query volume repays the build cost.")
        print("     There may still be a case on ACCURACY rather than cost — run "
              "the cost-per-correct mode, which prices accuracy in (S3 #8).")
        print(f"\n  {DISCLAIMER}")
        return 0

    n_star = math.ceil(a.build_cost / delta)
    print(f"  >> Break-even       : {n_star:,} queries at baseline={a.baseline}")
    if a.queries_per_month is not None:
        months = n_star / a.queries_per_month
        days = math.ceil(months * 30.0)
        print(f"  Queries/month       : {a.queries_per_month:,.0f}")
        print(f"  >> Break-even       : {months:,.3f} months (~{days:,} days)")
    else:
        print("  NOTE: supply --queries-per-month to convert the break-even volume "
              "into a calendar date.")
    print("  NOTE: this prices the BUILD once. A store that is rewritten, "
          "re-embedded or re-consolidated pays construction again — fold that "
          "into --build-cost or the figure flatters the memory path (S3 #1).")

    print(f"\n  {DISCLAIMER}")
    return 0


def cmd_store_growth(a):
    if a.writes_per_day <= 0:
        print("error: --writes-per-day > 0", file=sys.stderr)
        return 2
    if a.avg_size_kb <= 0:
        print("error: --avg-size-kb > 0", file=sys.stderr)
        return 2
    if a.ttl_days is not None and a.ttl_days <= 0:
        print("error: --ttl-days > 0", file=sys.stderr)
        return 2
    if a.max_items is not None and a.max_items <= 0:
        print("error: --max-items > 0", file=sys.stderr)
        return 2
    if a.max_kb is not None and a.max_kb <= 0:
        print("error: --max-kb > 0", file=sys.stderr)
        return 2

    print("=== Store growth and retention (CLAUDE.md S3 #3) ===")
    print(f"  Writes/day          : {a.writes_per_day:,.2f}")
    print(f"  Avg item size       : {a.avg_size_kb:,.2f} KB")
    if a.ttl_days is not None:
        print(f"  TTL                 : {a.ttl_days:,.2f} days")
    print("  Formula             : items(d) = writes/day x min(d, TTL); "
          "KB(d) = items(d) x avg size")

    for day in (30, 90, 365):
        live_days = min(float(day), a.ttl_days) if a.ttl_days is not None else float(day)
        items = a.writes_per_day * live_days
        print(f"  >> Day {day:<3d}          : {items:,.0f} items / {items * a.avg_size_kb:,.0f} KB")

    steady_items = (a.writes_per_day * a.ttl_days) if a.ttl_days is not None else None
    if steady_items is not None:
        print(f"  >> Steady state     : {steady_items:,.0f} items / "
              f"{steady_items * a.avg_size_kb:,.0f} KB (TTL holds it flat)")

    def _cap_day(cap_items, label, shown):
        if steady_items is not None and steady_items < cap_items:
            print(f"  >> {label:<17.17}: never reached — the TTL steady state "
                  f"({steady_items:,.0f} items) sits below {shown}")
            return
        day = math.ceil(cap_items / a.writes_per_day)
        print(f"  >> {label:<17.17}: reached on day {day:,} ({shown})")

    if a.max_items is not None:
        _cap_day(float(a.max_items), "--max-items cap", f"{a.max_items:,} items")
    if a.max_kb is not None:
        _cap_day(a.max_kb / a.avg_size_kb, "--max-kb cap", f"{a.max_kb:,.0f} KB")

    if a.ttl_days is None and a.max_items is None and a.max_kb is None:
        print("  NOTE: nothing forgets by default. With no TTL and no cap this "
              "store grows without bound until some load budget truncates it "
              "silently. An unbounded store is a decision nobody made (S3 #3).")
    print("  NOTE: a surface may impose its own hard cap below yours — "
          f"{KNOWLEDGE_POINTER}.")
    print("  NOTE: growth is only half the retention story. State what a delete "
          "LEAVES BEHIND — version history, embeddings, derived summaries, "
          "cached prefixes (S3 #7).")

    print(f"\n  {DISCLAIMER}")
    return 0


def cmd_cache_economics(a):
    if a.prefix_tokens <= 0:
        print("error: --prefix-tokens > 0", file=sys.stderr)
        return 2
    if a.cache_write_multiplier <= 0:
        print("error: --cache-write-multiplier > 0", file=sys.stderr)
        return 2
    if a.cache_read_multiplier <= 0:
        print("error: --cache-read-multiplier > 0", file=sys.stderr)
        return 2
    if a.invalidations_per_N_turns < 0:
        print("error: --invalidations-per-N-turns >= 0", file=sys.stderr)
        return 2
    if a.turns_per_month <= 0:
        print("error: --turns-per-month > 0", file=sys.stderr)
        return 2

    turns = a.turns_per_month
    invalidations = min(a.invalidations_per_N_turns * turns, turns)

    # Units are cache-adjusted input tokens (tokens x multiplier). Multiply by
    # your model's input price per token for currency — deliberately not a flag
    # and never a constant here, because that price moves.
    breaking = (invalidations * a.prefix_tokens * a.cache_write_multiplier
                + max(0.0, turns - invalidations) * a.prefix_tokens
                * a.cache_read_multiplier)
    stable = (a.prefix_tokens * a.cache_write_multiplier
              + max(0.0, turns - 1.0) * a.prefix_tokens * a.cache_read_multiplier)
    delta = breaking - stable

    print("=== Cache economics of a memory write pattern (CLAUDE.md S3 #1) ===")
    print(f"  Prefix tokens       : {a.prefix_tokens:,.0f}")
    print(f"  Write multiplier    : {a.cache_write_multiplier:,.3f}x")
    print(f"  Read multiplier     : {a.cache_read_multiplier:,.3f}x")
    print(f"  Invalidations/turn  : {a.invalidations_per_N_turns:,.4f}")
    print(f"  Turns/month         : {turns:,.0f}")
    print("  Formula             : breaking = inv x prefix x write + "
          "(turns - inv) x prefix x read")
    print("                        stable   = prefix x write + "
          "(turns - 1) x prefix x read")
    print(f"  Invalidations/month : {invalidations:,.0f}")
    print(f"  >> Cache-breaking   : {breaking:,.0f} cache-adjusted input tokens/month")
    print(f"  >> Stable prefix    : {stable:,.0f} cache-adjusted input tokens/month")
    print(f"  >> Monthly delta    : {delta:,.0f} cache-adjusted input tokens/month")
    if stable > 0:
        print(f"  >> Effective multiple: {breaking / stable:,.2f}x "
              "(COMPUTED from your inputs, not quoted as a constant)")
    print("  >> Multiply by your model's input price per token for currency; "
          "this tool ships no price.")
    if a.invalidations_per_N_turns <= 0:
        print("  NOTE: zero invalidations — the two designs converge. Re-run with "
              "the invalidation rate a memory write actually causes.")
    print("  NOTE: a write that lands ahead of the reused prefix invalidates "
          "everything after it. Append memory at the END of the prompt, or pay "
          "this bill once per turn (S3 #1).")
    print(f"  NOTE: multipliers are inputs, never defaults — {KNOWLEDGE_POINTER}.")

    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="memory_engineering_calc.py",
        description=(
            "Agent-memory decision calculator (stdlib only). Decision-support, "
            "not advice. Modes: cost-per-correct (the spine) - amortize - "
            "store-growth - cache-economics."
        ),
        epilog=(
            "No vendor constant is baked into this script: every priced fact is a "
            "required flag with no default, so the tool can never become a stale "
            "data source. For the dated figures a run needs,\n  "
            + KNOWLEDGE_POINTER
            + ".\n\nExit codes: 0 success - 2 any validation failure or argparse "
            "usage error. There is no exit 1."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser(
        "cost-per-correct",
        help="THE SPINE: cost / (queries x accuracy) for one or two systems",
        description=(
            "Cost per correct answer. Comparing raw cost across systems with "
            "different accuracy is meaningless; this is the unit that survives "
            "the comparison. System-B flags are all-or-nothing."
        ),
    )
    sp.add_argument("--total-cost-a", type=float, required=True,
                    help="total cost of system A over the measured window ($)")
    sp.add_argument("--queries-a", type=int, required=True,
                    help="queries system A answered in that window (> 0)")
    sp.add_argument("--accuracy-a", type=float, required=True,
                    help="system A accuracy as a fraction, 0 < a <= 1")
    sp.add_argument("--system-name-a", help='label for system A (default "system A")')
    sp.add_argument("--total-cost-b", type=float,
                    help="total cost of system B ($) — all three B flags or none")
    sp.add_argument("--queries-b", type=int,
                    help="queries system B answered (> 0) — all three B flags or none")
    sp.add_argument("--accuracy-b", type=float,
                    help="system B accuracy, 0 < a <= 1 — all three B flags or none")
    sp.add_argument("--system-name-b", help='label for system B (default "system B")')
    sp.set_defaults(func=cmd_cost_per_correct)

    sp = sub.add_parser(
        "amortize",
        help="break-even query volume for a memory build, against a NAMED baseline",
        description=(
            "Break-even volume for a memory build. --baseline is REQUIRED and has "
            "no default: an amortization figure is uninterpretable until you name "
            "what it is measured against, and a stateless baseline is not the "
            "same job."
        ),
    )
    sp.add_argument("--build-cost", type=float, required=True,
                    help="one-off construction cost of the memory store ($, >= 0)")
    sp.add_argument("--per-query-cost-with", type=float, required=True,
                    help="per-query cost WITH the memory system ($, >= 0)")
    sp.add_argument("--per-query-cost-without", type=float, required=True,
                    help="per-query cost on the baseline ($, >= 0)")
    sp.add_argument("--baseline", required=True, choices=BASELINES,
                    help="what the memory system is measured against (no default)")
    sp.add_argument("--queries-per-month", type=float,
                    help="optional: convert the break-even volume into a date (> 0)")
    sp.set_defaults(func=cmd_amortize)

    sp = sub.add_parser(
        "store-growth",
        help="footprint at 30/90/365 days and the day a supplied cap is reached",
        description=(
            "Growth of a durable store. Nothing forgets by default: with no TTL "
            "and no cap the projection is unbounded, and that is the finding."
        ),
    )
    sp.add_argument("--writes-per-day", type=float, required=True,
                    help="items written per day (> 0)")
    sp.add_argument("--avg-size-kb", type=float, required=True,
                    help="average stored item size in KB (> 0)")
    sp.add_argument("--ttl-days", type=float,
                    help="optional: time-to-live per item in days (> 0)")
    sp.add_argument("--max-items", type=int,
                    help="optional: item cap the surface or design imposes (> 0)")
    sp.add_argument("--max-kb", type=float,
                    help="optional: size cap in KB (> 0)")
    sp.set_defaults(func=cmd_store_growth)

    sp = sub.add_parser(
        "cache-economics",
        help="monthly delta between a cache-breaking and a stable-prefix design",
        description=(
            "Cache economics of a memory write pattern. Both multipliers are "
            "required flags with no default — they are vendor-controlled and they "
            "move. The effective multiple is computed per case, never asserted."
        ),
    )
    sp.add_argument("--prefix-tokens", type=float, required=True,
                    help="tokens in the reusable prompt prefix (> 0)")
    sp.add_argument("--cache-write-multiplier", type=float, required=True,
                    help="price multiple for writing the cache (required, no default)")
    sp.add_argument("--cache-read-multiplier", type=float, required=True,
                    help="price multiple for reading the cache (required, no default)")
    sp.add_argument("--invalidations-per-N-turns", type=float, required=True,
                    dest="invalidations_per_N_turns",
                    help="invalidations PER TURN as a rate over the N turns you "
                         "run: 1 = every turn breaks the prefix, 0.1 = one turn "
                         "in ten, 0 = never (>= 0)")
    sp.add_argument("--turns-per-month", type=float, required=True,
                    help="conversation turns per month (> 0)")
    sp.set_defaults(func=cmd_cache_economics)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
