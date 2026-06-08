---
name: fix-analyzer
description: "Root-cause a relevance bug in tokenization/analysis/mapping before touching the ranking formula. Reach for this on a no-match or wrong-match bug."
---

# Skill: Fix analyzer

A relevance bug is usually a mapping/analyzer bug, not a ranking tweak (§3 #2).

## Step 1 — Reproduce the match failure
Trace how the query and document are analyzed/tokenized (§3 #2).

## Step 2 — Check the mapping
Field types, analyzers, stemming, synonyms — does it match as intended? (§3 #2)

## Step 3 — Secure recall first
Fix matching/query expansion so the right doc is retrieved (§3 #5).

## Step 4 — Re-measure relevance
Confirm the fix on NDCG, don't trust the spot-check (§3 #1).

## Output
An analyzer/mapping root-cause and recall fix with the relevance re-measured. Traverse Tree 2 in the decision-trees file.
