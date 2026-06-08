---
name: budget-tokens
description: "Compute cost per request and right-size the context to fewest-high-precision chunks. Reach for this on a cost/context question."
---

# Skill: Budget tokens

More context is not better, and it costs tokens (§3 #5).

## Step 1 — Count the tokens
Input (context + prompt) + output tokens per request (§3 #5).

## Step 2 — Compute cost
Tokens × per-1k price × requests via `ai_rag_engineering_calc.py token-cost`; mark prices unverified (§3 #8).

## Step 3 — Right-size context
Fewest high-precision chunks — guard against lost-in-the-middle (§3 #5).

## Step 4 — Check the fit
Confirm chunk size × top-k fits the window via `ai_rag_engineering_calc.py chunk-budget` (§3 #5).

## Output
A token-cost read and a right-sized context recommendation with the monthly projection.
