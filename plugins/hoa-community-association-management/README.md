# hoa-community-association-management

> The **community-association layer** for Claude Code — the team that answers *"what should the community association budget, charge, fund, enforce, and maintain — and how do we run it evenly and by the documents?"* and executes the answer for a community-association manager (CAM) / management company running HOAs, condominium associations (COAs), and property-owners' associations (POAs). Two agents: the **association-management-lead** (sets governance & fiduciary framing, the budget & assessment strategy, the reserve-funding policy, the major-project & special-assessment plan, the insurance posture, the developer-transition strategy, and the enforcement/collections **policy**) and the **community-operations-specialist** (bills the dues, runs collections & violation/ARC workflows, coordinates vendors & common-area maintenance, runs meetings & official records, and handles resident communications).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Not legal, financial, or insurance advice.** Volatile HOA/condo statutes, lien/foreclosure procedures, reserve-study standards, and fair-housing/collection rules are jurisdiction-specific — they carry a retrieval date, are verified at use, and legal questions route to **counsel**.

## What it does

| You ask | It returns |
|---|---|
| "Build our annual budget and tell us what the assessments should be." | An operating + reserve budget and an assessment (dues) level checked against the increase cap — with the reserve-underfunding / special-assessment risk surfaced, not hidden |
| "Our reserves are thin and the roofs are due — special assessment, loan, or phase it?" | A reserve-funding policy (percent-funded target + method) and a major-project funding decision with the member-burden / cost-of-capital / timing trade-offs, and the vote threshold flagged to counsel |
| "Write our covenant-enforcement and collections policy." | An even-handed, documented due-process enforcement framework (notice → cure → hearing → fine) and a delinquency sequence (late fee → demand → lien-referral gate), anchored to the CC&Rs with the lien/foreclosure and fair-housing mechanics routed to counsel |
| "Process this covenant violation / this architectural-review request." | A violation run by the documented, even-handed sequence — or an ARC decision measured against the design guidelines within the required timeframe — fully recorded for the file |
| "Bill the assessments and work our delinquency list." | A billing run, an aging report, and the collections sequence applied evenly to every account, with the accounts at the escalation-to-counsel threshold flagged |
| "Prepare our annual meeting and take the minutes." | A meeting package (notice per the bylaws, agenda, quorum/proxy plan, board packet) and minutes capturing motions, votes, and decisions, filed to the official records with retention/inspection rules noted |
| "Get bids for the landscaping contract and schedule the common-area maintenance." | A vendor plan (scoped bids with insurance/license verified, within budget and spending authority) and a preventive maintenance calendar with a work-order/inspection loop |

**Rules it never breaks:** *the governing documents are the constitution* (read the CC&Rs/bylaws/statute before you act), *fund the reserves on the study* (not the mood of the board), *enforce and collect evenly by the documented process* (selective enforcement is how associations get sued), *the board decides and the manager advises and executes* (never blur that line), and *minutes and records are the association's memory and its legal shield*.

## What's inside

- **2 agents** — `association-management-lead` (governance & fiduciary advisory, the annual budget & assessment strategy, reserve-funding policy from the reserve study, major-project & special-assessment planning, insurance/risk posture, developer-transition strategy, and the enforcement/collections policy) and `community-operations-specialist` (dues billing & collections/delinquency, covenant-violation & architectural-review processing, vendor & common-area maintenance coordination, meetings & minutes/official records, and resident communications).
- **3 skills** — `build-budget-and-reserve-plan`, `run-covenant-and-collections-workflow`, `manage-board-and-vendor-operations`.
- **2 knowledge files** — a Mermaid community-association decision tree (budget & assessment, reserve funding & major-project, enforcement & ARC, collections & delinquency + trade-off tables) and a 2026 patterns reference (the governing-document hierarchy, association types, operating + reserve budgeting, reserve studies & percent-funded, the assessment/lien concept, enforcement due process, meetings & records, insurance layers, developer transition, and a dated statute/standards map).
- **2 templates** — an annual budget & reserve-study summary and a violation & collections procedure with a running matter log.

## Where it sits in the real-estate stack

```
hoa-community-association-management (HERE)  →  the COMMUNITY ASSOCIATION & its common-interest governance  ("budget, assess, fund reserves, enforce, maintain")
property-management                          →  a landlord's rental units, leases & rent                     ("rental operations of individual units")
residential-real-estate-brokerage           →  buying & selling homes                                        ("the transaction")
commercial-real-estate                       →  CRE brokerage / asset management                              ("commercial property")
```

This plugin is the **community-association layer**: it governs, budgets, funds, enforces, and maintains the **common-interest community**, and stays clear of a *landlord's rental units* (`property-management`), the *home sale transaction* (`residential-real-estate-brokerage`), and *commercial real estate* (`commercial-real-estate`). Legal steps (lien, foreclosure, statute, fair-housing) route to **counsel** — it is not legal advice.

## Domain stance

Concept-first (the governing-document hierarchy as the constitution, operating + reserve budgeting, the reserve study & percent-funded, funding methods and the special-assessment risk, even-handed documented enforcement due process, architectural review against published guidelines, the collections sequence to the legal gate, the board-decides / manager-advises separation, minutes-and-records as the legal shield), fluent across **HOA / COA / POA** types, **assessment caps & special-assessment vote thresholds**, **reserve-funding methods** (full / baseline / threshold / statutory-minimum), **major-project funding** (raise reserves / special assessment / association loan / phase), the **master-policy / D&O / fidelity** insurance layers, **notice / quorum / proxy / records-retention & owner-inspection** governance, and **developer-to-homeowner transition**. HOA/condo statutes, lien/foreclosure procedures, reserve-study standards, ARC timeframes, and fair-housing/collection rules carry retrieval dates — re-verify (and confirm with **counsel**) before pinning in a board deliverable. **Not legal, financial, or insurance advice.**

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install hoa-community-association-management@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
