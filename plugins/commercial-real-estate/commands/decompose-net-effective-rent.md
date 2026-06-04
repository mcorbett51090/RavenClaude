---
description: "Convert a face rent to net effective by netting TI, free rent, and leasing commissions, so comps and underwriting use the rent the landlord actually earns. Reach for this on any rent comp."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Decompose net effective rent

You are running `/commercial-real-estate:decompose-net-effective-rent` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Gather the concession package — Face rent, term, TI allowance, free-rent months, and the leasing commission for the comp and the subject.
2. Net to effective — Spread the concessions over the term to get the net effective rent per the same basis (§3 #5).
3. Compare like to like — Only compare NER to NER; a face-to-NER comparison overstates the subject's competitiveness.
4. Flag credit and term — Note tenant credit and term — a higher NER from a weak tenant on a short term is not a better lease.

## Output
A net-effective rent for each comp, an apples-to-apples spread to the subject, and credit/term flags. See [`../skills/decompose-net-effective-rent/SKILL.md`](../skills/decompose-net-effective-rent/SKILL.md). Traverse the matching tree in [`../knowledge/cre-decision-trees.md`](../knowledge/cre-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
