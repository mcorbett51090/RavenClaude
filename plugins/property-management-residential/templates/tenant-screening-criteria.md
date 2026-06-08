# Tenant Screening Criteria — Standard

> Output of `leasing-and-tenant-ops` / the `leasing-and-screening` skill. A consistent, documented standard
> **applied identically to every applicant**. This is an operational standard, **not legal advice** — every
> protected-class-adjacent or legally-constrained element is FLAGGED and routed to qualified counsel.

## 0. Fair-housing posture (read first)

- This standard is **flagged, not adjudicated** for legality. Protected classes (federal: race, color, national origin, religion, sex, familial status, disability — plus state/local additions like source of income) are an **escalation trigger**, not a checklist cleared here.
- Apply **the same criteria to every applicant**, in the same order, recorded the same way. The defense against a discrimination claim is uniformity + documentation.

## 1. Objective criteria (same for everyone)

| Criterion | Standard | Notes / FLAG |
|---|---|---|
| Income | <e.g. gross income ≥ ~2.5-3x rent> | source-of-income use is legally constrained → **FLAG to counsel** |
| Credit history | <threshold / what's disqualifying> | adverse-action notice may be required → **FLAG** |
| Rental history / prior eviction | <lookback + what disqualifies> | |
| Criminal history | <if used at all> | use is heavily legally constrained → **FLAG to counsel before using** |
| Occupancy standard | <persons per bedroom> | familial-status risk → **FLAG** |
| References / verification | <employment, prior landlord> | |

## 2. Process (uniform + documented)

1. Same application, same fee, same criteria, same order — for every applicant.
2. Record which criterion each decision (approve / conditional / deny) rests on, with the date.
3. Reasonable-accommodation / modification requests → **FLAG to counsel**, do not deny or adjudicate.
4. Adverse action (denial) → record the criterion; the required-notice question → **FLAG**.

## 3. PII handling

- Screening reports, SSNs, bank/pay data: minimized, referenced not quoted, never pasted into outputs. Handle under `ravenclaude-core/security-reviewer`.

## 4. Handoff

| What | Routed to |
|---|---|
| Fair-housing / denial / accommodation legality | **qualified counsel** (flag and route) |
| The lease document terms / enforceability | **qualified counsel** |
| Deposit trust-account treatment / tax | `finance` |
| The unit turn behind a move-out | `maintenance-coordinator` |

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
