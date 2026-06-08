# RevOps

The **revops** plugin — the revenue-operations (B2B GTM) craft: the lead-to-cash revenue engine *above* the CRM and the warehouse that ties marketing, sales, and customer success into one accountable funnel — distinct from the CRM platform build, the warehouse/BI, and the post-sale customer-health model.

## Agents

- **`revops-architect`** — The revenue shape and operating model: the lead-to-cash funnel and the bowtie (acquisition + retention/expansion as one motion), the RevOps data model, the GTM tech stack, and the SLAs/handoffs between marketing↔sales↔CS. Defines the funnel once, as one source of truth — not two teams with two definitions of MQL.
- **`pipeline-and-forecast-analyst`** — Pipeline and forecast: stage definitions and hygiene (objective buyer-action exit criteria), forecast methodology (weighted-by-stage vs. commit/category vs. AI/regression, each with its named bias), coverage ratios derived from win-rate, sales velocity, and deal inspection. Inspects the pipeline before trusting the math.
- **`gtm-systems-engineer`** — GTM systems and data quality: CRM hygiene and automation, lead routing and scoring (with speed-to-lead SLAs), territory/quota/comp operations (quota built bottoms-up from capacity), attribution modeling (the chosen lens, never ground truth), and data-quality enforcement at the point of entry.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install revops@ravenclaude
```

## Seams

- **Post-sale health, churn, retention, NRR drivers** → `customer-success-analytics`; this team owns the funnel *to* closed-won and the renewal pipeline, they own the health model after the close (the bowtie's right side).
- **The CRM platform build (objects, flows, Apex, validation rules)** → `salesforce`; we specify the RevOps data model + automation intent, they build it on the platform.
- **The warehouse revenue mart and the BI dashboards** → `data-platform` + `tableau`; we define the metric (one definition), they build the pipeline and the view.
- **Experiment / lift-test design for GTM changes** → `experimentation-growth-engineering`; we say what to test, they design the test.
- **Significance testing ("is this win-rate difference real")** → `applied-statistics`; we ask, they answer rigorously.
- **Lead PII and comp-plan confidentiality** → `data-governance-privacy`; we encode their policy into the data model and access rules.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `salesforce`, `data-platform`, `tableau`, and `customer-success-analytics`.
