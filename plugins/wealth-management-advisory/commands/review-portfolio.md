---
description: "Run a complete portfolio review against the client's IPS: drift analysis, rebalance-now-or-not decision, performance narrative with benchmark and disclosure, fee analysis, and rebalancing trade rationale if applicable. Output is advisor-prep narrative; never guarantees returns."
argument-hint: "[portfolio snapshot, e.g. 'IPS: 60/40, current: 68/32, YTD +6.2% vs. 60/40 blended benchmark +5.8%, client: 58-year-old, 7 years to retirement']"
---

You are running `/wealth-management-advisory:review-portfolio`. Use the `portfolio-review-analyst`
discipline and the `portfolio-review-and-rebalancing` skill.

## Steps

1. From the input, extract: IPS target allocation and tolerance bands, current allocation,
   review period, benchmark(s), client life stage and time horizon.
2. Run the **drift analysis** (Step 2 of the skill): compute drift per asset class vs. IPS target;
   compare to tolerance bands; identify which classes are outside tolerance and by how much.
3. Traverse the **rebalance-now-or-not decision tree** in
   `knowledge/advisory-decision-trees.md` top-to-bottom — land on one of the four outcomes
   (rebalance now / tax-managed drift-back / monitor / IPS update needed) and record the path taken.
4. Write the **performance narrative** (Step 4): period, benchmark with rationale, return
   attribution (allocation vs. selection), forward framing grounded in the IPS mandate.
   Include the mandatory past-performance disclosure: "Past performance does not guarantee
   future results."
5. Run the **fee analysis** (Step 5): weighted average expense ratio, advisory fee, total cost
   of ownership, any legacy product cost flag.
6. If rebalancing is recommended, write the **rebalancing trade rationale** (Step 6): which
   positions to trim/add, tax-sequencing note, documented rationale statement.
7. Flag any product recommendation in the rebalancing for `advisory-compliance-advisor` Reg BI
   review. Add the "not personalized investment advice" framing on the draft narrative.
8. Emit the Structured Output block with the review narrative, rebalancing decision, and
   handoff recommendations.
