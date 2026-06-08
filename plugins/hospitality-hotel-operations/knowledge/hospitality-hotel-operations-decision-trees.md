# Hospitality / Hotel Operations — Decision Trees

_Decision trees + a dated system/channel map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-08._

Traverse before making a rate move, deciding to overbook, shifting channel mix, or triaging a review-driven defect.

## Decision Tree: Discount for occupancy or hold rate?

RevPAR is the target — never buy occupancy with a giveaway that lowers revenue per available room.

```mermaid
graph TD
  A[Soft pickup vs. forecast for a date] --> B{Is the date still far enough out to recover demand?}
  B -- Yes --> C[Hold rate - protect ADR; revisit at the next pickup checkpoint]
  B -- No, close-in and soft --> D{Does the lower rate raise RevPAR after the give-back?}
  D -- No --> E[Hold - a discount that fills rooms but lowers RevPAR is a loss]
  D -- Yes --> F{Is the incremental occupancy profitable read against GOPPAR?}
  F -- No --> G[Hold - occupancy bought below variable+distribution cost erodes profit]
  F -- Yes --> H[Discount via a fenced rate - LOS / advance-purchase / segment, not an open BAR cut]
```

_A full hotel at a giveaway rate and an empty hotel at rack are both failures. Optimize RevPAR, check it against GOPPAR._

## Decision Tree: Should we overbook this date?

Overbooking is a yield tool with a guarantee attached — size it to the forecasted no-show rate, never past the walk you can absorb.

```mermaid
graph TD
  A[High-demand, likely sell-out date] --> B{Do you have a reliable no-show + late-cancel rate for this date type?}
  B -- No --> C[Do not overbook - without the rate it's a guess that risks a walk]
  B -- Yes --> D{Is the yield upside greater than the expected walk cost + brand damage?}
  D -- No --> E[Don't overbook - the rare walk isn't worth the marginal room]
  D -- Yes --> F{Is there an operations-owned walk-protocol the property can execute gracefully?}
  F -- No --> G[Build the walk-protocol first - hotel-operations-lead; do not overbook until it exists]
  F -- Yes --> H[Overbook to the forecasted no-show rate - not beyond the absorbable walk]
```

_A walk is a broken promise. The overbook size is the revenue-manager's; the walk-protocol is operations'._

## Decision Tree: Shift channel mix toward direct?

Drive direct to cut distribution cost — but never strand the demand the OTAs uniquely reach.

```mermaid
graph TD
  A[OTA commission eroding margin] --> B{Compare channels on NET ADR after commission - is direct's contribution actually higher?}
  B -- No --> C[The OTA booking nets more here - keep the mix; the OTA is acquisition, not a leak]
  B -- Yes --> D{Can direct capture the demand the OTA reaches, or is the OTA the only path to it?}
  D -- OTA is the only path --> E[Keep the OTA for that demand - shifting strands bookings you can't otherwise win]
  D -- Direct can capture it --> F{Is there a direct-booking value prop guests prefer - rate parity, loyalty, perk?}
  F -- No --> G[Build the direct value prop first - a parity-only direct channel doesn't move share]
  F -- Yes --> H[Shift mix - rate-fence the OTA, push direct value; protect the residual OTA acquisition]
```

_The OTA is a paid acquisition channel with a known cost. The question is the right mix, never zero OTA._

## Decision Tree: Triage a review-driven defect

The review is a defect report — close the loop to an operational fix, don't archive it.

```mermaid
graph TD
  A[A recurring review/verbatim theme] --> B{Does it map to an operational root cause - process, SOP, maintenance, staffing?}
  B -- No, isolated one-off --> C[Respond + service-recover the guest; log it, don't change the SOP yet]
  B -- Yes --> D{Frequency x score/repeat-rate impact - is it high enough to prioritize?}
  D -- No --> E[Backlog it - fix when a higher-impact theme is cleared]
  D -- Yes --> F[Map to the owner: route the SOP/maintenance/staffing fix to hotel-operations-lead]
  F --> G{Was the fix applied and re-measured in the next review/survey cycle?}
  G -- No --> H[Loop is open - it's comment-to-archive until re-measured]
  G -- Yes --> I[Loop closed - confirm the score/repeat-rate recovered; else re-diagnose]
```

_Measuring satisfaction is worthless without the action it drives. Rank by impact, not volume alone._

## Decision Tree: Cut labor for this shift?

Labor is the biggest controllable cost and the biggest service lever — schedule to the curve, never below the service floor.

```mermaid
graph TD
  A[Occupancy forecast lower than scheduled coverage] --> B{Does the forecast for this date type have a reliable arrival + room-turn load?}
  B -- No --> C[Don't cut on a guess - hold coverage until the pickup view firms up]
  B -- Yes --> D{Would the cut drop coverage below the service floor - a clean room by check-in, a staffed desk at the arrival peak?}
  D -- Yes --> E[Hold the floor - a labor win that drops the review score moved cost onto the guest, not off the P&L]
  D -- No --> F{Is the cut matched to WHEN the load is - the arrival peak and the turn window, not a flat headcount?}
  F -- No --> G[Re-shape the schedule to the curve first - cut the trough, protect the peak]
  F -- Yes --> H[Cut to the curve - flex the trough hours, keep the peak and the floor intact]
```

_Schedule to the occupancy forecast; the service floor is the line a cost number never crosses._

---

## System & channel map (2026, `[verify-at-build]`)

| Layer | Options | Notes |
|---|---|---|
| PMS (property management system) | Oracle OPERA, Cloudbeds, Mews, apaleo, StayNTouch, Little Hotelier | System of record for room status, rate, folio, guest profile `[verify-at-build]` |
| RMS (revenue management system) | IDeaS, Duetto, Atomize, Pace, BEONx | Automates demand forecasting + rate recommendations; verify model + PMS integration `[verify-at-build]` |
| Channel manager | SiteMinder, Cloudbeds, RateGain, Derbysoft | Distributes rate/availability to OTAs + GDS; watch parity + sync latency `[verify-at-build]` |
| OTAs / distribution | Booking.com, Expedia Group, Airbnb, Google Hotels, GDS | Commission typically ~15-25% — compare on net ADR, treat as acquisition `[verify-at-build]` |
| Reputation / reviews | TripAdvisor, Google, Booking.com reviews, Revinate, TrustYou, Medallia | Theme/sentiment coding feeds the comment-to-action loop `[verify-at-build]` |
| Guest satisfaction / survey | Medallia, Qualtrics, Revinate, GuestRevu | NPS / GSS / CSAT + verbatim capture; route significance tests to applied-statistics `[verify-at-build]` |
| Loyalty / CRM | Brand programs (Marriott Bonvoy, Hilton Honors, etc.), Revinate, Cendyn, Salesforce | Measure on repeat rate / direct share / CLV, not member count `[verify-at-build]` |

_KPI reference: RevPAR = ADR × Occupancy = Room Revenue ÷ Available Rooms; ADR = Room Revenue ÷ Rooms Sold; Occupancy = Rooms Sold ÷ Available Rooms; GOPPAR = Gross Operating Profit ÷ Available Rooms (the profit check on a RevPAR strategy). Net ADR = headline rate − commission/channel cost − discount/loyalty give-back. Re-verify any vendor/commission specific before quoting it to a consumer._
