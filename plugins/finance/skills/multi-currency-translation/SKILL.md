---
name: multi-currency-translation
description: "Translate/remeasure ONE entity's functional-currency trial balance into a presentation-currency (USD) TB before consolidate.py, via scripts/remeasure.py. Current-rate method (A&L @ closing, P&L @ average, equity @ historical; plug = CTA to OCI/equity) or temporal method (monetary @ closing, non-monetary @ historical, P&L @ average except REV_EXP_HIST @ historical; plug = remeasurement G/L to net income). Reuses statement_engine's section-signed presentation + reasoning trail — no new sign logic. Blocks on a missing/invalid rate_class, blocks when the balancing plug fails the analytical CTA self-check, and refuses a highly_inflationary + current_rate combo (ASC 830 vs IAS 29). Decision-support, not an audited remeasurement. Used by `controller`."
---

# Skill: multi-currency-translation

**Purpose:** [`consolidate.py`](../../scripts/consolidate.py) *flags* a non-functional-currency entity and emits an honest CTA note, but treats its trial balance as if already stated in the group presentation currency. This skill removes that simplification: [`remeasure.py`](../../scripts/remeasure.py) translates **one** entity's functional-currency trial balance into a **presentation-currency (USD) trial balance** that then feeds `consolidate.py`'s worksheet — **before** its `SystemExit 6` "consolidated balance sheet == 0.00" assertion, which **stays** the guardrail.

Engine: [`../../scripts/remeasure.py`](../../scripts/remeasure.py) (stdlib only, Python 3.8+). It **imports** [`statement_engine.py`](../../scripts/statement_engine.py): the translated debits/credits are pure arithmetic (functional amount × the rate its `rate_class` maps to), but the **presentation sign** of every line is `statement_engine._present`'s section-based convention reused verbatim, and the subtotals + reasoning trail come from `statement_engine.build_income_statement` / `build_balance_sheet`. **No new accounting-sign logic.**

## The two methods

| | CURRENT-RATE (translation) | TEMPORAL (remeasurement) |
|---|---|---|
| Assets & liabilities | all @ **closing** | monetary @ **closing**, non-monetary @ **historical** |
| Income / expense | all @ **average** | @ **average** EXCEPT non-monetary-linked (COGS / depreciation / prepaid amort — `REV_EXP_HIST`) @ **historical** |
| Equity | @ **historical** | @ **historical** |
| Balancing plug | **CTA** — a component of OCI / equity; does **not** touch net income | **remeasurement gain/(loss)** — flows through **net income** |
| When | functional currency ≠ reporting currency (local currency is functional) | reporting currency **is** the functional currency (or a highly inflationary economy) |

## The `rate_class` column (COA mapping)

The per-entity COA mapping gains one column: `rate_class ∈ {MONETARY, NONMONETARY, EQUITY_CONTRIB, EQUITY_RE, REV_EXP, REV_EXP_HIST}`. A **blank or invalid** value **BLOCKS** the run (`rc3`) exactly like an unmapped account — the same `statement_engine.lint_mapping` discipline — and the engine also blocks if a `rate_class` disagrees with the account's statement/section (e.g. `MONETARY` on an equity line). See [`examples/coa-mapping-fx.csv`](examples/coa-mapping-fx.csv).

## The `rates.json`

```json
{
  "method": "current_rate",
  "closing": 1.1,
  "average": 1.05,
  "historical": { "default": 1.0, "1200": 1.02 },
  "highly_inflationary": false
}
```

`historical` is an object: a `default` plus optional per-account overrides (keyed by account id). An optional `dividends: {"amount": <functional>, "declaration_rate": <rate>}` feeds the analytical CTA self-check (defaults to zero). See [`examples/rates-current.json`](examples/rates-current.json) and [`examples/rates-temporal.json`](examples/rates-temporal.json).

## The CTA self-check (blocks a wrong plug)

The balance-sheet-balancing plug is not trusted on faith. For the current-rate method the engine computes the **analytical** CTA —

```
begin_net_assets × (closing − historical)
  + NI × (closing − average)
  − dividends × (closing − declaration)
```

— and **BLOCKS** (`rc5`) unless it equals the balancing plug within 0.01. A plug that doesn't reconcile to the theory is a bug, not a CTA.

## Hyperinflation refusal (ASC 830 vs IAS 29)

A `highly_inflationary: true` + `method: "current_rate"` combination is **REFUSED** (`rc7`). Under **ASC 830** a highly inflationary economy's books are **remeasured** as if the reporting currency were the functional currency (use `method: "temporal"`), never translated at the current rate. **IAS 29** (restate-for-inflation-then-translate at closing) is a *different framework* and is **out of scope** — flag it for a human preparer.

## Zero-drift no-op

When the entity's functional currency **equals** the presentation currency there is nothing to translate: the engine short-circuits and the emitted presentation TB (`--out-tb`) is a **byte-identical copy** of the source, so the `consolidate.py` path for an all-USD group is unchanged. Verified in [`../../scripts/test_remeasure.py`](../../scripts/test_remeasure.py).

## Invocation

```shell
python3 scripts/remeasure.py \
  --entity skills/multi-currency-translation/examples/eur-sub.json \
  --coa    skills/multi-currency-translation/examples/coa-mapping-fx.csv \
  --tb     skills/multi-currency-translation/examples/tb-eur-sub-2026-06.csv \
  --rates  skills/multi-currency-translation/examples/rates-temporal.json \
  --presentation-currency USD \
  --out-tb eur-sub-usd.csv \
  --out    eur-sub-translation.json
```

Then point the `consolidate.py` config's entity `tb` at the emitted USD trial balance. The engine blocks on: an invalid entity profile (`rc2`), a functional TB that is out of balance (`rc4`), a missing/invalid `rate_class` (`rc3`), a failed CTA self-check (`rc5`), and refuses a hyperinflation + current-rate combo (`rc7`).

## Correctness discipline

- The golden fixtures [`examples/expected-remeasured-current.json`](examples/expected-remeasured-current.json) and [`examples/expected-remeasured-temporal.json`](examples/expected-remeasured-temporal.json) are **hand-derived by independent arithmetic** from the EUR trial balance (each carries its `_derivation`), **NOT** frozen from a `remeasure.py` run.
- The acceptance suite [`../../scripts/test_remeasure.py`](../../scripts/test_remeasure.py) asserts the load-bearing claims: current-rate golden (CTA = 200, NI = 1050), temporal golden (remeasurement loss = −80, NI = 970), the CTA self-check blocks on a wrong plug, a blank/invalid `rate_class` blocks, the hyperinflation combo is refused, the all-USD case is a byte-identical no-op, and the emitted TB is balanced (so `consolidate.py`'s `rc6` guardrail is never tripped by construction).

## What this is not

Not an audited translation, a GAAP/IFRS determination, or a live-rate-verified remeasurement. Sourcing the closing/average/historical rates, the IdP / warehouse wiring, and any real credentials are the **consumer's** step. Non-controlling interests, intra-period rate movements, translation of accumulated OCI, and IAS 29 restatement are out of scope for this slice — flag them for a human preparer. Outputs are decision-support (see [`../../CLAUDE.md`](../../CLAUDE.md) §3, §4 "currency mixing without explicit FX rate disclosure", §12 "GAAP/IFRS vs. management view").
