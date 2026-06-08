# Changelog — public-sector-grants

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth build-out — no agent / skill / command surface change; the three agents, three skills, three
commands, two templates, and the advisory hook are unchanged. This release deepens the knowledge,
best-practices, scenarios, and adds a runnable calculator.

- **Knowledge bank to 5 Mermaid decision trees** — added go/no-go on an opportunity (mission-fit +
  win-probability + match/sustainability gates), where the match / cost-share comes from (required-vs-encouraged,
  non-federal sourcing, in-kind valuation), and selected-items-of-cost (the extra 2 CFR 200 Subpart E test
  with prior-approval gates) alongside the existing sub-recipient-vs-contractor and cost-allowability trees.
  The dated 2026 grant-lifecycle / authority map (Grants.gov, SAM.gov/UEI, 2 CFR 200 Subparts E & F, FFR,
  the single-audit threshold) is extended and re-stamped — every row `[verify-at-build]`.
- **12 best-practices** (up from 8) — added `objectives-are-smart-or-wishes`, `period-of-performance-is-a-hard-boundary`,
  `the-recipient-owns-the-obligation`, and the indirect/match/authority rules; the index table is reconciled.
- **Scenarios bank to 5 field notes** — added `budget-line-with-no-narrative-drew-a-finding`,
  `match-pledged-with-federal-dollars`, and `drew-funds-ahead-of-need` (all dated, 9-field schema, `reviewed: false`).
- **Runnable calculator** — `scripts/grants_calc.py` (stdlib-only, argparse, ruff-clean, Python 3.9+):
  `indirect` (indirect-cost recovery on an MTDC base with the 2 CFR exclusions removed before the rate),
  `match` (required cost-share + shortfall, with an `--of-federal` gross-up), and `budget` (category roll-up,
  % of total, and a personnel line from FTE × salary × effort%). Decision-support, not an allowability determination.
- Bumped `version` 0.1.0 → 0.2.0 and reconciled the best-practices count (12) + calculator mention in `plugin.json`.

## 0.1.0 — 2026-06-08

Initial release. The funder-side grants discipline (find → propose → award → manage → report → close),
distinct from the donor-side `nonprofit-fundraising`.

- **3 agents** — `grant-strategist` (opportunity search + fit assessment, funder research, logic model / theory of
  change, go/no-go), `proposal-writer` (narrative mapped to review criteria, needs/problem statement, SMART goals &
  objectives, evaluation plan, budget + budget narrative), `grants-compliance-analyst` (2 CFR Uniform Guidance —
  allowable/allocable/reasonable costs, indirect rate & match, sub-recipient monitoring, drawdowns & federal financial
  reporting, single audit). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `opportunity-fit-and-logic-model`, `proposal-narrative-and-budget`, `uniform-guidance-compliance`.
- **Knowledge bank** — `public-sector-grants-decision-trees.md`: Mermaid trees (go/no-go on an opportunity,
  sub-recipient-vs-contractor classification, cost-allowability) + a dated 2026 grant-lifecycle / authority map
  (Grants.gov, SAM.gov, 2 CFR 200, the single-audit threshold) — `[verify-at-build]`.
- **8 best-practices**, **3 commands** (`assess-grant-fit`, `draft-proposal`, `check-cost-allowability`),
  **2 templates** (grant-proposal outline, budget narrative), **1 advisory hook**
  (`check-public-sector-grants-anti-patterns.sh`; `GRANTS_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: donor fundraising → `nonprofit-fundraising`; GL / fund accounting → `finance`; security controls for federal
  data → `cybersecurity-grc`. Requires `ravenclaude-core@>=0.7.0`.
