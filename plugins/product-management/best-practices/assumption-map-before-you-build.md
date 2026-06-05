# Map Assumptions Before You Build — Rank by Risk, Not by Confidence

**Status:** Absolute rule
**Domain:** Product discovery / risk management
**Applies to:** `product-management`

---

## Why this exists

Every product initiative rests on a set of assumptions — that the problem is real, that this segment has it acutely, that users will discover the feature, that the workflow change is tolerable, that the business model works. Teams that build without mapping and ranking their assumptions routinely discover the fatal assumption months into development, after the highest-cost investment. The failure is not that the assumption was wrong; it is that the team didn't know it was the riskiest thing they were betting on. An assumption map forces the team to be explicit about what they believe, rank the beliefs by how much the initiative depends on them, and test the riskiest ones cheapest before the expensive ones.

## How to apply

Build an assumption map at the start of every initiative, before design work begins.

```
Assumption Map — Format
──────────────────────────────────────────────────────
For each assumption, fill out one row:

Assumption                | Category    | Importance | Evidence Quality | Risk Score
                          |             | (If wrong, |  (How well do   | = Importance
                          |             |  does the  |  we know this   | × (1 - Evidence)
                          |             |  initiative|  is true?)      |
                          |             |  fail? 1-5)|  1=well 5=guess |
─────────────────────────────────────────────────────────────────────────────────────
Users struggle with X     | Desirability|     5      |        4        |    20 ← test first
They prefer solution Y    | Desirability|     4      |        3        |    12
They will change workflow | Feasibility |     3      |        4        |    12
Eng can build in 6 weeks  | Viability   |     4      |        2        |     8
Users will find the feature| Desirability|    3      |        3        |     9

Categories:
  Desirability — do users want it?
  Feasibility  — can we build it?
  Viability    — will it make business sense?

Risk Score = Importance × (Evidence quality / 5)
  Highest risk score = test first, cheapest available method.
```

**Do:**
- Include the engineering lead and a data analyst in the assumption mapping session — they hold assumptions the PM doesn't know about.
- Match the test method to the importance and cheapness: user interviews for desirability, spikes for feasibility, financial model for viability.
- Revisit the assumption map after each test; a tested assumption moves from "guess" to "evidence" and the risk score updates.

**Don't:**
- Rank assumptions by which ones you are most confident about — confidence is irrelevant; importance (what happens if this is wrong) is what matters.
- Treat the assumption map as a documentation exercise; it is a decision tool that answers "what should we test next?"
- Skip the map for "small" initiatives — the assumptions that kill small initiatives are proportionally just as fatal as those that kill large ones.

## Edge cases / when the rule does NOT apply

- **Maintenance and hardening work** (performance improvements, security patches, bug fixes) — the initiative has no desirability assumption; feasibility and viability assumptions still apply.
- **Regulatory or compliance-mandated work** — desirability is not in question; the build is required. Feasibility and timeline assumptions still benefit from mapping.

## See also

- [`../agents/product-discovery-lead.md`](../agents/product-discovery-lead.md) — owns assumption mapping and riskiest-assumption testing.
- [`./test-the-riskiest-assumption-first.md`](./test-the-riskiest-assumption-first.md) — the upstream house opinion; this doc operationalizes the ranking method that identifies which assumption is riskiest.

## Provenance

Codifies the product-discovery-lead's assumption mapping discipline from the product-management plugin's CLAUDE.md §2 #2 ("test assumptions before building") and the opportunity-solution tree framework. The importance × evidence risk-scoring matrix is drawn from Teresa Torres' assumption-testing practice and Strategyzer's assumption mapping methodology.

---

_Last reviewed: 2026-06-05 by `claude`_
