# Design the RFx Before You Publish It

**Status:** Absolute rule
**Domain:** Sourcing / RFx
**Applies to:** `procurement-sourcing`

---

## Why this exists

A poorly designed RFP or RFQ produces responses that cannot be compared, evaluated, or defended. The most common failure modes are: requirements written at different levels of specificity across sections (so suppliers fill the gaps differently), evaluation criteria stated after the fact (creating the appearance of post-hoc rationalization), and a scoring model that doesn't match the category's Kraljic position (running an auction-style price-only evaluation on a strategic supplier destroys the partnership relationship). The design discipline — requirements, evaluation criteria, weighting, and scoring model — must be locked before the RFx goes out, or the sourcing event produces a result that doesn't hold up to stakeholder scrutiny.

## How to apply

Complete the RFx design document before the document goes to suppliers.

```
RFx Design Checklist — Lock Before Publishing
──────────────────────────────────────────────────
□ REQUIREMENTS SECTION
  Every requirement is:
  - Specific (a supplier can write a precise response)
  - Testable (a scorer can assign a defensible score)
  - Categorized as Must-have (M) or Nice-to-have (N)
  Must-haves are pass/fail gates; a supplier that fails one M is eliminated.

□ EVALUATION CRITERIA AND WEIGHTING
  Named criteria and weights (sum to 100%):
  e.g.,  Technical / quality fit:  40%
         Price / TCO:              35%
         Supplier capability/risk: 15%
         Implementation plan:      10%
  Weighting reflects the Kraljic position (strategic = quality/risk heavier;
  leverage = price heavier; bottleneck = risk/continuity heavier).

□ SCORING RUBRIC (per criterion)
  Defined score values: e.g., 1=does not meet, 2=partially meets, 3=fully meets,
  4=exceeds. Scoring descriptors written before the first response arrives.

□ EVALUATOR ASSIGNMENT
  Named evaluators per criterion; no single evaluator scores the entire bid alone.

□ CONFLICT OF INTEREST DECLARATION
  All evaluators sign a COI declaration before receiving responses.
```

**Do:**
- Run the design document past a cross-functional stakeholder (end user + finance + legal) before publishing.
- Lock the scoring rubric in a dated document; any post-open change requires a documented amendment issued to all bidders.
- Align the evaluation weighting explicitly to the category strategy — if the category strategy says "partner this supplier for quality," price should not dominate the weighting.

**Don't:**
- Define evaluation criteria after opening responses — this is a procurement-integrity violation and invalidates the sourcing event.
- Let the weighting be driven by which supplier you want to win rather than what the category actually needs.
- Use vague requirements like "must have relevant experience" without a defined minimum or a way to differentiate responses.

## Edge cases / when the rule does NOT apply

- **Single-source negotiations** (sole-source justification approved, no competition) — RFx design is moot; replace with a structured single-source justification document.
- **Micro-purchases below the simplified-acquisition threshold** — a formal RFx design is not required; a brief price comparison memo suffices.

## See also

- [`../agents/category-strategist.md`](../agents/category-strategist.md) — owns RFx design and the link to category strategy.
- [`./segment-the-spend-before-you-source-it.md`](./segment-the-spend-before-you-source-it.md) — the Kraljic position that should drive RFx weighting is determined by the segmentation step.

## Provenance

Codifies the category-strategist's RFx design discipline from the procurement-sourcing plugin's CLAUDE.md §1 and `skills/segment-the-spend/SKILL.md`. The Kraljic-weighting linkage and conflict-of-interest requirements reflect standard procurement-governance practice across public and private sector organizations.

---

_Last reviewed: 2026-06-05 by `claude`_
