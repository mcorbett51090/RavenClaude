# Rate Plan — [Property Name] | [Date Range]

> Fill in all bracketed fields. Delete rows that are not applicable.
> Prepared by: [Name / Agent] | Date: [YYYY-MM-DD] | Reviewed by: [Name]

---

## 1. Demand Context

| Field                          | Value                       |
| ------------------------------ | --------------------------- |
| Date range                     | [e.g., July 4–7, 2026]      |
| Period type                    | [Compression / Shoulder / Soft] |
| On-the-books occupancy (OTB)   | [X rooms / Y%]              |
| STLY occupancy (same time last year) | [Z%]               |
| OTB pace vs. forecast          | [Ahead / On-pace / Behind]  |
| Days to arrival                | [N days]                    |
| Local events / demand catalysts| [Event name, dates]         |

---

## 2. Competitive Set Position

| Channel / Platform     | Comp-Set Average Rate | Our Current BAR | Gap (+/-) |
| ---------------------- | --------------------- | --------------- | --------- |
| [OTA / Rate Shopping]  | $[XXX]                | $[XXX]          | $[±XX]    |
| [Direct / Booking Engine] | $[XXX]            | $[XXX]          | $[±XX]    |

Comp-set definition: [List comp-set properties — hold constant; review annually]

---

## 3. Decision-Tree Outcome

_Traverse the raise-or-hold-rate tree in `knowledge/hospitality-hotels-decision-trees.md` and
record the branch path taken._

| Node                          | Answer                    |
| ----------------------------- | ------------------------- |
| Demand pace vs. forecast?     | [Ahead / On-pace / Behind] |
| Comp-set rate position?       | [Premium / Parity / Discount] |
| Days-to-arrival window?       | [>30 / 14–30 / 7–14 / <7] |
| Event / compression indicator?| [Yes / No]                |
| **Leaf decision**             | **[RAISE / HOLD / LOWER]** |

---

## 4. Rate Recommendation

| Room Type        | Current BAR | Recommended BAR | Change  | Effective Date |
| ---------------- | ----------- | --------------- | ------- | -------------- |
| Standard / King  | $[XXX]      | $[XXX]          | +$[XX]  | [Date]         |
| Double / Twin    | $[XXX]      | $[XXX]          | +$[XX]  | [Date]         |
| Suite            | $[XXX]      | $[XXX]          | +$[XX]  | [Date]         |

**Basis:** [State the demand evidence — e.g., "OTB pace 18% ahead of STLY, comp-set average
$15 below our current BAR — rate headroom confirmed"]

---

## 5. Length-of-Stay Controls

| Date(s)    | Control Type | Setting | Displacement Math                               |
| ---------- | ------------ | ------- | ----------------------------------------------- |
| [Date]     | MinLOS       | [N nights] | [Shoulder RevPAR × N nights vs. single-night fill — show math] |
| [Date]     | CTA (Closed to Arrival) | [Yes/No] | [Reason]                    |

---

## 6. Overbooking (if applicable)

| Input                          | Value       | Source                  |
| ------------------------------ | ----------- | ----------------------- |
| 12-month no-show rate          | [X%]        | [PMS history, date]     |
| Cancellation rate (same-day)   | [X%]        | [PMS history, date]     |
| Expected same-day rebookings   | [X rooms]   | [Historical]            |
| Walk cost (per walk)           | $[XXX]      | [Estimate: relocation + comp + loyalty] |
| Recommended overbook level     | [N rooms]   |                         |
| Expected RevPAR uplift         | $[X.XX]     | [From hotel_calc.py]    |
| Expected walk risk             | [N rooms / period] |                   |

---

## 7. RevPAR Impact Calculation

| Scenario           | ADR    | Occupancy % | RevPAR  |
| ------------------ | ------ | ----------- | ------- |
| Current (baseline) | $[XXX] | [X%]        | $[XXX]  |
| Recommended        | $[XXX] | [X%]        | $[XXX]  |
| **Delta**          |        |             | **+$[XX]** |

_Calculated using `scripts/hotel_calc.py` (revpar mode) — [date of calculation]._

---

## 8. Channel Implications

> Tag: any rate change triggers a parity check. Confirm the new BAR is loaded consistently
> across all channels before the rate goes live.

- [ ] BAR updated in PMS: [Opera / Mews / Cloudbeds — verify-at-use]
- [ ] BAR pushed to channel manager
- [ ] Parity confirmed on OTA extranets (Booking.com, Expedia)
- [ ] Comp-set monitoring alert set

---

## 9. Handoffs

- **`reservations-and-channel-analyst`** — confirm net ADR at the new BAR for each channel;
  check parity implications.
- **`hotel-ops-lead`** — if the RevPAR delta is >$5/available room, assess GOP impact.
- **`guest-experience-lead`** — if the rate move is aggressive on a compression night,
  confirm walk-recovery playbook is active.
