---
name: pricing-model-selection
description: "Choose the pricing model — subscription, per-seat, usage/consumption, tiered, flat-rate, freemium, or hybrid — by tracing the value of the product against consumption variance and acquisition needs. Reach for this when a product needs its first model, when a per-seat model is capping growth, or when an AI/usage-cost feature breaks the existing model. Pairs with value-metric-design (decide the metric alongside the model)."
---

# Skill: Pricing-Model Selection

The pricing model is *how* the customer is charged. It is downstream of the value
metric (what you charge *per*) — so sketch the metric (see `value-metric-design`)
before locking the model. This skill traces a product to its best-fit model and
names the runner-up.

## Step 0 — One opinion up front
**Hybrid is the default answer for anything consumption-driven.** A committed base
fee + an included allowance + metered overage gives the vendor a revenue floor and
the customer a predictable bill while still aligning price with value at the margin.
Reach for a *pure* model only when the product is genuinely simple (flat capability,
predictable use) or genuinely metered (clean per-event value).

## Step 1 — Characterize the value delivery
Answer three questions:
1. **Is value continuous (ongoing) or one-time/episodic?** Continuous → subscription
   family; episodic → transactional; one-time → perpetual + maintenance.
2. **How much does consumption vary across customers?** Low variance → seat or
   flat/tiered; high variance → usage or hybrid.
3. **Does value scale with the number of people, or with the capability itself?**
   People → per-seat; capability → flat-rate/tiered.

## Step 2 — Run the model-selection tree
Traverse [`../../knowledge/pricing-decision-trees.md`](../../knowledge/pricing-decision-trees.md) §1
to a leaf. Record the path you took.

## Step 3 — Apply the model-specific cautions
- **Per-seat:** caps at seat count and can *penalize adoption* (teams ration logins).
  If AI does the work, per-seat shrinks the account as the product succeeds — reconsider.
- **Usage-based:** bill-shock risk + unpredictable revenue. Add an included allowance,
  caps, and usage alerts; consider the hybrid instead.
- **Freemium:** a model only with a *measured conversion path* AND a *bounded
  cost-to-serve*. Absent either, use a time-boxed free trial.
- **Hybrid:** size the included allowance to the median customer; price overage to be
  felt but not punitive.

## Step 4 — Stress-test against the failure question
Ask: *"If this product becomes 10× more valuable to the customer, does our revenue
grow with it?"* If the model says no, you've picked a metric/model that caps the
company — go back to Step 1.

## Step 5 — Hand off
- The **dollar impact** (LTV, margin, cash) of the chosen model → `finance`.
- The **value metric** decision → `value-metric-design` (do it alongside, not after).
- WTP validation of the price points the model implies → `willingness-to-pay-research`.

## Output
A model recommendation with: the tree path, the runner-up and why it lost, the
model-specific cautions that apply, and the failure-question check.
