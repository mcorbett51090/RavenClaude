---
scenario_id: 2026-06-05-committed-use-and-right-sizing-overspend
contributed_at: 2026-06-05
plugin: gcp-cloud
product: billing
product_version: "unknown"
scope: likely-general
tags: [cost, committed-use, right-sizing, finops, labels, budget]
confidence: medium
reviewed: false
---

## Problem

A FinOps review of a GCP estate found compute spend ~40% higher than the workload justified, and **no one could attribute it**. Two compounding failures: (1) the team had bought **3-year committed-use discounts (CUDs)** sized to a peak-season VM fleet that had since been re-architected onto Cloud Run — so they were paying for committed GCE capacity they no longer ran, while *also* paying on-demand for the Cloud Run that replaced it; and (2) the on-demand VMs that remained were **provisioned for headroom that never materialized** (n2-standard-16 sustained at <10% CPU). Because resources were **unlabeled**, the monthly bill was one undifferentiated number and the overspend had hidden for three quarters.

## Constraints context

- Segment: a mid-size engineering org with a single billing account across ~15 projects; cost was "central IT's problem," so no team owned its own spend.
- The CUDs were a **sunk commitment** — you can't un-buy a 3-year resource-based CUD, so the answer was never "cancel it," it was "stop the bleeding going forward and don't repeat the mistake."
- No cost-allocation labels existed, so even *measuring* per-team or per-workload spend required a labeling backfill before any right-sizing decision could be defended with data.

## Attempts

- Tried: jump straight to resizing the big VMs. Outcome: premature — without labels and the actual utilization history, "it looks oversized" is a guess; a wrong downsize causes an incident and burns trust in the whole effort.
- Tried (first, the measurement layer): **label everything** with a consistent `team` / `env` / `workload` cost-allocation label scheme, backfilled across projects, then turned on a **label-filtered budget + the billing export to BigQuery** so spend could be sliced by dimension. Outcome: per-team attribution for the first time; the overspend localized to two teams and three workloads.
- Tried (right-sizing on evidence): pulled the **Recommender** right-sizing + idle-resource recommendations and cross-checked against ~30 days of utilization before acting; downsized the sustained-low VMs a tier at a time with a rollback watch, deleted genuinely-idle resources. Outcome: the on-demand half of the overspend came down without an incident.
- Tried (the commitment mistake, going forward): matched **future** CUD purchases to a **sustained-baseline** (the floor of actual usage over a quarter), not a peak — and preferred the flexibility that fits a Cloud-Run-heavy estate. Outcome: stopped buying capacity for a fleet shape the org had already moved off of.

## Resolution

The durable fix was **measure before you cut, then commit to the baseline, not the peak**: (1) a consistent cost-allocation **label** scheme + billing-export-to-BigQuery so spend is attributable per team/workload (you can't right-size what you can't see); (2) **Recommender-driven, utilization-backed** right-sizing and idle cleanup, applied incrementally with a rollback watch; (3) **commitment discipline** — size new CUDs to the sustained usage floor, not a peak that may not recur, and re-check commitments whenever the workload is re-architected. The mental model: an unattributed bill *hides* the overspend, and a commitment sized to a peak (or to an old architecture) *locks it in* — labels make it visible, Recommender + utilization make the cut defensible, and baseline-sized commitments keep the discount without the over-commit.

**Action for the next engineer hitting this pattern:** do **not** quote a savings number or resize anything until cost-allocation labels + the BigQuery billing export exist and you have ~30 days of utilization — every dollar figure here is workload-specific and must be derived from the client's own billing data, never a generic benchmark `[verify-at-use]`. Then act in order: label → attribute → Recommender-backed right-size (incrementally, with rollback) → size future commitments to the sustained baseline. Re-examine existing CUDs whenever a workload moves off the resource shape they were bought for.

Cross-reference: complements [`../knowledge/gcp-cloud-decision-trees.md`](../knowledge/gcp-cloud-decision-trees.md) `## Decision Tree: GCP billing — project, folder, or org budget?` and the best-practices [`label-everything-for-cost`](../best-practices/label-everything-for-cost.md), [`budget-alerts-per-project`](../best-practices/budget-alerts-per-project.md), and [`regional-by-default`](../best-practices/regional-by-default.md).
</content>
