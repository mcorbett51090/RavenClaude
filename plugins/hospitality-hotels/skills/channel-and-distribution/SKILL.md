---
description: "Analyze hotel channel mix and distribution economics: calculate net ADR after OTA commission and channel fees, diagnose an OTA-heavy mix, design a shift-to-direct plan, audit rate parity, and model total distribution cost (TDC) as a percentage of room revenue."
---

# Channel and Distribution

**Purpose:** optimize the hotel's distribution mix to maximize net ADR — ensuring that after every
channel takes its cut, the hotel captures the highest achievable revenue per booking.

## The operating loop

1. **Inventory the channels.** List every active channel with its commission or fee structure:
   - OTA (Booking.com, Expedia): commission % on gross booking value (typically 15–25%
     [verify-at-use])
   - GDS (Sabre, Amadeus, Travelport): transaction fee per segment ($4–$8 [verify-at-use])
     plus potential agency commission (8–10% for consortia [verify-at-use])
   - Booking engine / direct: platform fee (% or per-transaction), payment processing (1–3%),
     metasearch bidding cost (if applicable)
   - Wholesale / tour operator: contracted net rate + mark-up, effective commission implied
   - Voice / call center: labor cost per reservation allocation

2. **Calculate net ADR per channel.** For each channel:
   > Net ADR = Gross ADR × (1 − commission rate) − per-transaction fees

   Use `scripts/hotel_calc.py` (net-adr mode) for the arithmetic. Record the gap: the
   difference between the best-net-ADR channel and the worst is the distribution-efficiency
   opportunity.

3. **Calculate total distribution cost (TDC).** TDC = sum of all channel costs ÷ total room
   revenue. Benchmark: a TDC of 15–20% of room revenue is a watch zone; >20% is a structural
   problem [verify-at-use]. Segment TDC by channel to find the cost driver.

4. **Traverse the direct-vs-OTA decision tree.** See
   [`../../knowledge/hospitality-hotels-decision-trees.md`](../../knowledge/hospitality-hotels-decision-trees.md).
   The tree requires: current OTA share, direct-channel CAC, booking window by channel, and
   rate-parity status. Land on a recommendation (invest in direct / optimize OTA mix / accept
   current blend) with the net-ADR basis stated.

5. **Audit rate parity.** Check that the best publicly-available rate on each OTA equals (or
   exceeds) the best rate on the hotel's direct booking engine. Flag:
   - Opaque-channel leakage (Hotwire, Priceline net rate below BAR)
   - Package-rate exposure (bundled rates that imply a per-room rate below BAR)
   - Corporate/negotiated-rate public exposure (GDS rate visible to the public)
   - Metasearch bidding gap (hotel not bidding, OTA wins click at higher effective commission)

6. **Design the channel-shift plan (if needed).** A shift from OTA to direct requires:
   - Booking-engine investment (UX, mobile, value-proposition over OTA)
   - Metasearch presence and bidding strategy (Google Hotel Ads, Trivago, Kayak)
   - Member/loyalty direct-only rate (within parity rules: offer without publicizing rate
     below BAR on OTA)
   - Booking-window analysis: OTA dominates short window; direct dominates advance planners

7. **Output the recommendation.** Use the structure in step output below.

## Anti-patterns

- Channel recommendation without a net-ADR calculation.
- "Direct is always better" without subtracting direct CAC (booking engine cost + metasearch bid).
- Parity remediation of the symptom (a rate) without diagnosing root cause (why it leaked).
- Dropping a GDS channel without checking business-travel / consortia contribution.

## Output

A channel-economics table (gross ADR, commission, net ADR, TDC per channel), a channel-mix
assessment (OTA share vs. direct share vs. GDS share), a parity audit status, and a
recommendation with net-ADR basis. Reference
[`../../templates/channel-mix-model.md`](../../templates/channel-mix-model.md) for the artifact
structure.
