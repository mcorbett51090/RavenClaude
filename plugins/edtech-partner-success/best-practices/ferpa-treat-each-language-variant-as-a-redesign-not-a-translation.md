# Reshape parent comms per audience and treat each language as a re-design, not a re-render

**Status:** Pattern

**Domain:** FERPA-aware comms / Multilingual access

**Applies to:** `edtech-partner-success`

---

## Why this exists

A PSM-to-partner email re-sent verbatim to parents fails twice: it carries jargon parents can't act on, and it skips the audience-reshaping that determines whether the comm produces the action it asks for. Parents, school admins, district leadership, and students are four different rooms — same announcement, four different drafts. The multilingual layer compounds it: a literal Spanish rendering of an English announcement often misses the cultural context that decides whether a family acts, so each language is a re-design with cultural tuning, not a re-render — and for legal-bearing comms, a native-speaker review. The obligation isn't optional politeness: meaningful access for limited-English-proficient families rides on Title VI of the Civil Rights Act, and several states name specific languages and thresholds on top. `[verify-at-build — Title VI LEP obligations and state language thresholds are regulatory; confirm current guidance]` Underspecify the audience and the comm underperforms; over-translate literally and it lands flat.

## How to apply

Name the audience precisely before drafting, re-shape per audience, and treat each language as a fresh design with a native-speaker check for anything legal-bearing.

```
Comms reshaping discipline (per parent/family/student-facing comm):
  AUDIENCE SPEC (before drafting) — primary language? grade-band? socioeconomic
    context? engagement history? "this is going to families" is underspecified.
  RE-SHAPE PER AUDIENCE:
    parents            → jargon-free, action-oriented, 6th-8th grade reading level, ONE ask.
    school admin       → operational, scheduling, change-management.
    district leadership → strategic, outcome-focused, professional register.
    students           → age-appropriate, voice-appropriate; don't make parents the firewall.
  PLAIN-LANGUAGE PASS — define terms on first use; "adoption depth" doesn't translate —
    rewrite the IDEA, not the term. Read-aloud test: stumble = rewrite.
  MULTILINGUAL — each language is a re-design with cultural tuning, per Title VI (LEP access)
    + state language rules (NY top-8, CA/TX/IL/FL thresholds). `[verify-at-build]`
    Native-speaker review for any legal-bearing comm.
  THEN — run the cohort-residual + bucket screen before it ships (see sibling FERPA rules).
```

**Do:**
- State the source of a decision — "your school's leadership decided X based on Y data" lands better than "the district decided X," and when decisions rest on data, parents are entitled to know it.
- Keep the partner's institutional voice intact across variants (a parish school's tone ≠ a charter network's ≠ a public university's).

**Don't:**
- Ship one ask stacked with two others — a parent email asking for three things gets zero done.
- Ship a literal machine translation as the multilingual variant — it skips the cultural re-design and the native-speaker check.

## Edge cases / when the rule does NOT apply

- **Internal PSM-team comms** — plain English, no audience-reshaping or translation needed; the rule is for downstream partner audiences.
- **Single-language, single-audience operational note** (e.g., an admin scheduling confirmation) — the reshaping collapses to one pass; the residual/bucket screen still runs.
- **Higher-ed** — address the *student* as rights-holder after matriculation, not the parent; a "parent variant" may be inappropriate entirely.

## See also

- [`./screen-parent-comms-for-the-cohort-residual.md`](./screen-parent-comms-for-the-cohort-residual.md) — the residual screen that runs after reshaping
- [`./ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md`](./ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md) — the bucket classification that gates what the comm can say
- [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../knowledge/parent-comms-jurisdictional-bear-traps.md) — Title VI multilingual obligations + state language rules
- [`../agents/ferpa-comms-translator.md`](../agents/ferpa-comms-translator.md) — owns audience-reshaping and multilingual variants
- [`../agents/partner-profile-curator.md`](../agents/partner-profile-curator.md) — supplies top non-English household languages from the durable profile

## Provenance

Distilled from `agents/ferpa-comms-translator.md` (name-the-audience, read-aloud test, one-ask, don't-make-parents-the-firewall, state-the-source, each-language-is-a-re-design) and `knowledge/parent-comms-jurisdictional-bear-traps.md` (Title VI LEP, state language thresholds, native-speaker review) + house opinion §3 #7. Field guidance, not legal advice; regulatory specifics `[verify-at-build]`. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
