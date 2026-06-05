# Senior-care staffing decision tree — staff to acuity-based PPD vs. a fixed ratio (and agency vs. permanent hire)

**Last reviewed:** 2026-06-05 · **Confidence:** medium (industry labor benchmarks + CMS/state staffing-rule status web-verified this date, cited below). Labor benchmarks and the federal-rule status are date- and state-volatile — they carry inline `[verify-at-use]` markers and must be calibrated to the resident state's current rule and the community's actual data before any deliverable (CLAUDE.md §3 #8).

> Canonical decision tree for the `senior-care-finance-analyst` (the staffing/labor model) with a clinical assist from `clinical-care-compliance-specialist` (acuity scoring routes to the qualified clinician). Traverse top-to-bottom against the observable situation **before** recommending a staffing move. The order encodes the house discipline: **align existing labor to acuity before adding net headcount, and reallocate before you hire** (CLAUDE.md §3 #3 — staff to acuity-based PPD, not a fixed ratio; §3 #6 — labor cost and turnover are unit economics). The most expensive moves (net new permanent headcount; sustained agency reliance) sit at the bottom on purpose.
>
> **This tree COMPLEMENTS [`senior-care-decision-trees.md`](senior-care-decision-trees.md)** — that file's trees cover *why occupancy is declining*, *responding to a survey deficiency*, and *whether to accept a high-acuity move-in*. This one is the **staffing/labor** companion: given the acuity you have, how do you size and source the labor to cover it.

---

## When this applies

The community is staffing to a **fixed caregiver-to-resident ratio** (or "we always run N caregivers"), care quality or call-light response is slipping on some halls while others feel over-covered, and/or the building is leaning on **agency labor** — and someone has proposed "hire more caregivers" or "add a shift." Use this before authorizing headcount: a fixed ratio over- and under-staffs at the same time, and agency is the most expensive, lowest-stability way to cover a gap.

## Regulatory frame (read first — it changed)

- **Assisted living has no federal staffing ratio.** It is state-regulated; most states require "sufficient staffing" rather than a fixed number, and a growing set (e.g. Oregon's **Acuity-Based Staffing Tool** requirement) tie staffing to *resident acuity*. So acuity-based PPD is both the operational best practice and, increasingly, the regulatory expectation — but the specific rule is the resident **state's**, not a federal one `[verify-at-use]`.
- **The federal nursing-home minimum-staffing rule is currently rescinded.** CMS finalized a 3.48 total nurse-staffing HPRD standard (incl. 0.55 RN, 2.45 NA, plus 24/7 RN) in 2024, but Public Law 119-21 §71111 **bars CMS from enforcing it through Sept 30, 2034**, and the interim final rule rescinding it is effective **Feb 2, 2026**. Do **not** cite the 3.48-HPRD numbers as a live federal floor — they are a useful *reference target* for SNF acuity modeling, not a current mandate `[verify-at-use]`.

## The tree

```mermaid
flowchart TD
    START[Care quality slipping and/or heavy agency use - someone proposes hire more caregivers] --> Q0{Is staffing set by a FIXED ratio or by acuity-based PPD?}
    Q0 -->|Fixed ratio / fixed headcount| ACUITY[Build the acuity-based PPD model first - score acuity into care-minute tiers, compute required care-hours/day per hall/shift - scripts/senior_calc.py ppd-staffing]
    Q0 -->|Already acuity-based PPD| Q1{Does total required care-hours exceed total current care-hours across the building?}
    ACUITY --> Q1
    Q1 -->|NO - enough total hours, just mis-allocated| REALLOC[Reallocate over-staffed halls to high-acuity need - no net add; this is the cheapest fix]
    Q1 -->|YES - genuine total shortfall| Q2{Is the shortfall temporary/seasonal or structural/ongoing?}
    Q2 -->|Temporary - census spike, LOA, FMLA coverage| AGENCY[Bridge with agency / overtime SHORT-TERM only - track it as a lagging quality + margin signal, set an exit date]
    Q2 -->|Structural - sustained acuity rise| Q3{Does the residual gap (after reallocation) justify a permanent FTE vs the agency rate it displaces?}
    Q3 -->|NO - sub-FTE residual| FLEX[Use a part-time / flex pool or cross-training before a full FTE]
    Q3 -->|YES - >= ~1 FTE of sustained need| HIRE[Hire permanent to the residual - model fully-loaded cost vs displaced agency spend - scripts/senior_calc.py ppd-staffing + agency comparison]
```

## Rationale per leaf (cheap → expensive)

- **Build the acuity-based PPD model first** — a fixed ratio is the root cause; you cannot size labor to need until need is expressed as acuity-weighted care-hours. Score residents into care-minute tiers (ADL dependence, behavioral/cognitive support, clinical tasks — *clinical scoring routes to the clinician*), sum to required care-hours/day per hall/shift, divide by census for the acuity-based PPD. [`../scripts/senior_calc.py`](../scripts/senior_calc.py) `ppd-staffing` does the arithmetic.
- **Reallocate over-staffed halls** — the cheapest win, and the most-missed. A fixed ratio almost always leaves a low-acuity hall over-covered while a high-acuity hall is short; moving existing hours to need closes the gap with **zero** net cost and often eliminates the agency line that was plugging the high-acuity hole.
- **Bridge with agency / overtime — short-term only** — agency labor is a **lagging quality indicator** (inconsistent caregivers erode care continuity and satisfaction) and a margin leak; its cost surged industry-wide in 2022 and, while down, ran ~200 basis points above the 2013–2021 average in 2024 `[verify-at-use]`. Use it only for a *temporary* gap with a set exit date — never as the standing answer to a structural shortfall.
- **Flex / part-time / cross-training** — for a sub-FTE residual, a flex pool or cross-trained staff beats committing a full permanent FTE you can't keep busy.
- **Hire permanent to the residual** — the most expensive, slowest-to-reverse move. Only after reallocation, and only for a *sustained* ≥~1-FTE gap. Size the hire against the **fully-loaded** cost (wage + benefits + onboarding + turnover risk) vs the agency rate it displaces — a permanent caregiver is usually cheaper *and* higher-quality than standing agency, which is the whole point of getting off agency.

## Why labor is the lever (the unit economics)

Labor is by far the largest single expense — roughly **41% of revenue** in senior living, against an average **~15% operating profit** `[verify-at-use]`. A staffing model that mis-allocates labor is therefore simultaneously a margin problem (paying for hours where they aren't needed) and a quality problem (short where they are needed) — which is why §3 #3 and §3 #6 treat staffing-to-acuity and turnover as first-class operational metrics, not HR overhead.

## Escalation & guardrails

- Acuity scoring / clinical-need determinations → the qualified clinician (the team is not a clinical authority, CLAUDE.md §2).
- The resident state's specific AL/SNF staffing regulation → confirm against the state agency; survey/regulatory determinations route there (§2).
- Staff PII / employment-law specifics → out of scope; route to the operator's HR/legal counsel.
- Every figure entering a deliverable carries a source URL + retrieval date or an `[unverified — training knowledge]` / `[ESTIMATE]` mark (CLAUDE.md §3 #8).

## Sources (retrieved 2026-06-05)

- zumBrunnen — *2025 Senior Living Industry Performance Trends* (labor ~41% of revenue, ~15% operating profit, agency cost trend): https://zumbrunnen.com/financial-performance-trends-in-senior-living-a-balancing-act/
- Oregon DHS — *Acuity-Based Staffing* (state ABST requirement; AL is state-regulated, no federal ratio): https://www.oregon.gov/odhs/licensing/community-based-care/pages/acuity-based-staffing.aspx
- CMS — *Minimum Staffing Standards for Long-Term Care Facilities* fact sheet (the 3.48-HPRD rule as finalized): https://www.cms.gov/newsroom/fact-sheets/medicare-and-medicaid-programs-minimum-staffing-standards-long-term-care-facilities-and-medicaid-0
- AHA — *CMS repeals minimum staffing requirements for skilled nursing, long-term care facilities* (rescission; enforcement barred through 2034): https://www.aha.org/news/headline/2025-12-02-cms-repeals-minimum-staffing-requirements-skilled-nursing-long-term-care-facilities
- Federal Register — *Repeal of Minimum Staffing Standards for Long-Term Care Facilities* (interim final rule, effective 2026-02-02): https://www.federalregister.gov/documents/2025/12/03/2025-21792/medicare-and-medicaid-programs-repeal-of-minimum-staffing-standards-for-long-term-care-facilities
