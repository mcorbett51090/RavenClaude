# Repair Order Workflow — <RO # / vehicle / date>

> Output template for a single repair order from write-up to closeout and follow-up. Drives the estimate-and-DVI and RO-lifecycle skills. Every labor time / rate / part price carries a source + date or `[verify-at-use]`; no customer PII — reason in job types, not customer records.

## Header
- **RO # / vehicle (year-make-model):** _____
- **Date opened:** 2026-__-__  · **Advisor / tech:** _____
- **Concern (customer's words):** _____

## 1. Write-up & authorization
| Step | Captured? | Note |
|---|---|---|
| Complaint verified (conditions, when it occurs) | ☐ | |
| Diagnostic authorized (fee disclosed) | ☐ | _[verify-at-use] local rule_ |
| Repair authorization obtained before work | ☐ | |

## 2. Inspection (DVI) → estimate
| Recommended line | DVI evidence | Labor-guide hrs × rate | Parts (cost × matrix) | Urgency | Sell now / later |
|---|---|---|---|---|---|
| | photo/measure | _[verify-at-use]_ | _[verify-at-use]_ | safety/wear | |
| | | | | | |

- **Presented total:** _____  · **Approved total:** _____  · **Close rate this RO:** _____

## 3. Dispatch & parts staging
| Item | Status | Owner |
|---|---|---|
| Dispatched to skill-matched tech | ☐ | dispatch |
| Parts on-hand / ETA confirmed before start | ☐ | parts |
| Flat-rate flag time vs actual | ____ / ____ | tech |

## 4. WIP / RO aging (if it stalls)
| Stalled because | Owner | Action | Age (days) |
|---|---|---|---|
| approval / parts / tech / not-invoiced | | | |

## 5. Quality / comeback check
- **Multi-point verification before closeout:** ☐
- **First-time fix?** ☐  · **If returned — root cause:** _misdiagnosis / workmanship / part / incomplete / no-fault_

## 6. Declined work → follow-up
| Declined line | Urgency | Est. part life | Recontact date |
|---|---|---|---|
| | | | |

## Headline + handoffs
- **Headline:** _the one thing that determined this RO's margin or close_
- **Handoffs:** _shop-lead (rate/matrix) · service-advisor-estimator (re-quote/decline) · technician-workflow-manager (dispatch/comeback)_

---
_Plus the ravenclaude-core Structured Output block. All labor-time / rate / part-price / authorization-rule cells: verify-at-use before customer-facing use._
