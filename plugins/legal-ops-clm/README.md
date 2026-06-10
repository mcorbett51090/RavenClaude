# Legal Ops & CLM

The **legal-ops-clm** plugin — the operational / process layer of a corporate (in-house) legal function and contract lifecycle management (CLM): how legal work enters and gets triaged, how contracts get reviewed consistently against pre-set positions, and how signed contracts get tracked through obligations and renewals. Distinct from a law firm's own business (`legal-small-firm`).

> **Not legal advice.** This plugin provides operational and process support only. It does not render legal opinions or substitute for a qualified attorney. Every legal-judgement call (is a term enforceable, acceptable, or compliant) is owned by a licensed lawyer who signs off.

## Agents

- **`legal-ops-lead`** — Intake, workflow, and playbooks: structured legal intake & triage, the request-to-resolution workflow, contract playbooks that let business teams self-serve low-risk contracts (with bright-line escalation triggers), matter management, and legal-ops metrics & reporting. Designs how legal work flows — not the legal judgement itself.
- **`contract-review-specialist`** — Review mechanics: clause libraries with standard / fallback / walk-away positions, redline review that flags the *material* deviations by risk tier, key-term extraction, and approval routing. The key clauses — limitation of liability, indemnity, IP, term/termination, confidentiality — reviewed first and hardest.
- **`obligations-and-renewals-analyst`** — Post-signature lifecycle: obligation extraction & tracking (deliverables, SLAs, payment terms, notice periods, audit rights), renewal/expiry/auto-renew tracking with tiered notice-window alerts, and the contract repository & metadata model that makes contracts findable and reportable.

## The contract lifecycle this plugin covers

`intake → draft → review → negotiate → sign → manage → renew` — `legal-ops-lead` owns intake and the workflow, `contract-review-specialist` owns review/negotiate, and `obligations-and-renewals-analyst` owns manage/renew. The `sign` step (e-signature) is operational glue; the *judgement* at every step belongs to a human lawyer.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install legal-ops-clm@ravenclaude
```

## Seams

- **A law firm's own business (the firm as a company)** → `legal-small-firm`; this plugin serves a company's *internal* legal/legal-ops team.
- **Supplier sourcing and vendor selection** → `procurement-sourcing`; we handle the legal-ops mechanics of the supplier *contract* once the vendor is chosen.
- **What a DPA / cross-border-transfer / retention-deletion clause must say** → `data-governance-privacy`; we review and track the contract that carries it.
- **Security terms (right-to-audit, breach notification, security addendum)** → `security-engineering` + `ravenclaude-core/security-reviewer`.
- **Any actual legal opinion, deviation sign-off, or interpretation of ambiguous language** → a **qualified human lawyer**; this plugin never substitutes for one.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Pairs with `procurement-sourcing`, `data-governance-privacy`, and `security-engineering`.
