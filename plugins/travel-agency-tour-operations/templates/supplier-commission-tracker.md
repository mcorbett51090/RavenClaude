# Supplier Commission Tracker — <agency / period>

> Output template for the booked-vs-paid commission ledger and recovery worklist. **No traveler PII** — reference bookings by internal ID/placeholder, never traveler names or payment data. Rates and settlement terms are `[verify-at-use]` per supplier agreement.

## Context
- **Agency / advisor:** _____  · **Period:** _____  · **Prepared:** 2026-__-__
- **Host split (if applicable):** ____% to advisor `[verify-at-use]`

## Booked-vs-paid ledger
| Booking ID | Supplier | Supplier type | Commissionable value | Rate `[verify-at-use]` | Commission earned | Travel date | Statement rec'd? | Paid | Gap |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |

## Recovery worklist (gaps)
| Booking ID | Supplier | Gap $ | Cause (unbilled / short / past due) | Chase step (statement / claim / escalate) | Owner | Due |
|---|---|---|---|---|---|---|
| | | | | | | |

## Air settlement note
- **Rail:** _BSP / ARC_ `[verify-at-use]` · **Air commission expectation:** _often minimal — margin via fee_

## Preferred-supplier / consortia
| Program | Base uplift | Override / bonus status | Amenities attached |
|---|---|---|---|
| | | | |

## Metrics
- **Commission capture rate:** paid / earned = ____%  (target ~100%)
- **Days-to-collect (median):** _____
- **Preferred-supplier share:** ____%
- **Override / bonus earned this period:** _____

## Actions
- **Biggest leak:** _____ → **Owner + fix (process, not one booking):** _____ → **Review date:** _____

---
_Plus the ravenclaude-core Structured Output block. All rates, splits, and settlement terms verify-at-use against the supplier agreement/statement._
