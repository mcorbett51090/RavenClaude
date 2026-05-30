# Source-trace every load-bearing cell — a return value you can't reproduce will not survive an exam

**Status:** Absolute rule
**Domain:** Regulatory reporting — data lineage
**Applies to:** `regulatory-compliance`

---

## Why this exists

A regulatory return is a chain of numbers, and any number a reviewer or examiner can ask about must be reproducible from its source on demand. The trap is a cell that "came from the model" or "matched last period" with no traceable path back to the system of record. When the examiner picks a line and asks "where did this come from," the answer has to be a complete lineage — source system, account, period, extract timestamp, and every transformation applied — not "let me get back to you." A figure that cannot be reproduced is, in regulator terms, a figure that cannot be relied upon; reproducibility is the gate the `regulatory-reporting-analyst` will not waive. Rolling a number forward from last period because it reconciled then is the specific error: last period's reconciliation does not re-verify this period's source.

## How to apply

For every load-bearing input, capture the full lineage so any cell can be re-derived independently:

```
Cell             return + schedule + line reference
Source           system of record + GL account / table + period
Extract          extract timestamp + who/what pulled it + the query or report used
Transform        each transformation step (FX, mapping, aggregation, statutory-vs-GAAP adjustment) + logic
Destination      the return cell it feeds, with the version of the workbook
Reproducible?    a second person could re-derive the value from this lineage alone
```

Roll a prior-period number forward only after re-verifying it against the current source — not on the strength of last period's reconciliation.

**Do:**
- Record source → transformer → destination with version + timestamp for every material cell; reproducibility is the acceptance gate.
- Re-verify rolled-forward figures against current source each period.
- Make the lineage independently re-derivable — a reviewer who didn't build the return can follow it to the source.

**Don't:**
- Accept "it came from the model" as a lineage — name the model's inputs and the path.
- Trust a prior-period reconciliation as evidence for the current period's value.
- Apply a period cutoff inconsistently across schedules — the same cutoff, documented, across the whole return.

## Edge cases / when the rule does NOT apply

- **Genuinely immaterial cells** below the return's materiality floor need lineage proportionate to materiality — but state the floor and which regime's materiality definition applies (house opinion #7, #12) `[verify-at-build — materiality is regulator-specific]`.
- **Estimates and actuarial inputs** (technical provisions, risk margin) are reproducible at the *methodology* level — the assumption set, the curve, the model version — not as a single GL trace; the lineage points to the documented methodology.
- **Source-data quality issues** are raised to the controller before filing — they don't get silently corrected inside the return (see the fix-the-source rule).

## See also

- [`./filing-fix-the-source-not-the-return.md`](./filing-fix-the-source-not-the-return.md) — what to do when the lineage reveals bad source data.
- [`./filing-maker-checker-is-two-people.md`](./filing-maker-checker-is-two-people.md) — the checker re-walks the lineage.
- [`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md) — "Source-trace every load-bearing input"; the `supervisory-return-prep` skill.

## Provenance

Codifies the `regulatory-reporting-analyst` opinions "Source-trace every load-bearing input. A return cell that can't be reproduced is an exam exposure" and "Skeptical of last-period's reconciliations" ([`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md)), the anti-pattern "a regulatory return where any load-bearing cell isn't source-traceable," and the §8 `supervisory-return-prep` skill (data lineage) in [`../CLAUDE.md`](../CLAUDE.md).

---

_Last reviewed: 2026-05-30 by `claude`_
