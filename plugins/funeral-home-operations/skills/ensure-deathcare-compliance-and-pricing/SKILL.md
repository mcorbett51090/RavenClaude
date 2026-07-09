---
name: ensure-deathcare-compliance-and-pricing
description: Audit a funeral home's pricing and disclosures against the FTC Funeral Rule and clear the cremation-authorization and vital-records gates. Check the General Price List, Casket Price List, and Outer Burial Container list for required disclosures and itemization (no forced packages, embalming-not-required, telephone-price disclosure, no misrepresentation); confirm the cremation authorizing agent, positive ID, written authorization, and unbroken chain-of-custody before any irreversible step; and sequence the death certificate, certification, and disposition permits. Reach for this when the user asks "is our GPL compliant?", "what authorizes a cremation?", or "what vital records/permits do we need?". Used by `funeral-arrangement-and-compliance-specialist` (primary). Not legal advice — verify the current Rule + state law with counsel.
---

# Skill: ensure-deathcare-compliance-and-pricing

> **Invoked by:** `funeral-arrangement-and-compliance-specialist` (primary). Also consulted by `funeral-operations-lead` to confirm an operational change (a new package, a pre-need push) doesn't collide with the Funeral Rule.
>
> **When to invoke:** "Is our General Price List Funeral-Rule compliant?"; "which disclosures do we owe and when?"; "what authorizes a cremation and keeps custody airtight?"; "what vital records and permits do we need, in what order?"; any audit of pricing, disclosures, authorization, or vital records.
>
> **Output:** a Funeral-Rule pricing/disclosure audit (each gap named + a fix), the cremation authorization + positive-ID + chain-of-custody clearance, and the vital-records/permit sequence — **with every volatile jurisdiction-specific and Funeral-Rule item carrying a retrieval date, a re-verify step, and a "not legal advice — confirm with counsel + the licensing board" marker.**

## Procedure

1. **Traverse the compliance decision tree first.** Use [`../../knowledge/deathcare-compliance-decision-tree.md`](../../knowledge/deathcare-compliance-decision-tree.md): at-need vs pre-need → disposition → which price lists and disclosures fire → authorization & permits. Don't pattern-match a requirement to the request.
2. **Audit the price lists against the Funeral Rule structure.** Walk [`../../templates/general-price-list-checklist.md`](../../templates/general-price-list-checklist.md): the **General Price List** (itemized individual goods & services + required disclosures), the **Casket Price List**, and the **Outer Burial Container list**. Check itemization, the required disclosure lines, and that no item the law lets a family decline is bundled as a condition of another.
3. **Confirm the disclosure moments.** GPL given to anyone asking in person about arrangements/prices; CPL and OBC list before showing those items; the **telephone price disclosure** on a price call; the **embalming-not-required** disclosure and the **no-misrepresentation** rule throughout. Name any missing or mistimed disclosure as a gap with a fix.
4. **Clear the cremation authorization gate before any irreversible step.** For cremation (and alkaline hydrolysis), confirm **all** of: the correct **authorizing agent** (statutory priority — state-specific, verify), **positive identification**, **written authorization**, an unbroken **chain-of-custody / tracking**, and **no commingling**. If any element is missing → **STOP**; an irreversible step never proceeds on an incomplete authorization.
5. **Sequence the vital records and permits.** Death-certificate data + physician/ME certification → filing with the registrar within the deadline → the burial/cremation/transit **permit** → certified copies for the family. Note that deadlines, forms, and the certifier of record are jurisdiction-specific.
6. **Document the compliance record.** The itemized statement of goods & services, the disclosures given and when, and the signed authorizations — the record is both the compliance proof and the family's clarity.
7. **Mark every volatile item.** Flag each Funeral-Rule-revision, state-licensing, and permit-deadline item with a **retrieval date**, a **re-verify** instruction, and the **"not legal advice — confirm with counsel + the licensing board"** marker.

## Worked example

> User: "Review our General Price List — is it Funeral-Rule compliant? We also do cremations."

- **Tree:** at-need → both burial and cremation paths → GPL + CPL + OBC list in scope; cremation adds the authorization gate.
- **GPL audit:** itemization present, but the **embalming-not-required disclosure** is missing and "basic services of funeral director and staff" is bundled into two packages *without* the individual-selection option — both are gaps. Fix: add the required disclosure lines; unbundle so a family can decline any item the law allows.
- **CPL/OBC:** CPL present; the OBC list implies a container is required for cremation — a **misrepresentation** gap. Fix: state that cremation generally needs no outer burial container.
- **Cremation gate:** confirm the authorizing agent (verify your state's priority order), positive ID, written authorization, chain-of-custody, and no commingling before any cremation proceeds.
- **Vital records:** death-cert filing + certification → cremation permit → certified copies; note the state filing deadline.
- **Marking:** every Rule-specific and state-specific line flagged — retrieved 2026-07-09, **re-verify against the current FTC Funeral Rule + state law with counsel; not legal advice.**

## Guardrails

- Traverse the compliance tree before auditing — structure before line-item.
- Itemization + no forced packages + embalming-not-required + no misrepresentation are the non-negotiable Rule checks; name each gap with a fix.
- The cremation authorization + positive-ID + chain-of-custody gate must clear **before** the irreversible step — any missing element is a hard STOP.
- Match the requirement set to the disposition; cremation needs no outer burial container — don't imply otherwise.
- Vital-records deadlines, permit forms, and authorizing-agent priority are **jurisdiction-specific and volatile** — carry a retrieval date and re-verify.
- **Not legal advice.** Every Funeral-Rule-revision and state-law item is confirmed with counsel + the licensing board before reliance. See [`../../knowledge/deathcare-compliance-decision-tree.md`](../../knowledge/deathcare-compliance-decision-tree.md).
