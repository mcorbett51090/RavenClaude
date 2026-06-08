# A forecast is a commitment, not a hope

**Status:** Pattern
**Domain:** Forecasting
**Applies to:** `revenue-operations`

---

## Why this exists

A forecast that cannot name its methodology is not a forecast — it is a hope with a decimal point.
"We rolled up the pipeline" is not a methodology; it describes a mechanical data aggregation from
a CRM whose stage probabilities may never have been calibrated, whose data quality may be poor,
and whose stage-advancement discipline may be inconsistent across reps.

A forecast number carries authority only when it carries accountability. Accountability requires:
(1) a named methodology, (2) calibrated inputs, (3) a commit submitted by someone who owns the
number, and (4) a retrospective that measures commit accuracy and feeds back into methodology
calibration. Without all four, the number is a starting point for a conversation, not a business
commitment.

## How to apply

Before submitting or accepting any forecast number:

1. **Name the methodology.** Weighted-probability with empirically calibrated stage probabilities?
   Commit/category with manager overlay? AI-assisted with a named tool and a stated confidence
   interval? The methodology is required, not optional.
2. **State the assumptions.** Win-rate used (and source), pipeline coverage ratio (and win-rate
   denominator), stage probabilities (and whether empirical or estimated).
3. **Assign accountability.** A forecast has an owner — a name, a role, and a submission date.
   "The system" is not an owner.
4. **Measure accuracy.** After the period closes, compare the submitted forecast to actual.
   Segment by methodology, rep, manager, and stage. Feed the accuracy measurement back into the
   next period's calibration.

**Do:**

- Require that every forecast submission names the methodology, the assumptions, and the owner.
- Track forecast accuracy by rep and by manager every quarter; publish it to the team.
- Calibrate stage probabilities from historical win-rate data at least annually.
- When adopting an AI forecasting tool, treat it as a methodology that requires its own calibration
  and accuracy measurement — not as a black-box authority.

**Don't:**

- Accept a forecast number with no methodology attached ("here's what the CRM says").
- Use a forecast number as authoritative when the underlying CRM data has not been inspected
  for hygiene.
- Adopt AI-assisted forecasting before CRM data quality and activity capture are established.
- Treat "best case" as a forecast — it is an upside scenario, not a commitment.

## Edge cases / when the rule does NOT apply

In a very early-stage company with fewer than six months of closed-deal history, the methodology
may necessarily rely on market benchmarks and estimates rather than empirical calibration. This is
acceptable if and only if every estimate is labeled as such (e.g., "stage probability is an estimate
based on [benchmark source]; to be calibrated after Q3 close data"). A labeled estimate is honest;
an unlabeled estimate presented as empirical data is misleading.

## See also

- [`./stages-are-exit-criteria-not-vibes.md`](./stages-are-exit-criteria-not-vibes.md)
- [`./one-definition-of-pipeline.md`](./one-definition-of-pipeline.md)
- [`../skills/forecasting-methodology/SKILL.md`](../skills/forecasting-methodology/SKILL.md)
- [`../knowledge/revops-decision-trees.md`](../knowledge/revops-decision-trees.md)

## Provenance

Codifies the RevOps and sales-operations community practice of named-methodology forecasting and
commit accountability, aligned with the Clari / Gong approach to forecast accountability and the
broader enterprise-SaaS RevOps practitioner literature.

---

_Last reviewed: 2026-06-08 by `claude`._
