---
scenario_id: 2026-06-08-dirty-data-faked-the-funnel
contributed_at: 2026-06-08
plugin: marketing-operations
product: data-hygiene
product_version: "n/a"
scope: likely-general
tags: [data-hygiene, dedup, utm, attribution-integrity]
confidence: medium
reviewed: false
---

## Problem

A team built a quarterly funnel and CAC report on raw marketing-automation data and made budget calls from it. The risk: duplicate leads and inconsistent UTM tagging corrupt every conversion rate and attribution number downstream, so confident decisions rest on fiction (§3 #7).

## Context

- Motion: high-volume inbound with multiple form entry points.
- Constraint: data hygiene, dedup, and tracking integrity precede any analysis (§3 #7).
- The team reasoned from un-audited raw data.

## Attempts

- Tried: **measured the duplicate-lead rate first** (`audit-attribution-data`). Outcome: a double-digit duplicate rate was inflating lead counts and depressing every conversion rate.
- Tried: **audited UTM coverage** (§3 #2 #7). Outcome: a large share of touches were untagged or mixed-case, making channel attribution non-computable.
- Tried: **gated the analysis until hygiene cleared** (§3 #7). Outcome: post-dedup, the funnel rates and CAC moved materially — the original report had been wrong.

## Resolution

The fix was a **dedup + UTM-taxonomy enforcement pass before any reporting**, then a re-run of the funnel and CAC on clean data — **not** trusting the original numbers. The output was the data-integrity report and the corrected metrics.

**Action for the next consultant hitting this pattern:** **audit dedup and tracking integrity before you trust any funnel or ROI number.** A double-digit duplicate rate or untagged touches make the whole report fiction; fix the plumbing first. See Tree 3 and the `audit-attribution-data` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
