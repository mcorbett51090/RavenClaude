---
name: diagnose-retrieval
description: "Separate retrieval failure from generation failure by measuring recall@k before touching the model. Reach for this first on wrong answers."
---

# Skill: Diagnose retrieval

If the right passage isn't retrieved, no prompt or bigger model recovers it (§3 #1).

## Step 1 — Measure recall@k
Is the relevant passage in the top-k? via `ai_rag_engineering_calc.py retrieval-eval` (§3 #1).

## Step 2 — Split the failure mode
Low recall = retrieval bug; high recall + wrong answer = generation/grounding bug (§3 #1 #7).

## Step 3 — Check hybrid
Try BM25 + vector fusion on the failing queries, especially keyword-heavy ones (§3 #6).

## Step 4 — Fix the binding stage first
Retrieval before generation — don't swap the model on a retrieval bug (§3 #1).

## Output
A failure-mode split (retrieval vs generation) with the first fix named. Traverse Tree 2 in the decision-trees file.
