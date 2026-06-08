---
name: decompose-aum-growth
description: "Separate AUM growth into net new flows vs market and compute the organic growth rate. Reach for this on a growth question."
---

# Skill: Decompose AUM growth

A bull market can hide an organically shrinking practice (§3 #1 #7).

## Step 1 — Set the AUM bridge
Beginning AUM, ending AUM, net new flows, withdrawals.

## Step 2 — Separate flows from market
AUM growth − net new flows = market via `riaops_calc.py aum-revenue` (§3 #1).

## Step 3 — Compute organic growth
Net new flows ÷ beginning AUM — the real health metric (§3 #7).

## Step 4 — Read it against market
Strip market; organic growth is what survives a drawdown (§3 #7).

## Output
An AUM bridge separating net-new-vs-market with the organic growth rate. Traverse Tree 1 in the decision-trees file.
