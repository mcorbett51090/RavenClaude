# Write an operational definition before every metric

**Status:** Absolute rule
**Domain:** Process improvement — Measure phase
**Applies to:** `process-improvement`

---

## Why this exists

Two people measuring "cycle time" with different start and stop events produce incomparable numbers. Gage R&R studies can only assess repeatability and reproducibility *after* the definition is fixed; if the definition is ambiguous, the study itself measures noise. Every downstream calculation — sigma level, capability index, control-chart limits — inherits the definition's precision or its ambiguity. Undefined metrics are the most common and most invisible source of flawed DMAIC baselines.

## How to apply

An operational definition has four required elements — all four must be recorded before data collection begins:

| Element | Question it answers | Example |
|---|---|---|
| **Start event** | When does a unit's clock start? | "Timestamp of PO receipt in the ERP system" |
| **Stop event** | When does the clock stop / the judgment happen? | "Timestamp of shipment confirmation scan" |
| **Inclusion/exclusion rule** | Which units count? | "All domestic orders; exclude returns and cancelled POs" |
| **Data source** | Exactly where is the value recorded? | "Field `ship_confirmed_at` in table `orders`, warehouse DB" |

```
Example — "Order fulfillment cycle time"
  Start event:   `order_received_at` timestamp, orders table (ERP), UTC
  Stop event:    `ship_confirmed_at` timestamp, same table (ERP), UTC
  Inclusion:     Status = 'shipped'; domestic (country = 'US'); exclude RMA
  Unit:          Each order ID in the measurement window
  Recorded by:   ERP system (automatic); no manual entry
```

**Do:**
- Write the definition before the first data pull — even if the data already exists.
- Have two people independently apply the definition to five real units, compare results; if they differ, the definition needs refinement.
- Store the definition in the project charter's Measure phase section so it can be cited in control-plan documentation.

**Don't:**
- Use a metric name alone ("cycle time," "error rate," "on-time delivery") as if it were a definition.
- Allow the start or stop event to change between the baseline and the post-improvement re-measure.
- Accept a definition that requires a human judgment call unless you have also run an attribute agreement analysis.

## Edge cases / when the rule does NOT apply

- **Qualitative/exploratory scoping work** (e.g., stakeholder interviews, initial process walk): data collection is not yet happening; the operational definition is the output, not the input. Write it before the first count.
- **Re-using a pre-existing, documented metric** (e.g., a KPI your data warehouse already tracks with a published definition): cite the existing definition, verify it matches the CTQ, and flag any delta. You may not need to write a new one — but you do need to verify the existing one is sufficient.

## See also

- [`../agents/process-analyst.md`](../agents/process-analyst.md) — runs data-collection planning; the operational definition is the first deliverable of that work
- [`./voice-of-the-customer-defines-the-defect.md`](./voice-of-the-customer-defines-the-defect.md) — defines what a defect is; the operational definition specifies how you measure whether it occurred

## Provenance

Codifies house opinion in [`../CLAUDE.md`](../CLAUDE.md) §3 ("an operational definition before every metric") and the MSA/Gage R&R triage decision tree in [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md) ("Is the metric operationally defined?"). Standard Lean Six Sigma Measure-phase discipline; see also the existing best-practice `operational-definition-before-you-measure.md` which covers the same gate from the "do not measure ambiguity" angle — this rule adds the four-element template and the data-source requirement.

---

_Last reviewed: 2026-06-05 by `claude`_
