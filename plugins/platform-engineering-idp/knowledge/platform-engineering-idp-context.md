# Platform Engineering (IDP) Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible benchmarks come from

DORA bands, lead-time, and adoption benchmarks are **org-size-, domain-, and year-specific** and move with each annual State of DevOps report. The most defensible source is the org's own trailing delivery telemetry; published bands are a directional frame. **Name the source and date, or mark the figure `[unverified — training knowledge]` (§3 #8).**

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Elite deploy frequency | Often framed as on-demand / multiple per day | Classify against the current annual report, dated |
| Elite lead time | Often framed as under a day | Verify the band for the report year |
| Elite MTTR | Often framed as under an hour | Verify the band for the report year |
| Golden-path adoption | No universal target; track the trend + gap | Derive from the org's own on-path definition |

## Operating rhythm

- **Platform product review** monthly — adoption trend, the gap backlog, and survey signal (§3 #1 #7).
- **DORA read** per release window, classified against a dated source (§3 #3).
- **SLO/error-budget review** per window; gate platform change when the budget is spent (§3 #6).

## The standing caution

Security/compliance determinations, license obligations, and production incident command are **the qualified authority's** call — the team frames the decision and routes it. Keep internal credentials, service-account secrets, and contributor PII out of deliverables (§2).
