# community-association-management

> The **board's team** for Claude Code — the two agents that run a community association (HOA / condo COA) for a volunteer board and answer *"how do we run this association soundly, and how do we govern and enforce it without getting sued?"* Two agents: the **association-management-lead** (annual budget, assessment setting, reserve study & funding adequacy, vendor/contract management, insurance/master policy, meetings & notices) and the **governance-and-covenant-specialist** (board fiduciary duty, elections & quorum, open-meeting/records rules, fair-and-consistent covenant enforcement, the delinquency-to-collections/lien ladder, homeowner relations).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Are our reserves adequate, and what should dues be next year?" | A budget & reserve plan: the reserve-study read (component inventory, remaining useful life, **percent funded**), a funding plan (full / baseline / threshold), and the assessment set — framed, with adequacy *certification* flagged to a reserve specialist |
| "The roofs are failing and the reserve is short — special assessment or a loan?" | A special-assessment-vs-association-loan model: the lump-sum vs financed-through-assessments trade-off, the owner impact, and the reserve context that produced the choice |
| "An owner won't repaint — how do I enforce the covenant without a lawsuit?" | A fair-and-consistent enforcement ladder: the covenant cited, notice, an **opportunity to be heard (hearing)**, a consistent penalty schedule, a documented record, and the selective-enforcement guardrail — with the legal determination flagged to counsel |
| "An owner is 90 days delinquent — walk me through collections." | A state-flagged collections ladder (late fee → reminder/demand → payment-plan offer → pre-lien notice → **lien** → foreclosure where applicable), retrieval-dated and marked *not legal advice* |
| "Our annual election blew quorum — now what?" | A governance read: quorum/proxy/adjournment options under the governing documents and state election rules, the notice defects to avoid, and how to re-run it defensibly |
| "The board wants to act — are we protected?" | A fiduciary-duty check: duty of care/loyalty, the business-judgment rule as a *process* shield, a conflict check, open-meeting compliance, and the documentation that makes the decision defensible |

**Two rules it never breaks:** *the reserve study is the spine of the budget* (read **percent funded**, not just the reserve balance, before any assessment call) and *enforce covenants fairly and consistently or not at all* (selective enforcement is the fastest route to a lost lawsuit). And one caveat it always states: **reserve adequacy, fair enforcement, and collections/lien law are state-specific — this is operational guidance, not legal advice.**

## What's inside

- **2 agents** — `association-management-lead` (runs the association: annual budget, assessment setting, reserve study & funding adequacy, vendor/contract management, insurance/master policy, meetings & notices) and `governance-and-covenant-specialist` (governs & enforces: board fiduciary duty, elections & quorum, open-meeting/records rules, fair-and-consistent covenant enforcement, the delinquency-to-collections/lien ladder, homeowner relations).
- **3 skills** — `build-budget-and-reserve-plan`, `enforce-covenants-fairly`, `run-assessment-collections-ladder`.
- **2 knowledge files** — a Mermaid community-association decision tree (budget/assessments vs reserves vs governance/elections vs covenant-enforcement vs collections vs vendor, with the reserve-funding sub-choice) and a 2026 patterns reference (reserve-study methodology & percent funded, funding plans, special-assessment-vs-loan, the collections ladder, fair enforcement, board fiduciary duty, management-company vs self-managed, CAM software, CAI, and state-law variance).
- **2 templates** — an annual budget & reserve plan and a covenant-enforcement-and-collections timeline (state-flagged, retrieval-dated, not-legal-advice).

## Where it sits

```
property-management         →  owner/tenant residential leasing — apartments, single-family rentals   ("run the LEASE")
commercial-real-estate      →  the acquisition / cap-rate / asset-level investment                     ("own the ASSET")
marketing-operations        →  newsletter / brand / member-communications campaigns                    ("run the CAMPAIGN")
accounting-bookkeeping      →  the books / audit / tax return                                          ("keep the BOOKS")
community-association-management (HERE)  →  run the ASSOCIATION for the board: finances + governance    ("govern the COMMUNITY")
```

This plugin runs the *association* on behalf of its owner-members — the budget, the reserves, the covenants, the governance, the collections — and stays clear of owner/tenant *residential leasing* (property-management) and the *investment asset* (commercial-real-estate).

## Domain stance

Concept-first (percent funded and the reserve-study spine, full/baseline/threshold funding plans, special assessment vs loan, the fair-and-consistent enforcement ladder, board fiduciary duty and the business-judgment rule, open-meeting & records rules, the delinquency-to-collections/lien ladder), fluent across the CAM-software landscape (**AppFolio, Vantaca, TOPS / CINC**), the reserve-study discipline, and the industry body (**CAI — Community Associations Institute**). **State HOA/COA statutes vary materially** (e.g. **Davis-Stirling** in California, and every state's own act), statutes change, and CAM-software feature sets and reserve/insurance norms are volatile — every such claim carries a **state and/or retrieval date**, reserve *adequacy* is a professional determination, and enforcement/lien/fiduciary-scope questions are **operational guidance, not legal advice**: route the legal determination to counsel.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install community-association-management@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
