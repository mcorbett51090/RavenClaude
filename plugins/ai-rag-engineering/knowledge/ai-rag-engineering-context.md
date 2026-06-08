# AI / RAG Engineering Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible figures come from

Model IDs, token prices, context limits, and rate limits **move constantly** and differ across providers, tiers, and regions. Quoting any of them from memory is the most common confident error in this domain. **Verify against the provider's current docs/pricing page and mark anything recalled `[unverified — training knowledge]` (§3 #8).** Use the `claude-api` reference for Anthropic specifics rather than recalling them.

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Context window | Ranges widely by model and tier | Verify the model's current limit, dated |
| Token price | Differs by model, input vs output, and tier | Verify the live pricing page, dated |
| Optimal top-k | Often small (precision over volume) | Derive from the corpus's own eval (§3 #5) |
| Hybrid vs vector | Hybrid usually wins keyword-heavy corpora | Prove on your corpus's eval (§3 #6) |

## Operating rhythm

- **Eval-gated changes** — no chunking, retrieval, model, or prompt change ships without a before/after eval (§3 #3).
- **Retrieval-first triage** — wrong answers start at recall@k, not the model (§3 #1).
- **Cost/latency review** per endpoint — token cost and context utilization, prices verified live (§3 #4 #5 #8).

## The standing caution

Data-privacy, compliance (e.g. handling of user data sent to a provider), and licensing determinations are **the qualified authority's** call — the team frames the decision and routes it. Keep user data, prompt/query content, and retrieved-document PII out of deliverables and eval sets (§2).
