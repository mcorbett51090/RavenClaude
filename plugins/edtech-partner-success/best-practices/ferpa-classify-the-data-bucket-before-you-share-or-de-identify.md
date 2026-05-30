# Classify the data into the FERPA bucket before you share, quote, or de-identify it

**Status:** Absolute rule

**Domain:** FERPA-aware data handling / Data privacy

**Applies to:** `edtech-partner-success`

---

## Why this exists

Every FERPA decision starts by sorting the data into one of three buckets, and skipping that step is how a well-meaning PSM ships a privacy incident. The buckets: **education records** (protected), **PII** (protected), and **directory information** (disclosable *only* if the district formally designated that category AND the parent hasn't opted out). The two most common failures are (1) treating something as directory information that the district never designated — designations vary district to district — and (2) believing de-identification is safe when a small denominator makes the data re-identifiable from context ("the 3 students who chose option B" in a class of 25 names the other 22). FERPA explicitly prohibits identifiable-from-context disclosure, so de-identification that ignores the cohort residual isn't de-identification at all. House opinion §3 #7 sets the higher bar; the `ferpa-comms-translator` exists because none of this is obvious from the surface text. `[verify-at-build — FERPA directory-information + de-identification specifics are regulatory and shift; confirm against current DOE guidance]`

## How to apply

Sort first, then decide what's shareable; de-identification is a claim you have to *earn* against the residual, not assert.

```
Bucket classification (run BEFORE sharing / quoting / "anonymizing" any student data):
  1. Education record or PII? → protected. Sharing needs school-authorized educational
     use (vendor) or consent. Default: do not disclose.
  2. Directory information? → disclosable ONLY IF the district formally designated this
     category AND the parent has not opted out. Check the profile's directory-info line;
     each district differs — never assume.
  3. "De-identified"? → only if it survives the cohort-residual test:
       < 10  → treat as identifying (the residual names the rest)
       10-30 → scrutinize
       > 30  → usually safe
     and only if no category is itself identifying ("students in [program]",
     "[504] students" — often MORE disclosing than naming students directly).
  4. Higher-ed? → rights shifted to the STUDENT at 18 / matriculation. A "parent letter"
     about an adult student's record without consent is a violation.
  5. Any "uncertain" → route to the partner's counsel BEFORE acting. The PSM recognizes
     the SHAPE of the question and routes; it does not render a legal opinion.
```

**Do:**
- Keep student PII inside the plugin's working directory; even hypothetical examples use synthetic identifiers (constitution §2).
- Record the district's directory-information designation in the durable profile so the next comm is drafted against the right rules.
- Layer the state regime on top (CA SOPIPA, IL SOPPA, NY Ed Law §2-d, CT, CO, TX, VA, WA, UT, FL) when the partner sits in a covered state.

**Don't:**
- Call a dataset "de-identified" because the names are stripped — a small-cohort residual or an identifying category re-identifies it.
- Assume directory information is a fixed federal list; it's a per-district designation that can change.

## Edge cases / when the rule does NOT apply

- **General-level statements** ("what the program does for all students") with no individual or small-cohort reference — the identifiability trap isn't engaged.
- **Aggregate de-identified analytics over a large population** (> 30, no identifying category) — usually shareable; still record the basis.
- **Dependent-student / dual-enrollment higher-ed** — exceptions exist but are institution-policy-specific; route through the registrar rather than deciding.

## See also

- [`./screen-parent-comms-for-the-cohort-residual.md`](./screen-parent-comms-for-the-cohort-residual.md) — the comms-facing sibling rule (the residual checklist applied to a comm)
- [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../knowledge/parent-comms-jurisdictional-bear-traps.md) — the three-bucket model, rights-holder shift, COPPA, state typology, residual checklist
- [`../knowledge/edtech-reference-customer-patterns.md`](../knowledge/edtech-reference-customer-patterns.md) — the advocacy/quote consent overlay (separate consent for student/parent quotes)
- [`../agents/ferpa-comms-translator.md`](../agents/ferpa-comms-translator.md) — owns the bucket classification

## Provenance

Distilled from `knowledge/parent-comms-jurisdictional-bear-traps.md` (three-bucket model, directory-info-is-per-district, cohort-residual < 10 / 10-30 / > 30, identifying-category trap, higher-ed rights shift), `agents/ferpa-comms-translator.md`, and constitution §2 (student PII never leaves working dir) + house opinion §3 #7. Field guidance, not legal advice; regulatory specifics `[verify-at-build]`. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
