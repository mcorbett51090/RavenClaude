# customer-success-analytics plugin

> The **domain layer** of customer-success analytics for the RavenClaude marketplace: the metrics, signals, and health/renewal workflows that let a CS leader answer **"which accounts are at risk and who do I call today?"** in under two minutes. It sits *on top of* a warehouse + pipeline that `data-platform` builds — this plugin decides **what to measure and why**; `data-platform` decides **how to land it and stand up the surface**.

**Designed for:** a customer-success team (with revenue / retention accountability) that has — or is about to have — CRM, CS-platform, support, and collaboration data in a warehouse, and wants a transparent, explainable account-health and churn-risk view on top of it.

**Domain-neutral.** No EdTech / finance / Salesforce-app / K-12 assumptions. The signals and workflows here are universal CS mechanics; vertical overlays live in their own plugins.

## What this plugin gives you

- A conformed **CS-health data model** — the account spine, the daily health snapshot, the renewal/support/signal facts — designed so a *who-do-I-call-today* sort is cheap.
- A **transparent rule-based Green/Yellow/Red tier** where every Red shows *why* (no black-box ML in phase 1).
- A validated set of churn-**leading** signals (not lagging ones that merely describe an already-lost account) with thresholds tuned against your actual past churn.
- A **renewal-risk workflow** where risk = renewal proximity × engagement, with save-play triggers keyed off the health tier.
- A reference data-model template you can hand to `data-platform` to build.

## The two agents

| Agent | Owns |
|---|---|
| `cs-analytics-architect` | The unified CS-health data model + metric layer — conformed `dim_account` spine, `fct_account_health_snapshot`, renewal/support/signal facts, the transparent rule-based tier, and the mapping to a BI surface (Sigma/Tableau). |
| `churn-signal-analyst` | Identifying and validating churn-**leading** indicators, distinguishing leading from lagging, setting + tuning the rule thresholds against past churn, and the per-Red explainability contract. |

## The two skills

| Skill | What's inside |
|---|---|
| `health-tier-design` | Designing a transparent, explainable rule-based health tier from multi-source signals: signal selection, weighting, thresholds, per-signal evidence display, and tuning against actual past churn. |
| `renewal-workflow-design` | Designing the renewal-risk workflow and save-play triggers from the health tier + renewal proximity: the proximity × engagement rule, the watchlist surface, and the trigger-to-play mapping. |

## When to use it

- You're standing up an account-health / churn-risk dashboard and need to decide **which signals**, **what the tier means**, and **how each Red explains itself** — before anyone builds it.
- Your existing health score has stopped predicting (green accounts churn, red ones renew) and you need to retune the thresholds against the last renewal cycle.
- You want to anchor on your CS platform's native health score but surface support / escalation / usage signals alongside it — without replacing a black box with another black box.

## When *not* to use it

- You need to build the pipeline, the connectors, the warehouse, the identity-resolution matcher, or the BI embed itself — that's `data-platform`.
- You need a segment-specific renewal/QBR *motion* (K-12 budget cycle, academic calendar, FERPA comms) — that's a vertical plugin like `edtech-partner-success`. This plugin owns the domain-neutral analytics underneath it.

## How it pairs with `data-platform`

This plugin is the **domain layer**; `data-platform` is the **technical layer** below it.

| You need… | Goes to |
|---|---|
| Which signals, which entities, what the tier means, what fires a renewal play | **this plugin** (`cs-analytics-architect`, `churn-signal-analyst`) |
| The pipeline + connectors (Airbyte / Fivetran / a niche CS-platform loader) | `data-platform/etl-pipeline-engineer`, `connector-developer` |
| The warehouse, roles, RLS, identity-resolution matcher + `bridge_account_xref` | `data-platform/database-setup-guide` |
| The BI dashboard / embed itself (Sigma / Tableau / Superset / Cube) | `data-platform/dashboard-builder` |

The handoff is explicit in every agent's output (a mandatory `Handoff to data-platform:` line). Install the two together: this plugin designs the model + signals + tier; data-platform builds it.

## Requires

- `ravenclaude-core@>=0.7.0`
- Pairs with `data-platform` (the pipeline/warehouse/BI layer this one sits on top of)

## Install

```bash
/plugin marketplace add ravenclaude
/plugin install customer-success-analytics@ravenclaude
/plugin install data-platform@ravenclaude   # the technical layer this one pairs with
```

## Companion plugins (recommended when relevant)

- `data-platform` — the pipeline / warehouse / BI layer this plugin designs on top of (install together)
- `edtech-partner-success` — when the vertical is education; owns the segment-specific renewal/QBR/health-play motion above the domain-neutral analytics
- `applied-statistics` (when installed) — "is this metric movement real or noise?"; this plugin owns *which* signal and *what* threshold, applied-statistics owns *is the movement statistically real*

## See also

- `CLAUDE.md` — full team constitution (13 sections)
- `plugins/data-platform/CLAUDE.md` — the technical layer below this one
- `plugins/ravenclaude-core/CLAUDE.md` — the domain-neutral team constitution inherited by every plugin
