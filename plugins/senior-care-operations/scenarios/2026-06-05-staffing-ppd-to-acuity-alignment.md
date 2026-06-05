---
scenario_id: 2026-06-05-staffing-ppd-to-acuity-alignment
contributed_at: 2026-06-05
plugin: senior-care-operations
product: staffing
product_version: "n/a"
scope: likely-general
tags: [staffing, ppd, acuity, agency-labor, labor-cost]
confidence: medium
reviewed: false
---

## Problem

A community ran a **fixed caregiver-to-resident ratio** (a flat "1:8 days, 1:15 nights") regardless of how the resident population's acuity had drifted. Two failures showed up at once: high-acuity halls were chronically under-covered (call-light response times slipped, a survey-risk and satisfaction problem), while a lower-acuity hall was over-staffed relative to need — and the building was leaning on expensive agency labor to plug the high-acuity gap. The operator wanted to "add caregivers," but adding headcount to a fixed-ratio model just adds cost without aligning it to where the care need actually is.

## Context

- Segment: assisted-living + memory-care, ~100 residents, regional operator under budget pressure.
- Constraint: labor is the largest single expense — roughly **41% of revenue** in senior living (operators net ~15% operating profit on average), so a staffing model that mis-allocates labor is both a margin and a quality problem. Agency labor is a lagging quality indicator and a margin leak; its cost surged industry-wide in 2022 and, while it has come down, expenses remained ~200 basis points above the 2013–2021 average in 2024.
- Regulatory note: **assisted living has no federal staffing ratio** — it is state-regulated, and most states require "sufficient staffing" rather than a fixed number, with a growing number (e.g. Oregon's Acuity-Based Staffing Tool requirement) tying staffing to *resident acuity* rather than headcount. The federal **nursing-home** minimum-staffing rule (3.48 total HPRD, 0.55 RN, 2.45 NA) was finalized in 2024 but **repealed/suspended** — Public Law 119-21 §71111 bars CMS from enforcing it through Sept 30, 2034, and the interim final rule rescinding it is effective Feb 2, 2026. So for both AL and (currently) SNF, acuity-based PPD is an operational best practice, not a federal floor to copy.

## Attempts

- Tried: **converted from a fixed ratio to an acuity-weighted hours-per-resident-day (PPD) model.** Scored each resident's acuity (ADL dependence, behavioral/cognitive support, clinical tasks) into care-minute tiers, summed to required care hours per hall per shift, divided by census to get acuity-based PPD. Outcome: the model showed the high-acuity hall needed materially more PPD than the flat ratio gave it, and the low-acuity hall needed less — a reallocation, not a net add.
- Tried: **reallocated existing staff to acuity before authorizing any new hire**, and used the freed low-acuity hours to cover the high-acuity gap that agency had been filling. Outcome: agency reliance dropped, which is both a direct cost saving and a quality-stability gain (consistent caregivers).
- Tried: **modeled the residual gap** (after reallocation) as the *actual* hire need, and compared the fully-loaded cost of a permanent caregiver vs the agency rate it would displace. Outcome: the permanent hire was justified for the residual, and the agency line shrank.

## Resolution

The fix was **staffing to acuity-based PPD, not a fixed ratio** — a reallocation that closed the high-acuity coverage gap, cut agency reliance, and avoided a blanket headcount add. The output was a dated acuity-weighted PPD model per hall/shift with the agency-displacement arithmetic, not "hire more caregivers."

**Action for the next consultant hitting this pattern:** **staff to acuity-weighted PPD before adding headcount.** Score acuity into care-minute tiers, compute required PPD per hall/shift, reallocate existing hours to need first, and only then size the residual hire against the agency rate it displaces. A fixed ratio over- and under-staffs simultaneously. See [`../knowledge/senior-care-acuity-staffing-ppd-decision-tree.md`](../knowledge/senior-care-acuity-staffing-ppd-decision-tree.md) and the [`../scripts/senior_calc.py`](../scripts/senior_calc.py) `ppd-staffing` and `agency-vs-hire` modes.

**Sources (retrieved 2026-06-05):**
- zumBrunnen — 2025 Senior Living Industry Performance Trends (labor ~41% of revenue, ~15% operating profit, agency cost trend): https://zumbrunnen.com/financial-performance-trends-in-senior-living-a-balancing-act/
- Oregon DHS — Acuity-Based Staffing (state ABST requirement; no federal AL ratio): https://www.oregon.gov/odhs/licensing/community-based-care/pages/acuity-based-staffing.aspx
- CMS — FY2026 / staffing-rule repeal context (3.48 HPRD rule rescinded; enforcement barred to 2034): https://www.cms.gov/newsroom/fact-sheets/medicare-and-medicaid-programs-minimum-staffing-standards-long-term-care-facilities-and-medicaid-0 ; AHA — CMS repeals minimum staffing requirements: https://www.aha.org/news/headline/2025-12-02-cms-repeals-minimum-staffing-requirements-skilled-nursing-long-term-care-facilities

Staffing rules and the federal-rule status are date- and state-volatile — treat as `[verify-at-use]`; confirm the resident state's current AL/SNF staffing regulation and the live federal-rule status before any deliverable (§3 #8). Clinical acuity determinations route to the qualified clinician (§2).
