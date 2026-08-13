# GitHub gold-standard scorecard — <repo>

> Scored against the shipped catalog on <date>. **Structural coverage, not a security certification** — see the skill's honest-scope note.

## Score — PROPORTIONAL (the denominator is the count of APPLICABLE rows)

- **Core (rows 1–9, always applicable): __ / 18** (each row 0/1/2)
- **Agent-operability (rows A1–A3): __ / 6 — or N/A** — N/A **as a group** if the repo runs no agent-in-CI workflow (no `claude-code-action`/`@claude`-style workflow). N/A rows are **excluded from the denominator**, scored neither 0 nor 2.
- **Optional (row 10): pass | partial | fail | n/a** — scored separately, not in the band.

**Band = round(100 × score ÷ applicable_max):** gold ≥ 89% · silver 61–88% · bronze < 61%

- `applicable_max` = **18** (no agent-in-CI workflow) or **24** (agent-in-CI workflow present → the three agent rows apply).
- **Why proportional (RT-4):** fixed integer cutoffs cannot express a dynamic denominator, so a repo that aces the core but is thin on agent-operability is still judged on the fuller denominator. A no-agent-workflow repo can still reach gold on /18; an agent-in-CI repo is judged on /24.
- **Shape self-check (advisory):** compute `applicable_max` as `2 × (count of non-N/A rows among 1–9, A1–A3)`, and confirm the band's denominator equals that count before reporting the band.

## Per-dimension verdicts — core (rows 1–9 + optional 10)

| # | Dimension | Leverage | Verdict | Evidence (one line) | Catalog source |
|---|---|---|---|---|---|
| 1 | Branch-delete recovery | B | | | P3 §House-rule |
| 2 | Workflow static analysis | A | | | P4 §1.1 |
| 3 | Least-privilege permissions floor | B | | | P4 Rule 1 |
| 4 | SHA-pinned actions | A | | | P4 Rule 2 |
| 5 | OIDC over long-lived secrets | B | | | P4 Rule 3 |
| 6 | Semantic-PR / commit-message gate | A | | | P3 §1.5 |
| 7 | Secret scanning + push protection | A | | | P4 §1.6 |
| 8 | Required checks NOT path-filtered | A (trap) | | | P4 Rule 5 |
| 9 | Worktree lifecycle hygiene | C | | | P4 §1.3 |
| 10 | Merge queue / CODEOWNERS (optional) | C | | | P4 Rule 6 |

## Agent-operability rows (N/A **as a group** if the repo runs no agent-in-CI workflow)

| # | Dimension | Leverage | Verdict | Evidence (one line) | Catalog source |
|---|---|---|---|---|---|
| A1 | Agent-workflow least-privilege `permissions:` **and** default-token-suppression avoided (a push that must trigger downstream is authed as an App/PAT/OIDC, not the default `GITHUB_TOKEN`) | A | | | github-actions-hardening.md Rule 7 |
| A2 | Agent PR template present (`.github/PULL_REQUEST_TEMPLATE/agent_pr_template.md`) | B | | | agent-pr-identity.md |
| A3 | Structural anti-self-approval present (`agent-approval-check.yml` with ≥1 `EXCLUDED_APPROVERS` entry, counting only write-access reviewers) | A | | | claude-in-ci.md |

## Remediation queue (ranked by leverage — highest first)

Row 8 (a path-filtered required check) always leads if present; then Tier A (2, 4, 6, 7, A1, A3), then Tier B (3, 5, 1, A2), then Tier C (9, 10). `fail` outranks `partial` within a tier.

1. **[#_, verdict]** — apply: `<template or skill>` — because: `<catalog citation>`
2. …
