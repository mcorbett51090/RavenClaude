# Experiment design doc — <name>

> The one-page design a stakeholder signs off before launch. Pairs with
> [`analysis-plan.md`](analysis-plan.md) (the statistical pre-registration).

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Status:** draft / approved / running / complete

## Goal & hypothesis
- **Business goal:** <what we're trying to move and why>
- **Hypothesis:** <changing X will increase <primary metric> by at least <MDE>>

## Variants
| Arm | Description | Allocation |
|---|---|---|
| Control | <current experience> | 50% |
| Variant B | <the change> | 50% |

## Metrics
- **Primary:** <definition>
- **Guardrails:** <list — the things a "win" must not break>

## Sizing (from the power analysis)
- **α / power:** 0.05 / 0.80 · **MDE:** <effect> · **Baseline:** <current value>
- **Required n:** <per group> · **Traffic:** <units/day> · **Expected duration:** <days/weeks>
- **Randomization unit:** <user / account>

## Risks & rollback
- **Risks:** <what could go wrong>
- **Rollback plan:** <how to revert quickly if a guardrail breaks>

## Decision rule
- Ship / hold / iterate based on the pre-registered analysis plan. No peeking before the planned sample (or use the named sequential method).

**Sign-off:** <stakeholder> · <date>
