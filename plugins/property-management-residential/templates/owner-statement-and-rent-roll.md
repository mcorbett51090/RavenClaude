# Owner Statement & Rent Roll

> Output of `owner-and-portfolio-reporting-analyst` / the `owner-reporting-and-rent-roll` skill. The rent roll
> reconciles to reality; NOI is **operating-only**; the books of record belong to `finance`. Tenant PII never
> appears here.

## 1. Rent roll (the source of truth)

| Unit | Tenant | Lease start | Lease end | Market rent | Actual rent | Balance / aging | Status |
|---|---|---|---|---|---|---|---|
| | | | | | | | <occupied / vacant / notice / down> |

_Reconciles to the ledger every period. A balance that doesn't reconcile is a data-integrity problem to fix first._

## 2. Occupancy / vacancy

| Metric | This period | Notes |
|---|---|---|
| Physical occupancy | | units occupied / total |
| Economic occupancy | | actual rent collected / gross potential |
| Vacancy loss | | unrecoverable revenue from vacant days |
| Time-to-lease / turn time | | turn clock starts at NOTICE |

## 3. Delinquency & collections ladder

| Aging bucket | $ | # accounts | Ladder step (uniform) |
|---|---|---|---|
| 1-30 | | | reminder |
| 31-60 | | | late notice |
| 61-90 | | | pay-or-quit → **FLAG legal steps to counsel** |
| 90+ | | | counsel / charge-off review |

_One documented ladder applied to **every** account — selective enforcement is a fair-housing + financial-control risk._

## 4. Owner statement & NOI (operating-only)

| Line | $ |
|---|---|
| Operating income (rent + other operating) | |
| − Operating expenses (mgmt, R&M, turns-as-opex, taxes, insurance, utilities) | |
| **= NOI (operating-only)** | |
| _Excluded from NOI:_ debt service, capex, depreciation | _not here_ |
| Distributions to owner | |

_NOI = operating income − operating expenses, **excluding** debt service, capex, depreciation. NOI is **not** cash flow. Capex (roof, renovation-grade turn) is excluded — route capex/opex classification to `finance`._

## 5. Handoff to the books of record

| What | Routed to |
|---|---|
| Trust-account reconciliation, GL posting, audited financials, tax | `finance` |
| Acting on a delinquency (notice/non-renewal) or vacancy (re-lease) | `leasing-and-tenant-ops` |
| Eviction / collections / charge-off legality | **qualified counsel** (flag and route) |
| Tenant PII in any output | `ravenclaude-core/security-reviewer` |

---

```
Status: ...
Files changed: ...
Fair-housing / habitability flags: ...
Operational impact: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```
