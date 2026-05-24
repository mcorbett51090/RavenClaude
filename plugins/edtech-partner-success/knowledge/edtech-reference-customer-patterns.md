# EdTech reference-customer patterns — anonymization, consent, state-law variance

> **Last reviewed:** 2026-05-21. Status: pre-engagement-draft (no live K-12 advocacy program operating against this file yet; refresh on first real engagement signal via `/wrap`). Sources: FERPA / 34 CFR Part 99 (already referenced in [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md)), state-specific media-release rules (CA Education Code, NY Ed Law §2-d guidance, IL SOPPA, district-level photo / media release conventions), practitioner synthesis from EdTech vendor marketing programs. Refresh when: (a) FERPA / COPPA materially changes (e.g., a new amendment cycle), (b) a state media-release rule changes substantially, or (c) live engagement scenarios surface patterns this file doesn't cover.

This file is the **why-behind-the-anonymization-decision** for the advocacy program. The [`../skills/advocacy-program-design/SKILL.md`](../skills/advocacy-program-design/SKILL.md) skill consults this file before any case-study or reference ask. The [`../templates/case-study-draft.md`](../templates/case-study-draft.md) template uses these patterns in its pre-publication checklist.

## 1. The three-bucket anonymization model

Every reference-customer artifact falls into one of three buckets. Decide at the start; don't try to change buckets mid-process.

| Bucket | What can appear | Use when | District legal-review timeline (typical) |
|---|---|---|---|
| **A. Full attribution** | District name + named role (e.g., "Curriculum Director Jane Smith, Maple County USD") | Top-quartile partner + state allows district-personnel attribution + champion + their supervisor both sign off | 2-6 weeks (CA, NY, IL slower; TX, FL faster) |
| **B. District-only attribution** | District name + role only (e.g., "Curriculum Director, Maple County USD") | Most common bucket; champion willing but doesn't want personal name on it | 1-3 weeks |
| **C. Fully anonymous** | Generic descriptor (e.g., "a mid-sized K-12 district in the Pacific Northwest") | State media-release rule restricts attribution + or partner's policy is to never appear in vendor marketing | 0-1 week (faster because nothing to legal-review against) |

**The bucket is not the partner's preference alone.** It's the partner's preference + the state's media-release law + the district-internal policy. A partner can WANT full attribution and still need to use district-only because the state rule restricts it.

## 2. State-by-state variance (high-load-bearing states)

Cross-reference with the broader regulatory typology in [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md). What's specific to advocacy / reference-customer programs:

### California
- District-personnel attribution requires district-internal sign-off (not just personal sign-off)
- Student quotes require parental consent for under-18; under SOPIPA, vendor cannot solicit student PII for marketing under any circumstances
- District photos / video may require additional release per district policy

### New York (Ed Law §2-d state)
- District-level data-protection rider must remain in place even for advocacy purposes
- Student photos / video / quotes require parental consent + the data-protection rider does NOT cover marketing use; that's a separate consent
- District-personnel attribution: usually allowed with district sign-off

### Illinois (SOPPA state)
- District publishes a list of vendor contracts publicly; any new data-handling around marketing (e.g., a case study using student outcome data) re-triggers public disclosure
- District-personnel attribution: usually allowed with district sign-off

### Texas
- District-personnel attribution generally allowed
- Less restrictive media-release framework than CA / NY / IL
- Outcome data (e.g., assessment scores) requires district sign-off but rarely state-level review

### Florida
- District-personnel attribution generally allowed
- Recent state-level consent requirements around "controversial concepts" in education materials may extend to vendor case-study claims that touch curriculum content; be cautious with politically-fraught topic areas

### District-policy variance (not state-driven)

Some districts have **internal** policies stricter than the state default:
- Some districts have a blanket "no vendor case-study attribution" policy
- Some require all media-release-bearing content to go through the superintendent's office regardless of state framework
- Some require pre-publication review by the school board for any district-attributed content

**Implication:** check both state-law AND district-internal-policy before drafting. The partner's champion may know one but not the other.

## 3. The FERPA overlay for student / parent quotes

Quotes from students or parents are functionally always more fraught than quotes from district employees. The rules:

### Under-18 students

- **Parental consent required** for any quote that goes beyond district-designated directory information (per [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md) FERPA three-bucket model)
- Directory-info designation is district-specific — what's directory info in District A may not be in District B
- Consent must be specific to the use: "consent to be quoted in vendor marketing" is NOT covered by general district consent forms
- **Documented consent on file** is required; "the parent said it was OK in an email" is insufficient

### Parents (as parents, not as student-quote-proxies)

- A parent quoting *their own opinion* about the product is generally fine without student-level FERPA concern
- But the parent's quote should not include the student's name, grade, school, or specific outcomes unless that's been separately consented
- "My daughter loves the product" generic + first-name-only is usually OK; "my daughter at Maple Elementary improved from 67% to 93% in 4 months" requires explicit parental + district sign-off because it includes outcome data

