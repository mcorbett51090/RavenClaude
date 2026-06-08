# RevOps — Decision Trees

_Decision trees + a dated reference map. Reference rows are `[verify-at-build]` — re-check the definition/method against a current source before quoting. Last reviewed: 2026-06-08._

Traverse before choosing a forecast method, deriving coverage, picking an attribution model, or defining funnel stages.

## Decision Tree: Which forecast method should we use?

A forecast is a methodology with a named bias — match the method to the data you actually have.

```mermaid
graph TD
  A[Need a sales forecast] --> B{Do you have clean, multi-quarter historical deal data?}
  B -- No --> C[Weighted-by-stage from your own historical stage->close rates - simplest defensible method]
  B -- Yes --> D{Is the cycle stable and volume high enough to learn from?}
  D -- No, lumpy/few large deals --> E[Commit/category roll-up + rep deal inspection - sentiment beats a thin model on whale deals]
  D -- Yes --> F{Can you staff/trust an AI/regression model and its inputs?}
  F -- No --> G[Weighted-by-stage, back-tested against last 4 quarters - name the early-stage over-count bias]
  F -- Yes --> H[AI/regression forecast - but keep a commit roll-up beside it; the model can't see a black-swan deal]
  E --> I[Always inspect for stuck/aged/past-close-date deals before rolling up]
  G --> I
  H --> I
```

_Weighted over-counts early pipeline; commit is rep-sentiment-driven; AI/regression needs clean history and is blind to the unprecedented deal. State the bias every time, and back-test before you trust._

## Decision Tree: How much pipeline coverage do we actually need?

Coverage is derived from this segment's win-rate, not inherited as a folk "3x".

```mermaid
graph TD
  A[Need a coverage target] --> B{Do you have this segment's stage-weighted win-rate?}
  B -- No --> C[Compute it first from historical stage->close - do not borrow a 3x constant]
  B -- Yes --> D[Coverage = gap-to-target / stage-weighted win-rate]
  D --> E{Is the existing pipeline inspected for stuck/padded/past-close-date deals?}
  E -- No --> F[Inspect and clean first - coverage on padded pipeline is precise nonsense]
  E -- Yes --> G{Is coverage below the derived target?}
  G -- Yes --> H[Pipeline gap - drive build/velocity; name which lever moves the number]
  G -- No --> I[Coverage met on real pipeline - watch win-rate drift, not just the ratio]
```

_Required coverage = gap ÷ stage-weighted win-rate. "3x" is somebody else's win-rate. Derive from this segment's conversion, and only on inspected pipeline._

## Decision Tree: Which attribution model should drive this decision?

Attribution is a chosen lens, never ground truth — match the model to the question and name what it's blind to.

```mermaid
graph TD
  A[Need to credit revenue to touches] --> B{What decision does this feed?}
  B -- Top-of-funnel / demand-gen budget --> C[First-touch or W-shaped - credits demand creation; last-touch would defund it]
  B -- Closing / sales-assist budget --> D[Last-touch or W-shaped - credits the converting touch; first-touch ignores it]
  B -- Whole-journey budget split --> E{Do you have touch volume + clean data + stakeholder trust in a black box?}
  E -- No --> F[Multi-touch heuristic - linear or W-shaped; state the weighting is opinionated, not truth]
  E -- Yes --> G[Data-driven / algorithmic - but make it explainable; it needs volume and is a black box]
  C --> H[Triangulate: never let ONE model silently drive the budget]
  D --> H
  F --> H
  G --> H
  H --> I[Name what each model under/over-credits; treat divergence across models as a signal, not noise]
```

_Last-touch defunds demand; first-touch ignores closing; data-driven needs volume + clean data and is opaque. Name the distortion every time; triangulate rather than crown one model truth._

## Decision Tree: Is this pipeline stage well-defined?

A stage = an objective buyer-action exit criterion, not rep optimism — and its probability comes from your own history.

```mermaid
graph TD
  A[Defining or auditing a pipeline stage] --> B{Is the exit criterion a verifiable BUYER action?}
  B -- No, it's a seller hope/feeling --> C[Rewrite as a buyer action an outside observer could confirm - demo booked, MAP signed, procurement engaged]
  B -- Yes --> D{Does the stage mean the same thing for every rep?}
  D -- No --> E[The stage is ambiguous - tighten the criterion until 'stage 3' is one thing org-wide]
  D -- Yes --> F{Is the stage probability from YOUR history or a CRM default?}
  F -- CRM default 10/25/50/75 --> G[Replace with your own historical stage->close conversion - defaults bear no relation to your deals]
  F -- Your history --> H[Stage is sound - recompute conversion as it drifts; never let probability detach from history]
  C --> D
  E --> F
```

