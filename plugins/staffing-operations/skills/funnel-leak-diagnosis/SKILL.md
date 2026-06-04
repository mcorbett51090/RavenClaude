---
name: funnel-leak-diagnosis
description: Locate where the recruiting pipeline leaks by decomposing it stage by stage (order to workable to submittal to interview to offer to accept to start to billing), naming the leak stage and its likely cause. Reach for this when placements or submittal-to-fill are down and you need to find where candidates fall out.
---

# Skill: Funnel-leak diagnosis

Placements are down — but "down" is a number, and the fix lives at a *stage*. This skill finds the stage before anyone proposes a remedy.

## Step 1 — Lay out the full funnel
order → **workable** → submittal → interview → offer → accept → **start (post-credentialing)** → billing/extension. The two bolded transitions are the ones generalists skip and where staffing leaks most.

## Step 2 — Compute each stage's conversion
For the period in question and a healthy baseline period, compute the conversion at each transition. The leak is the stage whose conversion dropped most vs. baseline — not the stage with the lowest absolute conversion (some stages are always lossy).

## Step 3 — Clean the first denominator
Order → workable: strip dead/on-hold/uncompetitive orders. A desk drowning in dead orders looks like it has a sourcing leak when it has an intake problem.

## Step 4 — Read the leak stage's signature
| Leak stage | Likely cause | Pull |
|---|---|---|
| Workable→submittal | supply gap or recruiter capacity | submittals-per-workable-order; reqs-per-recruiter |
| Submittal→interview | submittal quality or client/MSP latency | submittal-to-interview (~3:1 `[ESTIMATE]`); time-to-present |
| Interview→offer | fit, or competing-offer loss on speed | interview-to-offer; competitor time-to-fill |
| Offer→accept | uncompetitive package or slow close | offer-acceptance; offer-to-accept latency |
| Accept→start | credentialing/clearance fallout | fall-off rate; credentialing turnaround (§3 #7) |
| Start→billing | early termination / missed extension | completion; extension; redeployment |

## Step 5 — Check speed alongside conversion
A funnel that converts well but slowly still loses placements — the fast submittal wins when two agencies work the same order (§3 #2). If conversion is fine but speed lags, the leak is latency, not quality.

## Step 6 — Separate "under-fed" from "under-performing"
Before any leak is attributed to recruiters, confirm they're being fed (reqs-per-recruiter, order quality). An under-fed recruiter produces a submittal-stage "leak" that is really a supply problem (§3 #4).

## Step 7 — Name the stage and the cause, not just the number
Output: "the leak is at offer→accept (acceptance fell 62%→48% vs. Q1), most likely an uncompetitive package given the competitor's faster close" — a stage and a cause, with the confirming data named.

## Reference
Traverse the funnel in [`../../knowledge/staffing-kpi-glossary.md`](../../knowledge/staffing-kpi-glossary.md) §A and the credentialing mechanics in [`../../knowledge/credentialing-and-compliance.md`](../../knowledge/credentialing-and-compliance.md). Output template: [`../../templates/recruiting-funnel-analysis.md`](../../templates/recruiting-funnel-analysis.md).
