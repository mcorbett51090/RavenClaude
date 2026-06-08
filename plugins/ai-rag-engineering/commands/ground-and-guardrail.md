---
description: "Add citations, refuse-on-empty-retrieval, and context-constraint to cut hallucination. Reach for this on a faithfulness question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Ground and guardrail

You are running `/ai-rag-engineering:ground-and-guardrail` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Require citations — Make the model cite the retrieved passage it grounded on (§3 #7).
2. Refuse on empty retrieval — If retrieval returns nothing relevant, refuse rather than fabricate (§3 #1 #7).
3. Constrain to context — Instruct and check that the answer stays within retrieved context (§3 #7).
4. Verify with the eval — Citations are how faithfulness is measured — close the loop (§3 #3 #7).

## Output
A grounding + guardrail design with citations, refusal, and a faithfulness check. See [`../skills/ground-and-guardrail/SKILL.md`](../skills/ground-and-guardrail/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user data / prompt PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
