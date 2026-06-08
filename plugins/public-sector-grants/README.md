# Public-Sector Grants

The **public-sector-grants** plugin — the funder-side craft of government and nonprofit grants: deciding whether to pursue an opportunity, writing a fundable proposal, and staying compliant once you win — distinct from the donor side (cultivation, major gifts, the annual fund), which lives in `nonprofit-fundraising`.

## Agents

- **`grant-strategist`** — Pursuit decisions: opportunity search and fit assessment, funder research (priorities, eligibility, the NOFO/RFP), the logic model / theory of change (inputs → activities → outputs → outcomes → impact), and a disciplined go/no-go (cost-to-apply, probability of award, strings attached, the sustainability tail past the period of performance).
- **`proposal-writer`** — The application: proposal narrative mapped to the funder's review/scoring criteria, the needs/problem statement, SMART goals and objectives, the evaluation plan, and the budget plus budget narrative — every number justified and traced to the logic model.
- **`grants-compliance-analyst`** — Post-award obligations under 2 CFR Uniform Guidance: the allowable/allocable/reasonable cost test, indirect-cost rate and match/cost-share, sub-recipient monitoring (risk assessment → sub-award → monitoring → audit follow-up), drawdowns and federal financial reporting, and single-audit readiness.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install public-sector-grants@ravenclaude
```

## Seams

- **The donor side (individual cultivation, major gifts, annual fund, events)** → `nonprofit-fundraising`; this plugin wins and manages grants, they raise gifts.
- **The GL, fund accounting, the books** → `finance`; we say what's allowable and how the budget maps, they post the entries.
- **Security controls for federal data the award makes you hold (NIST 800-171 / CUI / FISMA)** → `cybersecurity-grc`; we flag the obligation, they build the controls.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `nonprofit-fundraising`, `finance`, and `cybersecurity-grc`.

> **Not legal, financial, or audit advice.** This plugin advises on fit, fundability, and compliance posture; the org's authorized official, finance office, and auditor own the legal and financial sign-off. Allowability, deadlines, and thresholds trace to the current 2 CFR, the award terms, and the NOFO — verify before relying on any number.
