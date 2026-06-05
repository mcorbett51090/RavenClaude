# Fintech & Payments Engineering Plugin — Team Constitution

> Team constitution for the `fintech-payments-engineering` Claude Code plugin — **4** specialist agents for building payment and billing systems correctly — payment integration (Stripe-style), subscription/usage billing, money-safe ledgers and reconciliation, and PCI scope minimization — the engineering, with financial-regulatory and accounting routed out. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`payments-architect`](agents/payments-architect.md) | Payment system architecture: PSP/processor choice, money representation (integer minor units, multi-currency), the double-entry ledger as source of truth, reconciliation design, and the payment-flow topology | "design our payments architecture", "which payment processor?", "how should we store money / build a ledger?", "how do we reconcile?" |
| [`payments-integration-engineer`](agents/payments-integration-engineer.md) | PSP integration: payment intents/charges with idempotency keys, webhook signature verification + idempotent handling, 3DS/SCA, saved payment methods, refunds, retries and failure handling, and the charge state machine | "integrate Stripe", "handle payment webhooks safely", "add 3DS/SCA", "our charges sometimes double" |
| [`billing-subscriptions-engineer`](agents/billing-subscriptions-engineer.md) | Subscription and usage billing: plans and pricing models, proration, usage metering, invoicing, the billing cycle, dunning/failed-payment recovery, and emitting clean revenue events for finance | "build subscription billing", "handle proration", "meter usage-based pricing", "recover failed subscription payments" |
| [`payments-pci-compliance-advisor`](agents/payments-pci-compliance-advisor.md) | PCI-DSS scope minimization (the engineering posture): tokenization so card data never touches your servers, SAQ-A posture, secure handling of payment data, audit/logging of money operations, and routing the regulatory + verdict questions out | "how do we stay PCI compliant?", "minimize our PCI scope", "are we touching card data?", "what do we log for payments?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Money is integers in minor units, never floats.** Store amounts as integer cents (with currency); floating-point math on money is rounding error that becomes a reconciliation nightmare and a customer dispute.
2. **Every money operation is idempotent.** Charges, refunds, payouts, and webhook handlers all carry an idempotency key. Networks retry; a non-idempotent charge double-bills a customer — the cardinal payments sin.
3. **Keep a double-entry ledger as your source of truth.** Every money movement is balanced debits and credits in an append-only ledger; the PSP is an integration, not your accounting record. Reconcile the ledger to the PSP continuously.
4. **Verify and idempotently handle every webhook.** Verify the signature (it's an untrusted public endpoint) and dedupe by event id — webhooks are at-least-once and out-of-order. An unverified webhook is a spoofable money instruction.
5. **Minimize PCI scope — never touch the raw card number.** Tokenize via the PSP's client-side elements so card data never hits your servers (SAQ-A). The cheapest PCI compliance is the card data you never receive.
6. **This is engineering; accounting and regulation route out.** We build the ledger, integration, and billing; revenue recognition and GL route to `finance`, financial-services regulation to `regulatory-compliance`, and security verdicts to `ravenclaude-core/security-reviewer`.

## 3. Seams (the bridges to neighbouring plugins)

- **Revenue recognition (ASC 606), GL postings, the chart of accounts, financial close** → `finance`; this team produces the money events and ledger, that team does the accounting on top.
- **Financial-services regulation (money transmission, AML/KYC, licensing, regulator reporting)** → `regulatory-compliance`; we build the payment mechanics, not the regulatory compliance.
- **The security verdict on a PCI/payment-flow finding** → `ravenclaude-core/security-reviewer` (via `security-engineering`); we minimize scope and recommend, they clear it.
- **The API contract for our payment endpoints + webhook semantics** → `api-engineering`; the service implementation behind it → `backend-engineering` (idempotency/outbox).
- **End-user authentication around payments / stored-credential consent UX** → `auth-identity`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.


## 5. Knowledge & scenario banks + runnable tooling

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer):
  - [`knowledge/fintech-payments-engineering-decision-trees.md`](knowledge/fintech-payments-engineering-decision-trees.md) — charge-flow correctness, PCI scope / SAQ, decline-retry, reconciliation triage, refund/dispute/chargeback, payment-method selection, dunning path, and a dated 2026 capability map (PR #315).
  - [`knowledge/payment-ledger-and-psp-topology-decision-trees.md`](knowledge/payment-ledger-and-psp-topology-decision-trees.md) — **two NEW trees complementing the above**: the **ledger model** (table vs. mutable-balance anti-pattern vs. append-only double-entry) and **PSP topology + settlement timing** (single PSP vs. orchestration; fulfill-on-authorized vs. gate-on-settled; the ACH/SEPA delayed-settlement rule), with a dated ISO 20022 cross-border note.
  - **Traverse the relevant Mermaid tree top-to-bottom before designing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified-scenario preamble): [`scenarios/`](scenarios/) — field notes (idempotency-key double-charge, webhook replay + reconciliation, decline-retry storm + dunning, PCI scope-creep + tokenization). Secondary source; never replaces the knowledge bank, and never overrides a PCI/regulatory verdict (route those out per §3). The most-likely-to-benefit specialists — `payments-integration-engineer`, `payments-architect`, `payments-pci-compliance-advisor`, `billing-subscriptions-engineer` — should check the bank when a situation matches.

