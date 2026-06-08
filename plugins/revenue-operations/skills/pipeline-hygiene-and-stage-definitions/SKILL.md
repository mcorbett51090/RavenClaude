---
description: "Design pipeline stages with objective exit criteria, calibrate stage probabilities from historical win-rate data, run a data-hygiene audit on open pipeline, and produce a stage-definition document that supports any forecast methodology."
---

# Pipeline Hygiene and Stage Definitions

**Purpose:** produce a stage model where every deal's position reflects verifiable, objective
conditions — so the forecast built on top of it is trustworthy.

## When to use this skill

- Designing or redesigning opportunity stages for a CRM.
- Calibrating stage-probability defaults from historical closed-won data.
- Running a hygiene audit on open pipeline (stale deals, missing fields, stage age).
- Filling in the `templates/stage-definition-doc.md` template.

## Step 1: Gather the inputs

1. List existing stages (name, description, probability, forecast category).
2. Pull historical closed deals: close date, stage sequence, time-in-stage, closed-won vs
   closed-lost.
3. Identify the current hygiene problems: which fields are most often blank, which stages have
   the most "stuck" deals (age > 90 days), which stages have the highest loss rate.

## Step 2: Design the stage model

For each stage, define:

| Field | Description |
| --- | --- |
| Stage name | Short, action-oriented (e.g., "Technical Validation", not "Stage 3") |
| Definition | What it means for a deal to be in this stage |
| **Exit criteria** | The objective, binary conditions that must be true to move forward — verifiable in the CRM |
| Default probability | The empirically calculated win-rate for deals that reached this stage |
| Forecast category | Omitted / Pipeline / Best Case / Commit / Closed |

**Exit criteria discipline:** every criterion must be verifiable. Acceptable: "Champion confirmed
in CRM Contact record", "Technical win documented in opportunity notes", "Close date within 90
days." Not acceptable: "Rep believes deal will close", "Good feeling", "Verbal interest."

Typical stage model for a B2B SaaS deal:

| Stage | Exit Criteria (examples) | Forecast Category |
| --- | --- | --- |
| Prospect / MQL | Contact made, basic qualification (BANT or MEDDIC dimension) | Omitted |
| Discovery | Pain identified, budget process confirmed, next step scheduled | Pipeline |
| Technical Validation | Technical win achieved, champion confirmed | Best Case |
| Proposal | Written proposal delivered, decision criteria confirmed | Best Case |
| Verbal Commit | Verbal agreement to purchase, legal/procurement engaged | Commit |
| Closed Won | Contract signed, order booked | Closed |
| Closed Lost | Deal lost, reason documented | Closed |

## Step 3: Calibrate stage probabilities

Do not use the CRM vendor's default probabilities (e.g., Salesforce's 10/20/40/60/80 scale).
Calculate from historical data:

```
Stage win-rate = (deals closed won that reached this stage) ÷ (all deals that reached this stage)
```

Segment by: deal size (SMB vs. mid-market vs. enterprise), sales cycle length, and rep tenure if
sample size allows. Use at least 12 months of closed deals. Flag if sample size < 30 per stage.

## Step 4: Run the hygiene audit

For each open deal, score against:

1. **Age:** how long has this deal been in its current stage? Flag if > median × 2 for that stage.
2. **Required fields:** is close date set? Is amount set? Is next step documented and future-dated?
   Is champion/economic buyer identified?
3. **Stage-exit criteria met:** does the deal's CRM data actually support being in this stage?
   (Champion identified? Technical win documented?)
4. **Activity recency:** when was the last logged activity (call, email, meeting)? Flag if >
   30 days for mid-stage deals.

Score each deal: Green (all criteria met), Yellow (1-2 gaps), Red (3+ gaps or age outlier).

## Step 5: Produce the stage-definition document

Fill in [`../../templates/stage-definition-doc.md`](../../templates/stage-definition-doc.md).
Include: stage model table, exit criteria for each stage, empirically calibrated probabilities
(with the data source and date), the hygiene audit summary, and the CRM implementation notes
(which fields are required, which validation rules enforce exit criteria).

## Anti-patterns

- Stage names that are just labels ("Stage 1", "Stage 2") with no definition.
- Probabilities copied from a competitor or from the CRM vendor's default — not your data.
- Exit criteria that include subjective rep opinion ("rep confident", "deal feels warm").
- A hygiene audit that scores deals but produces no remediation actions (aging / missing data).
- A stage model designed without consulting the forecast methodology it must feed.

## Output

A completed `stage-definition-doc.md` with: stage model + exit criteria + empirical probabilities
+ hygiene audit summary. Pass to `crm-operations-architect` for CRM validation-rule design;
pass to `pipeline-forecast-engineer` for methodology alignment.
