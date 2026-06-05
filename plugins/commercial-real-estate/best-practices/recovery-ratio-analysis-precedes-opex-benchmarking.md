# Recovery Ratio Analysis Precedes OpEx Benchmarking

**Status:** Primary diagnostic
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

A property with $12/sf in operating expenses looks expensive compared to a market benchmark of $9/sf — unless 85% of those expenses are reimbursed by tenants, making the landlord's net burden $1.80/sf. Conversely, a property at $8/sf that recovers only 40% of expenses leaves the landlord with $4.80/sf of unrecovered cost that does not appear in a gross-expense comparison. OpEx benchmarking without recovery-ratio analysis produces misleading conclusions and incorrect NOI underwriting.

## How to apply

Before benchmarking operating expenses, compute the recovery rate and the net landlord burden:

```
Recovery Ratio Analysis — [Property Name]
───────────────────────────────────────────
Lease structure:  [ ] NNN  [ ] Modified gross  [ ] Full service / gross
Expense stop year:  ____  (for modified gross / full service leases)

Total operating expenses (trailing 12 months):     $______  ($___/sf)
  Recoverable expenses (CAM + tax + insurance):     $______  ($___/sf)
  Non-recoverable (management fee, structural, etc.): $______  ($___/sf)

Actual recoveries collected:                        $______  ($___/sf)
Recovery ratio:    recoveries ÷ recoverable expenses = ___%  [target by type: NNN ≈95%+, MG ≈60-80%]
Gross-up (for vacancy):  Recoveries if 100% occupied = $______

Net landlord burden:
  Total expenses                                    $______
  Less: actual recoveries                          ($______)
  Net landlord cost of operations:                  $______  ($___/sf)

Comparison to benchmark:  net landlord burden $___/sf vs. market ___/sf for [lease type]

Issues flagged:
  [ ] Recovery ratio below market — lease language or billing process?
  [ ] Caps or stops limiting recovery — model the NOI impact
  [ ] Expense category not recoverable under leases — identify and separate
```

**Do:**
- Run the recovery analysis on the trailing 12-month actual data before building the forward NOI model.
- Identify any recovery leakage: expense caps, lease-defined exclusions, or billing errors that reduce actual recoveries below contractual entitlement.
- Model the gross-up: what recoveries would be at stabilized occupancy, not actual vacancy-depressed collections.

**Don't:**
- Compare gross operating expenses to a per-sf benchmark without adjusting for lease structure — a full-service building's gross expenses are structurally different from a NNN building's.
- Treat the recovery ratio as fixed; it changes when vacancy changes, when expense stops reset, or when lease terms roll.
- Omit management-fee expenses from the opex total — they reduce NOI even if they are not separately recoverable.

## Edge cases / when the rule does NOT apply

Single-tenant NNN properties with full expense pass-through and no caps have a structural recovery ratio of approximately 100%; the analysis confirms the lease terms rather than diagnosing a problem.

## See also

- [`../agents/asset-property-manager.md`](../agents/asset-property-manager.md) — owns recovery management and tenant billing.
- [`./operating-expenses-are-an-underwriting-input-not-a-plug.md`](./operating-expenses-are-an-underwriting-input-not-a-plug.md) — the governing rule on building opex from the bottom up.

## Provenance

Codifies CLAUDE.md §3 #7 (operating expenses are an underwriting input, not a plug) with a recovery-ratio instrument that precedes any benchmarking step. Recovery-ratio analysis is standard practice in CRE asset management and acquisition due diligence [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
