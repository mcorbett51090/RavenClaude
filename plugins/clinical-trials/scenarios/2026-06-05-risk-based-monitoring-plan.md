---
scenario_id: 2026-06-05-risk-based-monitoring-plan
contributed_at: 2026-06-05
plugin: clinical-trials
product: monitoring
product_version: "n/a"
scope: likely-general
tags: [risk-based-monitoring, ich-e6r3, centralized-monitoring, sdv, quality-by-design]
confidence: medium
reviewed: false
---

## Problem

A sponsor was scoping the monitoring budget for a new multi-site trial and had defaulted to **100% on-site source data verification (SDV)** — the historical reflex. The CRO bid came back with a monitoring line item that consumed a large share of the trial budget. The ask: is 100% SDV still the right default under the current GCP framework, or is it spending heavily to verify data that verification barely touches? This is decision-support for the sponsor's clinical-ops lead — the plugin makes no monitoring determination (CLAUDE.md §2).

## Context

- Segment: multi-site interventional trial, moderate complexity, electronic data capture in place.
- Constraint: the relevant framework moved. **ICH E6(R3)** was adopted **6 January 2025** and entered into force **23 July 2025**; the **FDA issued its final E6(R3) guidance in September 2025** [verify-at-use]. R3 formalizes **risk-proportionate, quality-by-design** monitoring and a shift toward **centralized + targeted** oversight, explicitly away from one-size-fits-all 100% SDV.
- 100% SDV is also a weak quality lever on the evidence: a TransCelerate analysis found SDV impacts on average only **~1% of site-entered CRF data**, and only **~2.4% of critical-data queries** were SDV-driven, while 100% SDV is estimated to consume **~25–40% of trial cost** [verify-at-use]. The team was budgeting the most expensive control for the least marginal quality.

## Attempts

- Tried: grounded the framework change rather than asserting it from memory — confirmed the R3 dates and the risk-proportionate framing against current sources before recommending anything (volatile regulatory facts get a date + `[verify-at-use]`, CLAUDE.md §3 #8). Outcome: established that "100% SDV by default" is no longer the framework's expectation.
- Tried: ran a **risk-assessment-first** read — identified the trial's *critical data* and *critical processes* (the endpoints, eligibility, consent, safety reporting) and proposed concentrating verification there, with **centralized/statistical monitoring** to flag outlier sites and **targeted on-site visits** triggered by risk signals (a deviation cluster, an enrollment anomaly), rather than a flat per-site schedule. Outcome: a risk-proportionate monitoring plan skeleton, not a flat-SDV bid.
- Tried (the move that worked): translated the shift into the budget — reallocate from blanket on-site SDV toward centralized monitoring + risk-triggered visits, with the SDV percentage *set by data criticality*. Paired it with the [`../knowledge/trials-monitoring-intensity-decision-tree.md`](../knowledge/trials-monitoring-intensity-decision-tree.md) so the intensity decision is a documented traversal, not a reflex. Outcome: a defensible, R3-aligned monitoring plan that the sponsor could right-size to the trial's actual risk.

## Resolution

100% SDV was the wrong default under ICH E6(R3): the framework expects **risk-proportionate, quality-by-design** monitoring, and the evidence shows SDV touches ~1% of data while consuming a large share of cost. The fix was a risk-assessment-first plan — verify *critical* data intensively, use centralized monitoring to find the sites that need an on-site visit, and trigger on-site intensity from risk signals rather than a flat schedule.

**Action for the next consultant hitting this pattern:** don't budget 100% SDV by reflex. Start from a **risk assessment** of the trial's critical data and processes (the R3 / RBM core), default to centralized + targeted monitoring, and let **data criticality set the SDV percentage**. Date the R3 facts (`[verify-at-use]` — R3 in force 2025-07-23; FDA final guidance Sept 2025) and confirm against the current guidance and the sponsor's SOPs. Cross-reference [`../knowledge/trials-monitoring-intensity-decision-tree.md`](../knowledge/trials-monitoring-intensity-decision-tree.md).

**Sources (retrieved 2026-06-05):**
- ICH — *Guideline for Good Clinical Practice E6(R3), Step 4 Final* (adoption 2025-01-06): https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf
- FDA — *E6(R3) Good Clinical Practice (GCP)* guidance (Sept 2025): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e6r3-good-clinical-practice-gcp
- ACRP — *FDA Publishes ICH E6(R3): What it Means for U.S. Clinical Trials* (in-force date, RBM): https://acrpnet.org/2025/09/16/fda-publishes-ich-e6r3-what-it-means-for-u-s-clinical-trials
- Applied Clinical Trials — *Risk-Based Monitoring Versus Source Data Verification* (SDV ~1% of data, cost share): https://www.appliedclinicaltrialsonline.com/view/risk-based-monitoring-versus-source-data-verification

Regulatory dates and SDV statistics are volatile / source-dependent — every figure carries a retrieval date and a `[verify-at-use]`; confirm against the current ICH/FDA text before any deliverable (CLAUDE.md §3 #8).
