---
name: build-grant-pipeline-and-prospect-fit
description: Build a prioritized, capacity-weighted grant pipeline and decide whether to pursue each opportunity by scoring funder fit BEFORE effort and running a real go/no-go — traverse the grants-lifecycle decision tree (grant type → funder fit → go/no-go), then return a fit score per prospect, a pursue/pass verdict weighing eligibility, capacity to deliver, cost-to-apply vs expected value, and compliance burden, plus the conditions that would flip each call. Reach for this when the user asks "should we apply for this grant?", "is this funder a fit?", "build our grant pipeline", or "go/no-go on this RFP". Used by `grants-strategy-lead` (primary).
---

# Skill: build-grant-pipeline-and-prospect-fit

> **Invoked by:** `grants-strategy-lead` (primary). Also consulted by `grants-compliance-and-reporting-specialist` when a heavy compliance burden should feed back into a future go/no-go.
>
> **When to invoke:** "Should we apply for <opportunity>?"; "is this funder a fit?"; "build our grant pipeline"; "go/no-go on this RFP"; "which prospects match our program?"; any move from a funding landscape to a prioritized pursue/pass decision.
>
> **Output:** a fit score per prospect + a go/no-go verdict + a prioritized, capacity-weighted pipeline + the 1-2 flip conditions per call.

## Procedure

1. **Restate the program and the prospect universe.** Capture the program (its need, activities, target population, geography, and the org's real *delivery* capacity + budget) and the prospects in scope (federal / state / foundation / corporate). Fit is measured against the program, so name the program precisely first.
2. **Classify each opportunity in the tree's terms.** Grant type (federal / state / foundation / corporate; project vs general-operating vs capacity; competitive vs formula) sets the compliance weight before anything else — traverse [`../../knowledge/grants-lifecycle-decision-tree.md`](../../knowledge/grants-lifecycle-decision-tree.md).
3. **Score funder fit — before effort.** Rate alignment on **mission**, **geography**, **population served**, **funding type** (does the funder give the *kind* of support you need — project vs operating vs capacity), and **typical award size** vs your ask. Call out the *weak* dimensions explicitly; a high-dollar misaligned funder is negative ROI even if won.
4. **Run the go/no-go gate.** For each aligned prospect weigh: **eligibility** (are you even allowed to apply?), **capacity to deliver** (not just to write the proposal), **cost-to-apply vs expected value** (effort × win-probability × award size), and the **compliance burden** the award would create. Recommend **PASS** when the math says pass — a documented pass is a win, not a failure.
5. **Prioritize into a pipeline.** Sequence the pursues against real capacity and deadlines — you cannot write ten strong proposals at once. Rank by expected value adjusted for effort and win-probability; stagger deadlines; mark the must-win vs the stretch.
6. **State the flip conditions.** For each borderline call, name the 1-2 facts that would change it (e.g., "if the cost-match must be cash not in-kind, we pass"; "if we can partner to add the missing capacity, this flips to pursue").
7. **Hand off.** Pursues go to [`write-and-assemble-grant-proposals`](../write-and-assemble-grant-proposals/SKILL.md) to build the case; flag any compliance commitment that needs a pre-check with the compliance specialist.

## Worked example

> User: "We run an after-school literacy program in two rural counties. Here are five grants — which do we go after?"

- **Program:** rural K-8 literacy, two counties, capacity to serve ~200 students, small team (delivery capacity is the binding constraint).
- **Fit scoring:** a state Dept-of-Ed **formula** literacy grant scores high on mission/geography/population and gives *project* support → strong fit. A national foundation funding *urban* youth scores low on geography → **weak fit, likely pass** despite a big number. A corporate STEM sponsorship is off-mission (literacy ≠ STEM) → pass.
- **Go/no-go:** the state grant is eligible, deliverable at current capacity, low cost-to-apply, moderate compliance (pass-through federal → 2 CFR 200 flows down — note the burden) → **PURSUE**. A federal competitive grant requiring a full RCT evaluation exceeds the team's *delivery + evaluation* capacity → **PASS this cycle**, revisit if an evaluation partner joins.
- **Pipeline:** #1 state formula grant (must-win, nearest deadline); #2 a regional foundation project grant (aligned, winnable); hold the federal competitive as a next-year stretch with a partner.
- **Flip condition:** if a university evaluation partner commits, the federal competitive flips to pursue.

## Guardrails

- **Fit before effort** — never score-to-pursue a misaligned funder because the dollar amount is attractive; that's mission drift with a compliance tax.
- **The go/no-go is a real gate** — a documented PASS is the correct output when eligibility/capacity/value/burden don't clear.
- **Capacity to *deliver*, not just to write** — winning a grant you can't execute is a compliance and reputation liability.
- **Sequence against real capacity** — a pipeline that assumes infinite writing/delivery bandwidth is fiction.
- Individual/major-donor cultivation is **not** this skill → route to `nonprofit-fundraising`.
- Volatile funder facts (deadlines, eligibility, portal steps) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/grants-management-patterns-2026.md`](../../knowledge/grants-management-patterns-2026.md). **Not legal/accounting advice.**
