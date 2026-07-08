---
name: finance-elt-staging
description: "Normalize a raw accounting-system trial-balance export (QuickBooks Online / NetSuite / Xero / Sage Intacct) into the ONE canonical staging schema — account,description,debit,credit,entity,period,currency — that the close autopilot consumes, via a data-driven per-source column-map. Stamps entity/currency dimensions + a close-period watermark, blocks on an unbalanced export, writes atomically. Runs scripts/tb_stage.py. Used by `controller`."
---

# Skill: finance-elt-staging

**Purpose:** Turn a messy vendor export into the **canonical trial-balance staging table** the rest of the controller-autopilot reads — without hand-editing headers, and without a per-vendor code branch. This is the ELT *staging* seam: the deterministic transform between "a connector produced a raw CSV" and "`statement_engine.py` / `reconcile_summary.py` can consume it."

Engine: [`../../scripts/tb_stage.py`](../../scripts/tb_stage.py) (stdlib only, Python 3.8+).

## The load-bearing contract

The canonical staging columns are, **exactly and in this order**:

```
account,description,debit,credit,entity,period,currency
```

This header is **byte-identical to a dbt staging model** (`stg_trial_balance`). A locally-staged CSV and the warehouse staging table are therefore the **same contract** — "local CSV == staging columns" is the whole point. Do **not** reorder or rename it; every downstream engine keys off these names. `validate` rejects any file whose header isn't byte-identical.

## When to use

- You have a raw TB export from an accounting system and need the canonical staging CSV that feeds [`produce-gaap-statements`](../produce-gaap-statements/SKILL.md) and [`reconciliation-summary`](../reconciliation-summary/SKILL.md).
- You are wiring a new source (a new entity's GL) — you author its **column-map**, not new code.

## How it works — one adapter, data-driven per source

There is **no per-vendor code path**. Each source is described by a small **column-map JSON** ([`examples/column-map-netsuite.json`](examples/column-map-netsuite.json), [`examples/column-map-qbo.json`](examples/column-map-qbo.json)):

| Key | Meaning |
|---|---|
| `map` | `{canonical_col: source_col}` — at minimum `account`, `description` |
| `amount_column` | *(optional)* one **signed** net-amount column to split into debit/credit (NetSuite-style) |
| `amount_sign` | `debit_positive` (default) or `credit_positive` — which sign is a debit |
| `constants` | static injections for columns the export lacks (`entity`, `currency`) |
| `close_period` | the **close-period watermark** stamped into every row's `period` |

The two example maps target the **same** entity/period from **different source shapes** — NetSuite's single signed amount and QBO's separate `Debit`/`Credit` columns — and both normalize to the identical canonical output. That is the reuse claim, proven by the acceptance suite.

## The three disciplines that make it honest

1. **Dimensions + a close-period watermark are stamped, not assumed.** `entity` and `currency` become explicit columns (so a multi-entity / multi-currency staging table can be filtered downstream), and every row carries the `period` being closed — the watermark that makes staging partitionable / incrementally loadable by close period.
2. **Blocks on a bad export.** `stage` validates its own output *before* publishing — canonical header, numeric debit/credit, non-blank dimensions + watermark, and the fundamental invariant **debits == credits** — and refuses (non-zero exit) to emit a broken trial balance rather than silently landing it.
3. **Atomic write.** Output is written to a temp file and `os.replace`d into place, so a reader never sees a half-written staging file.

## Invocation

```shell
# Normalize a raw NetSuite-style export -> canonical staging CSV
python3 scripts/tb_stage.py stage \
  --raw        examples/raw-export-netsuite.csv \
  --column-map examples/column-map-netsuite.json \
  --out        staging/trial-balance-MRI-2026-06.csv

# CLI can override/supply the dimensions + watermark (reuse one map across periods)
python3 scripts/tb_stage.py stage \
  --raw examples/raw-export-netsuite.csv --column-map examples/column-map-netsuite.json \
  --out staging/tb.csv --period 2026-07 --entity MRI-UK --currency GBP

# Validate any canonical staging file (columns/types + debits==credits)
python3 scripts/tb_stage.py validate --staging staging/trial-balance-MRI-2026-06.csv
```

The staged CSV then flows straight into `statement_engine.py --tb` and `reconcile_summary.py --tb`.

## Extraction is a separate, credentialed tier — not this skill

This skill operates on a raw export **file**. Pulling that file from a vendor API (OAuth2, rotating refresh tokens, rate limits, pagination) is a **separate tier** with real credential-handling failure modes. Read them before wiring a live connector:

- **Blocking connector facts + the rotating-refresh-token failure mode:** [`../../knowledge/finance-elt-connector-facts.md`](../../knowledge/finance-elt-connector-facts.md)
- **Per-entity wiring (ENV-VAR NAMES only — never values):** [`../../templates/connector-config.template.json`](../../templates/connector-config.template.json)

## Correctness discipline

- The golden [`examples/expected-staging-2026-06.csv`](examples/expected-staging-2026-06.csv) is **hand-derived** from the raw export by independent arithmetic (each signed amount split by sign), **not** frozen from a `tb_stage.py` run — so a staging bug cannot ship inside its own golden. Acceptance suite: [`../../scripts/test_elt_stage.py`](../../scripts/test_elt_stage.py).
- All fixtures are **synthetic and obviously fake** (the Meridian Robotics worked entity); no company data, PII, or secrets.

## What this is not

Not an accounting/audit/tax opinion, and not a live connector — outputs are decision-support (see [`../../CLAUDE.md`](../../CLAUDE.md) §3). Staging normalizes structure and enforces the TB invariant; it does **not** validate that the source GL is itself correct, reconciled, or complete. A balanced staging file is a necessary, not sufficient, condition for a trustworthy close — reconciliation (`reconciliation-summary`) and the governed review→approve→lock spine (`close-approval-workflow`) still apply.
