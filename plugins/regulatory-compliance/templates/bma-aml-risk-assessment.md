# BMA AML/ATF risk-assessment workpaper — [Entity name]

> The business-wide (enterprise) + customer-level AML/ATF risk assessment the AMLR 2008 requires of a BMA-regulated financial institution. Fill this before setting CDD depth or designing controls. Grounded in [`../knowledge/bma/aml-atf.md`](../knowledge/bma/aml-atf.md). **Compliance workpaper, not legal advice.** **Never commit real customer PII** — the pre-write hook flags it; for SAR-adjacent content treat as `regulator-only`.

**Entity (the RFI):** [legal name + BMA sector/licence]
**Prepared by (MLRO / Compliance Officer):** [name] **Date:** [YYYY-MM-DD]
**Reviewer / approver:** [name + role]
**Confidentiality:** internal (client-confidential if real data)
**Frameworks:** POCA 1997; AMLR 2008; BMA General + sector AML/ATF Guidance Notes; AML/ATF Ministerial Advisory 2/2025 (high-risk jurisdictions)

---

## A. Business-wide (enterprise) risk assessment

Rate each factor (Low / Medium / High) with a documented basis. The output drives the risk-based program — not a fixed template.

| Risk factor | Description for this entity | Inherent rating | Basis |
|---|---|---|---|
| **Customer** | [customer types: PEPs, complex ownership, non-resident, high-net-worth, nominee] | | |
| **Product / service** | [products carrying ML/TF risk: cross-border payments, custody, trust structures, digital assets] | | |
| **Geography** | [exposure to FATF/CFATF higher-risk countries — Reg 11(1)(aa) EDD trigger] | | |
| **Delivery channel** | [face-to-face vs non-face-to-face / intermediated / online] | | |
| **Transaction** | [volume, value, cash intensity, occasional transactions] | | |

**Overall inherent business risk:** [Low/Medium/High] — [rationale]

## B. Controls & residual risk

| Control area | In place? | Effectiveness | Residual rating |
|---|---|---|---|
| CDD / EDD procedures (Reg 5–7 / Reg 11) | | | |
| Sanctions & PEP screening (International Sanctions Act 2003) | | | |
| Ongoing monitoring / transaction monitoring | | | |
| Record-keeping (≥ 5 years) | | | |
| SAR/STR internal-disclosure → FIA reporting (POCA s.46) | | | |
| Training | | | |
| Independent testing / assurance | | | |

**Overall residual business risk:** [Low/Medium/High] vs the firm's stated risk appetite — [over/under-controlled?]

## C. Compliance-function & governance

- **Reporting Officer (MLRO):** [name — fit-and-proper under SEA Act s.11A]
- **Compliance Officer:** [name + authority/seniority]
- **Board/senior-management oversight cadence:** [frequency]
- **Last business-wide risk-assessment review:** [date] **Next due:** [date]

## D. Customer-level risk-rating model (the rubric this entity applies)

| Axis | Inputs | Weighting |
|---|---|---|
| Customer type | [PEP? legal-person opacity? sector] | |
| Product | [risk of the product taken] | |
| Geography | [country risk incl. FATF/CFATF lists] | |
| Channel | [face-to-face vs not] | |

**Tier outputs → CDD depth:** Low → SDD (where permitted, documented basis) · Standard → CDD · High **or any EDD trigger (PEP, high-risk country, opaque ownership, correspondent/nested)** → EDD (independent verification + senior approval + recorded rationale-to-proceed + shorter refresh).
*(Traverse the CDD-depth tree in [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md).)*

## E. Conclusion & actions

- **Residual position vs appetite:** [statement]
- **Gaps + remediation (owner + target date):** [list]
- **Citations:** POCA 1997; AMLR 2008 (flag `[unverified]` regulation numbers per the source file); BMA Guidance Notes.
- **Open questions for counsel:** [any legal-conclusion items]

---

**Sources:** [`../knowledge/bma/aml-atf.md`](../knowledge/bma/aml-atf.md) (operational obligations + verbatim-confirmed pins), the BMA General/sector AML/ATF Guidance Notes, and the firm's own customer-risk-rating rubric. Only POCA s.42A/46/47/49, SEA Act s.11A, and AMLR Reg 11/11(1)(aa) are verbatim-confirmed — cite other regulation numbers as indicative until confirmed against the AMLR 2008 PDF.
