# Every quote carries an explicit validity date — never "until further notice"

**Status:** Absolute rule
**Domain:** Freight quoting
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

An ocean or air rate without a validity date is a liability. Spot market rates move weekly; BAF and GRI can move monthly; a quote accepted three months after issuance at a rate that is now below buy cost creates a margin-negative shipment — or a customer dispute when the forwarder tries to re-quote. "Until further notice" is a contractual ambiguity that benefits neither party. Explicit validity is a professional discipline and a commercial protection.

## How to apply

Every quote, whether a spot quote to a transactional account or a rate proposal inside an RFQ response, carries an explicit validity date at the top of the document.

**Validity guidance by mode and rate type:**

| Mode / scenario | Typical validity range | Rationale |
|---|---|---|
| Ocean FCL spot quote | 5–7 days | GRI and space allocation moves weekly |
| Ocean LCL spot quote | 5–10 days | CFS rates more stable; space still moves |
| Air freight spot quote | 2–5 days | Fuel surcharges and capacity move fast |
| Road / domestic spot | 7–14 days | Fuel and driver costs more stable |
| RFQ / tender rate proposal | As stated in RFQ — typically 30–90 days | Match the customer's stated validity requirement |
| Contract / SLA rate | Stated contract period (e.g., 1 Jan – 31 Dec YYYY) | Fixed with agreed review mechanism |

**Volatility clause (for quotes at the longer end of validity):**
When quoting validity beyond 10 days on ocean or beyond 5 days on air, add a subject-to clause:

```
This quote is valid until [DATE], subject to:
- General Rate Increase (GRI) or Peak Season Surcharge (PSS) announcements by the operating carrier.
- Bunker Adjustment Factor (BAF) changes beyond ±[X]% of the quoted rate.
- Force-majeure events affecting routing or port access.
In the event of a material change, we will notify you immediately with a revised rate.
```

**Do:**
- Print the validity date in a prominent position — top of the quote sheet, not buried in the footer.
- Set a follow-up task in the CRM to chase the customer before expiry — an expired un-actioned quote is a sales opportunity lost.
- When a customer returns after validity has expired, re-quote rather than honour the stale rate; explain the market movement.

**Don't:**
- Quote "rates subject to change" without a date — that is not a validity, it is an escape clause that erodes trust.
- Extend validity verbally without confirming in writing and checking current buy rates first.
- Issue a rate and forget to log the validity in the CRM — if you cannot track it, you cannot manage it.

## Edge cases / when the rule does NOT apply

Long-term contract rates may reference a fixed period (e.g. annual contract) rather than a calendar date. These still carry an explicit period — the rule does not relax, the validity format changes. For internal cost estimates or "budget only / not for quoting" rates, the validity rule is advisory; mark them clearly as not a customer-facing quote.

## See also
- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — all-in quote construction
- [`../skills/freight-pricing-mechanics/SKILL.md`](../skills/freight-pricing-mechanics/SKILL.md) — rate volatility handling

## Provenance

Codifies `freight-rate-quoter`'s quoting discipline and house opinion §1 ("Quote all-in, never base-only"). Standard commercial practice in all forwarding and NVOCC rate quoting.

---

_Last reviewed: 2026-06-05 by `claude`_
