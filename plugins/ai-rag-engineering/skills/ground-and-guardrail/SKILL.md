---
name: ground-and-guardrail
description: "Add citations, refuse-on-empty-retrieval, and context-constraint to cut hallucination. Reach for this on a faithfulness question."
---

# Skill: Ground and guardrail

An un-grounded, un-cited generation invites confident fabrication (§3 #7).

## Step 1 — Require citations
Make the model cite the retrieved passage it grounded on (§3 #7).

## Step 2 — Refuse on empty retrieval
If retrieval returns nothing relevant, refuse rather than fabricate (§3 #1 #7).

## Step 3 — Constrain to context
Instruct and check that the answer stays within retrieved context (§3 #7).

## Step 4 — Verify with the eval
Citations are how faithfulness is measured — close the loop (§3 #3 #7).

## Output
A grounding + guardrail design with citations, refusal, and a faithfulness check.
