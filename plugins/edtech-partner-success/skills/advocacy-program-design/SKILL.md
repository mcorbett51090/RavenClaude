---
name: advocacy-program-design
description: Design a structured EdTech advocacy program with 5-tier ladder (logo → quote → case study → speaker → peer call). Health-score eligibility gate (top-quartile only), 2-asks-per-year ceiling, state-by-state anonymization overlay (CA/NY/IL stricter; TX/FL more permissive), FERPA consent for student/parent quotes. Used by `success-playbook-designer` + `ferpa-comms-translator` + `edtech-partner-success-manager`.
---

# Skill: advocacy-program-design

> **Invoked by:** `success-playbook-designer` (when authoring an advocacy play), `ferpa-comms-translator` (when writing partner-facing content), `edtech-partner-success-manager` (when handling Marketing's "got anyone for a case study?" ping), `ravenclaude-core/documentarian` (when drafting case-study content).
>
> **When to invoke:** any time the work is "turn a partner's success into a marketable / referenceable artifact." Case studies, references, testimonials, speaker programs, peer-to-peer connections, advocacy event design.
>
> **Output:** a partner-segment-appropriate advocacy plan (or single advocacy artifact) that has passed the FERPA / district-legal-review / consent / state-media-release checks before publication.

## The advocacy-program shape

An advocacy program isn't a list of case studies — it's a **structured pipeline** with tiers, governance, and partner-asks-per-year ceilings. Skip the structure and the program degenerates into "we ask the loudest champion for whatever Marketing needs this quarter."

### Tier 1 — Logo + private use

- Partner allows their name/logo to appear on the vendor's customer page
- No content (no quote, no story)
- Lowest-friction ask; most partners will agree

### Tier 2 — Public attributed quote

- Partner allows a short (1-2 sentence) quote with district + named role attribution
- Quote sourced from real partner correspondence (paraphrased + approved)
- Usually 1-2 week district-legal-review turnaround

### Tier 3 — Full case study

- District-attributed or anonymized depending on state-law + partner preference
- See [`../../templates/case-study-draft.md`](../../templates/case-study-draft.md) for the artifact shape
- 4-12 week timeline for K-12 (depending on district legal-review timeline + state-specific media-release rules)

### Tier 4 — Speaker program

- Partner agrees to speak at a vendor event (webinar, conference, customer summit)
- Requires confidence that the partner can carry the narrative in real-time + answer prospect questions
- Highest-effort ask; reserve for top-quartile partners with strong champion redundancy

### Tier 5 — Peer-to-peer reference calls (with prospects)

- Partner agrees to be available for 30-minute calls with prospects evaluating the product
- Highest leverage for sales but heaviest ongoing time-burden on the partner
- Cap at 2-3 calls per year per partner

## The flow

When invoked, the agent should:

1. **Confirm the trigger** — what's the advocacy ask? (Marketing wants a case study / Sales wants a reference / Conference needs a speaker / etc.)
2. **Health-score filter** — only top-quartile-health partners are eligible. Bottom-quartile partners are explicitly excluded (their story is unstable + the ask burns goodwill they don't have). See [`partner-health-scoring.md`](../partner-health-scoring/SKILL.md).
3. **Pipeline check** — consult [`../templates/reference-pipeline-tracker.md`](../../templates/reference-pipeline-tracker.md). Has the partner already been asked recently? (2-asks-per-year ceiling for most.)
4. **Match topic to strength** — what is THIS partner uniquely best positioned to speak to? Feature X they got value from? Specific use case? Segment-shaped story? Generic-happy-customer is the wrong reason to pick a reference.
5. **State-law overlay** — per [`../knowledge/edtech-reference-customer-patterns.md`](../../knowledge/edtech-reference-customer-patterns.md), confirm the partner's state allows the attribution level the ask requires. Some states (CA, NY, IL) have stricter district-personnel media-release rules than others.
6. **FERPA overlay** (when student/parent quotes are involved) — under-18 quotes require parental consent for anything beyond directory-info; see [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../../knowledge/parent-comms-jurisdictional-bear-traps.md). If consent is heavy, swap to a teacher or admin quote.
7. **Draft the artifact** using the appropriate template (case-study-draft.md, etc.).
8. **Run the pre-publication checklist** built into the artifact template.
9. **Update the pipeline tracker** with the new ask + status.

## The mandatory pre-publication checks

Before any advocacy artifact ships externally:

- [ ] **District legal review complete** (or explicitly waived in writing by the named district decision-maker)
- [ ] **Named-individual sign-off** for every quote (role + name on file)
- [ ] **State media-release rule** checked (per knowledge file)
- [ ] **No student PII** beyond directory-info designation
- [ ] **Numbers sourced** (every claim has a data range)
- [ ] **AI-feature claims** consistent with current COPPA-amended consent posture (post April 22 2026)
- [ ] **Sub-processor disclosure** still matches current vendor-side list

## Anti-patterns this skill flags

- **Defaulting to the loudest champion** instead of matching topic-to-strength. The most-vocal partner isn't always the right reference.
- **Asking bottom-quartile-health partners for advocacy.** Their story is unstable; the ask burns goodwill they need for their own recovery.
- **Skipping the state-law check** because "the partner said yes." District personnel can agree to attribution and STILL be in violation of their state's media-release rules. Confirm against the state-typology overlay.
- **Quoting students or parents without consent collection.** FERPA isn't optional; "the parent said it was OK in an email" is not sufficient documentation.
- **Asking the same partner more than 2× per year.** They stop being a partner and become a marketing asset; they opt out at the next renewal.
- **Repeating the same ask type.** Asking a partner for a case study, then a second case study, then a third. Step up the ask each time (case study → speaker → peer call), don't repeat.

## When NOT to invoke

- The advocacy ask is for a partner in recovery / red-health. Defer until partner is stable.
- The ask is mid-renewal-conversation (it conflates the relationship; advocacy asks should sit OUTSIDE the renewal motion when possible).
- The state-law overlay rules out the partner's attribution + the ask requires named attribution.

## Refresh triggers

- COPPA / FERPA / state student-privacy law materially changes the case-study consent overlay
- A state-specific media-release rule changes (rare; CA / NY / IL most likely)
- The 2-asks-per-year ceiling stops matching observed partner-fatigue patterns
- Marketing's advocacy-quota incentives change in a way that erodes the gates

## References

- [`../knowledge/edtech-reference-customer-patterns.md`](../../knowledge/edtech-reference-customer-patterns.md) — state-by-state anonymization / consent / media-release variance
- [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../../knowledge/parent-comms-jurisdictional-bear-traps.md) — FERPA on student/parent quotes
- [`../templates/case-study-draft.md`](../../templates/case-study-draft.md) — the case-study artifact
- [`../templates/reference-pipeline-tracker.md`](../../templates/reference-pipeline-tracker.md) — the per-partner advocacy status board
- [`../templates/cross-functional-partnership-map.md`](../../templates/cross-functional-partnership-map.md) — Marketing function row for how the ask routes
- [`partner-health-scoring.md`](../partner-health-scoring/SKILL.md) — health-score eligibility gate
