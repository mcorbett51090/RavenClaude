---
name: bma-licensing-classification
description: Classify a Bermuda (non-insurance) entity into its BMA sector + licence class and resolve its AML/ATF position before any capital/Code/filing advice. Used by `bma-financial-institutions-specialist`. Traverses the BMA decision trees, then the sector files.
---

# Skill: bma-licensing-classification

**Purpose:** Take a Bermuda entity (or a person operating "in or from within Bermuda") and determine, in order, **(1)** which BMA sector Act governs, **(2)** which licence class within it, **(3)** its AML/ATF status, and **(4)** its filing/fee/supervisory obligations — so every downstream capital/Code/filing answer is computed against the right yardstick. Used by `bma-financial-institutions-specialist`.

## When to use

- A new Bermuda entity or business line needs its BMA licensing position determined
- A "do we need a BMA licence, and which one?" question
- Before quoting any capital/net-asset floor, Code-of-Conduct obligation, or filing — the class fixes all three
- Before concluding "we're (not) in scope for AML" — a licensing exemption is not an AML exemption
- NOT for Bermuda **insurance** (route to `bermuda-insurance-specialist`) and NOT for legal/eligibility opinions (counsel)

## The playbook

### Step 0 — Insurance gate
Insurance / reinsurance / captive / ILS → **stop and route to `bermuda-insurance-specialist`**. This skill is the non-insurance perimeter only.

### Step 1 — Traverse the sector/licence tree
Open [`../../knowledge/bma/decision-trees.md`](../../knowledge/bma/decision-trees.md) and traverse the **"Which BMA sector + licence applies"** tree. Resolve the **licensable activity** (not the entity's label) → sector Act:

| Activity | Sector Act | Sector file |
|---|---|---|
| Deposit-taking | Banks and Deposit Companies Act 1999 | [`banking.md`](../../knowledge/bma/banking.md) |
| Trustee business | Trusts (Regulation of Trust Business) Act 2001 | [`trust.md`](../../knowledge/bma/trust.md) |
| Corporate services (for profit) | Corporate Service Provider Business Act 2012 | [`corporate-services.md`](../../knowledge/bma/corporate-services.md) |
| Collective investment vehicle | Investment Funds Act 2006 | [`fund-administration.md`](../../knowledge/bma/fund-administration.md) |
| Administering funds for others | Fund Administration Provider Business Act 2019 | [`fund-administration.md`](../../knowledge/bma/fund-administration.md) |
| Investment business | Investment Business Act 2003 | [`investment-business.md`](../../knowledge/bma/investment-business.md) |
| Money services | Money Service Business Act 2016 | [`msb-and-digital-assets.md`](../../knowledge/bma/msb-and-digital-assets.md) |
| Digital assets | Digital Asset Business Act 2018 | [`msb-and-digital-assets.md`](../../knowledge/bma/msb-and-digital-assets.md) |

**A single entity can need multiple licences** — resolve each licensable activity separately.

### Step 2 — Fix the licence class
Within the sector, fix the **class** (it drives capital/net-asset floor + the applicable Code): bank vs deposit company vs restricted (s.14); unlimited vs limited trust (s.11); unlimited vs limited CSP; Authorised vs Registered fund class; Licensed/Class A/Class B/Non-Registrable (investment business); Class T/M/F (digital assets).

### Step 3 — Resolve the AML/ATF position
Traverse the **"Is this entity AML/ATF-regulated"** tree in the same decision-trees file. If it carries on a relevant financial-business activity, it is an **AML/ATF-regulated financial institution** (POCA 1997 + AMLR 2008; BMA supervises under SE Act 2008) — **regardless of any licensing exemption.** Then pull the operational obligations from [`aml-atf.md`](../../knowledge/bma/aml-atf.md): CDD/EDD (Reg 11/11(1)(aa)), MLRO appointment, risk assessments, FIA reporting. Beneficial ownership: 10% gatekeeper vs 25% statutory (BO Act 2025; RoC-held register).

### Step 4 — Obligations
From [`supervision-and-filings.md`](../../knowledge/bma/supervision-and-filings.md): the periodic filing(s) and cadence for the sector, the annual fee (due 31 March; many non-insurance figures are `[unverified]`), the change-of-control regime, and any OpRes/cyber code in scope.

### Step 5 — Output
Fill the [`../../templates/bma-licensing-classification-workpaper.md`](../../templates/bma-licensing-classification-workpaper.md). State the sector + class + AML status + filing obligations, cite the Act + section for each, and **flag every `[unverified]` pin** for confirmation against the primary PDF.

## Common pitfalls

- **Mapping the entity's label to a sector** ("it's a fund → IFA") instead of resolving the licensable activity.
- **Quoting a capital/net-asset figure before the class is fixed** — or quoting one that carries `[unverified]` in the sector file as if settled.
- **Treating a licensing exemption as an AML exemption** — exempt PTCs are still AML/ATF-regulated FIs.
- **Conflating the 10% gatekeeper and 25% statutory beneficial-ownership thresholds.**
- **Applying a US MRA/MRIA ladder** to a BMA supervisory communication (use [`../../knowledge/regulator-finding-severity-triage.md`](../../knowledge/regulator-finding-severity-triage.md)).

## See also

- Trees: [`../../knowledge/bma/decision-trees.md`](../../knowledge/bma/decision-trees.md)
- Template: [`../../templates/bma-licensing-classification-workpaper.md`](../../templates/bma-licensing-classification-workpaper.md), [`../../templates/bma-change-of-control-notification.md`](../../templates/bma-change-of-control-notification.md)
- Agent: [`../../agents/bma-financial-institutions-specialist.md`](../../agents/bma-financial-institutions-specialist.md)
- Best practices: [`../../best-practices/bma-classify-the-sector-and-licence-before-you-advise.md`](../../best-practices/bma-classify-the-sector-and-licence-before-you-advise.md), [`../../best-practices/bma-a-licensing-exemption-is-not-an-aml-exemption.md`](../../best-practices/bma-a-licensing-exemption-is-not-an-aml-exemption.md)
