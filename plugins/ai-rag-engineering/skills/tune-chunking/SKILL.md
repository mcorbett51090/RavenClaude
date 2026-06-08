---
name: tune-chunking
description: "Tune chunk size, overlap, and structure-awareness against the eval and the context budget. Reach for this on a chunking question."
---

# Skill: Tune chunking

A chunk that splits the answer is a retrieval bug introduced at ingestion (§3 #2).

## Step 1 — Inspect the failing chunks
Are answering units (tables, sections) split or buried? (§3 #2)

## Step 2 — Adjust size + overlap
Tune against recall@k, not a guessed default (§3 #2).

## Step 3 — Add structure-awareness
Keep tables/sections intact; add metadata for pre-filtering (§3 #2).

## Step 4 — Check the context budget
Size × top-k + overhead vs window via `ai_rag_engineering_calc.py chunk-budget` (§3 #5).

## Output
A chunking design tied to recall@k and the context budget. Traverse Tree 2 in the decision-trees file.
