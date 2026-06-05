# Surcharge Stack Literacy — Name Every Charge Correctly

**Status:** Absolute rule
**Domain:** Freight-forwarding sales
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

Using the wrong surcharge name in a quote or email is a credibility signal to a sophisticated shipper. Saying "fuel surcharge" when the correct term is "BAF" (Bunker Adjustment Factor), or conflating "demurrage" (charges for holding a container on the terminal) with "detention" (charges for keeping a container at the customer's facility), tells a supply chain professional that they are dealing with someone who doesn't fully know their business. Correct terminology also prevents disputes: a quote that uses vague terms creates room for argument at invoice time.

## How to apply

Use the canonical term for each charge, every time:

| Charge | Correct term | Common wrong term | Notes |
|--------|-------------|-------------------|-------|
| Fuel recovery on ocean shipments | BAF — Bunker Adjustment Factor | "Fuel surcharge" | Carrier-specific; changes monthly or per-GRI |
| Currency adjustment | CAF — Currency Adjustment Factor | "Exchange surcharge" | Applied on certain trade lanes |
| Terminal handling at origin | THC — Terminal Handling Charge (origin) | "Port charges" | Carrier-assessed; some lanes all-in |
| Terminal handling at destination | THC — Terminal Handling Charge (dest.) | "Destination charges" | Separate from drayage/delivery |
| Low-sulphur fuel surcharge | LSS — Low Sulphur Surcharge | "Clean fuel charge" | IMO 2020-era charge |
| Fees for using a port security facility | ISPS — International Ship and Port Facility Security | "Security surcharge" | Not universal; confirm by lane |
| US customs filing fee | AMS — Automated Manifest System | "Filing fee" | Required for all US imports |
| EU customs entry notification | ENS — Entry Summary Declaration | "EU filing" | Required for EU imports |
| General rate increase | GRI | "Rate increase" | Scheduled by carriers; named, not vague |
| Container held on terminal past free days | Demurrage | "Port storage" | Free days defined in B/L |
| Container held at shipper/consignee past free days | Detention | "Container rental" | Separate from demurrage |
| Volume-based rate discount | W/M — Weight or Measure | "Freight rate" | LCL billing unit: 1 W/M = 1 CBM or 1,000 kg (whichever is greater) |

**Do:**
- Use the acronym and the spelled-out term on first use in any document: "BAF (Bunker Adjustment Factor)."
- Confirm whether a surcharge applies on a specific lane before including it — not all surcharges apply to all routes.
- When a carrier uses a non-standard name for a standard charge, note both: "Carrier surcharge X (equivalent to LSS)."

**Don't:**
- Use "misc. charges" or "port charges" as a line item — every charge must be identified by its correct name.
- Confuse demurrage and detention in a customer conversation — the customer may be suffering one and not the other, and the fix is different.
- State a surcharge amount without confirming it against the carrier's current tariff; example amounts are clearly labeled as examples.

## Edge cases / when the rule does NOT apply

Road/domestic trucking surcharges (fuel surcharge is the accepted term in road freight, not BAF) follow different conventions. The rule applies to international ocean and air freight charges; domestic road freight conventions differ.

## See also

- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — builds the all-in quote with the correct surcharge stack.
- [`./quote-all-in-never-base-only.md`](./quote-all-in-never-base-only.md) — the governing rule that requires naming all charges in every quote.

## Provenance

Codifies CLAUDE.md §3 #6 (name the charge correctly). Surcharge terminology follows industry-standard definitions from Incoterms 2020, IATA, FIATA, and major carrier tariffs. Demurrage/detention distinction is a recognized source of shipper confusion in BIMCO and DCSA industry documentation [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
