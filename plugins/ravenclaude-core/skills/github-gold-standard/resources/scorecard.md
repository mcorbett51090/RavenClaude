# GitHub gold-standard scorecard — <repo>

> Scored against the shipped catalog on <date>. **Structural coverage, not a security certification** — see the skill's honest-scope note.

**Core score: __ / 18** — band: gold (16–18) · silver (11–15) · bronze (≤10)
**Optional (row 10): pass | partial | fail | n/a**

## Per-dimension verdicts

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

## Remediation queue (ranked by leverage — highest first)

Row 8 (a path-filtered required check) always leads if present; then Tier A (2, 4, 6, 7), then Tier B (3, 5, 1), then Tier C (9, 10). `fail` outranks `partial` within a tier.

1. **[#_, verdict]** — apply: `<template or skill>` — because: `<catalog citation>`
2. …
