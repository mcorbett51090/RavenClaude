# Channel Mix Model — [Property Name] | [Period: Month/Quarter YYYY]

> Fill in all bracketed fields. Delete rows that are not applicable.
> Prepared by: [Name / Agent] | Date: [YYYY-MM-DD] | Reviewed by: [Name]

---

## 1. Channel Inventory

| Channel              | Type            | Commission / Fee | Contract Notes               |
| -------------------- | --------------- | ---------------- | ----------------------------- |
| Booking.com          | OTA             | [X%] of gross booking | [Parity clause: Y/N]     |
| Expedia Group        | OTA             | [X%] of gross booking | [Parity clause: Y/N]     |
| GDS (Sabre/Amadeus/Travelport) | GDS  | $[X] per segment + [X%] agency commission | [Corp loaded: Y/N] |
| Direct — Booking Engine | Direct       | [Platform fee %] + [Payment processing %] | [Engine: ARI / SynXis / Sitelink — verify-at-use] |
| Metasearch (Google Hotel Ads) | Direct-assisted | [Bidding cost: CPC $X or CPA %X] | |
| Wholesale / Tour Operator | Wholesale | [Contracted net rate: $XXX] | [Allotment: X rooms/night] |
| Voice / Call Center  | Direct          | [Labor cost allocation: $X per reservation] | |

---

## 2. Net ADR by Channel

> Net ADR = Gross ADR × (1 − commission rate) − per-transaction fees
> Calculated using `scripts/hotel_calc.py` (net-adr mode) — [date of calculation].

| Channel              | Gross ADR | Commission / Fee | Net ADR | Net ADR Gap vs. Best |
| -------------------- | --------- | ---------------- | ------- | -------------------- |
| Booking.com          | $[XXX]    | $[XX.XX]         | $[XXX]  | −$[XX]               |
| Expedia              | $[XXX]    | $[XX.XX]         | $[XXX]  | −$[XX]               |
| GDS                  | $[XXX]    | $[XX.XX]         | $[XXX]  | −$[XX]               |
| Direct (booking engine) | $[XXX] | $[XX.XX]        | $[XXX]  | $0 (best)            |
| Wholesale            | $[XXX]    | $[XX.XX]         | $[XXX]  | −$[XX]               |

**Best net ADR channel:** [Direct / GDS / Other] at $[XXX]
**Worst net ADR channel:** [OTA / Wholesale] at $[XXX]
**Opportunity (shift worst → best):** $[X.XX] net ADR uplift per room-night shifted

---

## 3. Channel Mix (Volume)

| Channel              | Room-Nights | % of Total | Revenue Contribution | Revenue % |
| -------------------- | ----------- | ---------- | -------------------- | --------- |
| OTA (all)            | [X]         | [X%]       | $[XXX,XXX]           | [X%]      |
| Direct (engine + voice) | [X]      | [X%]       | $[XXX,XXX]           | [X%]      |
| GDS                  | [X]         | [X%]       | $[XXX,XXX]           | [X%]      |
| Wholesale            | [X]         | [X%]       | $[XXX,XXX]           | [X%]      |
| **Total**            | **[X]**     | **100%**   | **$[XXX,XXX]**       | **100%**  |

**Direct share:** [X%] — Benchmark target: ≥35% for independents [verify-at-use]
**OTA share:** [X%] — Watch zone: >50% indicates structural OTA dependency

---

## 4. Total Distribution Cost (TDC)

| Cost Element                   | Amount     | % of Room Revenue |
| ------------------------------ | ---------- | ----------------- |
| OTA commissions (all OTAs)     | $[XX,XXX]  | [X%]              |
| GDS fees + agency commissions  | $[XX,XXX]  | [X%]              |
| Booking engine fees            | $[XX,XXX]  | [X%]              |
| Metasearch bidding             | $[XX,XXX]  | [X%]              |
| Payment processing             | $[XX,XXX]  | [X%]              |
| **Total Distribution Cost**    | **$[XX,XXX]** | **[X%]**       |

**TDC benchmark:** 15–20% = watch zone; >20% = structural problem [verify-at-use]
**Current TDC vs. benchmark:** [above / within / below]

---

## 5. Rate Parity Audit

| Channel              | Current Rate | Direct BAR | Parity Status | Root Cause (if violation) |
| -------------------- | ------------ | ---------- | ------------- | ------------------------- |
| Booking.com          | $[XXX]       | $[XXX]     | [OK / VIOLATION] | [Opaque / Package / Corp rate exposure] |
| Expedia              | $[XXX]       | $[XXX]     | [OK / VIOLATION] | |
| Metasearch (Google)  | $[XXX]       | $[XXX]     | [OK / VIOLATION] | |

**Open violations:** [N] — Remediation required before rate changes go live.

---

## 6. Decision-Tree Outcome (direct-vs-OTA)

_Traverse the direct-vs-OTA tree in `knowledge/hospitality-hotels-decision-trees.md`._

| Node                              | Answer                |
| --------------------------------- | --------------------- |
| Current OTA share                 | [X%]                  |
| Direct CAC vs. OTA commission     | [Direct lower / Higher / Similar] |
| Booking-window: OTA vs. direct    | [OTA shorter / Direct longer / Similar] |
| Parity violations present?        | [Yes / No]            |
| **Leaf recommendation**           | **[Invest in direct / Optimize mix / Accept current blend]** |

---

## 7. Recommended Actions

| Action                          | Priority | Owner    | Expected Net-ADR Uplift | Timeline |
| ------------------------------- | -------- | -------- | ----------------------- | -------- |
| [e.g., Add metasearch bidding]  | High     | E-commerce mgr | $[X.XX]/booking  | [30 days] |
| [e.g., Negotiate OTA commission] | Medium  | Revenue mgr | $[X.XX]/booking   | [90 days] |
| [e.g., Fix parity violation]    | High     | Reservations mgr | n/a (risk removal) | [Immediate] |

---

## 8. Handoffs

- **`revenue-manager`** — confirm BAR strategy for any channel-shift period; update rate
  loading across all channels after mix change.
- **`hotel-ops-lead`** — if TDC reduction is material (>1% of room revenue), assess GOP impact.
- **`guest-experience-lead`** — if direct-booking investment changes pre-arrival touchpoints,
  align the guest-journey design.
- **`marketing-operations-demand-gen`** — metasearch bidding, loyalty-value proposition, and
  direct-channel customer acquisition are a seam (this plugin owns economics; that plugin owns
  campaign execution).
