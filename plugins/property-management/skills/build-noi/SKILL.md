---
name: build-noi
description: "Build the EGI-to-NOI bridge from gross potential rent and translate to value at a cap rate. Reach for this on an NOI or valuation question."
---

# Skill: Build NOI

Gross rent is not the scorecard — NOI is (§3 #4).

## Step 1 — Set gross potential rent
GPR at asking, the starting line for the bridge.

## Step 2 — Subtract vacancy and loss
Vacancy, loss-to-lease, concessions, bad debt → effective gross income (§3 #5).

## Step 3 — Add other income, subtract opex
Other income in, operating expense out, capex below the line via `property_management_calc.py noi` (§3 #4 #7).

## Step 4 — Translate to value
NOI ÷ cap rate, with the cap-rate source + date marked (§3 #8).

## Output
An EGI-to-NOI bridge with optional cap-rate value, each line baselined. Traverse Tree 1 in the decision-trees file.
