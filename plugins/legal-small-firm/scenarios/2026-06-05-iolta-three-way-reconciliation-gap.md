---
scenario_id: 2026-06-05-iolta-three-way-reconciliation-gap
contributed_at: 2026-06-05
plugin: legal-small-firm
product: trust-accounting
product_version: "n/a"
scope: likely-general
tags: [iolta, trust-accounting, three-way-reconciliation, rule-1-15, ethics]
confidence: medium
reviewed: false
---

## Problem

During an operations review, a 2-attorney firm could not produce a defensible trust-account audit trail. They had an IOLTA account and individual client ledgers in the billing system, but had **never reconciled the client ledgers against the bank statement** — only the checkbook against the bank statement. They could not prove that each client's funds were intact and un-commingled. The owner believed "the trust account balances" was sufficient. A bar audit (or a single bounced trust check) would have flagged this immediately — and this must be framed as decision-support, never legal advice, with the call routed to the attorney and the state bar rules (CLAUDE.md §2, §3 #6).

## Context

- Segment: small-business + family-law mix, independent, single IOLTA account, advance fees and settlement funds flowing through trust.
- Constraint: this is a **reconciliation-discipline** gap, not a misappropriation finding — but the inability to perform a **three-way reconciliation** is exactly what turns a routine audit into a problem. The plugin stores no client funds and resolves no ethics question; it standardizes the *firm's* trust-accounting discipline as decision-support for the responsible attorney (§2).
- The team confused a **two-way** reconcile (bank statement ↔ checkbook) with the required **three-way** reconcile.

## Attempts

- Tried: mapped current practice against the three-way reconciliation standard. **Three-way reconciliation** requires three figures to agree: (1) the **adjusted bank statement balance**, (2) the **trust account book/checkbook balance**, and (3) the **sum of all individual client ledger balances**. The firm was doing only (1)↔(2); the missing leg — that the client ledgers sum to the bank balance — is the one that proves no client's funds were used for another's. Outcome: named the specific missing control.
- Tried: confirmed the volatile compliance facts against sources rather than memory — (a) ABA **Model Rule 1.15** requires client funds be held **separate** from the lawyer's own (no commingling), **complete records** kept, and records **retained for five years** after termination of the representation (the ABA floor; many states differ); (b) a wave of states is **tightening** — reporting indicates 12 state bars adopting a uniform standard cutting the monthly reconciliation deadline from 45 to **30 days** and mandating three-way reconciliation, with a **July 1, 2026** compliance date and automatic disciplinary referral for non-compliance. Outcome: grounded the two facts that gate the recommendation, both marked `[verify-at-use]` because trust rules are state-specific.
- Tried (the move that worked): instituted a **monthly three-way reconciliation** with a named owner and a calendared date, a written SOP, and a hard rule that earned fees are not withdrawn until billed and the client ledger supports it. Outcome: a reconcilable, audit-ready trail with a recurring control, not a once-a-year scramble.

## Resolution

The gap was **the missing third leg of the reconciliation**, not effort — a balanced checkbook is not proof that client funds are intact. A monthly three-way reconciliation (bank ↔ book ↔ client ledgers) with a written SOP, a named owner, and a calendared date closed it. Trust accounting is a non-negotiable hard guardrail — the call routes to the attorney and the applicable state bar rules (§3 #6).

**Action for the next consultant hitting this pattern:** confirm a **three-way** reconciliation is happening monthly (bank statement ↔ trust book balance ↔ sum of client ledgers) — a two-way reconcile is the most common false sense of security. Verify the **state**'s specific deadline and retention rule at use (the ABA floor is a 5-year retention and a per-state reconciliation cadence; several states are moving to a 30-day cadence + mandatory three-way by 2026). Frame every output as decision-support for the responsible attorney; route anything touching client funds, PII, or ethics to the attorney and to `ravenclaude-core` `security-reviewer`. See [`../knowledge/legal-intake-and-trust-decision-trees.md`](../knowledge/legal-intake-and-trust-decision-trees.md) (IOLTA tree).

**Sources (retrieved 2026-06-05):**
- ABA Model Rule 1.15 (Safekeeping Property): https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/rule_1_15_safekeeping_property/
- Three-Way IOLTA Reconciliation guidance: https://stephsbooks.com/blog/iolta-three-way-reconciliation
- State-bar tightening (45→30 day deadline; mandatory three-way; July 1 2026): https://stephsbooks.com/news/three-way-iolta-reconciliation-mandatory-12-states
- Illinois ARDC Client Trust Account Handbook (a representative state handbook): https://www.iardc.org/Files/ClientTrustAccountHandbook.pdf

Trust-accounting and IOLTA rules are **state-specific and volatile** — every figure (deadline, retention period, reconciliation cadence) is `[verify-at-use]` against the firm's specific state bar rule, and the ethics call routes to the attorney (§3 #6, §3 #8).
