# Quote All-In, Never Base-Only

**Status:** Absolute rule
**Domain:** Freight-forwarding sales
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

A base ocean or air rate without the surcharge stack is not a quote — it is the setup for a dispute. When a shipper receives an "ocean freight: $850/TEU" number and later sees a commercial invoice with $1,340 in surcharges they were not told about, the relationship is damaged and the trust that differentiates a professional forwarder from a commodity rate-shopper is gone. The all-in quote, with every surcharge named and explained, is the professional standard. It is also the rule that protects the seller: an all-in quote prevents the "that wasn't in the quote" argument at invoice time.

## How to apply

Every customer-facing quote must include the following elements:

```
All-In Quote Structure
────────────────────────
Route:  [Origin port / city] → [Destination port / city]
Mode:   [FCL 20' / FCL 40' / FCL 40'HC / LCL / Air / Express]
Incoterm assumed:  ________________
Validity:  Valid until [date] — subject to GRI/PSS/BAF after validity

Charge                        | Basis            | Amount
──────────────────────────────|──────────────────|────────
Ocean / air base freight      | per container / W/M / kg | $
BAF / Fuel surcharge          | per container / kg | $
CAF (if applicable)           | per container     | $
THC — origin                  | per container     | $
THC — destination             | per container     | $
LSS / Low sulphur surcharge   | per container     | $
ISPS (if applicable)          | per container     | $
AMS / ENS filing (if req.)    | per B/L           | $
Destination delivery / drayage| per container     | $
Other: _______________        | ________________  | $
──────────────────────────────|──────────────────|────────
TOTAL ALL-IN                  |                  | $

Chargeable basis:  [ ] Actual weight ___kg  [ ] Volumetric ___kg  [ ] W/M ___  [ ] Per container
Margin:  [Buy: $___  Sell: $___  Margin: $___ (__% )]  (internal field — not on customer-facing copy)
```

**Do:**
- Name every surcharge; never bundle "misc. surcharges" as a line item.
- State the validity date on every quote — rates move; an undated quote is an open-ended commitment.
- Show the Incoterm the quote assumes so the customer knows which charges are their scope.

**Don't:**
- Send a base-rate-only quote and add surcharges at invoicing — this is the most common freight billing dispute pattern.
- Quote "subject to surcharges TBD" without listing the surcharge stack; TBD is not a quote.
- State an example surcharge amount as if it were a live figure — mark example rates as `[example — confirm against live rates/tariff]`.

## Edge cases / when the rule does NOT apply

Internal rate-check queries between colleagues (e.g., "quick check — what's the current BAF on Asia-USEC?") are not customer-facing quotes and do not require the full format. Any number shared with a customer, directly or via a TMS/portal output, is a quote and requires the full format.

## See also

- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — owns the all-in quote build and surcharge stack.
- [`./surcharge-stack-literacy-name-every-charge-correctly.md`](./surcharge-stack-literacy-name-every-charge-correctly.md) — the companion rule on correct surcharge terminology.

## Provenance

Codifies CLAUDE.md §3 #1 (quote all-in, never base-only) and §3 #6 (name the charge correctly). Industry-standard: all-in quoting is the professional norm in freight forwarding and is explicitly required under many shipper RFQ frameworks and MSC/Maersk tariff disclosure practices [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
