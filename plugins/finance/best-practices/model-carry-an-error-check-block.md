# Carry a single error-check block that returns zero when the model is sound

**Status:** Pattern
**Domain:** Financial modeling / auditability
**Applies to:** `finance`

---

## Why this exists

A model that *looks* right and a model that *proves* it is right are different artifacts. The difference is a dedicated **error-check block** — a small panel of integrity tests, each of which returns 0 (or TRUE) when the model is internally consistent and a loud non-zero when it is not. Without it, a broken link, a sign error, or a stale input hides until a reviewer happens to stumble on it — usually in front of an audience. The `model-review` skill runs a 7-pass review whose error-check pass looks for exactly this; the discipline is to bake those checks *into the model* so they re-run on every recalc rather than relying on a human to re-walk them. A green error-check block is the model's own statement that its mechanics tie; a red flag in it is a stop-ship signal.

## How to apply

Put every integrity test in one labelled block, each row a check that should read 0, plus a single master flag that aggregates them:

```
Error-check block (one tab, or a panel top-right of each statement):
  BalanceCheck          = TotalAssets − (TotalLiab + Equity)        # must be 0 every period
  CashTie               = CF_EndingCash − BS_Cash                   # must be 0
  RetainedEarningsTie   = RE_open + NetIncome − Dividends − RE_close # must be 0
  DebtScheduleTie       = Debt_BS − Debt_schedule_ending            # must be 0
  PP&E_RollTie          = PPE_open + Capex − Deprec − PPE_close     # must be 0
  NoNegativeInventory   = MIN(InventoryRow)                          # must be ≥ 0
  MASTER_FLAG           = SUM(ABS of all checks)                     # 0 = clean; anything else = STOP
```

Conditional-format `MASTER_FLAG` red when non-zero so it is impossible to miss.

**Do:**
- Aggregate every check into one master flag, and surface that flag where a reviewer sees it first.
- Test each *tie* the three-statement model relies on (balance, cash, RE roll, debt, PP&E) — the checks mirror the links.
- Re-read the error block before sending the model anywhere; a non-zero flag is a blocker, not a footnote.

**Don't:**
- Scatter ad-hoc check cells across tabs where nobody re-reads them — one block, one flag.
- Wrap a failing check in `IFERROR(...,0)` to make the flag green — that is the integrity failure the block exists to catch.
- Ship a model with a non-zero master flag and a note "will fix" — fix it or label the model draft/blocked.

## Edge cases / when the rule does NOT apply

- **Single-statement analyses** (a standalone margin walk, a quick P&L bridge) have no balance sheet to tie — they carry only the checks relevant to their own mechanics, which may be none.
- **Designed, disclosed circulars** may make a check momentarily non-zero mid-iteration; the block reads the *converged* state, and the designed loop is documented per [`./model-design-disclose-circular-references.md`](./model-design-disclose-circular-references.md).
- **A genuinely throwaway scratch calc** carries no error block — but the moment it feeds a deliverable, the block attaches.

## See also

- [`./link-the-three-statements.md`](./link-the-three-statements.md) — the ties the error block tests (`BalanceCheck`, cash tie).
- [`./model-derive-the-cash-flow-bridge-from-net-income.md`](./model-derive-the-cash-flow-bridge-from-net-income.md) — the bridge whose ending cash the `CashTie` check verifies.
- [`./model-design-disclose-circular-references.md`](./model-design-disclose-circular-references.md) — why a check may flash non-zero inside a designed loop.
- [`../skills/model-review/SKILL.md`](../skills/model-review/SKILL.md) — the error-check pass of the 7-pass review.

## Provenance

Codifies the error-check pass of the `model-review` 7-pass review ([`../CLAUDE.md`](../CLAUDE.md) §8), the `financial-modeler` "balance check on every BS tab" opinion, and house opinion #11 (models age — they need self-tests). Adjacent to the existing linkage and cash-bridge rules.

---

_Last reviewed: 2026-05-30 by `claude`_
