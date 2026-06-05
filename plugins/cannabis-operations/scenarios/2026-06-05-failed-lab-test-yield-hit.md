---
scenario_id: 2026-06-05-failed-lab-test-yield-hit
contributed_at: 2026-06-05
plugin: cannabis-operations
product: cultivation
product_version: "n/a"
scope: segment-specific
tags: [testing, remediation, microbial, pesticide, yield, cultivation]
confidence: medium
reviewed: false
---

## Problem

A mid-size cultivator was modeling gross yield (harvest weight) as saleable yield and was repeatedly short on committed wholesale orders. The gap was **compliance testing**: a recurring share of batches failed the state's required lab panel — most often **microbial (total yeast & mold / Aspergillus)**, occasionally **pesticide/heavy-metal** — and failed product can't be sold. The operator had no test-fail rate in the cultivation economics, so every margin and yield projection was optimistic. **seed-to-sale-compliance-specialist** (testing/remediation) and **cannabis-finance-analyst** (yield economics) co-own this; outputs are decision-support, not a lab or legal opinion (CLAUDE.md §2, §3 #6).

## Context

- Segment: cultivation (segment-specific — the testing-yield reality is sharpest at the grow; a resale dispensary inherits it as supply risk, not yield).
- Constraint: states require pre-sale testing for contaminants (microbials incl. Aspergillus species, pesticides, heavy metals, residual solvents, mycotoxins) with **state-specific action levels** — California, for example, fails a sample on **any detection** of the named Aspergillus species, Salmonella, or STEC [verify-at-use]. The **remediation asymmetry is the load-bearing fact:** many **microbial** failures can be remediated (e.g. irradiation / ozonation, where the state and the buyer allow it) and the lot recovered; **pesticide** failures typically mean **destruction with no remediation path**. So a pesticide fail is a near-total loss; a microbial fail is a *cost-and-delay*, not always a write-off.
- The team also wasn't separating **failure cause** in its records, so it couldn't tell a fixable contamination-control problem from an unfixable input problem.

## Attempts

- Tried: modeling saleable yield = harvest yield. Outcome: chronic shortfalls against committed orders; margins missed every quarter.
- Tried: confirmed the framing against current sources rather than memory — required panels and **action levels are state-specific** (never generalize one state's thresholds); the **microbial-remediable vs pesticide-destroy** asymmetry holds across most programs; specific fail-rate percentages vary widely by operator, genetics, environment, and state and are **not reliably published** — so any rate used must be the operator's **own** measured rate, marked `[ESTIMATE]` until enough batches accrue. Outcome: grounded the economics on the *operator's* data, not an industry average.
- Tried (the move that worked): (1) introduced a **test-fail rate** (by cause) into the cultivation yield model so projections used *saleable* yield; (2) attacked the controllable driver — microbial — at the source (environmental controls, post-harvest handling, drying/curing humidity) rather than relying on remediation, since predominant contaminants are environment- and handling-driven; (3) built a **remediation decision step**: microbial fail → evaluate remediation (state- and buyer-permitting) before writing off; pesticide/heavy-metal fail → treat as destruction and trace the **input** (nutrient/IPM) that caused it. Outcome: projections matched reality, microbial fail rate trended down, and a fixable problem stopped being mistaken for inevitable loss.

## Resolution

The hit was an **un-modeled compliance cost**, not bad luck — harvest yield is not saleable yield until it passes the state panel. Putting a cause-tagged test-fail rate into the economics, controlling microbial contamination at the source, and adding a microbial-remediate-vs-pesticide-destroy decision step converted a chronic shortfall into a planned, shrinking line item.

**Action for the next consultant hitting this pattern:** never model harvest yield as saleable yield — subtract a **cause-tagged** test-fail rate (use the operator's own measured rate, `[ESTIMATE]` until it stabilizes). Separate **microbial** (often remediable, a cost+delay) from **pesticide/heavy-metal** (usually destruction). Confirm the **state's** required panel, action levels, and whether remediation is *permitted for resale* before recommending it (`[verify-at-use]` — both vary by state, CLAUDE.md §3 #3). Frame as decision-support; route regulated-record or diversion questions to `ravenclaude-core` `security-reviewer` (CLAUDE.md §2).

**Sources (retrieved 2026-06-05):**
- Colorado Dept. of Public Health & Environment — marijuana microbial pathogen & TYM reference: https://cdphe.colorado.gov/laboratory-home/certification-of-cannabis-testing-facilities/cannabis-reference-library/marijuana
- Medicinal Genomics — Cannabis Microbial Testing Regulations by State (state-by-state panels/action levels): https://medicinalgenomics.com/resource/cannabis-microbial-testing-regulations-by-state/
- Frontiers in Microbiology — Total yeast & mold in high-THC cannabis (genotype/environment/handling drivers): https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2023.1192035/full

Required panels, action levels, and remediation-permissibility are **state-specific and volatile**; specific fail-rate percentages are operator-dependent and not reliably published — `[verify-at-use]` / `[ESTIMATE]` against the operator's own lab data and state regulator before any deliverable (CLAUDE.md §3 #3, #6, #8).
