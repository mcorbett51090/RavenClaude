#!/usr/bin/env python3
"""ai_rag_engineering_calc.py — a zero-dependency AI / RAG Engineering decision calculator.

Removes arithmetic error from 3 recurring ai / rag engineering decisions:

  retrieval-evalRecall@k, precision@k, and F1 for a retrieval result.

  token-cost    Cost per request and monthly projection from token counts.

  chunk-budget  Does chunk size x top-k fit the context window?

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No user data / prompt PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No user data / prompt PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_retrieval_eval(a):
    if a.total_relevant <= 0 or a.k <= 0:
        print("error: --total-relevant > 0 and --k > 0", file=sys.stderr)
        return 2
    if a.relevant_retrieved < 0 or a.relevant_retrieved > a.total_relevant or a.relevant_retrieved > a.k:
        print("error: 0 <= --relevant-retrieved <= min(--total-relevant, --k)", file=sys.stderr)
        return 2
    recall = a.relevant_retrieved / a.total_relevant
    precision = a.relevant_retrieved / a.k
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    print("=== Retrieval eval (CLAUDE.md S3 #1 #3) ===")
    print(f"  Relevant retrieved  : {a.relevant_retrieved:g}")
    print(f"  Total relevant      : {a.total_relevant:g}")
    print(f"  k                   : {a.k:g}")
    print(f"  >> Recall@{a.k:g}        : {_pct(recall)}  (relevant retrieved / total relevant)")
    print(f"  >> Precision@{a.k:g}     : {_pct(precision)}  (relevant retrieved / k)")
    print(f"  >> F1               : {_pct(f1)}")
    if recall < 0.8:
        print("  >> Low recall CAPS generation — fix retrieval before the model/prompt (S3 #1)")
    else:
        print("  >> Recall healthy — if answers are still wrong, check grounding/faithfulness (S3 #7)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_token_cost(a):
    if a.input_tokens < 0 or a.output_tokens < 0 or a.input_price < 0 or a.output_price < 0:
        print("error: tokens and prices must be >= 0", file=sys.stderr)
        return 2
    input_cost = (a.input_tokens / 1000.0) * a.input_price
    output_cost = (a.output_tokens / 1000.0) * a.output_price
    cost_per_req = input_cost + output_cost
    print("=== Token cost (CLAUDE.md S3 #5 #8) ===")
    print(f"  Input tokens        : {a.input_tokens:,.0f}  @ {_money(a.input_price)}/1k")
    print(f"  Output tokens       : {a.output_tokens:,.0f}  @ {_money(a.output_price)}/1k")
    print(f"  Input cost          : {_money(input_cost)}")
    print(f"  Output cost         : {_money(output_cost)}")
    print(f"  >> Cost per request : {_money(cost_per_req)}")
    if a.requests_per_month:
        print(f"  Requests/month      : {a.requests_per_month:,.0f}")
        print(f"  >> Monthly cost     : {_money(cost_per_req * a.requests_per_month)}")
    if a.input_tokens > 4 * a.output_tokens and a.output_tokens > 0:
        print("  NOTE: input (context) dominates — fewer high-precision chunks cuts cost (S3 #5)")
    print("  NOTE: prices are [unverified - training knowledge]; verify the live pricing page (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_chunk_budget(a):
    if a.chunk_size <= 0 or a.top_k <= 0 or a.context_window <= 0:
        print("error: --chunk-size, --top-k, --context-window must be > 0", file=sys.stderr)
        return 2
    if a.prompt_overhead < 0 or a.max_output < 0:
        print("error: --prompt-overhead and --max-output must be >= 0", file=sys.stderr)
        return 2
    context_tokens = a.chunk_size * a.top_k
    prompt_tokens = context_tokens + a.prompt_overhead
    needed = prompt_tokens + a.max_output
    headroom = a.context_window - needed
    print("=== Chunk budget vs context window (CLAUDE.md S3 #5) ===")
    print(f"  Chunk size          : {a.chunk_size:g} tokens")
    print(f"  Top-k               : {a.top_k:g}")
    print(f"  Retrieved context   : {context_tokens:,.0f} tokens")
    print(f"  Prompt overhead     : {a.prompt_overhead:,.0f} tokens")
    print(f"  Reserved output     : {a.max_output:,.0f} tokens")
    print(f"  Total needed        : {needed:,.0f} tokens")
    print(f"  Context window      : {a.context_window:,.0f} tokens")
    if headroom >= 0:
        print(f"  >> FITS — token headroom: {headroom:,.0f} tokens")
        print("  NOTE: fitting is necessary, not sufficient — fewest high-precision chunks still wins (S3 #5)")
    else:
        print(f"  >> DOES NOT FIT — over by {abs(headroom):,.0f} tokens; cut top-k or chunk size (S3 #5)")
    print("  NOTE: context window is [unverified - training knowledge]; verify the model's docs (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='ai_rag_engineering_calc.py',
        description="AI / RAG Engineering decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('retrieval-eval', help='relevant retrieved, total relevant, k -> recall@k + precision@k + F1')
    sp.add_argument('--relevant-retrieved', type=float, required=True, help='relevant passages found in the top-k')
    sp.add_argument('--total-relevant', type=float, required=True, help='total relevant passages that exist')
    sp.add_argument('--k', type=float, required=True, help='k (number of passages retrieved)')
    sp.set_defaults(func=cmd_retrieval_eval)

    sp = sub.add_parser('token-cost', help='input+output tokens x per-1k price x requests -> cost/req + monthly')
    sp.add_argument('--input-tokens', type=float, required=True, help='input tokens per request (context + prompt)')
    sp.add_argument('--output-tokens', type=float, required=True, help='output tokens per request')
    sp.add_argument('--input-price', type=float, required=True, help='price per 1k input tokens $')
    sp.add_argument('--output-price', type=float, required=True, help='price per 1k output tokens $')
    sp.add_argument('--requests-per-month', type=float, default=0.0, help='requests per month')
    sp.set_defaults(func=cmd_token_cost)

    sp = sub.add_parser('chunk-budget', help='chunk size, top-k, overhead vs window -> fits? + headroom')
    sp.add_argument('--chunk-size', type=float, required=True, help='tokens per chunk')
    sp.add_argument('--top-k', type=float, required=True, help='number of chunks retrieved')
    sp.add_argument('--context-window', type=float, required=True, help='model context window (tokens)')
    sp.add_argument('--prompt-overhead', type=float, default=500.0, help='prompt scaffolding tokens')
    sp.add_argument('--max-output', type=float, default=1000.0, help='reserved output tokens')
    sp.set_defaults(func=cmd_chunk_budget)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
