# Screen every parent-facing comm for the small-cohort residual

**Status:** Absolute rule

**Domain:** FERPA-aware comms / Data privacy

**Applies to:** `edtech-partner-success`

---

## Why this exists

Parent / family / student comms carry a higher bar than a PSM-to-partner email: parents are not the partner's customers, the comms may surface in legal discovery, and the jurisdictional layer (federal FERPA + state law) shifts the rules by where the partner sits (house opinion #7). The most common FERPA bear trap is not direct PII disclosure — it is the **residual**: "the 3 students who chose option B" names nobody, but in a small class everyone can identify the three; "students receiving the new intervention" structurally names everyone with that accommodation. FERPA explicitly prohibits this identifiable-from-context disclosure. A comm that trips it is a privacy incident, and "FERPA-compliant" asserted without naming who reviewed it is an anti-pattern the `ferpa-comms-translator` flags.

## How to apply

Run the cohort-residual checklist before any parent-facing comm goes out. The PSM's job is to *recognize the shape of the question* and route — not to render a legal opinion.

```
Cohort-residual screen (run on every parent/family/student-facing comm):
  1. Does the comm name a number? ("3 students", "12% of the cohort", "top 5 performers")
  2. Is the denominator small enough that classmates/parents can identify the named or missing?
       Field rule of thumb:  < 10 → treat as identifying
                            10-30 → scrutinize
                             > 30 → usually safe
  3. Does it name a category that is itself identifying?
       ("students in [program]", "students receiving [intervention]", "[504] students")
       — often MORE disclosing than naming students directly
  4. Does it disclose anything the district hasn't designated as directory information?
  5. Does it assume parental rights in a HIGHER-ED context? (rights shift to the
     student at age 18 or postsecondary matriculation)
  6. Does it trigger a state-specific notification/formatting requirement?
       (CA SOPIPA, IL SOPPA, NY Ed Law §2-d, CT PA 16-189, CO HB 16-1423, TX, VA, WA, UT, FL)
  → Any answer "uncertain" → route to the partner's counsel BEFORE sending.
```

**Do:**
- Treat a group small enough to be socially countable in context as PII, even with no name given.
- Flag the state-specific layer explicitly when the partner sits in a student-privacy-law jurisdiction; recommend counsel review when a comm names individual students or small cohorts.
- For non-English-primary households, require a translation (Title VI) that is culturally tuned, not a literal rendering — and review by a native speaker for legal-bearing comms.

**Don't:**
- Send a parent comm naming a < 10 cohort without consent.
- Assume the parent is the rights-holder in a higher-ed context (a "parent letter" about an adult student's record without the student's consent is a FERPA violation).
- Frame a COPPA-relevant individual-student comm as marketing — naming a child's behavior to that child's parents is school-authorized educational use only.

## Edge cases / when the rule does NOT apply

- **General-level comms** ("here's what the program does for all students") with no individual or small-cohort reference — FERPA's identifiability trap isn't engaged; COPPA isn't the lever (FERPA is, at the general level).
- **The district has formally designated** the disclosed category as directory information *and* the parent hasn't opted out — disclosable. But each district's directory designation differs; don't assume.
- **Dependent-student / dual-enrollment higher-ed cases** — exceptions exist but are institution-policy-specific; route through the registrar rather than deciding.

## See also

- [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../knowledge/parent-comms-jurisdictional-bear-traps.md) — the FERPA three-bucket model, K-12/higher-ed rights shift, COPPA, state-by-state typology, Title VI, the cohort-residual checklist
- [`../agents/ferpa-comms-translator.md`](../agents/ferpa-comms-translator.md) — the agent that authors and screens these comms
- [`./check-rostering-before-calling-a-partner-red.md`](./check-rostering-before-calling-a-partner-red.md) — the sibling diagnostic rule in this plugin

## Provenance

Distilled from `knowledge/parent-comms-jurisdictional-bear-traps.md` (Last reviewed 2026-05-21) — the identifiable-from-context trap, the < 10 / 10-30 / > 30 rule of thumb, the higher-ed rights shift, the COPPA bright line, and the "X students" cohort-residual checklist — plus `edtech-partner-success/CLAUDE.md` house opinion #7 and the `ferpa-comms-translator` anti-pattern list. Field guidance, not legal advice. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
