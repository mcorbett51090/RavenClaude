# Platform Engineering (IDP) Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible benchmarks come from

DORA bands, lead-time, and adoption benchmarks are **org-size-, domain-, and year-specific** and move with each annual State of DevOps report. The most defensible source is the org's own trailing delivery telemetry; published bands are a directional frame. **Name the source and date, or mark the figure `[unverified — training knowledge]` (§3 #8).**

> **Dated correction (2026-09-23):** DORA's 2025 report dropped the elite/high/medium/low tier structure the "Elite ___" framing below assumes, replacing it with seven team archetypes, and expanded to 5 metrics — adding deployment rework rate and renaming MTTR to "failed deployment recovery time" (regrouped as a throughput metric) `[re-verified 2026-09-23; CD Foundation "The DORA 4 key metrics become 5", 2025-10-16; dora.dev metrics history]`. The rows below are kept as **directional/illustrative frames only** (per this file's own caveat) — for a current classification, cite the org's own trailing telemetry against the *current* DORA report, not a fixed "elite" threshold.

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Elite deploy frequency | Often framed as on-demand / multiple per day | Classify against the current annual report, dated |
| Elite lead time | Often framed as under a day | Verify the band for the report year |
| Elite failed deployment recovery time (formerly "MTTR") | Often framed as under an hour | Verify the band for the report year; DORA's 2025 report reports this as a throughput metric, not stability |
| Golden-path adoption | No universal target; track the trend + gap | Derive from the org's own on-path definition |

## Operating rhythm

- **Platform product review** monthly — adoption trend, the gap backlog, and survey signal (§3 #1 #7).
- **DORA read** per release window, classified against a dated source (§3 #3).
- **SLO/error-budget review** per window; gate platform change when the budget is spent (§3 #6).

## The standing caution

Security/compliance determinations, license obligations, and production incident command are **the qualified authority's** call — the team frames the decision and routes it. Keep internal credentials, service-account secrets, and contributor PII out of deliverables (§2).
