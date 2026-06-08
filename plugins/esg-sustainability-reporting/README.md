# ESG & Sustainability Reporting

The **esg-sustainability-reporting** plugin — the corporate ESG & sustainability-disclosure craft: the reporting layer that turns a company's sustainability obligations (regulatory, insurer-driven, procurement-driven) into a scoped, framework-aligned, **assurable** disclosure — distinct from the audited ledger, the raw data pipeline, and the regulatory filing route themselves.

## Agents

- **`esg-reporting-architect`** — Framework selection and scoping: which standard(s) apply (CSRD/ESRS, ISSB IFRS S1/S2, GRI, the SEC climate rule), double vs financial materiality, the reporting boundary and governance, the disclosure roadmap, and the crosswalk between overlapping frameworks so a shared data point is sourced once and disclosed against each.
- **`ghg-accounting-analyst`** — The GHG inventory: GHG Protocol Scopes 1/2/3 (all 15 Scope-3 categories), activity data and emission-factor sourcing (with vintage), location-based vs market-based Scope 2, base-year setting and the recalculation policy, the inventory boundary, and data-quality tiering.
- **`disclosure-and-assurance-lead`** — Disclosure drafting and assurance readiness: drafting the disclosure with its evidence trail, building data controls, limited vs reasonable assurance readiness, gap assessment, and auditor liaison.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install esg-sustainability-reporting@ravenclaude
```

## Seams

- **The audited financial-statement number a climate disclosure ties to** → `finance`; we consume the number, they produce and audit it.
- **The activity-data lineage, the pipeline controls, and personal data in the ESG data set** → `data-governance-privacy`; we specify the control objective, they own the lineage and the privacy posture.
- **The financial-regulator filing mechanic (SEC/EFRAG submission route, the legal filing obligation)** → `regulatory-compliance` + counsel; we produce the disclosure content, the filing route is theirs.
- **A legal-sufficiency opinion on a filing / a financial-audit opinion on the figures** → counsel / the assurance provider; we ready the disclosure *for* assurance, we do not issue the opinion.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `finance`, `data-governance-privacy`, and `regulatory-compliance`.
