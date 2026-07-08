---
name: consolidate-entities
description: "Roll up N entity trial balances (same period) into a group consolidation — reuses statement_engine per entity, then applies a BALANCED intercompany-elimination journal so IC receivable/payable and IC revenue/COGS net to zero, emits an entity-columns + eliminations + consolidated worksheet, and flags (does not remeasure) non-functional-currency entities for CTA. Runs scripts/consolidate.py. 'Eliminate before you consolidate.' Used by `controller`."
---

# Skill: consolidate-entities

**Purpose:** Turn several single-entity trial balances into one **group** view. The hard part of consolidation is not the addition — it is the **elimination**. Two legal entities each book their side of an intercompany transaction (a loan, an internal sale), so a naive sum **double-counts** it. Consolidated statements must show only what the group transacted with the *outside world*.

Engine: [`../../scripts/consolidate.py`](../../scripts/consolidate.py) (stdlib only, Python 3.8+). It **imports** [`statement_engine.py`](../../scripts/statement_engine.py) — consolidation adds no new accounting-sign logic; it composes the engine that already gets classification and the SECTION-based presentation sign right (so an intercompany line, like any contra-account, is signed by its section's natural side, never by the account's `normal_balance`).

## The discipline: eliminate before you consolidate

This is the auditor's mantra and the order the engine enforces:

1. **Produce** each entity's statements via `statement_engine.run` — same blocking classification discipline, one column per entity.
2. **Sum** by statement line into a worksheet. This pre-elimination total *still contains the intercompany balances on both sides* — the worksheet surfaces the double-count rather than hiding it.
3. **Eliminate** from an intercompany-transactions CSV expressed as a **balanced elimination journal** (Σ debits == Σ credits — asserted, `rc4` if not). Each amount is converted to a presentation sign with the same section convention, so every IC line nets to `0.00` in the consolidated column. Because the journal balances, the **consolidated balance sheet still balances to `0.00`** — asserted (`rc6`), not assumed.
4. **Flag** currency translation. See the honest caveat below.

## Honest note on currency translation (CTA)

An entity whose **functional currency differs from the group's presentation currency** needs a real remeasurement: assets at the closing rate, income at the average rate, equity at historical rates, with the plug landing in a **cumulative translation adjustment (CTA)** component of equity / OCI. **This engine does NOT perform that remeasurement.** It *flags* the entity and emits a CTA note; the provided trial balance is treated as if already stated in the presentation currency. That is a stated simplification, not a multi-currency close. A rigorous translation and its CTA must be prepared separately — this output is decision-support, not an audited consolidation (see [`../../CLAUDE.md`](../../CLAUDE.md) §3, §12 "GAAP/IFRS vs. management view", §4 "currency mixing without explicit FX rate disclosure").

## Invocation

```shell
python3 scripts/consolidate.py \
  --config skills/consolidate-entities/examples/atlas-group-2026-06.json \
  --out consolidated.json
```

The config JSON lists the entities (each: `profile`, `coa`, `tb`, optional `role`), the `presentation_currency`, the `fiscal_period`, and the `eliminations` CSV — all paths relative to the config file. The engine **blocks** if any entity's period disagrees with the group period, if an entity profile is invalid, if an entity has unmapped accounts (unless `--no-strict`), if the elimination journal is unbalanced, if an elimination line matches no worksheet line, or if the consolidated balance sheet fails to balance.

## The intercompany-eliminations CSV

Columns: `ic_id,description,statement,section,line,debit,credit`. Model each elimination as the reversing journal entry that removes the intercompany balance, and let the whole file balance (Σ debit == Σ credit). Worked example — a parent→sub loan and a parent→sub internal sale:

| ic_id | statement | section | line | debit | credit |
|---|---|---|---|---|---|
| IC-LOAN | BS | CurrentAssets | Intercompany receivable | 0 | 100000 |
| IC-LOAN | BS | CurrentLiabilities | Intercompany payable | 100000 | 0 |
| IC-SALE | IS | Revenue | Intercompany revenue | 200000 | 0 |
| IC-SALE | IS | COGS | Intercompany cost of goods sold | 0 | 200000 |

The IC sale is **revenue-neutral to the group**: consolidated revenue and COGS each drop by 200k, so gross profit and net income are **unchanged** — the group simply didn't sell to an outside customer. (An intercompany sale with **unrealized profit still sitting in ending inventory** would need an extra margin elimination; this fixture deliberately has none, and that limitation is called out here rather than silently assumed away.)

## Correctness discipline

- The golden fixture [`examples/expected-consolidated-2026-06.json`](examples/expected-consolidated-2026-06.json) is **hand-derived from the two source trial balances by independent arithmetic**, NOT frozen from an engine run.
- The acceptance suite [`../../scripts/test_consolidate.py`](../../scripts/test_consolidate.py) asserts the load-bearing claims: the pre-elimination sum **double-counts** each IC amount, the consolidated column **nets each IC line to zero**, the consolidated balance sheet **balances**, subtotals equal the goldens, an unbalanced elimination journal is **blocked**, and the non-USD subsidiary is **flagged for CTA**.

## Reuse per group

Entities and the group are **data** — a different set of profiles + trial balances + one eliminations CSV consolidates a different group with zero code change. Authoring a correct per-entity COA mapping is the real per-entity work (see [`../author-coa-mapping/SKILL.md`](../author-coa-mapping/SKILL.md)); authoring the elimination journal is the real per-group work.

## What this is not

Not an audit opinion, a GAAP/IFRS consolidation determination, or a multi-currency remeasurement. Non-controlling interests, step acquisitions, goodwill, and unrealized-inventory-profit eliminations are out of scope for this slice — flag them for a human preparer. Outputs are decision-support (see [`../../CLAUDE.md`](../../CLAUDE.md) §3).
