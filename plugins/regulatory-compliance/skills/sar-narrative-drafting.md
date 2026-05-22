---
name: sar-narrative-drafting
description: Draft SAR / STR narratives that survive regulator review — typology + the W's + what to omit + reviewer sign-off chain. Used by `aml-kyc-analyst` (primary). Confidentiality class always at least client-confidential; often regulator-only.
---

# Skill: sar-narrative-drafting

**Purpose:** Draft SAR (Suspicious Activity Report) / STR (Suspicious Transaction Report) narratives that survive regulator (FinCEN, FIU, equivalent) review. Used by `aml-kyc-analyst` (primary).

## When to use

- Drafting a SAR / STR for filing
- Reviewing a SAR / STR drafted by a junior analyst
- Continuing-activity reports on a previously filed case
- Training a team on SAR narrative quality

## Important confidentiality note

**SAR / STR content is regulator-only.** It must not leave the secure environment, must not be shared with the subject customer, must not appear in any general-purpose committed file. The plugin's [`hooks/scrub-confidential-pre-write.sh`](../hooks/scrub-confidential-pre-write.sh) is one defensive layer; treat the agent's working directory itself as restricted. **For SAR / STR drafting, flip the hook from `exit 0` to `exit 1` (blocking).**

## The shape of a strong narrative

A SAR narrative answers the W's, plus the *why*:

- **Who** — the subject (full identifying details per FinCEN's structured fields; in the narrative, name them clearly).
- **What** — the suspicious activity: transactions, accounts, instruments, amounts.
- **When** — dates / range; chronology if pattern matters.
- **Where** — locations: bank branches, geographies, counterparty jurisdictions.
- **Why suspicious** — the typology: the pattern that raises the suspicion. *This is the load-bearing part.*
- **How** — mechanics: how the activity was structured.

## The typology is the answer

A strong narrative names the typology (the recognized pattern that makes the activity suspicious). Common typologies:

- **Structuring (cuckoo smurfing / classic structuring)** — splitting transactions to evade reporting thresholds
- **Layering** — moving funds through multiple accounts / entities to obscure source
- **Trade-based money laundering** — over/under-invoicing, phantom shipments, multiple invoicing
- **Funnel accounts** — deposits in many locations, withdrawals in one
- **Mirror trading** — paired buy/sell across jurisdictions
- **Pass-through / shell-entity layering** — beneficial-ownership opacity
- **Cash-intensive business inconsistency** — declared business doesn't match deposit pattern
- **Round-tripping** — funds out and back through an unrelated jurisdiction
- **Politically Exposed Person (PEP) atypical activity** — activity inconsistent with declared profile

Naming the typology elevates the narrative from "unusual" to "matches a recognized pattern of [typology]."

## What to include

1. **Opening sentence:** "This SAR is being filed to report [typology shorthand] activity by [subject], involving [amount] across [period]."
2. **Subject identification:** full identifying details (name, DOB, address, account numbers, etc.) — these usually go in structured fields, but the narrative references them clearly.
3. **Chronology:** dated bullet list of the activity (start with the earliest related activity, even if pre-suspicion).
4. **The typology — *why* this is suspicious:** the pattern, with reasoning, with reference to specific behaviors / amounts / counterparties.
5. **Customer context:** declared business / SoF / SoW, why the observed activity is inconsistent.
6. **Prior reporting:** is this a continuing-activity report? Reference prior SAR / STR ID.
7. **Investigation steps taken:** internal review, sources consulted, parties interviewed.
8. **Status of relationship:** maintained / restricted / exited.
9. **Closing sentence:** "Filing is intended to alert [regulator/FIU] to the above and is not a determination that any illegality has occurred."

## What to omit

- **Speculation about ultimate criminal use.** Report observed facts; don't allege specific crimes.
- **Editorial language.** No "obviously suspicious", "clearly a scam", "must be money laundering." Just the facts and the typology.
- **Information about other customers** unless directly related and necessary.
- **Internal opinions / disagreements.** The narrative is a single firm position.
- **Subject tipping language.** Standard discipline; the subject must not learn the SAR was filed.

## Continuing-activity reports

If the pattern persists past a prior SAR:

- Reference the prior SAR ID in the opening.
- Summarize what's *new* — don't re-litigate the prior report.
- Update on relationship status (still open? Restricted? Exited?).

Cadence: most regulators expect continuing reports if pattern persists past 90 days from the prior SAR.

## Quality check before filing

- [ ] Typology named explicitly
- [ ] Chronology dated and complete
- [ ] Subject identifying details accurate (cross-check with KYC file)
- [ ] No speculation about criminal-law violations
- [ ] No tipping content
- [ ] Maker-checker sign-off recorded
- [ ] Filing within statutory deadline (often 30 days from detection; check the specific regime)

## Anti-patterns

- "Customer wired $X to a high-risk jurisdiction" with no typology named — describes activity, doesn't explain suspicion
- Narrative that asserts criminal intent
- Narrative shared in a generic ticketing system with no access control
- "Will continue to monitor" — meaningless closer; just file the report
- Continuing-activity report that re-narrates the prior case
- Long narratives that bury the key fact — FinCEN's published guidance favors clarity over thoroughness

## See also

- Skill: [`./aml-program-review.md`](./aml-program-review.md)
- Template: [`../templates/sar-narrative-template.md`](../templates/sar-narrative-template.md)
- Agent: [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)
