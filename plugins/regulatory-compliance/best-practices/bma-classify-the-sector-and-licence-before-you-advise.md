# BMA — classify the sector and licence class before you advise

**Status:** Absolute rule — every BMA non-insurance answer (capital, net assets, Code obligation, reporting) is computed against a *sector + licence class*; fixing those is the first decision, not an input discovered mid-analysis.

**Domain:** Bermuda / BMA financial institutions (non-insurance)

**Applies to:** `regulatory-compliance`

---

## Why this exists

The BMA is an **integrated regulator** with a separate Act and a separate set of licence classes for each sector it supervises — banking, trust, corporate services, investment funds, fund administration, investment business, money service business, and digital asset business. The single most consequential early decision is *which sector Act governs* and *which licence class within it applies*, because the class drives the capital/net-asset floor, the applicable Code of Conduct, and the reporting obligations. Pattern-matching the entity's label to a sector ("it's a fund → Investment Funds Act") instead of resolving the actual **licensable activity** carries the wrong sector's obligations through the entire analysis.

## How to apply

**Fix the sector and licence class before advising:**

1. **Confirm it is non-insurance** — insurance/reinsurance/captive/ILS routes to `bermuda-insurance-specialist`, not here.
2. **Resolve the licensable activity → sector Act** (traverse the sector/licence tree in [`../knowledge/bma/decision-trees.md`](../knowledge/bma/decision-trees.md)):
   - deposit-taking → Banks and Deposit Companies Act 1999
   - trustee business → Trusts (Regulation of Trust Business) Act 2001
   - company formation / nominee / resident-rep / corporate admin for profit → Corporate Service Provider Business Act 2012
   - a collective investment vehicle → Investment Funds Act 2006
   - administering funds for others → Fund Administration Provider Business Act 2019
   - dealing/arranging/managing/advising/safeguarding/promoting investments → Investment Business Act 2003
   - money transmission / FX / payment services → Money Service Business Act 2016
   - issuing/exchanging/custodying digital assets → Digital Asset Business Act 2018
3. **Fix the licence class within the sector** — it is load-bearing: a deposit company ≠ a full bank ≠ a restricted bank; a limited trust licence ≠ unlimited; a Class A Registered Person ≠ a Class B ≠ a full investment-business licensee; an Institutional Fund ≠ a Standard Fund.
4. **Check for multiple licences** — one entity can hold several BMA licences; resolve each licensable activity separately.
5. **State the sector + class explicitly** in any memo — every figure inherits it.

**Do:** resolve the licensable activity first; map to the sector Act; fix the licence class; treat a multi-activity entity as multiple licensing questions.

**Don't:** map an entity's label to a sector; quote a capital/net-asset figure or Code obligation before the class is fixed; carry one sector's obligations onto another.

## Edge cases / when the rule does NOT apply

A pure jurisdiction-comparison or a generic conduct question may not need a class determination — but anything touching capital, net assets, a Code obligation, or a return does. Section pins and net-asset figures are **BMA-current and version-specific**; many carry `[unverified]` in the sector files (BMA primary sites block automated fetch) — never hard-code one from memory; confirm against the Act PDF.

## See also

- [`../knowledge/bma/decision-trees.md`](../knowledge/bma/decision-trees.md) — the sector/licence classification tree this rule operationalizes
- [`../knowledge/bma/`](../knowledge/bma/) — the six sector files (banking, trust, corporate-services, fund-administration, investment-business, overview)
- [`../agents/bma-financial-institutions-specialist.md`](../agents/bma-financial-institutions-specialist.md) — owns the BMA non-insurance perimeter
- Sister rule for insurance: [`bermuda-state-the-capital-regime-before-you-model.md`](./bermuda-state-the-capital-regime-before-you-model.md)

## Provenance

Surfaced during the 2026-06-04 BMA build-out: the new `bma-financial-institutions-specialist` covers five-plus sectors, each with its own Act and licence classes, but had no citable rule making the sector-and-class determination the explicit first step (mirroring the insurance-side rule). Grounded in the BMA sector knowledge files. Section pins + figures are `[unverified]` where the sector files mark them.

---

_Last reviewed: 2026-06-04 by `claude`_
