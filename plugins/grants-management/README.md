# grants-management

> The **grantee-side lifecycle team** for Claude Code — the team that answers *"should we go after this grant, how do we win it, and how do we keep it clean through closeout?"* Two agents: the **grants-strategy-lead** (pipeline, funder fit, go/no-go, proposal strategy & narrative) and the **grants-compliance-and-reporting-specialist** (post-award compliance, budgets/indirect costs, reporting, subrecipient monitoring, audit readiness).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Not legal or accounting advice.** The compliance surface is US-federal-heavy and the governing facts move (2 CFR Part 200 revisions, SF-form versions, portal behavior). Volatile facts carry retrieval dates and are re-verified against the primary source before you rely on them.

## What it does

| You ask | It returns |
|---|---|
| "Should we apply for this — is the funder a fit?" | A fit score (mission/geography/population/funding-type alignment) + a go/no-go verdict weighing capacity and compliance burden, with the conditions that would flip it |
| "Build our grant pipeline." | A prioritized, capacity-weighted pipeline of prospects (federal / state / foundation / corporate) with fit scores, deadlines, and a pursue/pass call per row |
| "Draft the logic model and narrative." | A needs statement → logic model / theory of change → SMART objectives → evaluation plan → a NOFO-rubric-aligned narrative that chains end to end |
| "Assemble the full proposal / LOI." | The assembled package: narrative, budget + budget narrative, attachments, and a NOFO-criteria crosswalk — from a reusable boilerplate library |
| "Is this cost allowable? What indirect rate can we charge?" | A cost-principle test (allowable / allocable / reasonable, 2 CFR 200) + the indirect-rate path (NICRA vs 10% de minimis) with the reasoning |
| "Build the FFR and the RPPR." | The SF-425 Federal Financial Report + the performance report (RPPR/SF-PPR) mapped to the award's reporting calendar |
| "Subrecipient or contractor? Are we audit-ready?" | The 2 CFR 200.331 substance determination + a subrecipient monitoring plan, and a Single-Audit readiness check with the closeout checklist |

**Two rules it never breaks:** *fit before effort* (a grant you're not a fit for is negative ROI even if you win it), and *the budget mirrors the narrative* (every line ties to an activity, every activity has a line — the top reviewer red flag when it doesn't).

## What's inside

- **2 agents** — `grants-strategy-lead` (builds the pipeline, scores funder fit, runs go/no-go, and drives the logic model + proposal narrative + assembly) and `grants-compliance-and-reporting-specialist` (runs 2 CFR 200 cost allowability, indirect rates, time & effort, FFR/RPPR reporting, subrecipient monitoring, Single Audit, and closeout).
- **3 skills** — `build-grant-pipeline-and-prospect-fit`, `write-and-assemble-grant-proposals`, `manage-post-award-compliance-and-reporting`.
- **2 knowledge files** — a Mermaid grants-lifecycle decision tree (grant type → fit → go/no-go → apply → award → comply → report → close, + the funder/grant-type matrix + the subrecipient-vs-contractor test) and a 2026 grants-management-patterns reference (funder & grant types, logic model / theory of change, federal mechanics, 2 CFR 200 cost principles & indirect rates, reporting forms, subrecipient monitoring, Single Audit, tooling map).
- **2 templates** — a full grant-proposal outline (with a NOFO-criteria crosswalk) and a post-award compliance & reporting tracker.

## Where it sits in the funding stack

```
nonprofit-fundraising      →  individuals / major donors / annual fund / events   ("raise philanthropic dollars from people")
public-sector-govtech      →  the GRANTMAKER: design a funding program / NOFO      ("run a funding program as an agency")
accounting-bookkeeping     →  the general ledger / payroll / the 990               ("keep the books")
grants-management (HERE)   →  WIN the right grants, then run them CLEAN            ("pursue, win & administer institutional grants")
```

This plugin is the **grantee-side lifecycle** (with light grantmaker admin): it pursues, wins, and administers institutional/competitive grants — distinct from raising individual gifts (`nonprofit-fundraising`), from *being* the funder (`public-sector-govtech`), and from the ledger itself (`accounting-bookkeeping`). It does grant *cost allowability + fund reporting*, not the books.

## Domain stance

Concept-first (funder fit-before-effort, go/no-go gating, logic-model/theory-of-change, budget-mirrors-narrative, the allowable/allocable/reasonable cost test, subrecipient-vs-contractor substance, time & effort, compliance-calendar-from-day-one), fluent in the **US-federal mechanics** (SAM.gov registration + UEI, Grants.gov Workspace, the SF-424 family, 2 CFR Part 200 Uniform Guidance, indirect rates / NICRA / de minimis, SF-425 FFR + RPPR, Single Audit) and across grants systems (**Fluxx, Submittable, SmartSimple**, and **Instrumentl** for prospecting). Federal citations, form versions, and rate figures carry retrieval dates — re-verify against the primary source before pinning in a client deliverable. **Not legal or accounting advice.**

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install grants-management@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
