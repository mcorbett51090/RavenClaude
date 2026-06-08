# CSAT and CES measure different things

**Status:** Pattern
**Domain:** CX measurement and satisfaction programs
**Applies to:** `customer-support-cx-operations`

---

## Why this exists

CSAT (Customer Satisfaction Score) and CES (Customer Effort Score) are frequently combined,
averaged together, or used interchangeably in CX reporting. This produces a blind spot: you can
have high CSAT and high effort (you solved the problem the hard way), or low CSAT with low effort
(the product failed but the support interaction was easy). Each metric reveals something the
other hides.

Running only CSAT tells you whether customers are satisfied with the outcome but not how
exhausting the journey was. Running only CES tells you whether the interaction was easy but not
whether the problem was actually solved. A complete quality program needs both.

## How to apply

**CSAT** — measures outcome satisfaction:
- Question: "How satisfied were you with your support experience today?" (1–5 scale or 1–10)
- Dispatch: post-resolution, after the ticket is closed. Not in-flight.
- Reports: CSAT% = (4+5 responses) / total responses. Report by agent, by contact category,
  by channel. Always disclose the sample size.
- What it detects: whether the problem was solved, whether the agent was helpful, whether
  the policy was reasonable.

**CES** — measures interaction effort:
- Question: "How easy was it to resolve your issue today?" (CES 2.0: 1–7 scale, or 3-point
  Easy/Neither/Difficult)
- Dispatch: immediately post-interaction (within 5 minutes of close). Before cognitive load fades.
- Reports: CES% = (6+7 on a 7-point scale) or Easy% on a 3-point scale. Report separately
  from CSAT.
- What it detects: channel friction, number of contacts required, agent clarity, wait time pain.
  CES is a stronger predictor of repeat contact and churn for low-complexity service encounters
  than CSAT alone (CEB/Gartner research).

**Do:**

- Run both programs on separate survey instruments dispatched at different times.
- Report CSAT and CES on separate charts; never combine into one index.
- Diagnose high CSAT + low CES as "solved the problem the hard way — reduce effort."
- Diagnose low CSAT + high CES as "the product or policy failed, not the support interaction."

**Don't:**

- Average CSAT and CES into a single composite score.
- Use CES to evaluate agent performance in isolation — it conflates product complexity, policy,
  and channel design with agent behavior.
- Report CSAT without a sample size — a 5-star score on 2 responses is not a signal.
- Ask both questions in the same survey at the same time — timing changes what each measures.

## Edge cases / when the rule does NOT apply

For a very small team (<5 agents, <50 surveys/month), running both programs simultaneously may
produce underpowered data for either. In that case, prioritize CSAT for the first 3 months to
establish a baseline, then add CES once survey volume allows statistically meaningful CES reporting.
The rule against conflation still applies — just sequence them.

## See also

- [`./deflect-with-answers-not-walls.md`](./deflect-with-answers-not-walls.md)
- [`../skills/support-quality-and-csat/SKILL.md`](../skills/support-quality-and-csat/SKILL.md)
- [`../scripts/cx_calc.py`](../scripts/cx_calc.py) for CSAT% and CES% calculation from raw counts.

## Provenance

Based on the CEB (now Gartner) "The Effortless Experience" research (Dixon, Toman, DeLisi) and
the established CX measurement literature distinguishing transactional satisfaction from effort
scores. CES as a churn predictor is supported by Gartner and HBR research (2010–2023).

---

_Last reviewed: 2026-06-08 by `claude`._
