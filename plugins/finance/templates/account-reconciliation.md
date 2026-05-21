# Account reconciliation — [Account name] / [GL #]

> Standard recon workpaper. Audit-trail discipline: preparer + reviewer signatures, source-doc citations, dated.

**Period:** [YYYY-MM or YYYY-Qn]
**Account name:** [e.g., "Cash — Operating account, Bank XYZ"]
**GL account number:** [e.g., "10010"]
**Currency:** [USD / etc.]
**Prepared by:** [name] — [YYYY-MM-DD]
**Reviewed by:** [name] — [YYYY-MM-DD]
**Materiality threshold:** [e.g., reconciling items > $X are escalated]
**Confidentiality:** internal | client-confidential

---

## Balance summary

| Source | Balance | As of date | Source citation |
|---|---:|---|---|
| GL balance | $X | YYYY-MM-DD | GL export, file: [...] |
| Source / sub-ledger balance | $Y | YYYY-MM-DD | Source: [bank statement / sub-ledger / system export] |
| **Variance (GL − Source)** | **$Z** | | |

---

## Reconciling items

| # | Description | Amount | Age (days) | Status | Source / evidence |
|---|---|---:|---:|---|---|
| 1 | [e.g., "In-transit deposit from customer X"] | $A | 3 | Will clear next period | Bank batch ID [...] |
| 2 | [e.g., "Bank fee not yet recorded"] | $B | 5 | JE to book | Bank statement [...] |
| 3 | ... | ... | ... | ... | ... |
| | **Sum of reconciling items** | **$Σ** | | | |

**Variance after reconciling items:** [should equal 0 or be within materiality]

---

## Reconciling items > 30 days old

[Items aged > 30 days are escalated, not rolled forward. List here with escalation status.]

- [Item — age — owner — escalation status]

---

## JEs proposed from this recon

| JE # | Description | DR | CR | Amount |
|---|---|---|---|---:|
| | | | | |

---

## Sign-off

- **Preparer:** [name] — [YYYY-MM-DD]
- **Reviewer:** [name] — [YYYY-MM-DD]

**Source files:**
- [GL export path]
- [Sub-ledger / bank-statement file path]
- [Supporting docs path]