**Runnable tooling** — [`scripts/recon_diff.py`](scripts/recon_diff.py) (stdlib only, Python 3.9+) mechanizes the Reconciliation-discrepancy-triage tree: diff your internal ledger against a PSP report (CSV in, triage report + JSON out), classifying every non-zero difference into PSP_ONLY / LEDGER_ONLY / AMOUNT_MISMATCH / CURRENCY_MISMATCH so each gets an owner. Money is integer minor units end-to-end (a float amount is rejected loudly — §2 #1); it exits non-zero on any discrepancy so a CI recon gate can use it. It is a **differ, not a money-mover** — it posts nothing, calls no PSP, and makes no network request; the accounting treatment of a delta routes to `finance`, a suspected-fraud delta to `ravenclaude-core/security-reviewer` (§3). Owned primarily by `payments-architect`; `payments-integration-engineer` uses it to confirm a webhook-handling fix closed a discrepancy.


## 6. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built or recorded N-A with reason). PR #315 already added the consolidated decision-tree knowledge, `best-practices/`, and `templates/`; this build-out closes the net-new gaps (scenarios bank + runtime-tier dispositioning) and adds two topic-specific trees complementing #315's.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (idempotency-key double-charge, webhook replay + reconciliation, decline-retry storm + dunning, PCI scope-creep + tokenization) matching the existing `scenarios/README.md` index + 9-field schema. Surfaced behind the mandatory unverified-scenario preamble. |
| 2 | **Decision-tree knowledge (NEW)** | **BUILT** — `knowledge/payment-ledger-and-psp-topology-decision-trees.md`: ledger-model tree + PSP-topology/settlement-timing tree. Chosen because #315's file already covers charge-flow / PCI / decline / reconciliation / method / dunning — the ledger-model and PSP-topology design decisions were the gaps. Grounded + cited + dated. |
| 3 | **Bundled MCP server** | **N-A (RECOMMEND, don't bundle)** — the official **Stripe MCP** (`@stripe/mcp` local / `https://mcp.stripe.com` remote via OAuth) is **credentialed + write-capable** (scoped by a Restricted API Key — a secret) and per-consumer, so per `docs/best-practices/bundled-mcp-servers.md` it is recommend-not-bundle: documented with the secret as a **reference** (env-var name / RAK, never a literal) and a mandatory `ravenclaude-core/security-reviewer` gate (payments = high blast radius). No payments MCP clears the zero-config + read-only-by-default bar → no `mcpServers` entry, no `x-mcpAttribution`/`NOTICE.md`. No invented servers. (Recommended setup below.) |
| 4 | **LSP server** | **N-A** — this plugin is payment-method/design guidance, not tied to one source language; the LSP config belongs to the code plugin editing the source (`backend-engineering` ships one). |
| 5 | **Runnable script (`scripts/`)** | **BUILT** — `scripts/recon_diff.py` (ledger-vs-PSP reconciliation differ; the one runtime item with real, groundable value — see §5). `ruff check`-clean, stdlib only. |
| 6 | **bin/ / monitors / output-styles / settings defaults / themes** | **N-A** — no groundable, broadly-valuable instance. The single runtime artifact (`recon_diff.py`) lives under `scripts/`; deliverables are governed by the agents' Output Contract, not a styling surface. |
| 7 | **skills / hooks / commands / templates** | **SUFFICIENT** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover payment-flow architecture, integration, reconciliation, PCI-scope, and subscription billing. The scenarios + new topology trees + recon script extend reach without a new agent or skill. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.3.0` entry. **NOTICE.md N-A** — nothing third-party is bundled (the Stripe MCP is recommend-not-bundle; the script is original, stdlib-only). |

### Recommended (not bundled) MCP server — Stripe MCP

Per `docs/best-practices/bundled-mcp-servers.md`, a per-consumer / credentialed / write-capable server is **recommend, don't bundle**. The official Stripe MCP is exactly that.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Stripe MCP** (official, `@stripe/mcp` / remote `https://mcp.stripe.com`) | **Credentialed** (tool permissions are scoped by a Stripe **Restricted API Key** — a secret) and **write-capable** (it can act on the Stripe account); per-consumer (each merchant's own account/keys). Payments = high blast radius. | Consumer-configured, **gated through `ravenclaude-core/security-reviewer` before adoption**; secret carried as a **reference** (env-var name / vault URI), never a literal; **human confirmation of tool calls** enabled (Stripe's own recommendation), and a **least-privilege Restricted API Key** scoped to only the needed verbs. Local: `npx -y @stripe/mcp --api-key=$STRIPE_SECRET_KEY` (key from a reference); remote: `https://mcp.stripe.com` via OAuth. `[verify-at-use — package name, endpoint, RAK scoping, and the prompt-injection caution against mixing MCP servers are all vendor-volatile]`. |

> Verified 2026-06-05 against Stripe's MCP documentation: the local `@stripe/mcp` package + the remote `https://mcp.stripe.com` (OAuth) endpoint, tool permissions controlled by a Restricted API Key, and Stripe's recommendation to enable human confirmation of tool calls and exercise caution against prompt injection when combining MCP servers. Package/endpoint/RAK details are version-volatile — re-confirm at use. Source: https://docs.stripe.com/mcp


## 7. Milestones

- **v0.2.x** — 4-agent fintech-payments team; 6 skills, 4 templates, 4 commands, 1 advisory hook. PR #315 added the consolidated decision-tree knowledge bank, `best-practices/`, and `templates/`.
- **v0.3.0** — value-add build-out: scenarios bank (4 scenarios), a NEW topic-specific decision-tree file (ledger-model + PSP-topology/settlement trees, complementing #315's), `scripts/recon_diff.py` (reconciliation differ), CHANGELOG, and the value-add completeness disposition (§6). Bundled-MCP / LSP / bin / monitors / styles / themes dispositioned N-A with reasons; Stripe MCP recorded as recommend-not-bundle with reference creds + a security-reviewer gate.
