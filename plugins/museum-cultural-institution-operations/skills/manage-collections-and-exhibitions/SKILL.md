---
name: manage-collections-and-exhibitions
description: Steward a collection and build the exhibitions it feeds — run the accession/deaccession ethics gate (AAM/AAMD; deaccession proceeds fund collection care/acquisition only), cataloging, provenance & NAGPRA due diligence, condition reporting, loans in/out, insurance/valuation, storage & environmental controls, the collections-CMS fit (TMS/Axiell/PastPerfect/CollectionSpace), and the exhibition project lifecycle (concept → checklist & loans → interpretation → budget → schedule → install/condition → evaluation). Reach for this when the user asks "should we accession/deaccession this?", "run the provenance/NAGPRA due diligence", "TMS vs Axiell vs PastPerfect vs CollectionSpace?", or "plan this temporary/traveling exhibition". Used by `collections-and-engagement-specialist` (primary).
---

# Skill: manage-collections-and-exhibitions

> **Invoked by:** `collections-and-engagement-specialist` (primary). Also consulted by `museum-operations-lead` for the earned-revenue/budget side of an exhibition.
>
> **When to invoke:** "Should we accession/deaccession this?"; "run the provenance / NAGPRA due diligence"; "which collections CMS?"; "plan this exhibition"; "arrange this loan in/out"; any move on the collection or its exhibitions.
>
> **Output:** an ethics-gated collections call (or an exhibition project plan) with provenance/NAGPRA cleared, cataloging/condition/insurance addressed, the CMS fit named, and the seams to the operations-lead and adjacent plugins stated.

## Procedure

1. **Run the ethics/provenance gate FIRST.** Traverse [`../../knowledge/museum-operations-decision-tree.md`](../../knowledge/museum-operations-decision-tree.md) Tree A. For an **accession/loan/acquisition**: is provenance established (1970-UNESCO import history, Nazi-era 1933–45 gap, legal title)? Is the object NAGPRA/culturally-sensitive? A red flag **holds** the transaction. For a **deaccession**: proceeds fund **collection care/acquisition only** (AAM/AAMD) — funding operations/a deficit/a capital project is a hard STOP; then confirm collections-policy compliance + board approval.
2. **Catalog to a standard.** Object ID, accession number, medium/dimensions, provenance chain, rights, current location — captured in the CMS, not a spreadsheet. This record is the substrate for loans, exhibitions, and digital access.
3. **Protect the object.** Condition-report at every transfer (loan, storage move, install); confirm environmental controls (temp, RH, light, IPM); set insurance valuation and wall-to-wall coverage for loans. Name any gap as a conservation/liability risk.
4. **Fit the CMS to the collection** (if that's the question). Traverse Tree C: collection size, staff capacity, budget, open-source-vs-vendor → TMS / Axiell / PastPerfect / CollectionSpace — and include the **data-migration cost** as part of the decision (it's a decade-long commitment).
5. **Run the exhibition as a project** (if that's the question). Use [`../../templates/exhibition-project-plan.md`](../../templates/exhibition-project-plan.md): concept & feasibility → object checklist & loan requests (12–24-month lead times) → interpretation/labels/accessibility → budget (earned + contributed, *with* the operations-lead) → critical-path schedule → install & condition sign-off → run/program → de-install & **evaluation**.
6. **State the seams and flip conditions.** Earned-revenue/budget → `museum-operations-lead`; event *production* → `event-management`; grant *lifecycle* → `grants-management`. Name the 1-2 facts that would change the call.

## Worked example

> User: "A donor wants to gift us a 4th-century vase, and separately we're thinking of deaccessioning three duplicate prints to cover this year's deficit. Advice?"

- **The vase (accession):** ethics gate first — a 4th-century antiquity triggers the **1970-UNESCO** check. Ownership/export history back to 1970? If there's a gap → **HOLD**: research provenance before accepting; an unprovenanced antiquity is a looting/repatriation risk. If clean → accept, catalog, condition-report, insure, storage plan.
- **The prints (deaccession):** **STOP.** Deaccessioning to cover an operating deficit is an AAM/AAMD violation — proceeds are restricted to collection care/acquisition. The deficit is solved on the operating side (route to `museum-operations-lead`). If the prints are genuinely out-of-scope, deaccession *is* permissible, but the proceeds must be ring-fenced for acquisition/care, with board approval and a documented rationale.
- **Seam:** the deficit itself → `museum-operations-lead`; if a grant could fund the acquisition of a better example → `grants-management`.

## Guardrails

- The ethics/provenance gate runs **before** any recommendation — never accession/loan/acquire on hope, never deaccession to fund operations.
- NAGPRA/cultural-patrimony obligations are consulted, not skipped — consent before display/publish.
- Condition-report at **every** transfer; a loan without insurance/valuation is a liability.
- A CMS is chosen on collection size/budget/staff **and migration cost** — never on a demo.
- The exhibition budget is built *with* the operations-lead (earned + contributed) — this skill owns the content, not the revenue target.
- Volatile standards (AAM/AAMD/ICOM/NAGPRA wording) and CMS pricing/features carry a **retrieval date** and are re-verified before a board commitment. See [`../../knowledge/museum-operations-patterns-2026.md`](../../knowledge/museum-operations-patterns-2026.md).
