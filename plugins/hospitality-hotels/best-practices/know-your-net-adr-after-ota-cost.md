# Know your net ADR after OTA cost

**Status:** Pattern
**Domain:** Hotel channel and distribution management
**Applies to:** `hospitality-hotels`

---

## Why this exists

Gross ADR — the headline rate a guest pays — is a fiction from the hotel's perspective if it
doesn't subtract the channel cost. An OTA booking at $200 ADR with an 18% commission nets $164
to the hotel. A direct booking at $164 nets the same amount (assuming zero other distribution
cost) and is economically equivalent. A hotel that celebrates "$200 average rate" without knowing
its distribution cost is managing to an illusion.

The consequence of ignoring net ADR: hotels over-invest in high-commission channels, set rates
that look competitive but are actually below their cost-recovery floor after distribution, and
cannot make rational channel-mix decisions because they lack the denominator.

## How to apply

- **Do:** Calculate net ADR for every channel before any channel or pricing decision:
  `Net ADR = Gross ADR × (1 − commission rate) − per-transaction fees`
- **Do:** Build (and maintain) a channel-cost table: each channel with its commission or fee,
  updated at least annually when contracts renew.
- **Do:** Report total distribution cost (TDC) as a percentage of room revenue, not as an
  absolute dollar line. TDC% normalizes for occupancy and rate changes.
- **Do:** Use the net-ADR comparison to rank channels by true economic contribution, not by
  gross booking volume.

**Don't:**

- Recommend adding an OTA channel without first calculating net ADR vs. the direct-channel
  net ADR.
- Set a pricing floor (minimum BAR) without factoring in the channel cost — a BAR that covers
  the cost floor on a direct booking may be below the cost floor when booked through a high-
  commission OTA.
- Compare channel volumes (bookings or room-nights) without weighting by net ADR.

## Edge cases / when the rule does NOT apply

- **OTA incremental demand:** if an OTA generates demand that would not exist on the direct
  channel (new market segments, international reach), the full commission cost is analogous to
  a marketing spend, and the net-ADR comparison to direct is not the right frame — incremental
  net ADR (net of OTA commission, vs. zero revenue without the OTA) is the correct frame.
- **Contracted group / consortia rates:** GDS consortium bookings often carry a higher agency
  commission (8–10% on top of GDS fee) but deliver high-value corporate guests whose total
  lifetime value exceeds the commission cost. Factor in LTV, not just single-stay net ADR.

## See also

- [`./revpar-is-the-north-star-not-occupancy-alone.md`](./revpar-is-the-north-star-not-occupancy-alone.md)
- [`../knowledge/hospitality-hotels-decision-trees.md`](../knowledge/hospitality-hotels-decision-trees.md) — direct-vs-OTA tree
- [`../scripts/hotel_calc.py`](../scripts/hotel_calc.py) — net-adr mode calculates net ADR given gross ADR and commission rate

## Provenance

Standard hospitality distribution economics doctrine, codified in the HSMAI Distribution
Strategy Council guidance and Phocuswright / STR distribution-cost research. The total
distribution cost (TDC) benchmark (15–20% watch zone) is widely cited in industry literature
[verify-at-use].

---

_Last reviewed: 2026-06-08 by `claude`._
