# Search & Relevance Engineering Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible figures come from

Relevance benchmarks, latency targets, and engine behaviors are **corpus-, engine-version-, and date-specific**. The most defensible source is the org's own judgment list and trailing query/click logs; published targets are directional. **Name the source and date, or mark the figure `[unverified — training knowledge]` and verify against the engine's current docs (§3 #8).**

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Good NDCG | No universal threshold; track the trend vs baseline | Derive from the org's judgment list |
| p95 latency target | Often framed in the low hundreds of ms for interactive search | Set against the product's UX requirement |
| Click-derived judgments | Useful but position-biased | Debias before trusting (§3 #6) |
| Offline-to-online transfer | Often partial, sometimes none | Confirm with an A/B every time (§3 #6) |

## Operating rhythm

- **Eval-gated tuning** — no ranking, analyzer, or mapping change ships without an offline before/after on the judgment list (§3 #1 #3).
- **Mapping-first triage** — a relevance bug starts at the analyzer/mapping, not the boost (§3 #2).
- **Online A/B** for every offline win before declaring victory (§3 #6); latency held to the p95 budget (§3 #4).

## The standing caution

UX design, legal/policy, and product determinations are **the qualified authority's** call — the team frames the decision and routes it. Keep search queries, click logs, and user identifiers out of deliverables and judgment/A-B data (§2).
