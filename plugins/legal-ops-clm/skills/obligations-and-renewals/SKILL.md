---
name: obligations-and-renewals
description: "Extract and track contract obligations as owned items, watch renewals / expiries / auto-renew with tiered notice-window alerts, and model the contract repository metadata so contracts are findable and reportable — operational support, not legal advice."
---

# Obligations & Renewals

> Operational/process support only — not legal advice. This skill extracts, structures, tracks, and alerts on what a contract *says*; a lawyer interprets ambiguous language and owns the consequence of a breach. Ambiguity is flagged, not guessed.

## Signature is the start — extract the obligations
A signed contract is a list of commitments. Extract deliverables, SLAs, payment terms, notice periods, and audit rights, and make each a tracked item with a **named owner**, a due date or trigger, and a status. An obligation with no owner is one nobody meets.

## Track the notice window, not just the expiry
An auto-renew fires unless notice is given within a window before expiry — so track the **notice-window deadline** per contract, not just the end date. Tier alerts (90/60/30 days) to a named owner so the renew/renegotiate/exit decision happens while there's still time. A renewal alert that fires at expiry is a decision you didn't get to make.

## Model the repository as a schema
The contract repository is metadata, not a folder convention: counterparty, type, value, effective/expiry dates, auto-renew flag, owner, status, governing law, and obligation links. Named fields a query can hit are what make contracts findable and the reports possible.

## Reports and alerts that route to an owner
Expiring-soon, notice-window-closing, obligation-due, by-value, by-counterparty — each routed to the owner who can act, not a dashboard nobody reads.

## Output
An obligations register (item + owner + trigger + status), a renewal/expiry tracker (expiry + auto-renew + notice deadline + tiered alerts), and/or a repository metadata schema with the reports it enables. Take key-term seeds from `contract-review-specialist`; feed obligation/renewal health to `legal-ops-lead`'s metrics; flag any ambiguous obligation for a human lawyer.
