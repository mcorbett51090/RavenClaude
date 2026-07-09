---
name: author-coa-mapping
description: "Author and validate the per-entity chart-of-accounts → statement-line mapping — the bespoke, judgment-laden asset that makes the close reusable per company and where mis-statements hide. Coverage-checked with statement_engine.py --lint-map. Used by `controller`."
---

# Skill: author-coa-mapping

**Purpose:** Build and validate the COA→statement-line mapping for a new entity. This is the genuinely reusable-per-company asset — the pivot engine is a commodity, but a *correct* mapping is bespoke and judgment-laden, and it is exactly where a misstatement hides. Treat authoring + validating the mapping as the deliverable, not an assumed input.

## When to use

- Onboarding a new entity/company to the close autopilot.
- A chart of accounts changed (new accounts, reorg) and the mapping must be refreshed.

## The mapping contract

A CSV, one row per GL account:

```
account,description,statement,section,line,normal_balance
```

- `statement` ∈ `IS` | `BS`
- `section` (IS) ∈ `Revenue` `COGS` `OpEx` `OtherIncomeExpense` `Tax`
- `section` (BS) ∈ `CurrentAssets` `NonCurrentAssets` `CurrentLiabilities` `NonCurrentLiabilities` `Equity`
- `line` — the statement line label the account rolls into
- `normal_balance` ∈ `debit` | `credit` (validation + documentation; presentation sign is derived from the **section**, which is what makes contra-accounts — e.g. accumulated depreciation — correct)

## Authoring discipline

1. **Every TB account must map to exactly one line.** No account left behind — the engine blocks (`--strict`) on any unmapped account.
2. **Classify by economic substance, not by account number.** Interest expense is `OtherIncomeExpense`, not `OpEx` or `COGS`; a mis-map here silently distorts gross profit and operating income while net income still ties (see the negative fixture).
3. **Contra-accounts stay in their asset/revenue section** with their natural `normal_balance`; the engine signs them correctly from the section.
4. **State the basis** (accrual vs cash; GAAP vs management view) — house rule §3 #12.

## Validate before you run

```shell
python3 scripts/statement_engine.py \
  --entity examples/meridian-robotics.json \
  --coa    <your-mapping>.csv \
  --tb     <your-trial-balance>.csv \
  --lint-map
```

`--lint-map` reports unmapped accounts, invalid statement/section values, bad `normal_balance`, and duplicates. A clean lint is the pre-build gate for the whole close cycle. Start from [`../produce-gaap-statements/examples/coa-mapping.csv`](../produce-gaap-statements/examples/coa-mapping.csv) as a worked template.

## Reuse note

The mapping is the per-entity unit of reuse. Keep one mapping CSV per entity beside its entity profile; the same engines then run unchanged for every company.
