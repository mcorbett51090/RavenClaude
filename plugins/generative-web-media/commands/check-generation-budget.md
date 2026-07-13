---
description: "Report a project's AI-generation spend against its per-project cap (spent / remaining / by draft-vs-final tier), failing loudly when over budget. You supply every unit price — the tool bakes in zero prices; all provider prices are [unverified]."
argument-hint: "[path to the spend .jsonl] [--budget <cap>]"
---

You are running `/generative-web-media:check-generation-budget`. Use `asset-provenance-guardian` + the `generation-budget-guard` skill.

> The tool BAKES IN ZERO PRICES. Every unit price is user-supplied; provider prices are `[unverified — confirm on provider pricing page]`. Outputs are decision-support arithmetic, not a quote.

## Steps

1. **Ensure spend is being logged.** Each generation should append a spend line:

   ```shell
   python3 scripts/gen-budget.py add --ledger media/spend.jsonl \
     --model flux2-pro --unit-price 0.055 --count 8 --tier final --label "hero variants"
   ```

   (`--unit-price` is YOUR number from the provider's pricing page.)

2. **Report spend vs the cap:**

   ```shell
   python3 scripts/gen-budget.py status --ledger media/spend.jsonl --budget 25.00
   ```

   It prints spent / remaining / by-tier and **exits non-zero if over budget** (LOUD-FAIL — never a silent pass).

3. **Interpret** — if over budget, stop generating or raise the cap deliberately. If draft spend dwarfs final spend, the cheap-draft-then-final discipline is working; if premium spend is spread across many iterations, tighten it (draft first).

## Output

The budget status (spent / remaining / by-tier / over-budget flag) and the recommendation. Every price echoed as `[unverified]`.
