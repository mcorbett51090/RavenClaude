---
name: build-rag-eval
description: "Build a judgment set and measure recall@k, precision@k, faithfulness, and answer-relevance with a baseline. Reach for this before shipping any change."
---

# Skill: Build RAG eval

A RAG system without an offline eval is shipping on vibes (§3 #3).

## Step 1 — Build the judgment set
Representative queries with the relevant passages and ideal answers labeled (§3 #3).

## Step 2 — Measure retrieval
Recall@k and precision@k via `ai_rag_engineering_calc.py retrieval-eval` (§3 #1 #3).

## Step 3 — Measure generation
Faithfulness (grounded?) and answer-relevance (addresses query?) (§3 #3 #7).

## Step 4 — Baseline before changing
Record the baseline; every change reports a before/after delta — no eval, no ship (§3 #3).

## Output
An eval harness with recall@k, precision@k, faithfulness, answer-relevance, and a baseline. Traverse Tree 1 in the decision-trees file.
