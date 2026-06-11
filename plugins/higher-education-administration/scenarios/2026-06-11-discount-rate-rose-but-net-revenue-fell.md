---
scenario_id: 2026-06-11-discount-rate-rose-but-net-revenue-fell
contributed_at: 2026-06-11
plugin: higher-education-administration
product: enrollment-and-financial-aid
product_version: "n/a"
scope: likely-general
tags: [net-tuition-revenue, discount-rate, yield, diminishing-returns]
confidence: medium
reviewed: false
---

## Problem

An institution celebrated its largest entering class in a decade, then found the operating budget
short. The risk: the class had been filled by raising institutional aid, and the discount rate had
climbed past the point where the marginal aid dollar still added net enrolled revenue.

## Context

- Surface: the strategic enrollment plan, evaluated on headcount and applicants.
- Constraint: net tuition revenue (gross − institutional aid), not class size, funds operations.
- The team optimized the number the board cheered (class size), not the one that pays salaries.

## Attempts

- Tried: **modeled net tuition revenue across the actual discount scenarios** via
  `higher_ed_calc.py net_tuition_revenue` and `discount_rate`. Outcome: the discount rate had risen
  from 49% to 55%; net tuition revenue per student fell enough that total net revenue dropped despite
  more students.
- Tried: **found the diminishing-returns inflection** — the last cohort of aided admits contributed
  below the cost to serve. Outcome: a clear "stop discounting here" line.
- Tried: **segmented the aid** (price- vs. fit-sensitive). Outcome: a chunk of aid had gone to
  fit-sensitive students who would have enrolled anyway — pure margin given away.

## Resolution

The fix was to **set the discount envelope against net tuition revenue, segment leveraging aid, and
exhaust non-aid yield levers first** — not to chase headcount. The output was the net-revenue model,
the diminishing-returns point, and the segmented aid recommendation.

**Action for the next consultant hitting this pattern:** **when a class grows on more discount, pull
net tuition revenue before celebrating.** A bigger class at a higher discount routinely lowers net
revenue. See `best-practices/net-tuition-revenue-is-the-real-number.md`,
`best-practices/discount-rate-has-a-diminishing-return.md`, and
`knowledge/enrollment-and-net-revenue-reference.md`.
