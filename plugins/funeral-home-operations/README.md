# funeral-home-operations

> The **deathcare-operations team** for Claude Code — the specialists who help a funeral director, owner, or manager *serve a grieving family with dignity while keeping the practice solvent and compliant.* Two agents: the **funeral-operations-lead** (runs the business — case flow, staffing, capacity, pre-need, aftercare, margins) and the **funeral-arrangement-and-compliance-specialist** (the arrangement conference, FTC Funeral Rule pricing/disclosures, cremation authorization, and vital records).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Not legal or financial advice.** Deathcare law varies by state and country, and the FTC Funeral Rule is periodically revised. Every volatile legal, licensing, permit, or benchmark item in this plugin's output carries a retrieval date and a "confirm with counsel + the licensing board" marker. Cremation authorization and vital-records steps are decision-support, not a substitute for your jurisdiction's requirements.

## What it does

| You ask | It returns |
|---|---|
| "My margins are slipping — where do I start?" | A scoped operations read: the case-flow stage that gates throughput, staffing/capacity vs call volume, pre-need mix, and the margin levers — with the family-experience check that keeps a cost cut from costing the reputation |
| "Families wait too long between first call and arrangement." | A stage-by-stage pipeline read (first call → removal → arrangement → preparation → services → billing → aftercare) naming the real constraint stage and a fix |
| "Is our General Price List Funeral-Rule compliant?" | A GPL / Casket / Outer-Burial-Container-list audit against the FTC Funeral Rule's itemization and disclosure requirements, each gap named — flagged as not legal advice, verify with counsel |
| "Walk me through the arrangement conference." | A grief-aware, itemized conference: selections a family actually chose, the required disclosures given at the right moment, disposition documented, nothing forced |
| "What authorizes a cremation and keeps custody airtight?" | A cremation authorization + positive-ID + chain-of-custody checklist (authorizing agent, written auth, tracking, no commingling), with state-permit steps flagged to verify |
| "What vital records and permits do we need?" | A death-certificate / certification / burial-cremation-transit-permit sequence with deadlines and certified-copy needs, jurisdiction-specific items marked to verify |

**Two rules it never breaks:** *the family's dignity and the practice's solvency are held together — never one at the other's expense,* and *compliance and compassion are the same act — honest, itemized Funeral-Rule disclosure IS the grief-aware move.*

## What's inside

- **2 agents** — `funeral-operations-lead` (runs the case-flow / staffing / capacity / pre-need / aftercare / margin side and routes) and `funeral-arrangement-and-compliance-specialist` (the arrangement conference, the FTC Funeral Rule, cremation authorization & chain-of-custody, vital records & permits).
- **3 skills** — `run-funeral-arrangement-and-intake`, `manage-case-logistics-and-fulfillment`, `ensure-deathcare-compliance-and-pricing`.
- **2 knowledge files** — a Mermaid deathcare-compliance decision tree (at-need vs pre-need → disposition → which price lists & disclosures fire → authorization & permits) and a 2026 funeral-operations-patterns reference (case-flow pipeline, disposition mix & the cremation-rate shift, staffing/on-call, pre-need funding, aftercare, family experience, technology, dated benchmarks).
- **2 templates** — an at-need arrangement worksheet and a General Price List compliance checklist.

## The seam between the two agents

```
funeral-operations-lead                         →  RUN THE BUSINESS   (case flow · staffing · capacity · pre-need · aftercare · margins)
funeral-arrangement-and-compliance-specialist   →  ARRANGE & COMPLY   (the conference · FTC Funeral Rule · cremation auth · vital records)
```

The lead is first contact for any new problem; it scopes, reads the operational picture, and hands the arrangement conference, pricing/disclosures, authorization, and vital records to the specialist. The specialist owns the regulatory spine — GPL/CPL/OBC lists, itemization, the telephone-price and embalming-not-required disclosures, no-misrepresentation, cremation ID/authorization/custody, and permits.

## Where it sits (and where it stops)

```
funeral-home-operations (HERE)  →  arrange · price · disclose · authorize · fulfill the services   ("serve the family, compliantly & solvently")
cemetery / interment            →  grounds · grave opening/closing · plot operations               (ADJACENT — out of scope; coordinate with, don't run)
behavioral-health-practice      →  clinical grief / bereavement therapy                            ("treatment" — this team refers, does not treat)
accounting-bookkeeping          →  the books · payroll · tax · the accounting behind the statement ("the ledger itself")
```

This plugin does deathcare **operations and arrangement compliance**. It coordinates *with* the cemetery but does not run interment; it *refers* grief to clinical care but does not treat; it owns the itemized statement's structure but hands the books to `accounting-bookkeeping`.

## Compliance stance

Concept-first (the FTC Funeral Rule's itemization + disclosure structure, the disposition-specific requirement sets, cremation authorization & chain-of-custody, vital-records sequencing, pre-need trust-vs-insurance funding), grief-aware throughout. **Deathcare law varies by state and country and the Funeral Rule is periodically revised** — every volatile legal, licensing, permit, and benchmark claim carries a retrieval date, a re-verify step, and a "not legal advice — confirm with counsel + the licensing board" marker. Re-verify before pinning anything in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install funeral-home-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
