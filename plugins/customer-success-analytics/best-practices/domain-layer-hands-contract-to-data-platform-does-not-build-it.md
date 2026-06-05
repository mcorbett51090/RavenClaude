# This plugin delivers a contract — data-platform builds it

**Status:** Absolute rule
**Domain:** CS analytics — layer boundary
**Applies to:** `customer-success-analytics`

---

## Why this exists

The `customer-success-analytics` plugin is the **domain layer**: it designs the metric definitions, the tier rules, the signal selection, and the mart schema. The `data-platform` plugin is the **technical layer**: it builds the pipeline, the warehouse, the identity-resolution matcher, and the BI surface. Confusion about who builds what is the most common source of scope creep and unowned work in a CS analytics engagement. This rule makes the boundary explicit so neither plugin builds the other's deliverable.

## How to apply

For every CS analytics work item, classify it as domain or technical before assigning:

| Work item | Owner | Seam |
|---|---|---|
| Define which signals compose the tier | `customer-success-analytics` | Hands spec to data-platform |
| Define the mart schema (table names, columns, grain, NULL rules) | `customer-success-analytics` | Hands DDL contract to data-platform |
| Define the tier rule expression and thresholds | `customer-success-analytics` | Hands rule doc to data-platform |
| Build the dbt models / warehouse tables | `data-platform` | Receives contract from this plugin |
| Land data from Salesforce / CS platform / support tool | `data-platform` | Receives signal requirements from this plugin |
| Build the BI surface (Sigma / Tableau / Superset) | `data-platform/dashboard-builder` | Receives "what to show" spec from this plugin |
| Implement the identity-resolution matcher | `data-platform` | Receives grain requirement from this plugin |

The output of a `customer-success-analytics` engagement is a **domain contract** (mart schema + tier rule + signal spec), not a running pipeline. The pipeline is data-platform's deliverable.

**Do:**
- Include an explicit `Handoff to data-platform:` section in every output — it names the build work that is being handed across the seam.
- Specify the contract in enough detail that data-platform can build it without returning to this plugin for decisions — column names, grain, NULL behavior, append-only vs. upsert.

**Don't:**
- Write dbt model YAML or Airbyte connection configs — that is data-platform's lane.
- Let the domain contract stay implicit because "data-platform will figure it out" — an implicit contract produces a mart that doesn't match the tier rule.
- Accept a BI-tool-computed metric as "good enough" — the mart-is-the-single-source rule applies.

## Edge cases / when the rule does NOT apply

- Solo engagement where the same person is playing both domain analyst and data engineer — the boundary is still maintained conceptually (domain design before build), even if the same agent executes both phases.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — the agent that produces and owns the domain contract
- [`../CLAUDE.md`](../CLAUDE.md) — §1 layer boundary table and §11 seams to neighbouring plugins

## Provenance

Codifies the layer boundary in `CLAUDE.md` §1 — the two-layer table that defines what this plugin owns and what data-platform owns. A plugin that builds across the seam creates unowned maintenance debt on both sides.

---

_Last reviewed: 2026-06-05 by `claude`_
