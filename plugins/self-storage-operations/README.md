# self-storage-operations

> The **operator's team** for Claude Code — the two agents that run a self-storage facility as a business and answer *"how do I run this site, and how do I earn every dollar it can?"* Two agents: the **self-storage-operations-lead** (facility operations, staffing, security/access, maintenance, move-in/out flow, multi-site) and the **storage-revenue-and-occupancy-specialist** (street vs in-place rate, ECRIs, dynamic pricing, occupancy economics, delinquency/lien, ancillary revenue).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "How and how often should I raise rates on my existing tenants?" | An ECRI program: cadence, increase size by tenure and in-place-vs-street gap, a churn guardrail, and the projected NOI lift |
| "My street rates and my in-place rates are way apart — what do I do?" | A dynamic-pricing plan: street rate by unit type against physical/economic occupancy, unit-mix rebalancing, a promotion policy, and the PMS/pricing-tool wiring |
| "I have tenants 60+ days past due — walk me through the lien and auction." | A state-flagged delinquency-to-lien timeline (late fees → overlock → pre-lien/lien notices → advertising → auction on StorageTreasures/Lockerfox → sale → surplus), retrieval-dated and marked *not legal advice* |
| "Should I go remote/unmanned or keep a manager on site?" | An operating-model recommendation (staffed / hybrid / remote-kiosk) with the labor, access-control, call-center, and security implications |
| "We had a break-in — tighten access control and cameras." | A security posture review: gate/keypad access, individual door alarms, camera coverage + retention, lighting, overlock discipline, with a prioritized remediation list |
| "How do I get more revenue per unit beyond rent?" | An ancillary-revenue plan: tenant-insurance/protection-plan attach rate, admin/late fees, retail, and the move-in capture point |

**Two rules it never breaks:** *ECRIs are the core profit lever* (existing tenants have high switching costs, so a well-sized increase flows almost entirely to NOI), and *economic occupancy is the honest number* (physical occupancy flatters — read revenue-vs-street before any rate call). And one caveat it always states: **lien law varies by US state and this is operational guidance, not legal advice.**

## What's inside

- **2 agents** — `self-storage-operations-lead` (runs the facility: operating model, staffing, security, maintenance, move-in/out flow, multi-site) and `storage-revenue-and-occupancy-specialist` (runs the money: street vs in-place rate, ECRIs, dynamic pricing, occupancy economics, delinquency/lien, ancillary revenue).
- **3 skills** — `optimize-occupancy-and-dynamic-pricing`, `run-delinquency-and-lien-process`, `manage-facility-operations-and-security`.
- **2 knowledge files** — a Mermaid self-storage operations decision tree (revenue vs operating-model vs security vs maintenance vs multi-site, with the revenue sub-branches) and a 2026 self-storage-patterns reference (occupancy metrics, ECRI mechanics, dynamic pricing, unit-mix, the state-varying lien timeline, tenant insurance/ancillary, PMS & aggregator landscape, REIT benchmarks, remote/kiosk).
- **2 templates** — a delinquency-lien timeline (state-flagged, retrieval-dated, not-legal-advice) and an ECRI & pricing plan.

## Where it sits

```
commercial-real-estate     →  the lease / acquisition / cap-rate / asset investment   ("own the ASSET")
property-management         →  residential — apartments, single-family, HOA           ("manage the RESIDENTIAL")
field-service-management    →  generic mobile-crew dispatch / work orders             ("dispatch the CREW")
marketing-operations        →  paid-search / aggregator campaigns / brand / creative  ("run the CAMPAIGN")
accounting-bookkeeping      →  the books / P&L / sales tax                            ("keep the BOOKS")
self-storage-operations (HERE)  →  run the storage BUSINESS: ops + revenue           ("operate the FACILITY & earn its dollars")
```

This plugin operates the storage *business* — the operating model, the rates, the ECRIs, the lien process, the revenue per unit — and stays clear of the *asset* (commercial-real-estate), the *residential* variant (property-management), and generic *dispatch* (field-service-management).

## Domain stance

Concept-first (physical vs economic occupancy, street vs in-place rate, the ECRI as the core profit lever, dynamic pricing, unit-mix, the delinquency-to-lien timeline, tenant insurance/ancillary), fluent across the PMS platforms (**Storable / SiteLink / storEDGE, Easy Storage Solutions, Yardi Breeze**), the marketplace aggregators (**SpareFoot, Neighbor**), the auction platforms (**StorageTreasures, Lockerfox**), and the REIT benchmarks (**Public Storage, Extra Space, CubeSmart**). **Lien law varies by US state**, statutes change, and PMS/pricing-tool feature sets and REIT benchmarks are volatile — every such claim carries a **state and/or retrieval date**, and the lien mechanics are **operational guidance, not legal advice**: route the legal question to counsel.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install self-storage-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
