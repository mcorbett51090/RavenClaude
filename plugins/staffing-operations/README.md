# staffing-operations

A healthcare + education **staffing operations & analytics consulting** plugin for Claude Code. Six specialist agents, ten skills, ten templates, five commands, an advisory anti-pattern hook, and a research-grounded knowledge bank — built so a solo consultant can walk into a staffing-firm engagement already grounded in the KPIs, the segment economics, the 2023–2026 trends, the competitor map, and (for a Soliant-shaped client) the employer profile.

Vertical-explicit (staffing) but segment-flexible: travel / per-diem / locum / direct-hire / school-based. Inherits the `ravenclaude-core` protocols (Capability Grounding, Structured Output).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install staffing-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## The team

| Agent | Owns |
|---|---|
| `staffing-engagement-lead` | Scopes the engagement, routes to specialists, synthesizes the board-ready readout |
| `staffing-operations-analyst` | KPI definitions, scorecards, fill-rate & margin diagnostics, recruiter productivity |
| `recruiting-funnel-strategist` | Pipeline leaks, req aging, conversion ratios, desk capacity, redeployment |
| `healthcare-staffing-specialist` | Travel/locum/allied/per-diem economics, bill/pay/burden, credentialing |
| `education-staffing-specialist` | School-based roles, IDEA/IEP compliance, academic-calendar seasonality, teletherapy |
| `workforce-market-analyst` | Market sizing, trend analysis, competitor intelligence, benchmarking |

## Commands

- `/staffing-operations:build-staffing-scorecard` — a scorecard where every KPI has definition, window, baseline, owner, and a triggered action
- `/staffing-operations:diagnose-fill-rate` — fill-rate diagnosis in the order that prevents the wrong fix
- `/staffing-operations:analyze-recruiter-productivity` — under-fed vs. under-performing, normalized for req supply
- `/staffing-operations:competitive-brief` — segment-by-segment positioning with a where-to-play call
- `/staffing-operations:market-trend-readout` — SIA-anchored, triangulated, inflection-named trend read

## What's inside

- **`knowledge/`** — staffing KPI glossary (~30 metrics with formulas/benchmarks), healthcare economics, credentialing & compliance, education fundamentals, 2023–2026 market trends + sizing, competitor landscape, a Soliant Health employer profile, and the diagnostic decision trees. Every external figure carries a source + retrieval date; advisory numbers are marked `[ESTIMATE]`.
- **`skills/`** — scorecard build, fill-rate diagnostics, dashboard design, funnel-leak diagnosis, recruiter-capacity model, bill-rate/margin modeling, credentialing-pipeline design, seasonality-aligned readout, competitive-positioning analysis, trend-analysis readout.
- **`templates/`** — scorecard, dashboard spec, funnel analysis, margin model, competitive brief, trend readout, engagement SOW, discovery questionnaire, exec readout, weekly ops review.
- **`bi-report/data.json`** — synthetic, de-identified demo data shaping the dashboard tiles.
- **`hooks/`** — an advisory PostToolUse hook that flags fill-rate-without-time-to-fill, margin-without-bill/pay/burden, unsourced market numbers, and PII shapes (`STAFFING_OPS_STRICT=1` to block).
- **`best-practices/`** — seven named, citable rules distilled from the knowledge bank.

## The standing biases (constitution §3)

Every KPI ships with a definition, window, and baseline. Fill rate pairs with time-to-fill; margin decomposes into bill − pay − burden. Diagnose the funnel before blaming the recruiter. Seasonality is structural — align to the cycle, not the calendar quarter. Credentialing time is part of time-to-fill. Compliance is the product in these two segments. Cite the source and date for every external number. No candidate/client PII in deliverables.

## A note on the Soliant client context

The bundled employer profile reflects research as of 2026-06: Soliant's current parent is **The Vistria Group** (PE, since July 2024) — *not* Adecco (that lineage ended in 2020). Education (K-12 special education) is ~75% of revenue / ~80% of EBITDA, so the school-based book is the strategic core despite "Health" in the name. Several figures could not be read first-hand and are flagged `[unverified]` in [`knowledge/soliant-company-profile.md`](knowledge/soliant-company-profile.md) — confirm them directly before client-facing use.

## License

MIT. The marketplace is private by default; remove the `email` field from manifests before any public push.
