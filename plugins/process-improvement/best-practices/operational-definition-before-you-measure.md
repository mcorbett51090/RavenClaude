# Write the operational definition before you measure — an ambiguous metric makes every later number noise

**Status:** Absolute rule — if two people measuring the same thing can record different values, the variation you "find" is measurement ambiguity, not process behavior. The definition comes before the first data point, not after.

**Domain:** DMAIC / process improvement (Measure)

**Applies to:** `process-improvement`

---

## Why this exists

Every number a DMAIC produces inherits the precision of the definition behind it. "Resolution time," "defect," "on-time," "complete" all feel obvious until two people count them and disagree — and then the baseline, the capability index, and the after-measure are all built on sand. An operational definition removes the ambiguity by making the metric **reproducible**: a clear unit, a precise start and stop, an explicit inclusion/exclusion rule, and a named data source, such that any two people given the same raw events compute the identical value.

This is the prerequisite to the baseline rule (`measure-the-baseline-before-you-change-anything.md`) and to the measurement-trust gate (the Gage R&R / MSA decision tree): you cannot run a meaningful Gage R&R on a metric nobody has defined, because the "operator variation" is just people interpreting an ambiguous instruction differently.

## How to apply

Before collecting any data, write down — in one place a stranger could execute:

1. **Unit + direction** — what is counted/measured, in what unit, and which direction is "better."
2. **Start and stop events** — the exact timestamps/conditions that bound the measurement (e.g., "from `created_at` to first `solved_at`, not last").
3. **Inclusion/exclusion rules** — what counts and what doesn't (e.g., "exclude tickets reopened after 30 days; cap open-time at 30 days").
4. **The defect/threshold** — for a defect metric, the exact customer CTQ or spec limit that makes a unit defective (a defect is a failure against the customer's requirement, not an internal preference).
5. **Data source + extraction** — the system, field, and query that yields the number, so the definition is auditable against reality.

**Do:**
- Test the definition by having two people independently measure the same 10 records — if they disagree, the definition isn't done.
- Freeze the definition for the life of the project; the before and after must use the identical one.
- Audit the data source against the definition (does the system actually record what you think it does?).

**Don't:**
- Accept a metric name ("cycle time") as a definition — names are not operational.
- Let the definition drift between baseline and post-improvement measure (it silently invalidates the comparison).
- Define a "defect" by internal opinion rather than the customer CTQ / spec.

## Edge cases / when the rule has nuance

- **Judgment/attribute metrics** (pass/fail, good/bad by inspection) need an *attribute agreement* check, not just a written definition — appraisers must agree with a known standard and each other. Route the inference to `applied-statistics`.
- **Composite metrics** (a score blended from several inputs) need each input operationally defined, not just the rollup.

## See also

- Best-practice: [`./measure-the-baseline-before-you-change-anything.md`](./measure-the-baseline-before-you-change-anything.md) — the baseline this definition makes trustworthy
- Knowledge: [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md) — the MSA / Gage R&R measurement-trust tree (operational definition is its first gate)
- Skill: [`../skills/process-capability-and-spc/SKILL.md`](../skills/process-capability-and-spc/SKILL.md)

## Provenance

Distilled from `CLAUDE.md` §3 house opinion #8 ("Voice of the Customer defines the defect") and §4 ("a defect defined by internal preference"). Operational-definition discipline is standard DMAIC Measure-phase practice. `[unverified — training knowledge]` — the two-person reproducibility test is a common heuristic, not a numeric standard.

---

_Last reviewed: 2026-06-03 by `claude`_
