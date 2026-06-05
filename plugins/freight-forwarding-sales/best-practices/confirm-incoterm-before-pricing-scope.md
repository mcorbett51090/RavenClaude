# Confirm the Incoterm Before Pricing Scope

**Status:** Absolute rule
**Domain:** Freight-forwarding sales
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

The Incoterm determines who pays for what, who carries risk at each transfer point, and whether the freight forwarder's scope includes origin services, main carriage, destination services, or all three. A quote built on the assumption of CIF terms (seller pays main carriage and insurance, risk transfers at origin) has a completely different scope from one built on DAP terms (seller delivers to the destination, bears risk throughout transit). Quoting the wrong scope is the most common structural quoting error in freight forwarding — and the most costly, because the error is often discovered at invoice time.

## How to apply

Confirm the Incoterm as the first step in any quote build:

```
Incoterm Confirmation — Pre-Quote Checklist
─────────────────────────────────────────────
Transaction party:  [ ] Seller (exporter)  [ ] Buyer (importer)
Trade route:  [Origin country] → [Destination country]
Mode:  [ ] Ocean  [ ] Air  [ ] Road  [ ] Multimodal

Incoterm stated by customer:  ________________
Incoterm confirmed as applicable (not assumed):  [ ] Yes  [ ] Need to clarify

If containerized ocean: Is the customer using FOB or FCA correctly?
  [ ] FOB stated — flag: FOB is a sea-only term; for containerized cargo, FCA is the correct
      term under Incoterms 2020; clarify with the customer before building the scope.
  [ ] FCA confirmed — seller's scope ends at hand-over to the carrier at named place.

Scope map based on confirmed Incoterm:
  Origin pick-up / trucking:  [ ] Seller pays  [ ] Buyer pays  [ ] N/A
  Export clearance:            [ ] Seller pays  [ ] Buyer pays
  Origin THC:                  [ ] Seller pays  [ ] Buyer pays  [ ] Included in main freight
  Main carriage:               [ ] Seller pays  [ ] Buyer pays
  Insurance:                   [ ] Seller pays (req for CIP)  [ ] Optional / buyer arranges
  Destination THC:             [ ] Seller pays  [ ] Buyer pays
  Import clearance + duty/VAT: [ ] Seller pays (DDP)  [ ] Buyer pays
  Destination delivery:        [ ] Seller pays  [ ] Buyer pays  [ ] Not included

Build quote for:  [ ] Origin only  [ ] Main carriage only  [ ] Door-to-door  [ ] Other: ___
```

**Do:**
- Use the decision tree in `knowledge/freight-sales-decision-trees.md` (Incoterms selection tree) if the customer asks which term to use — don't guess.
- Flag FOB usage on containerized cargo to the customer; many shippers use FOB as a generic "I handle export, you handle import" shorthand, but the legal scope under Incoterms 2020 is specific and may not match their intent.
- Document the confirmed Incoterm on the face of the quote — "Quote assumes [Incoterm] [named place]."

**Don't:**
- Assume the Incoterm from the customer's description of "who does what" — confirm the term explicitly.
- Quote a DDP scope without confirming that the forwarder can actually serve as or appoint an importer of record in the destination country — DDP without IOR capability is an unfulfillable quote.
- Use CIF for containerized cargo as if it were standard; CIF assumes goods crossing the ship's rail, which creates a risk gap at the container yard.

## Edge cases / when the rule does NOT apply

Domestic road-only shipments do not use Incoterms; the scope is defined by the trucking contract terms. Incoterms apply to international commercial transactions; for purely domestic moves, the freight scope is defined by the road-freight service agreement.

## See also

- [`../agents/trade-lane-compliance-advisor.md`](../agents/trade-lane-compliance-advisor.md) — owns Incoterms interpretation and the FOB/FCA clarification workflow.
- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — uses the confirmed Incoterm scope to build the all-in quote.

## Provenance

Codifies CLAUDE.md §3 #7 (confirm the Incoterm before pricing) and the anti-pattern "quoting the wrong scope for the Incoterm." Based on ICC Incoterms® 2020 rules; FCA vs FOB for containerized cargo is explicitly addressed in the Incoterms 2020 guidance [unverified — cite ICC Incoterms 2020 text for binding questions].

---

_Last reviewed: 2026-06-05 by `claude`_
