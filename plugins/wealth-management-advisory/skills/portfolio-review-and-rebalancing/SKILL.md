---
name: portfolio-review-and-rebalancing
description: "Run a complete portfolio review: assess allocation against the IPS, traverse the rebalance-now-or-not decision tree, write the performance narrative with proper disclosures, analyze fee drag, and produce a rebalancing rationale or IPS update recommendation. Output is advisor-prep work; never guarantees returns."
---

# Portfolio Review and Rebalancing

**Purpose:** help the advisor conduct a disciplined, IPS-anchored portfolio review — from drift
analysis through the rebalancing decision narrative and performance commentary — so every portfolio
action is traceable to the client's investment policy and the rationale is documented.

---

## The review operating loop

### Step 1 — Retrieve and verify the IPS

Before touching any allocation data:
- Pull the client's current IPS (or draft one using
  [`../../templates/investment-policy-statement.md`](../../templates/investment-policy-statement.md)
  if one doesn't exist).
- Confirm: target allocation, tolerance bands (e.g., ±5% for equities), prohibited investments,
  benchmark(s), rebalancing trigger policy (calendar, threshold, or hybrid).
- If the IPS is stale (>2 years since last update or a major life event has occurred), flag for
  update before the review proceeds.

### Step 2 — Drift analysis

Measure current allocation vs. IPS target:
- Calculate current weights across asset classes (domestic equity, international equity, fixed
  income, alternatives, cash).
- Compute drift: `current_weight − target_weight` in percentage points.
- Compare drift to IPS tolerance bands.
- Identify which asset classes are outside tolerance and by how much.
- Note the direction: over-weight risk assets (equity-rich drift) vs. under-weight (de-risked drift).

### Step 3 — Rebalance-now-or-not decision

Traverse the rebalance-now-or-not decision tree in
[`../../knowledge/advisory-decision-trees.md`](../../knowledge/advisory-decision-trees.md)
top-to-bottom before writing the narrative. The path through the tree determines the output.

Key factors to assess:
- **Drift magnitude vs. IPS tolerance:** is the portfolio outside its bands?
- **Tax cost:** are there embedded short-term gains? Long-term gains? Harvesting opportunities?
- **Time horizon:** how close is the client to a distribution event (retirement, education draw)?
- **Alternative rebalancing levers:** can drift be corrected through new contributions, RMD
  redirection, or tax-loss harvesting first?
- **Emotional context:** is the client anxious about rebalancing? Document the rationale for
  either action.

Outcome paths from the tree:
1. **Rebalance now** — drift is outside tolerance; no significant tax friction; recommend execution.
2. **Tax-managed drift-back** — drift is material but tax friction is high; use cash flows or
   harvesting to correct over 1–2 quarters.
3. **Monitor** — drift is within tolerance bands; schedule next review.
4. **IPS update needed** — client's situation has changed enough that the target allocation
   itself should be revisited before rebalancing.

### Step 4 — Performance narrative

Structure:
1. **Period and benchmark:** state the review period and the benchmark(s) used. Name the benchmark
   and explain why it is appropriate for this client's IPS. Use a blended benchmark that matches
   the IPS target allocation (e.g., "60% MSCI ACWI / 40% Bloomberg US Aggregate [verify-at-use]").
2. **Return attribution:** separate allocation effect (the IPS target drove this) from selection
   effect (fund/manager choice drove this). If a single fund or asset class dominated, name it.
3. **Forward framing:** ground the forward narrative in the IPS mandate — "the portfolio is
   positioned per the IPS to deliver [objective] over a [time horizon] horizon." Never imply a
   future return.
4. **Mandatory past-performance disclosure:** any sentence that references a historical return
   requires the disclosure: "Past performance does not guarantee future results."

### Step 5 — Fee analysis

- **Weighted average expense ratio:** sum of (position weight × fund expense ratio) across all
  holdings. Compare to a low-cost blended alternative scenario.
- **Advisor fee:** add advisory fee to arrive at total cost of ownership (expense ratio + advisory
  fee + any transaction costs).
- **Legacy product costs:** if the portfolio contains variable annuities or high-cost mutual funds,
  analyze M&E charges, internal fund expenses, surrender charge timeline, and compare to current
  alternatives — accounting for tax consequences of any switch.
- **Materiality framing:** the fee drag compounds. Quantify the long-run impact in dollar terms
  over the time horizon, not just basis points — clients understand dollars better.

### Step 6 — Rebalancing execution guidance

If rebalancing is recommended:
- Identify the trades: which holdings to trim (over-weight), which to add (under-weight).
- Tax sequencing: consider harvesting losses in over-weight positions first; prefer trimming in
  tax-advantaged accounts when possible; flag short-term vs. long-term gain positions.
- Document the rationale: "We are rebalancing from [current weight] to [target weight] in [asset
  class] because the portfolio has drifted outside its ±[X]% IPS tolerance band, and the
  rebalancing cost (estimated [$Y] in realized gains) is justified by restoring the client's
  documented risk mandate."

---

## Anti-patterns

- Rebalancing without reference to the IPS or tolerance bands.
- Performance narrative with no benchmark identification.
- Performance figures in any document without a past-performance disclosure.
- Recommending a product switch based on fee alone without suitability analysis.
- An IPS with a target allocation but no tolerance bands — without bands, drift is unmeasurable.
- Language that implies the recent performance trend will continue.

---

## Output

Portfolio review narrative (drift analysis + rebalancing decision + performance narrative + fee
analysis), rebalancing trade rationale (if applicable), or IPS update recommendation. Route any
product recommendation through `advisory-compliance-advisor` for Reg BI clearance. Use
[`../../templates/investment-policy-statement.md`](../../templates/investment-policy-statement.md)
for IPS drafts.
