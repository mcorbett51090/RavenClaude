# Itinerary & Quote — <trip name / cohort>

> Output template for a designed, documented, transparently-priced itinerary. **No traveler PII** — use placeholders (Traveler A, Party of N), never names, passport, or payment data. Every supplier fare rule and penalty is `[verify-at-use]` at booking.

## Trip context
- **Trip / reference:** _____  · **Prepared:** 2026-__-__  · **Advisor:** _____
- **Party:** _N travelers (placeholders only)_  · **Dates:** _____  · **Structure:** _FIT / group (see below)_
- **Budget band + must-haves:** _____

## Itinerary structure (before pricing)
| Seq | Date(s) | Element (supplier / type) | Inclusions | Confirmation # | Status |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

## Quote (itemized — transparent)
| Line | Basis | Amount | Commissionable? | Note |
|---|---|---|---|---|
| Supplier cost (net / commissionable) | | | | |
| Service / planning fee | _charged when commission won't cover the work_ | | n/a | |
| Taxes & fees | | | | |
| Travel insurance (offered) | | | | |
| **Total to traveler** | | | | |

## Cancellation & payment schedule (per supplier — verify-at-use)
| Supplier | Deposit | Final payment date | Cancellation penalty schedule | Verified |
|---|---|---|---|---|
| | | | | `[verify-at-use]` |
| | | | | `[verify-at-use]` |

## If group: block terms
- **Block size:** _____ · **Cutoff date:** _____ · **Attrition %:** _____ · **TC/comp benefit:** _____ `[verify-at-use]`

## Change log
| Date | Change | Authorized by | New confirmation / penalty impact |
|---|---|---|---|
| | | | |

## Commission handoff
- **Expected commission by supplier:** _log to the tracker_ → [`supplier-commission-tracker.md`](supplier-commission-tracker.md)

---
_Plus the ravenclaude-core Structured Output block. All fare rules, penalties, and terms verify-at-use against the live supplier at booking._