_A stage defined by rep optimism is why the forecast misses. Exit criteria are buyer actions an outsider can confirm; stage probabilities come from your own history, never the CRM defaults._

## Decision Tree: Does the quota reconcile to capacity?

Quota is built bottoms-up from ramped-rep capacity, not handed down from the board number.

```mermaid
graph TD
  A[Setting a quota / territory target] --> B{Do you have a bottoms-up capacity model?}
  B -- No --> C[Build it first: ramped + ramping reps x expected productivity - a top-down-only number misses predictably]
  B -- Yes --> D[Capacity = (fully-ramped reps + ramping reps x ramp fraction) x productivity per rep]
  D --> E{Does capacity x productivity meet the board ask?}
  E -- Yes --> F[Quota is makeable - assign it; watch ramp + productivity assumptions as reality lands]
  E -- No, board ask exceeds capacity --> G{Which lever closes the gap?}
  G -- Hire / ramp earlier --> H[Staffing decision - model the new ramp curve, re-reconcile]
  G -- Raise productivity --> I[Name the enablement/process change that moves it - don't just assume it]
  G -- Accept the gap --> J[Flag it explicitly - an un-makeable quota breaks comp behavior, not just the forecast]
```

_Capacity model first, board number second. When the two don't meet, the gap is a staffing/ramp/productivity decision — never a bigger number stapled onto the same heads._

---

## Reference map (2026, `[verify-at-build]`)

### Funnel metric glossary

| Term | Working definition | Note |
|---|---|---|
| MQL | Marketing-qualified lead — meets the agreed fit + engagement threshold to pass to sales | Define by criteria *sales accepts*; pair with an accept/reject loop `[verify-at-build]` |
| SAL | Sales-accepted lead — sales has accepted the MQL for follow-up | The handoff checkpoint; closes the marketing↔sales loop `[verify-at-build]` |
| SQL | Sales-qualified lead — sales has qualified it into active pursuit | Often the opportunity-creation trigger `[verify-at-build]` |
| Conversion rate | Volume passing stage N→N+1 ÷ volume entering stage N | Compute per segment/source; the funnel's core diagnostic `[verify-at-build]` |
| Sales velocity | (open opps × win-rate × avg deal size) ÷ avg cycle length | The lever-finder; isolates which input a change moves `[verify-at-build]` |
| Pipeline coverage | open pipeline ÷ gap-to-target | Derive the *target* from win-rate, never a folk 3x `[verify-at-build]` |
| Win-rate | won opps ÷ (won + lost) closed opps | By segment/source/stage; beware including no-decision `[verify-at-build]` |

### Forecast methods

| Method | Inputs | Known bias `[verify-at-build]` |
|---|---|---|
| Weighted-by-stage | stage × historical stage->close rate × deal size | Over-counts early-stage pipeline; only as good as the stage rates |
| Commit / category | rep roll-up into commit / best-case / pipeline | Rep sentiment (sandbagging or happy-ears); not statistical |
| AI / regression | clean multi-quarter history, deal features | Blind to unprecedented deals; needs data hygiene + a champion |

### Attribution models

| Model | Credits | Distorts (`[verify-at-build]`) |
|---|---|---|
| First-touch | the demand-creating touch | Over-credits top-of-funnel; ignores closing influence |
| Last-touch | the final touch before conversion | Defunds demand creation; over-credits bottom-of-funnel |
| Linear | every touch equally | Flattens real influence differences |
| W-shaped / position-based | first, lead-creation, opp-creation touches | Opinionated weighting; still a heuristic, not truth |
| Data-driven | algorithmic per-touch credit | Needs volume + clean data; a black box to stakeholders |

### Comp / quota mechanics

| Mechanic | Working definition | Watch-for `[verify-at-build]` |
|---|---|---|
| Quota (bottoms-up) | ramped-rep capacity × productivity, reconciled to the board number | A top-down-only quota misses predictably |
| Capacity model | ramped reps × ramp curve × expected productivity | The reconciliation surface against the board target |
| OTE / pay mix | base : variable split at target | Drives risk appetite and behavior |
| Accelerators / caps | over-attainment multipliers / ceilings | Caps invite end-of-period deal-dumping/holding |
| Clawback | reversal on early churn | Its absence rewards bad-fit closes |

_The funnel is a bowtie: model acquisition (left) and retention/expansion (right) as one connected motion — the right side hands to `customer-success-analytics`. Re-verify any definition/method/model specific before quoting it to a consumer._
