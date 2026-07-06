---
name: close-schedules
description: "Produce the recurring close supporting schedules — fixed-asset depreciation rollforward, prepaid amortization, and deferred-revenue waterfall — from summarized inputs, each self-checking so beginning + movements == ending (and NBV = cost − accumulated depreciation) to the cent. Straight-line, blocks (--strict) on a schedule that does not tie. Runs scripts/schedule_engine.py. Used by `controller`."
---

# Skill: close-schedules

**Purpose:** Generate the supporting schedules a controller re-derives every close and staples behind the balance sheet as tie-out evidence — fixed-asset depreciation, prepaid amortization, deferred-revenue recognition. Producing them is a **commodity** (a fixed-asset sub-ledger or an ERP amortization module already does it); this engine earns its place the way the rest of the controller-autopilot does — it is **self-checking and blocking**, so a schedule can enter the governed close ([`close-approval-workflow`](../close-approval-workflow/SKILL.md)) as evidence rather than as an unverified attachment.

Engine: [`../../scripts/schedule_engine.py`](../../scripts/schedule_engine.py) (stdlib only, Python 3.8+).

## When to use

- You are wiring the close cycle and need the depreciation / prepaid / deferred-revenue schedules that support the fixed-asset, prepaid, and deferred-revenue balance-sheet lines.
- You want a rollforward whose arithmetic is *checked*, not just presented.

## The three schedules

| Subcommand | Rollforward identity | Ties into |
|---|---|---|
| `depreciation` | beginning NBV + additions − depreciation − disposals(NBV) = ending NBV | NonCurrentAssets (net of accumulated depreciation, a contra) |
| `prepaid` | opening + additions − amortization = ending | CurrentAssets (prepaid expenses) |
| `deferred-revenue` | opening + billings − recognized = ending | CurrentLiabilities (deferred/unearned revenue) |

## The two disciplines that make it honest

1. **Every schedule must tie.** Each subcommand is a rollforward whose identity is *beginning + movements == ending*, asset-by-asset **and** in total. Depreciation carries three parallel rollforwards — gross cost, accumulated depreciation, and NBV — with the cross-tie **NBV = gross cost − accumulated depreciation** checked at both ends. `--strict` exits non-zero (rc5) on a schedule whose portfolio rollforward does not tie. A schedule that does not tie is not evidence — it is a plug wearing a schedule's clothes.
2. **Straight-line, disclosed.** Straight-line depreciation (full-month convention), straight-line prepaid amortization, and ratable revenue recognition, each with a **final-period catch-up** so the balance lands exactly at its floor (salvage for an asset, zero for a fully-amortized prepaid or fully-recognized contract). The method is stamped on the artifact. Anything a real close needs beyond straight-line — accelerated/MACRS **tax** depreciation, usage-based recognition, ASC 606 variable consideration, partial-period conventions — is **out of scope** and must be modeled explicitly, never assumed here.

## Presentation sign (reuses the statement-engine convention)

Amounts carry the sign of the **statement section** the schedule ties into, not an account's normal balance — the same rule as [`statement_engine._present()`](../../scripts/statement_engine.py). Gross fixed assets and prepaids are asset-section (debit-positive) positive magnitudes; **accumulated depreciation is a contra-asset** (credit-natural) presented as a positive number that *reduces* NBV within the asset section; deferred revenue ties into a liability section (credit-positive). This is what keeps the contra correct.

## Invocation

```shell
python3 scripts/schedule_engine.py depreciation \
  --assets examples/fixed-assets-2026-06.csv --period 2026-06 --strict --out fa-rollforward.json

python3 scripts/schedule_engine.py prepaid \
  --prepaids examples/prepaids-2026-06.csv --period 2026-06 --strict

python3 scripts/schedule_engine.py deferred-revenue \
  --contracts examples/deferred-revenue-2026-06.csv --period 2026-06 --strict
```

Input CSV shapes (SYNTHETIC examples in [`examples/`](examples/)):

- **depreciation** — `asset_id,description,cost,salvage_value,useful_life_months,in_service_month,disposal_month,disposal_proceeds` (disposal columns optional).
- **prepaid** — `prepaid_id,description,total_amount,term_months,start_month`.
- **deferred-revenue** — `contract_id,description,billing_amount,term_months,start_month`.

`--period` is `YYYY-MM`. The output also carries a full month-by-month `full_schedule` per prepaid/contract for the whole term (drains to exactly 0).

## Correctness discipline (from the FORGE red-team)

- The golden fixture [`examples/expected-schedules-2026-06.json`](examples/expected-schedules-2026-06.json) is **hand-derived from the source CSVs by independent arithmetic**, NOT frozen from an engine run — so a bug cannot ship inside its own golden. Worked cases: a mid-life machine (24/60 months), an addition placed in service in the period (depreciates its first month), and a mid-life disposal (removes cost + accumulated depreciation, books a $2,000 gain on proceeds).
- The acceptance suite [`../../scripts/test_schedules.py`](../../scripts/test_schedules.py) asserts each rollforward ties, matches the golden, and that `--strict` blocks (rc5) a non-tying schedule.

## Coordinating the tax calendar

The recognition/depreciation cadence here is the **book** view. Where book and tax diverge (MACRS vs. straight-line, ASC 606 vs. tax timing) that difference feeds the ASC 740 provision and the tax calendar — coordinated (not determined) via [`../../knowledge/tax-close-calendar.md`](../../knowledge/tax-close-calendar.md) and [`../../templates/tax-calendar.md`](../../templates/tax-calendar.md). Those are **controller coordination** aids; a tax determination routes to a licensed CPA / tax advisor.

## What this is not

Not an audit opinion, a GAAP determination, or a tax-basis calculation — outputs are decision-support (see [`../../CLAUDE.md`](../../CLAUDE.md) §3). A schedule derived from a summarized input file is not a substitute for a fixed-asset sub-ledger reconciled to the GL, nor for a tax depreciation calc; those land with the ELT / sub-ledger tier.
