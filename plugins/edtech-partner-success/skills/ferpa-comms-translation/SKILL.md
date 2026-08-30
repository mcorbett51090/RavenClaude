---
name: ferpa-comms-translation
description: "Reshape a partner communication into a FERPA-safe, audience-appropriate message — classify the data bucket, screen the small-cohort residual, reshape per audience, treat each language as a redesign. Used by ferpa-comms-translator and by any PSM drafting parent/admin/leadership copy. NOT advocacy quotes (that's advocacy-program-design) and NOT a legal opinion."
---

# Skill: ferpa-comms-translation

> **Invoked by:** `ferpa-comms-translator` (primary), `edtech-partner-success-manager` (partner-facing copy), `qbr-composer` (school/district decks, especially non-English-primary), `partner-profile-curator` (partner terminology).
>
> **When to invoke:** turning a PSM-to-partner message into a parent / family / student / admin-facing comm, or producing a multilingual variant. NOT for internal analytics, QBR composition, or case-study quotes (route quotes to `advocacy-program-design`).
>
> **Output:** audience-shaped draft + flagged privacy concerns + multilingual variants when Title VI applies + named reviewer. Keep every example generic — no real student data.

The slash command `/edtech-partner-success:translate-ferpa-safe-comms` is the same playbook on the user surface. This file is what other agents auto-load.

Legal matrices stay in knowledge. This skill is the procedure.

## Flow

1. **Name the audience before drafting.** Parents, school admins, district leadership, and students are four rooms. Primary language? grade-band? K-12 vs higher-ed (rights-holder shift)? Underspecified audience = underperforming comms.

2. **Classify the data into its FERPA bucket** ([`ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md`](../../best-practices/ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md)): education records (protected), PII (protected), or directory information (disclosable *only* if the district designated that category and the parent hasn't opted out). Designations vary district to district — don't assume.

3. **Screen for the small-cohort residual** ([`screen-parent-comms-for-the-cohort-residual.md`](../../best-practices/screen-parent-comms-for-the-cohort-residual.md)): "the 3 students who chose option B" names nobody directly but identifies them. De-identification is a claim you earn against the residual, not assert. Field rule of thumb lives in [`parent-comms-jurisdictional-bear-traps.md`](../../knowledge/parent-comms-jurisdictional-bear-traps.md) — read it before any parent/family/student-facing draft.

4. **Reshape per audience, don't re-send verbatim.** One ask. Read-aloud test for parents. Strip PSM jargon. Don't make parents the firewall.

5. **Treat each language as a re-design, not a re-render** ([`ferpa-treat-each-language-variant-as-a-redesign-not-a-translation.md`](../../best-practices/ferpa-treat-each-language-variant-as-a-redesign-not-a-translation.md)). Native-speaker review for anything legal-bearing. `[verify-at-build — Title VI LEP obligations and FERPA de-identification specifics are regulatory; confirm current guidance]`

6. **Pre-send checklist** (all six, from the translator agent):
   1. Does the comm name a number / small cohort?
   2. Is the denominator small enough to identify the missing or named?
   3. Does it name a category that itself is identifying (program participation, intervention status)?
   4. Is anything claimed that the district hasn't formally disclosed as directory information?
   5. Does it assume parental rights in a higher-ed context?
   6. Does it trigger any state-specific requirement (CA SOPIPA/CCPA, IL SOPPA, NY Ed Law 2-d, CT, CO, TX, …)?

7. **Name who reviewed it.** "FERPA-compliant" without a named reviewer is an anti-pattern.

8. **Escalate any genuine privacy/PII verdict** to `ravenclaude-core/security-reviewer`. This plugin supplies the domain screen, not the legal sign-off.

## What this skill does NOT cover

- Case-study / advocacy quotes and consent ladders → `advocacy-program-design`
- Partner terminology (named programs, contacts) → `partner-profile-curator`
- Legal opinion on whether a disclosure is FERPA-compliant → counsel via `security-reviewer`
- State-by-state matrices → [`parent-comms-jurisdictional-bear-traps.md`](../../knowledge/parent-comms-jurisdictional-bear-traps.md)

## References

- Knowledge: [`../../knowledge/parent-comms-jurisdictional-bear-traps.md`](../../knowledge/parent-comms-jurisdictional-bear-traps.md)
- Command (same playbook, user-invoked): [`../../commands/translate-ferpa-safe-comms.md`](../../commands/translate-ferpa-safe-comms.md)
- Advocacy quotes: [`../advocacy-program-design/SKILL.md`](../advocacy-program-design/SKILL.md)
