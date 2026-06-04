# P&C Insurance — Claude Code plugin

An underwriting-and-claims team for a P&C carrier, MGA, or agency analyst — it reads the combined ratio as loss plus expense, prices risk to the loss ratio rather than the competitor, manages the claims severity-and-frequency story, and reads catastrophe load the way an underwriting result that hit a decade-best ~92 combined in 2025 demands.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
p&c insurance depth on top.

## What it does

Decomposes the combined ratio into loss and expense, underwrites to the loss ratio and rate adequacy, separates frequency from severity in claims, and isolates the catastrophe load. Produces underwriting guidelines, claims-review frameworks, and portfolio-result reads an underwriting leader acts on.

## Agents

- **`underwriting-lead`** — The engagement — scoping the underwriting question, framing the result, routing, and synthesizing a portfolio action plan.
- **`pc-underwriter`** — Risk selection and pricing — underwriting guidelines, rate adequacy, the loss ratio, and account-level decisions.
- **`claims-specialist`** — Claims operations — frequency/severity, indemnity leakage, LAE, cycle time, and reserve adequacy.
- **`actuarial-pricing-analyst`** — The numbers — combined-ratio decomposition, loss triangles, cat load, line-of-business analytics, as decision-support.

## Skills

- **`decompose-the-combined-ratio`** — Split the combined ratio into loss and expense, then attritional and catastrophe, so a deteriorating result is diagnosed correctly. Reach for this on any result question.
- **`price-to-rate-adequacy`** — Price risk to expected loss plus expense plus profit load against loss trend, not to the competitor, so growth doesn't grow a loss. Reach for this on any pricing question.
- **`separate-frequency-and-severity`** — Decompose a loss-ratio move into frequency and severity, since they have opposite responses, before prescribing. Reach for this when the loss ratio moves.
- **`review-claims-leakage`** — Read indemnity leakage, LAE, and cycle time as managed metrics, not minimized payout, to find the controllable gap. Reach for this on a claims-cost question.
- **`read-the-portfolio-result`** — Read the underwriting result by line of business, attritional-vs-cat and net-of-reinsurance, so the mix story is visible. Reach for this on a portfolio review.

## Slash commands

- **`/insurance-pc:decompose-the-combined-ratio`** — Decompose the combined ratio
- **`/insurance-pc:price-to-rate-adequacy`** — Price to rate adequacy
- **`/insurance-pc:separate-frequency-from-severity`** — Separate frequency from severity

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install insurance-pc@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a rating engine, a policy-admin system, or a licensed actuarial/legal authority — pricing and reserving guidance is decision-support, and rate filings belong to a credentialed actuary. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
