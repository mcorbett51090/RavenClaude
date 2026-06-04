# BMA — a licensing exemption is not an AML exemption

**Status:** Absolute rule — a carve-out from a BMA *licence* requirement does **not** remove the entity's *AML/ATF* obligations; conflating the two is a recurring, examinable error.

**Domain:** Bermuda / BMA AML/ATF

**Applies to:** `regulatory-compliance`

---

## Why this exists

Several BMA sector regimes exempt specified entities from the **licence** requirement — most notably the **private trust company (PTC)** exemption under the Trusts (Regulation of Trust Business) Exemption Order 2002, and the Corporate Service Provider Business Act carve-out for entities already AML-regulated under another regime. The recurring error is to read "exempt from the licence" as "exempt from AML." It is not. Since 2018, exempt PTCs are **expressly captured as AML/ATF-regulated financial institutions** under the Proceeds of Crime (AML/ATF) Regulations 2008, and the BMA remains their AML/ATF supervisor. The licensing exemption removes the licence application and prudential-licensing obligations; it leaves the full customer-due-diligence, risk-assessment, MLRO, and suspicious-activity-reporting obligations intact.

## How to apply

**Separate the two questions every time:**

1. **Does the entity need a BMA licence?** (the licensing question)
2. **Is the entity an AML/ATF-regulated financial institution?** (the AML question)

These are answered against **different tests**. A "yes" exemption to (1) is silent on (2). Traverse the AML-regulated tree in [`../knowledge/bma/decision-trees.md`](../knowledge/bma/decision-trees.md):

- If the entity carries on a relevant financial-business activity (trust, CSP, banking, investment business, fund admin, MSB, digital asset business, long-term insurance), it is **AML/ATF-regulated** — POCA 1997 + AMLR 2008 apply and the BMA supervises (SE Act 2008) — **regardless of any licensing exemption**.
- Confirm the AML obligations explicitly in the advice: CDD/EDD, a documented risk assessment, an appointed Reporting Officer/MLRO, and SAR/STR reporting to the Financial Intelligence Agency.

**Do:** answer "need a licence?" and "AML-regulated?" as two separate questions; state that an exemption is licensing-only; confirm CDD/EDD/MLRO/reporting still apply.

**Don't:** advise that an exempt PTC or a carved-out CSP has "no AML obligations"; let "we have no retail customers" or "we don't need a licence" stand as an AML exemption.

## Edge cases / when the rule does NOT apply

If the entity genuinely carries on **no** relevant financial-business activity, it may be outside the AML/ATF perimeter — but document that no-scope basis (the decision is itself a record). Regulated **non-financial** businesses (real estate, gaming, high-value-goods dealers) are AML-supervised by a different Bermuda competent authority, not the BMA — route accordingly. The exact AMLR 2008 regulation numbers for the PTC capture are `[unverified]` in the source files; confirm against the Regulations before a citation gates advice.

## See also

- [`../knowledge/bma/decision-trees.md`](../knowledge/bma/decision-trees.md) — the AML-regulated determination tree
- [`../knowledge/bma/trust.md`](../knowledge/bma/trust.md) (PTC exemption) · [`../knowledge/bma/corporate-services.md`](../knowledge/bma/corporate-services.md) · [`../knowledge/bma/overview.md`](../knowledge/bma/overview.md) (AML/ATF frame)
- [`edd-is-depth-not-document-count.md`](./edd-is-depth-not-document-count.md) · [`aml-risk-rate-before-you-choose-cdd-depth.md`](./aml-risk-rate-before-you-choose-cdd-depth.md)

## Provenance

Surfaced during the 2026-06-04 BMA build-out: the trust and CSP sector files both flag the licensing-exemption-≠-AML-exemption trap, but it had no standalone citable rule. Grounded in POCA 1997 + AMLR 2008 + the 2018 capture of exempt PTCs as AML/ATF-regulated FIs (`[unverified]` regulation numbers per the source files).

---

_Last reviewed: 2026-06-04 by `claude`_
