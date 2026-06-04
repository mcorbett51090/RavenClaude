---
name: pci-scope-minimization
description: "Minimize PCI-DSS scope (engineering posture): use PSP client-side tokenization so the raw PAN never touches your servers (SAQ-A), reduce scope ruthlessly, log money operations for audit without ever logging card data, and route attestation/regulation/verdict out."
---

# PCI Scope Minimization

## Never touch the PAN
PSP **client-side elements/tokenization**: card data goes browser -> PSP directly; you store a **token**. That's **SAQ-A** — the cheapest compliance is data you never receive.

## Minimize scope
Every system touching card data is **in scope**. Tokenization shrinks scope to ~nothing — pursue scope reduction **before** controls.

## Log safely
Audit who/what/which-payment; **never** log PAN/CVV (a CVV in a log is a serious violation).

## Route out
Formal attestation + money-transmission/AML -> `regulatory-compliance`/legal; security verdict -> `security-reviewer`. **Not legal advice.**
