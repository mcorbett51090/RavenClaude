---
name: willingness-to-pay-research
description: "Design a willingness-to-pay study — Van Westendorp PSM, Gabor-Granger, conjoint/MaxDiff, or a live price A/B test — choosing the method by the decision it serves and the data available, with sample-frame and bias guards. Reach for this before setting a price number, when defending a price, or when stated WTP and behavior disagree. Routes statistical significance to applied-statistics."
---

# Skill: Willingness-to-Pay Research

A price with no WTP evidence is a guess wearing a number. This skill picks the
research method, designs it with the right guards, and routes the significance read
to `applied-statistics`.

## Step 0 — Two guards that apply to every survey method
1. **Stated WTP overstates real WTP.** People say they'll pay more than they do.
   Discount survey numbers toward any behavioral data you have.
2. **Ask the buyer, not just the user.** In B2B the budget holder and the user are
   often different; a study that surveys only users mis-reads the budget.

## Step 1 — Pick the method by the decision
Run [`../../knowledge/pricing-decision-trees.md`](../../knowledge/pricing-decision-trees.md) §3:
- **Need a rough acceptable range, early & cheap?** → **Van Westendorp PSM** (the four
  price-perception questions → acceptable range + too-cheap/too-expensive points).
  *Returns a range, not a price.*
- **Picking a number once you have a band?** → **Gabor-Granger** (purchase intent at
  set price points → demand + revenue curve).
- **Question is about packaging / which features drive WTP?** → **Conjoint / MaxDiff**
  (choice-based feature-price tradeoffs).
- **Have live traffic and can experiment?** → **Live price A/B test** — observed
  behavior beats every survey. Route significance to `applied-statistics`.

## Step 2 — Design the instrument
- **Sample frame:** who qualifies, how you reach them, and whether they represent the
  target segment (not just whoever answers).
- **Who to ask:** buyers (budget) for the price decision; users for the value
  perception. Often both, segmented.
- **Bias guards:** avoid anchoring (don't lead with your preferred price), randomize
  price-point order, neutral framing.
- **Sample size:** size it for the precision you need — hand the power/sizing math to
  `applied-statistics` rather than guessing.

## Step 3 — Run / spec and read
- Van Westendorp → report the acceptable range + the optimal-price-point indicators
  as a *band and a sanity check*, never as "the price."
- Gabor-Granger → plot demand and revenue curves; the revenue-maximizing point is a
  candidate, not a mandate (consider strategy, not just the curve peak).
- Conjoint → translate part-worths into which feature belongs in which tier (feed
  `packaging-and-tiering`).
- A/B test → report effect size + CI; route significance to `applied-statistics`.

## Step 4 — Discount toward behavior & bound the claim
Apply the Step-0 discount. State the confidence the evidence supports — a 40-response
Van Westendorp is a directional band, not a validated price.

## Output
A study design (method + sample frame + who-to-ask + bias guards + sample size) or,
if already run, the WTP band/curve with its confidence bound and the behavioral
discount applied. Hand the actionable band to `pricing-strategist`; hand significance
to `applied-statistics`.
