# Scope the jurisdiction and regime before you map a control or a term

**Status:** Absolute rule
**Domain:** Jurisdiction scoping / regulatory mapping
**Applies to:** `regulatory-compliance`

---

## Why this exists

The same word means different things across regulators, and the same control answers to different cites in different regimes. "Material" in BMA insurance regulation is not "material" in US bank regulation is not "material" in IFRS; an MRA/MRIA severity ladder anchored to Federal Reserve SR 13-13 does not map onto a BMA supervisory letter; a control written against "applicable AML rules" maps to nothing verifiable. The failure mode is silent: an analyst applies a US response timeline to a Bermuda finding, or carries a threshold definition across a border it doesn't survive, and the error only surfaces in front of an examiner. Naming the **regulator + regime** first — before mapping a control, classifying a finding, or using a threshold word — is what stops a term or a timeline from being quietly mis-applied across a jurisdiction boundary.

## How to apply

Resolve jurisdiction and regime *first*, then map cites, terms, and timelines inside that scope. The first node of the severity-triage tree exists for exactly this reason: a BMA finding branches out before any US tier is considered.

```
Step 0  Name the regulator + regime         -> "BMA / Bermuda insurance"  or  "US / FINRA Rule 3310"
Step 1  If BMA/Bermuda                       -> route to bermuda-insurance-specialist for terminology mapping
                                                (supervisory letters / Insurance Act directions — NOT MRA/MRIA)
Step 2  Cite the regulator's own section     -> "BMA Insurance (Group Supervision) Rules 2011, Rule 21(1)(b)"
Step 3  Define each threshold word IN-SCOPE  -> state the materiality definition AND which regime it belongs to
Step 4  Cross-jurisdiction control?          -> record a cite per regime; name which regime governs
```

State the resolved scope on the artifact's `Jurisdiction:` line (Output Contract) so no reader inherits the wrong regime.

**Do:**
- Name the regulator and regime before mapping any control, classifying any finding, or using "material" / "significant" / "reportable".
- Route BMA/Bermuda matters to `bermuda-insurance-specialist` for the terminology mapping before applying any US-anchored ladder or timeline.
- When a control answers to two regulators, record both cites and name which regime governs (house opinion #12).

**Don't:**
- Assume a BMA supervisory letter equals a US MRA — the BMA sets response timing and board involvement in the letter and the underlying rule, not the US ladder.
- Carry a threshold definition ("material ≥ $X") across a jurisdiction boundary without re-checking the regime's own standard.
- Write "per applicable laws" — name the regulator, the regime, and the section.

## Edge cases / when the rule does NOT apply

- **Genuinely single-jurisdiction work** for a domestic-only entity still needs Step 0 stated once, but Steps 1 and 4 are moot — there is one regime and no cross-border mapping.
- **Principle-level policy text** (governance commitments, code-of-conduct principles) is often jurisdiction-stable; what diverges across borders is the *definitions, thresholds, and escalation paths*, not the principle. Scope those, not the whole policy.
- **Legal-conclusion questions** ("which jurisdiction's law governs this contract?") are out of scope — the `Legal-advice gate:` flips to counsel-required. The compliance team scopes the *regulatory* regime for documentation; the choice-of-law opinion routes to counsel.

## See also

- [`./classify-severity-before-you-respond.md`](./classify-severity-before-you-respond.md) — the severity tree whose first node is the BMA/jurisdiction branch this rule generalizes.
- [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) — the BMA / Bermuda jurisdictional carve-out and the US tier anchors.
- [`../agents/bermuda-insurance-specialist.md`](../agents/bermuda-insurance-specialist.md) — owns the BMA terminology mapping.
- [`../agents/policy-and-procedure-writer.md`](../agents/policy-and-procedure-writer.md) — "jurisdictional adaptation: what diverges, what stays"; the definitions-section discipline.

## Provenance

Codifies house opinions #1 (cite the regulation), #7 (materiality/threshold definitions in writing), #11 (primary-source provenance), and #12 (jurisdiction matters — same word, different regulators) in [`../CLAUDE.md`](../CLAUDE.md) §3, plus the BMA/Bermuda jurisdictional carve-out and "default to the higher severity / route BMA first" structure in [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) (last reviewed 2026-05-22; US tiers anchored to Federal Reserve SR 13-13 and OCC News Release 2014-150, with OCC Bulletin 2025-29 flagged NPR-only / not finalized).

---

_Last reviewed: 2026-05-30 by `claude`_
