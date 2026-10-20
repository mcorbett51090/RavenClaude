#!/usr/bin/env python3
"""Claude app cost & context-budget estimator (stdlib-only, Python 3.8+).

A *calculator*, not a data source: the user supplies every token count and
price. It removes arithmetic error from three recurring claude-app-engineering
decisions, mirroring the discipline of the cost-lever and cache-hit-rate
decision trees in ``knowledge/cost-and-caching-decision-trees.md``:

  * ``cache``   -- prompt-cache break-even + cost with/without caching over N
                   repeated requests (the Lever-1 question).
  * ``budget``  -- context-window budget check: does prefix + history +
                   per-turn growth fit the window, and for how many turns.
  * ``batch``   -- interactive vs Batch-API cost for latency-tolerant work
                   (the Lever-3 question).

PRICES AND THE CACHE MULTIPLIERS ARE NOT BAKED IN AS FACT. Defaults are dated,
[verify-at-use] snapshots; the real numbers are inputs. The Claude platform
ships monthly -- confirm prices, the cache write/read multipliers, and the
context-window size against the current pricing/docs (the plugin's
``knowledge/model-selection-and-2026-capability-map.md`` is the freshness
anchor) before quoting anyone. Outputs are decision-support, not a quote.

Examples:
    python3 claude_cost_estimator.py cache \\
        --cached-tokens 40000 --uncached-tokens 500 --requests 100 \\
        --input-price 5.0
    python3 claude_cost_estimator.py budget \\
        --prefix-tokens 40000 --history-tokens 12000 \\
        --per-turn-tokens 1500 --window 200000
    python3 claude_cost_estimator.py batch \\
        --input-tokens 2000 --output-tokens 800 --requests 5000 \\
        --input-price 5.0 --output-price 25.0
"""

from __future__ import annotations

import argparse
import math
import sys

# --- Dated, [verify-at-use] default snapshots (NOT authoritative) -----------
# Prompt-cache multipliers, retrieved 2026-05-28 from the Anthropic prompt-
# caching docs; re-confirm before relying on them. Cache reads cost ~0.1x base
# input; cache writes cost ~1.25x for the 5m TTL, ~2x for the 1h TTL.
DEFAULT_CACHE_READ_MULT = 0.1
DEFAULT_CACHE_WRITE_MULT_5M = 1.25
DEFAULT_CACHE_WRITE_MULT_1H = 2.0
# Batch API discount, same retrieval date: ~50% off standard token prices.
DEFAULT_BATCH_DISCOUNT = 0.5

VERIFY_NOTE = (
    "[verify-at-use] prices + cache/batch multipliers are dated snapshots, "
    "not authoritative -- confirm against current Anthropic pricing/docs."
)


def _per_token(price_per_million: float) -> float:
    """Convert a $/1M-token price to $/token."""
    return price_per_million / 1_000_000.0


def _check_non_negative(args: argparse.Namespace, *names: str) -> str | None:
    """Return an error message for the first negative numeric argument, else None."""
    for name in names:
        value = getattr(args, name)
        if value is not None and value < 0:
            return f"--{name.replace('_', '-')} must be >= 0 (got {value})"
    return None


def _cache_break_even(
    cached: int, in_tok: float, write_mult: float, read_mult: float, n: int
) -> int | None:
    """Smallest request count i in 1..n where caching is cheaper, in closed form.

    Cumulative cached cost minus cumulative uncached cost after i requests is
    cached * price * ((write - 1) + (i - 1) * (read - 1)); the uncached remainder is
    full-priced either way and cancels. So caching wins at request 1 if write < 1,
    otherwise at 2 + floor((write - 1) / (1 - read)) when reads are cheaper than base
    input, and never when they are not. O(1) instead of a loop over every request.
    """
    if cached <= 0 or in_tok <= 0 or n < 1:
        return None
    gap = write_mult - 1.0
    if gap < 0:
        first_win = 1
    elif read_mult >= 1.0:
        return None
    else:
        # round() first: a quotient like 2.9999999999999996 is really the tie 3.
        first_win = math.floor(round(gap / (1.0 - read_mult), 9)) + 2
    return first_win if first_win <= n else None