### Teacher / admin / district staff quotes

- District-employee-as-employee quotes are generally lower-friction
- BUT: some districts treat any media-bearing attribution as a personnel matter requiring HR / superintendent sign-off
- Confirm the district's specific policy, not just the state framework

## 4. Parent-consent collection patterns (when student/parent quotes are needed)

If a case study genuinely needs a student or parent quote, the consent-collection process:

1. **Identify the candidate quote source via the champion** (the curriculum director or principal — not the vendor approaching the parent directly)
2. **District sends the consent request** using the district's existing parental-consent infrastructure (translates per Title VI multilingual rules — see [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md))
3. **Consent is specific** — for THIS quote, for THIS purpose (vendor marketing), with explicit language about what gets published
4. **The vendor never has direct contact with the parent for consent purposes**
5. **Documentation is retained** by the district + a copy provided to the vendor for the case-study file

This is 3-6 weeks of process for a single quote. Usually the right answer is **use a teacher / admin quote instead**.

## 5. Sub-processor + AI-feature disclosure overlay

Post April 22, 2026 COPPA full enforcement (see [`ai-in-edtech-2026.md`](ai-in-edtech-2026.md)), a reference-customer artifact has a new overlay:

- If the case study mentions AI features, the sub-processor list at the time of publication should be the current one (not the one from the partner's original contract)
- AI-training claims need to be consistent with the COPPA-amended consent posture — saying "the AI learned from our partner's data" without separate opt-in consent is now a problem
- For under-13 student data: AI-training under-13 data is now a separate-consent matter; advocacy claims that imply otherwise are FTC-violation territory ($51,744/violation/day penalties)

## 6. The 2-asks-per-year ceiling

Beyond the legal / consent layer, there's a relationship layer: partners get fatigued by advocacy asks. The norm:

- **2 asks per year per partner** for most partners
- Asks should **step up gradually** — first ask = quote, second = case study or speaker, not just two case studies in a row
- A third ask in a year is the threshold for renegotiating the relationship — the partner is now a marketing asset, not a customer
- **Withdraw from the pipeline during recovery** — any partner with red-health is off-limits for advocacy asks until they're stable

## 7. Anonymization-by-state quick-decision matrix

When the PSM (or `success-playbook-designer` authoring an advocacy play) needs a quick decision:

| Partner state | Default anonymization bucket | Champion-attribution OK? |
|---|---|---|
| CA | District-only (Bucket B) | Only with district-personnel-attribution sign-off (rare to obtain quickly) |
| NY | District-only (Bucket B) | Yes with district sign-off |
| IL | District-only (Bucket B); re-disclosure trigger | Yes with district sign-off |
| CT | District-only (Bucket B) | Yes with district sign-off |
| TX | Full attribution (Bucket A) | Yes — generally lower friction |
| FL | Full attribution (Bucket A) | Yes; check for content-policy overlap |
| Most other states | Full attribution (Bucket A) default | Yes with champion + supervisor sign-off |

**Always verify against current district-internal policy** — the state default doesn't override a stricter district policy.

## 8. Anti-patterns this file flags

- **Asking a partner for advocacy during active renewal negotiation.** Conflates the relationship; the partner may say yes to keep the renewal smooth and resent it later.
- **Using student outcome data in a case study without district sign-off on the specific data points.** Outcomes are usually sensitive even when individual students aren't named.
- **Reusing the same case study after the partner's relevant champion has left.** The story is now stale and may misrepresent the partner's current state.
- **Quoting a teacher who's no longer at the district.** Even if the quote was given while they were employed there, post-departure attribution can violate district policy.
- **Implying outcomes the partner hasn't actually claimed.** Reference customers tolerate accurate stories; they don't tolerate vendor-side embellishment.
- **State-default attribution without checking district policy.** Texas allows district-personnel attribution but THIS Texas district may have an internal "no vendor marketing" policy.

## 9. Refresh triggers

- FERPA, COPPA, or state student-privacy law materially changes (specifically around consent-for-marketing-use)
- A state-level media-release rule changes (rare; California's the most likely to evolve)
- Live engagement scenarios surface patterns this file doesn't cover (`/wrap` slash command)
- A district-policy-stricter-than-state-law pattern surfaces that this file's matrix should warn about
- The 2-asks-per-year ceiling stops matching observed partner-fatigue patterns

## 10. References

- [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md) — FERPA + state student-privacy framework (this file builds on it)
- [`ai-in-edtech-2026.md`](ai-in-edtech-2026.md) — COPPA-amended consent posture for AI-feature claims in case studies
- [`../skills/advocacy-program-design/SKILL.md`](../skills/advocacy-program-design/SKILL.md) — the playbook this knowledge serves
- [`../templates/case-study-draft.md`](../templates/case-study-draft.md) — the artifact whose pre-publication checklist uses these patterns
- [`../templates/reference-pipeline-tracker.md`](../templates/reference-pipeline-tracker.md) — the per-partner status board
