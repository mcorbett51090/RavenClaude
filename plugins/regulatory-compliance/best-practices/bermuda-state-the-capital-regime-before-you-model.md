# Bermuda — state the insurance class and capital regime before you model

**Status:** Absolute rule — modeling a Bermuda (re)insurer's capital before fixing its **class** and **capital regime** produces numbers against the wrong yardstick; the regime is the first decision, not an input you discover later.

**Domain:** Bermuda insurance / prudential

**Applies to:** `regulatory-compliance`

---

## Why this exists

The `bermuda-insurance-specialist` agent carries rich prose but had **no citable rule** of its own, and its single most consequential decision — which **insurance class** the entity is registered as, and therefore which **BMA capital regime** applies — was undocumented as a rule. The class drives the capital framework (which solvency calculation, which return, which valuation basis), and getting it wrong means every capital number is computed against the wrong standard. This rule makes the class-and-regime determination the explicit first step.

## How to apply

**Fix the class and regime before modeling capital:**

1. **Determine the registration class** — Bermuda registers insurers by class (e.g. Class 1/2/3/3A/3B/4 for general business; Class A–E and the IIGB/Innovative classes for long-term; plus the special-purpose/ILS structures). The class follows the nature and scale of the business.
2. **Map the class to its capital regime:**
   - The **Bermuda Solvency Capital Requirement (BSCR)** / **Enhanced Capital Requirement (ECR)** and **Minimum Margin of Solvency (MMS)** apply per class.
   - Valuation is on the **Economic Balance Sheet (EBS)** basis for the classes that use it.
   - Note where **Solvency II equivalence** or the **ICS** (Insurance Capital Standard) interact with the entity's group/cross-border position.
3. **State the regime explicitly in any capital model or memo** — it's the assumption every figure inherits and the first thing the BMA tests.
4. **For ILS / SPI / segregated-account structures**, the structural form changes the capital and reporting treatment — confirm it before modeling.

**Do:** identify the registration class first; map it to BSCR/ECR/MMS + EBS; state the regime up front; confirm group-level SII-equivalence/ICS interaction; treat ILS/SAC structures as a distinct determination.

**Don't:** model capital on a generic "insurer" basis before fixing the class; assume a Solvency II or US-RBC mental model transfers to Bermuda; quote a class-specific threshold or ratio from memory.

## Edge cases / when the rule does NOT apply

A pure advisory question that doesn't touch capital (a licensing-process question, a conduct matter) may not need the full regime determination — but anything touching solvency, the ECR/MMS, or a capital return does. Specific class definitions, capital ratios, EBS valuation rules, and SII-equivalence/ICS status are **BMA-current and version-specific** — `[verify-at-build]`; never hard-code a Bermuda capital figure from training memory. Genuine legal/actuarial sign-off remains with qualified counsel/actuaries (house rule).

## See also

- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — the regime-selection tree (which routes *to* the Bermuda specialist) **and** the **Bermuda class/capital** tree that operationalizes this rule
- [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) — the BMA severity vocabulary (supervisory letter / Insurance Act direction)
- [`../agents/bermuda-insurance-specialist.md`](../agents/bermuda-insurance-specialist.md) — owns the Bermuda capital regime
- BMA Insurance Act + the class-specific prudential rules — authoritative (`[verify-at-build]` current rules)

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01): the `bermuda-insurance-specialist` is a named agent with rich prose but had **zero** dedicated best-practice or tree for its own primary subject (class + capital regime). (Panel 2 corrected Panel 1's "zero rule/tree" framing — the agent does have a BMA severity-tree *branch* — but confirmed the class/capital-regime gap is real.) Grounded in the BMA prudential framework. Class definitions + capital ratios are `[verify-at-build]`. (The matching class/capital *tree* ships in [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md).)

---

_Last reviewed: 2026-06-01 by `claude`_
