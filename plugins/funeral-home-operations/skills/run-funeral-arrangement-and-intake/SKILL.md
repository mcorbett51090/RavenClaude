---
name: run-funeral-arrangement-and-intake
description: Run a grief-aware, FTC-Funeral-Rule-compliant arrangement — from first-call intake through the arrangement conference to documented, itemized selections and disposition. Traverse the deathcare-compliance decision tree so the right disclosures (GPL, CPL, Outer Burial Container list, telephone-price, embalming-not-required, no-misrepresentation) are given at the right moment, itemize without forcing a package, select the disposition and its requirements, and capture it in the arrangement worksheet. Reach for this when the user asks "walk me through the arrangement conference", "how do we handle a first call", or "arrange this service correctly". Used by `funeral-arrangement-and-compliance-specialist` (primary). Not legal advice — verify jurisdiction-specific items with counsel.
---

# Skill: run-funeral-arrangement-and-intake

> **Invoked by:** `funeral-arrangement-and-compliance-specialist` (primary). Also consulted by `funeral-operations-lead` to frame first-call intake before routing the conference.
>
> **When to invoke:** "Walk me through the arrangement conference"; "how should we handle a first call?"; "arrange this service correctly + compliantly"; any move from a death notification to a documented, itemized arrangement.
>
> **Output:** a grief-aware, itemized arrangement — first-call intake captured, the Funeral Rule disclosures given at the right moment, the disposition and its requirements selected, and everything documented in the arrangement worksheet. **Not legal advice — jurisdiction-specific items verified with counsel.**

## Procedure

1. **Handle the first call as the relationship, not a data-entry step.** Capture decedent + informant data, the location of the decedent, and the immediate need (removal now?), with a grief-aware tone — this call sets whether the family stays. Dispatch the removal/transfer; confirm any time-sensitive constraints (religious timelines, ME hold, out-of-state transport).
2. **Traverse the compliance decision tree before pricing anything.** Use [`../../knowledge/deathcare-compliance-decision-tree.md`](../../knowledge/deathcare-compliance-decision-tree.md): at-need vs pre-need → disposition → which price lists and disclosures fire. Don't pattern-match a form to the request.
3. **Give the General Price List at the start of the in-person arrangement discussion** — and the Casket Price List and Outer Burial Container list before showing those items. On a phone inquiry, give the telephone price disclosure. These are given *unprompted*, at the right moment.
4. **Give the embalming-not-required disclosure and never misrepresent a legal requirement.** Embalming is rarely legally required; offer refrigeration / a closed timeline as the alternative. State plainly what is and isn't required.
5. **Select the disposition and apply its own requirement set.** Burial, cremation, alkaline hydrolysis, or green/natural burial each carry different merchandise, permits, and disclosures (and, for cremation/hydrolysis, the authorization path). Don't apply a burial checklist to a green-burial family.
6. **Itemize; never force a package.** Walk the family through services (visitation, funeral, memorial, graveside, celebrant) and merchandise (casket, urn, vault/outer container) as individual selections — a family may buy only what it wants and decline any item the law lets it decline.
7. **Document everything in the worksheet.** Capture selections, the disclosures given (with when), the disposition, and the authorizations in [`../../templates/at-need-arrangement-worksheet.md`](../../templates/at-need-arrangement-worksheet.md). For cremation, route to the authorization/custody gate in [`ensure-deathcare-compliance-and-pricing`](../ensure-deathcare-compliance-and-pricing/SKILL.md). Confirm fulfillability on the practice's capacity with [`manage-case-logistics-and-fulfillment`](../manage-case-logistics-and-fulfillment/SKILL.md) before committing a service date.

## Worked example

> User: "A family just called — their father died at home overnight. Walk me through arranging this as a cremation with a memorial service."

- **First call:** capture decedent/informant data and the home location; dispatch the removal now; confirm no ME involvement and any family timeline. Grief-aware tone throughout — this is the relationship's first impression.
- **Tree:** at-need → **cremation** → CPL / alternative-container price info fires; **no** outer burial container needed (say so); embalming-not-required disclosure given (a memorial-with-cremation rarely needs it); cremation authorization path opens.
- **Disclosures:** GPL given at the start of the in-person conference; CPL before showing containers; embalming-not-required stated.
- **Itemize:** the memorial service, celebrant, cremation, an urn, and a life-tribute video — each a separate selection, nothing forced as a package. The family declines a viewing casket (rental/alternative container instead) — honored.
- **Disposition requirements:** cremation permit + the **authorization + positive-ID + chain-of-custody** gate (→ compliance skill) before the irreversible step.
- **Document:** all selections + disclosures-given timestamps + the pending authorization captured in the arrangement worksheet.

## Guardrails

- Traverse the compliance tree **before** any pricing or disposition step — structure before form.
- The GPL is given to anyone asking about arrangements/prices in person; never withheld or delayed.
- Itemize — no forced packages; a family may decline any item the law lets it decline.
- The embalming-not-required disclosure is non-negotiable; never present embalming as mandatory when it isn't.
- Match the requirement set to the disposition — never one generic form for burial, cremation, aquamation, and green burial.
- For cremation/hydrolysis, the **authorization + positive-ID + chain-of-custody** gate must clear before the irreversible step — route to [`ensure-deathcare-compliance-and-pricing`](../ensure-deathcare-compliance-and-pricing/SKILL.md).
- **Not legal advice** — jurisdiction-specific permits, deadlines, and the current Funeral Rule text carry a retrieval date and are confirmed with counsel + the licensing board. See [`../../knowledge/deathcare-compliance-decision-tree.md`](../../knowledge/deathcare-compliance-decision-tree.md).
