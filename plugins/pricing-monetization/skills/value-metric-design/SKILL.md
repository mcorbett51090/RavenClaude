---
name: value-metric-design
description: "Choose the value metric — what you charge per (seats, usage units, records, transactions, outcomes) — the single highest-leverage pricing decision. Reach for this when a product's metric caps growth, when expansion isn't automatic, or before setting any price number. Scores candidate metrics on value-alignment, expansion-with-success, and budget-predictability."
---

# Skill: Value-Metric Design

The value metric is *what you charge per*. It is the highest-leverage decision in
pricing — a right metric makes expansion automatic; a wrong one caps the company
forever. Decide it **before** the number.

## Step 0 — The three tests every value metric must pass
A strong value metric is simultaneously:
1. **Value-aligned** — it tracks the value the customer captures (not your cost).
2. **Expanding** — it grows as the customer becomes more successful (so expansion is
   automatic, not a re-sell).
3. **Predictable** — the customer can forecast and budget it (no bill shock).

These trade off. The most value-aligned metric is often the least predictable.

## Step 1 — Enumerate candidate metrics
List every plausible per-unit: seats, active users, API calls, GB stored/processed,
records/contacts, transactions, monetary volume processed, outcomes (resolved
tickets, qualified leads), workspaces/projects. Don't pre-filter yet.

## Step 2 — Score each candidate through the tree
Run each candidate through [`../../knowledge/pricing-decision-trees.md`](../../knowledge/pricing-decision-trees.md) §2.
Reject cost proxies. Flag the bill-shock risks. Note which metrics the customer can
*game down* (e.g. deactivating "active users") — those leak revenue.

## Step 3 — Resolve the alignment-vs-predictability tension
The usual resolution: **a steady metric for the base + a value-aligned metric for
expansion.** E.g. price the platform on seats/workspaces (predictable) and the
consumption on usage (aligned) — the hybrid pattern. Don't force one metric to do
both jobs if they conflict.

## Step 4 — Run the failure question
*"If this product becomes 10× more valuable, does our revenue grow with it?"* A metric
that answers no caps the business — discard it however convenient it is to bill.

## Step 5 — Validate, then set tiers
Hand the chosen metric to `willingness-to-pay-research` to find the price points, then
to `packaging-and-tiering` to fence the tiers along the metric.

## Output
A value-metric recommendation with: each candidate's three-test score, the
gaming/bill-shock risks, how the alignment-vs-predictability tension was resolved, and
the failure-question result. Name the *one* metric (or the base+expansion pair) you'd
bet the business on.
