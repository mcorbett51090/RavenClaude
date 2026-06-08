# marketing-operations-demand-gen

The **martech/demand-gen layer** for the modern B2B marketing function. This plugin's team helps you
design lead lifecycles, build MQL→SQL handoff contracts with Sales, configure marketing automation
platforms, implement multi-touch attribution, manage campaign operations, and prove marketing's
contribution to pipeline — all with the discipline that turns martech investment into revenue evidence.

> **The one-line philosophy:** attribution is a model (not the truth), an MQL is a handoff contract
> (not a trophy), and a UTM taxonomy is infrastructure — everything else is downstream of getting
> those three things right.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Design our lead lifecycle / MQL definition / MQL→SQL SLA" | **marketing-operations-demand-gen** (`marketing-ops-lead`) |
| "Evaluate or select our martech stack / MAP / CRM tools" | **marketing-operations-demand-gen** (`marketing-ops-lead`) |
| "Design a demand gen strategy / channel mix / ABM vs inbound" | **marketing-operations-demand-gen** (`demand-gen-strategist`) |
| "Plan a campaign calendar / allocate budget across channels" | **marketing-operations-demand-gen** (`demand-gen-strategist`) |
| "Build a nurture sequence / lifecycle flow in HubSpot or Marketo" | **marketing-operations-demand-gen** (`marketing-automation-engineer`) |
| "Implement lead scoring / fix deliverability / clean our contact list" | **marketing-operations-demand-gen** (`marketing-automation-engineer`) |
| "Set up multi-touch attribution / design UTM taxonomy" | **marketing-operations-demand-gen** (`attribution-analyst`) |
| "Prove marketing's pipeline contribution / ROI by channel" | **marketing-operations-demand-gen** (`attribution-analyst`) |
| "Model the CRM opportunity pipeline / SQL→Closed-Won mechanics" | `revenue-operations` |
| "Run an A/B test on a landing page or email" | `experimentation-growth-engineering` |
| "Improve site SEO / brand / web design" | `web-design` |
| "Build the data pipeline / warehouse / BI layer for marketing data" | `data-platform` |

## What's inside

- **4 agents** — `marketing-ops-lead`, `demand-gen-strategist`, `marketing-automation-engineer`,
  `attribution-analyst`.
- **3 skills** — `lead-scoring-and-lifecycle`, `attribution-modeling`, `campaign-operations`.
- **3 commands** — `/marketing-operations-demand-gen:design-lead-scoring`,
  `:build-attribution-model`, `:plan-campaign`.
- **2 templates** — `campaign-brief`, `utm-taxonomy`.
- **Knowledge bank** — `knowledge/marketing-ops-decision-trees.md`: Mermaid trees for
  attribution-model selection, channel-mix allocation, and lead-score design, plus a dated 2026
  capability map of the martech landscape.
- **6 best-practices** and **1 advisory hook** (flags missing UTM conventions, attribution claims
  without a named model, hard-coded conversion-rate/CAC figures without a date, and email sends
  without a consent/suppression note).

## House opinions (the short list)

1. MQL is a handoff contract, not a trophy — bilateral SLA with Sales.
2. Attribution is a model, not the truth — always name the model.
3. A UTM taxonomy or your data is noise — treat it as infrastructure.
4. Nurture the not-yet-ready — don't spam them.
5. Lead scores decay — maintain them with recency weighting and negative scoring.
6. One source of truth for campaign cost — reconcile to finance.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
