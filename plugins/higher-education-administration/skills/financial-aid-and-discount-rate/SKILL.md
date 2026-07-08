---
name: financial-aid-and-discount-rate
description: "Model the tuition discount rate and net tuition revenue, and spend institutional aid as deliberate yield leverage rather than a gap-filler. Distinguishes gross vs net, aid as leverage vs entitlement. Discount-rate norms are volatile -> verify-at-use; cohort-level only, no student PII."
---

# Financial Aid & Discount Rate

The discount rate is the largest single lever on both *who* enrolls and *how much net revenue* a class produces — and it's the one most likely to drift upward one aid package at a time until it's a budget problem no one decided.

> **Advisory, not financial-aid-compliance or packaging advice.** Discount-rate norms and aid rules are volatile and institution-/regulation-specific. Every specific here is `[verify-at-use]`; individual packaging belongs to the aid office. No student PII.

## The core distinction

| Concept | Definition | Why it matters |
|---|---|---|
| Gross tuition | Sticker price × enrollment | The number that looks like revenue but isn't |
| Institutional aid (discount) | Tuition-funded grants/scholarships | Not cash out — foregone revenue |
| **Tuition discount rate** | Institutional aid ÷ gross tuition | The share of sticker you never collect |
| **Net tuition revenue** | Gross tuition − institutional aid | The number the budget actually spends |

**The rule:** model **net tuition revenue**, not gross headcount or gross tuition. A bigger class bought with a higher discount rate can produce *less* net revenue.

## Aid as leverage, not entitlement

- **Leverage** = an aid dollar placed where it changes an enrollment decision at the margin.
- **Gapping / default packaging** = aid that would have enrolled the student anyway, or a gap that costs a yield you could have kept.
- The leveraging question: for this admit segment, what is the **yield response per discount dollar**? Spend where the curve is steepest (`[verify-at-use]` — it's institution- and segment-specific).

## Metrics table

| Metric | What it tells you | Watch for |
|---|---|---|
| Tuition discount rate | Share of sticker foregone | Year-over-year creep with no strategy behind it |
| Net tuition revenue per student | Real yield of the class | Falling even as headcount rises |
| Net revenue at scenario | Class economics at each discount level | The break-even yield for a discount change |
| Aid yield response | Enrollment lift per discount dollar | Spending where the curve is flat |

## Workflow

1. Compute the current discount rate and net tuition revenue per student (attach definitions, `[verify-at-use]`).
2. Segment admits by likely yield response to aid.
3. Model net revenue at each discount scenario; state the break-even yield.
4. Recommend a discount move only where it does yield work at the margin — never as a default gap-fill.

## Anti-patterns

- Reporting gross tuition or headcount as "revenue."
- Letting the discount rate rise package-by-package with no net-revenue model.
- Aiding segments that would have enrolled anyway.

## See also

- Traverse the **discount-rate / aid-leverage decision** tree in [`../../knowledge/higher-ed-decision-trees.md`](../../knowledge/higher-ed-decision-trees.md).
- [`../enrollment-funnel-and-yield/SKILL.md`](../enrollment-funnel-and-yield/SKILL.md), [`../../templates/enrollment-funnel-model.md`](../../templates/enrollment-funnel-model.md).
- Best practices: [`../../best-practices/the-discount-rate-is-a-strategy-not-an-accident.md`](../../best-practices/the-discount-rate-is-a-strategy-not-an-accident.md), [`../../best-practices/aid-leverages-enrollment-spend-it-deliberately.md`](../../best-practices/aid-leverages-enrollment-spend-it-deliberately.md).
