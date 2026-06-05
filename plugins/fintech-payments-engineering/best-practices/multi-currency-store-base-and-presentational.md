# Store amounts in the transaction currency; present in the display currency

**Status:** Absolute rule
**Domain:** Multi-currency / money representation
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

A payment system that stores all amounts converted to a single base currency
(e.g. always USD) at the time of the transaction loses the transaction currency
permanently. When the display currency, reporting currency, or revenue-
recognition currency differs from the stored currency, the system must re-derive
the exchange rate — which may no longer be available. Disputes, refunds, and
reconciliation all require the original transaction amount in the original
transaction currency. Conversion is a presentational and accounting concern,
not a storage concern.

## How to apply

**Storage:** always store `(amount_minor_units, currency_code)` as the canonical
pair. Never convert to a base currency at write time.

**Presentation:** apply the FX rate at read time for display, reporting, or
aggregation purposes. Store the applied rate and source separately if needed
for audit.

**Ledger:** the double-entry ledger entry carries the transaction currency pair.
If the ledger needs to aggregate across currencies (e.g. for a P&L), it does so
at reporting time with dated exchange rates, not at write time.

```python
from dataclasses import dataclass

@dataclass
class MoneyAmount:
    minor_units: int       # Always integer — house opinion #1
    currency: str          # ISO 4217 — "USD", "EUR", "GBP"
    # Never a float; never a "converted" amount stored here

@dataclass
class LedgerEntry:
    id: str
    amount: MoneyAmount    # Original transaction currency
    description: str
    type: str              # debit / credit
    created_at: datetime

# At display time only:
def display_amount(amount: MoneyAmount, display_currency: str, fx_rate: Decimal) -> str:
    if amount.currency == display_currency:
        return format_minor_units(amount.minor_units, amount.currency)
    converted = int(amount.minor_units * fx_rate)  # still an integer
    return format_minor_units(converted, display_currency) + f" (from {amount.currency})"
```

**Do:**
- Store the original transaction currency for every money record.
- Apply FX at display/reporting time, not at storage time.
- When an FX rate is applied for reporting, store the rate, its source, and its
  date alongside the report — not next to the transaction.

**Don't:**
- Store amounts only in a base currency after conversion.
- Use floating-point for FX rate arithmetic — use `Decimal` (Python) or an
  integer-scaled fixed-point representation.
- Perform FX conversion during webhook processing (you may not have the right
  rate at event time; store the original and convert later).

## Edge cases / when the rule does NOT apply

- Single-currency products: the pair is still correct, it just always has the
  same currency code. Don't skip the currency field "for simplicity."

## See also

- [`../agents/payments-architect.md`](../agents/payments-architect.md) — owns multi-currency design
- [`./money-is-integers.md`](./money-is-integers.md) — minor-unit integer storage applies in every currency
- [`./double-entry-ledger-is-source-of-truth.md`](./double-entry-ledger-is-source-of-truth.md) — the ledger entry always carries the transaction currency

## Provenance

Standard multi-currency payment system design practice. The "store in transaction
currency, present in display currency" principle is documented in Stripe's multi-
currency documentation and Martin Fowler's "Quantity" pattern (Patterns of
Enterprise Application Architecture). Revenue recognition currency conversion
routes to `finance`.

---

_Last reviewed: 2026-06-05 by `claude`_