def cmd_cache(args: argparse.Namespace) -> int:
    """Prompt-cache break-even + total cost across N repeated requests."""
    problem = _check_non_negative(
        args,
        "cached_tokens",
        "uncached_tokens",
        "requests",
        "input_price",
        "cache_read_mult",
        "cache_write_mult",
    )
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 2
    write_mult = (
        DEFAULT_CACHE_WRITE_MULT_1H
        if args.ttl == "1h"
        else DEFAULT_CACHE_WRITE_MULT_5M
    )
    if args.cache_write_mult is not None:
        write_mult = args.cache_write_mult
    read_mult = args.cache_read_mult

    in_tok = _per_token(args.input_price)
    cached = args.cached_tokens
    uncached = args.uncached_tokens
    n = args.requests

    # No caching: every request pays full price for the whole prompt.
    no_cache_total = (cached + uncached) * in_tok * n

    # With caching: request 1 writes the cached prefix (write premium) + pays
    # full price for the uncached remainder; requests 2..N read the prefix
    # (read multiplier) + full price for the uncached remainder.
    first = (cached * in_tok * write_mult + uncached * in_tok) if n >= 1 else 0.0
    rest = (cached * in_tok * read_mult + uncached * in_tok) * max(n - 1, 0)
    cache_total = first + rest

    savings = no_cache_total - cache_total
    pct = (savings / no_cache_total * 100.0) if no_cache_total else 0.0

    # Break-even: smallest request count where caching is cheaper.
    break_even = _cache_break_even(cached, in_tok, write_mult, read_mult, n)

    lines: list[str] = [
        "=== Prompt-cache cost estimate ===",
        f"  cached prefix tokens : {cached:,}",
        f"  uncached tokens/req  : {uncached:,}",
        f"  requests             : {n:,}",
        f"  TTL                  : {args.ttl} "
        f"(write x{write_mult}, read x{read_mult})",
        "",
        f"  no caching total     : ${no_cache_total:,.4f}",
        f"  with caching total   : ${cache_total:,.4f}",
        f"  savings              : ${savings:,.4f} ({pct:.1f}%)",
    ]
    if break_even is not None:
        lines.append(f"  break-even at        : request #{break_even}")
    else:
        lines.append(
            "  break-even           : not reached within "
            f"{n} request(s) -- the prefix is too small or reused too few "
            "times to beat the write premium."
        )
    if savings <= 0:
        lines.append(
            "  NOTE: caching does NOT pay off here -- you pay the write "
            "premium without enough reads to recover it. See the "
            "cache-hit-rate-collapse decision tree."
        )
    lines.append("")
    lines.append(VERIFY_NOTE)
    print("\n".join(lines))
    return 0


def cmd_budget(args: argparse.Namespace) -> int:
    """Context-window budget check across multi-turn growth."""
    problem = _check_non_negative(
        args, "prefix_tokens", "history_tokens", "per_turn_tokens", "window", "reserve_output"
    )
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 2
    prefix = args.prefix_tokens
    history = args.history_tokens
    per_turn = args.per_turn_tokens
    window = args.window
    reserve = args.reserve_output

    base = prefix + history
    usable = window - reserve
    headroom = usable - base

    lines: list[str] = [
        "=== Context-window budget ===",
        f"  context window       : {window:,}",
        f"  reserved for output  : {reserve:,}",
        f"  usable for input     : {usable:,}",
        f"  fixed prefix tokens  : {prefix:,}",
        f"  starting history     : {history:,}",
        f"  growth per turn      : {per_turn:,}",
        "",
        f"  used at turn 0       : {base:,}",
        f"  headroom             : {headroom:,}",
    ]

    if base > usable:
        lines.append(
            "  STATUS: OVER BUDGET at turn 0 -- prefix + history already "
            "exceed the usable window. Trim context, retrieve instead of "
            "holding, or move to a larger-window model / compaction."
        )
        rc = 1
    elif per_turn <= 0:
        lines.append("  STATUS: fits; no per-turn growth specified.")
        rc = 0
    else:
        turns = headroom // per_turn
        lines.append(
            f"  STATUS: fits for ~{turns:,} more turn(s) before the usable "
            "window is exhausted."
        )
        lines.append(
            "  At that point: enable compaction / context editing, or "
            "summarize+truncate history (see context-engineering-2026.md)."
        )
        rc = 0

    lines.append("")
    lines.append(
        "[verify-at-use] the context-window size is model-specific and dated "
        "-- confirm against the capability map before relying on it."
    )
    print("\n".join(lines))
    return rc


