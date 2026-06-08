# Changelog — public-sector-grants

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

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
