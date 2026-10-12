# description-budget-raises.md

Append-only. One entry per budget-raise PR, never edited (mirrors
`scripts/artifact-budgets.seed.json`'s own append-only convention elsewhere in
this repo). Format: `<date> | PR #<n> | chars:<old>-><new> tokens:<old>-><new> | <reason>`

No raises yet. The ceiling was seeded 2026-09-08 at chars=310696 tokens=66608
(see `description-budget.json` in this directory).

2026-10-11 | PR #1337 | chars:310696->312943 tokens:66608->67085 | Re-seed pinned_posture.skill_count 956->963 after adding ravenclaude-core/wallet-passes (375-char description) and catching the corpus that had grown past the 2026-09-08 pin. Ceiling restamped at today's measured total from scripts/skill-description-baseline.py (tiktoken cl100k_base).

2026-10-12 | PR (pending, branch feat/pp-layering-resolution) | chars:312943->313438 tokens:67085->67187 | Re-seed pinned_posture.skill_count 963->964 after adding power-platform/solution-layering-resolution (a disambiguating-category skill for diagnosing/resolving Dataverse solution layering). Ceiling restamped at today's measured total from scripts/skill-description-baseline.py (tiktoken cl100k_base).