def cmd_batch(args: argparse.Namespace) -> int:
    """Interactive vs Batch-API cost for latency-tolerant work."""
    problem = _check_non_negative(
        args, "input_tokens", "output_tokens", "requests", "input_price", "output_price"
    )
    if problem is None and not 0.0 <= args.batch_discount <= 1.0:
        problem = f"--batch-discount must be between 0 and 1 (got {args.batch_discount})"
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 2
    in_tok = _per_token(args.input_price)
    out_tok = _per_token(args.output_price)
    n = args.requests
    discount = args.batch_discount

    per_req = args.input_tokens * in_tok + args.output_tokens * out_tok
    interactive = per_req * n
    batch = interactive * (1.0 - discount)
    savings = interactive - batch

    lines = [
        "=== Interactive vs Batch-API cost ===",
        f"  input tokens/req     : {args.input_tokens:,}",
        f"  output tokens/req    : {args.output_tokens:,}",
        f"  requests             : {n:,}",
        f"  batch discount       : {discount * 100:.0f}%",
        "",
        f"  interactive total    : ${interactive:,.4f}",
        f"  batch total          : ${batch:,.4f}",
        f"  savings              : ${savings:,.4f}",
        "",
        "  Batch only applies to latency-tolerant / offline work "
        "(evals, backfills, bulk jobs, the eval judge) -- you cannot batch "
        "an interactive request.",
        "",
        VERIFY_NOTE,
    ]
    print("\n".join(lines))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Claude app cost & context-budget estimator. A calculator: you "
            "supply token counts + prices. Prices/multipliers are dated "
            "[verify-at-use] defaults, not authoritative."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_cache = sub.add_parser(
        "cache", help="prompt-cache break-even + cost over N requests"
    )
    p_cache.add_argument(
        "--cached-tokens",
        type=int,
        required=True,
        help="tokens in the stable cached prefix",
    )
    p_cache.add_argument(
        "--uncached-tokens",
        type=int,
        default=0,
        help="tokens below the breakpoint, full-priced every request",
    )
    p_cache.add_argument(
        "--requests", type=int, required=True, help="repeated same-prefix requests"
    )
    p_cache.add_argument(
        "--input-price",
        type=float,
        required=True,
        help="$/1M input tokens (dated -- verify at use)",
    )
    p_cache.add_argument(
        "--ttl",
        choices=["5m", "1h"],
        default="5m",
        help="cache TTL (sets the default write multiplier)",
    )
    p_cache.add_argument(
        "--cache-read-mult",
        type=float,
        default=DEFAULT_CACHE_READ_MULT,
        help="cache-read price multiplier vs base input (dated)",
    )
    p_cache.add_argument(
        "--cache-write-mult",
        type=float,
        default=None,
        help="override the cache-write multiplier (dated)",
    )
    p_cache.set_defaults(func=cmd_cache)

    p_budget = sub.add_parser(
        "budget", help="context-window budget across multi-turn growth"
    )
    p_budget.add_argument("--prefix-tokens", type=int, required=True)
    p_budget.add_argument("--history-tokens", type=int, default=0)
    p_budget.add_argument(
        "--per-turn-tokens",
        type=int,
        default=0,
        help="token growth added per conversation turn",
    )
    p_budget.add_argument(
        "--window",
        type=int,
        required=True,
        help="context-window size for the model (dated -- verify at use)",
    )
    p_budget.add_argument(
        "--reserve-output",
        type=int,
        default=0,
        help="tokens to reserve for the response (kept out of the input budget)",
    )
    p_budget.set_defaults(func=cmd_budget)

    p_batch = sub.add_parser("batch", help="interactive vs Batch-API cost")
    p_batch.add_argument("--input-tokens", type=int, required=True)
    p_batch.add_argument("--output-tokens", type=int, required=True)
    p_batch.add_argument("--requests", type=int, required=True)
    p_batch.add_argument(
        "--input-price", type=float, required=True, help="$/1M input (dated)"
    )
    p_batch.add_argument(
        "--output-price", type=float, required=True, help="$/1M output (dated)"
    )
    p_batch.add_argument(
        "--batch-discount",
        type=float,
        default=DEFAULT_BATCH_DISCOUNT,
        help="fractional discount, e.g. 0.5 for 50%% (dated)",
    )
    p_batch.set_defaults(func=cmd_batch)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
