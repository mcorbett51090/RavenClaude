---
description: "Architect a money-safe payment system: PSP choice, integer money, double-entry ledger, money events, reconciliation."
argument-hint: "[payment use case + geography]"
---

You are running `/fintech-payments-engineering:design-payments-architecture`. Use `payments-architect` + the `payment-flow-architecture` skill.

## Steps
1. Choose the PSP by scope/geography/methods/PCI-burden.
2. Represent money as integer minor units; design the double-entry ledger as source of truth.
3. Define the money-event model + reconciliation.
4. Route accounting to finance, regulation to regulatory-compliance.
5. Emit (from `templates/payment-ledger.md`) + Structured Output block.
