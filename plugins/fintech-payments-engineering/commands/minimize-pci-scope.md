---
description: "Minimize PCI scope with tokenization (SAQ-A), audit-log money ops without card data, route attestation/verdict out."
argument-hint: "[payment data flows]"
---

You are running `/fintech-payments-engineering:minimize-pci-scope`. Use `payments-pci-compliance-advisor` + the `pci-scope-minimization` skill.

## Steps
1. Ensure tokenization so the raw PAN never touches your servers (target SAQ-A).
2. Identify and remove any in-scope card-data handling.
3. Audit-log money ops without PAN/CVV.
4. Route attestation/regulation to regulatory-compliance/legal, the verdict to security-reviewer.
5. Emit (from `templates/pci-scope-checklist.md`) + Structured Output block.
