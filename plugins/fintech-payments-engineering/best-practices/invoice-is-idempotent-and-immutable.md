# Treat invoices as immutable records; credit note for corrections

**Status:** Absolute rule
**Domain:** Billing / invoicing
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

An invoice is a financial document. In many jurisdictions, deleting or
retroactively editing a sent invoice is illegal or creates accounting
inconsistencies `[verify-at-use — local tax regulation applies]`. Teams that
"fix" an invoice by editing its line items after sending it break the audit
chain, confuse the customer, and may create duplicate revenue-recognition
records. The correct accounting workflow for a correction is to void the
incorrect invoice and issue a credit note, or to create a correction invoice
alongside the original. The invoice is immutable; the correction is a new
document.

## How to apply

**Creation:** generate invoices idempotently — use the billing period +
customer id as the idempotency key so the same invoice is never created twice
for the same period.

**Correction:** if an invoice has an error after creation:
- If not yet finalized/sent: void and recreate.
- If finalized/sent: issue a credit note to reverse the incorrect amount, then
  issue a new invoice for the correct amount.

**Never:** modify line items on a finalized invoice.

```python
def finalize_invoice(customer_id: str, period: str) -> Invoice:
    # Idempotent creation — returns existing if already created for this period
    existing = db.get_invoice(customer_id, period)
    if existing and existing.status != "draft":
        return existing  # Already finalized — do not modify

    invoice = billing_api.create_invoice(
        customer=customer_id,
        auto_advance=False,  # Don't auto-finalize; we finalize explicitly
        idempotency_key=f"invoice:{customer_id}:{period}",
    )
    billing_api.finalize_invoice(invoice.id)
    ledger.post_invoice(invoice)
    return invoice

def correct_invoice(invoice_id: str, correction: dict) -> tuple:
    invoice = db.get_invoice_by_id(invoice_id)
    if invoice.status in ("draft", "open"):
        # Before payment: void and recreate
        billing_api.void_invoice(invoice_id)
        return create_corrected_invoice(correction), None
    else:
        # After payment: credit note + new invoice
        credit_note = billing_api.create_credit_note(invoice_id=invoice_id, ...)
        new_invoice = create_corrected_invoice(correction)
        return new_invoice, credit_note
```

**Do:**
- Use idempotency keys on invoice creation to prevent duplicate invoices.
- Post a ledger entry for every invoice creation, void, and credit note.
- Check local tax law requirements for invoice correction procedures —
  route to `finance` and `regulatory-compliance`.

**Don't:**
- Edit line items on a finalized invoice — this is an immutable record.
- Delete invoices instead of voiding them — deleted records have no audit trail.
- Issue a credit note without a corresponding corrected invoice.

## Edge cases / when the rule does NOT apply

- Draft invoices (not yet finalized or sent): freely modify before finalization.

## See also

- [`../agents/billing-subscriptions-engineer.md`](../agents/billing-subscriptions-engineer.md) — owns invoicing lifecycle
- [`./double-entry-ledger-is-source-of-truth.md`](./double-entry-ledger-is-source-of-truth.md) — every invoice event posts to the ledger
- [`./reconcile-continuously.md`](./reconcile-continuously.md) — credit notes and correction invoices must reconcile to the PSP

## Provenance

Standard accounting and invoicing practice. Invoice immutability is a standard
principle in accounting software design. Local tax law requirements for invoice
correction vary by jurisdiction and route to `finance` + `regulatory-compliance`.
Stripe invoice API documentation `[verify-at-use]`.

---

_Last reviewed: 2026-06-05 by `claude`_
