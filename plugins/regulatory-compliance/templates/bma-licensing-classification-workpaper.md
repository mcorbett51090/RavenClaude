# BMA licensing-classification workpaper — [Entity name]

> Determines the BMA sector + licence class and the AML/ATF position for a Bermuda (or "in or from within Bermuda") entity, **before** any capital/Code/filing advice. Traverse [`../knowledge/bma/decision-trees.md`](../knowledge/bma/decision-trees.md) as you fill this in. **This is a compliance workpaper, not legal advice** — licence-eligibility and statutory-interpretation conclusions route to counsel.

**Entity:** [legal name]
**Prepared by:** [name] **Date:** [YYYY-MM-DD]
**Reviewer (independent):** [name]
**Confidentiality:** internal (client-confidential if real entity data)

---

## 1. Threshold question — is it insurance?

- [ ] Insurance / reinsurance / captive / ILS → **STOP. Route to `bermuda-insurance-specialist`** (this workpaper is non-insurance only).
- [ ] Non-insurance → continue.

## 2. Licensable activity → sector Act

Identify the **primary licensable activity** (not the entity's label). Tick all that apply — an entity can need multiple licences.

| Activity | Sector Act | Applies? |
|---|---|---|
| Takes deposits / lends from deposits | Banks and Deposit Companies Act 1999 | [ ] |
| Carries on the business of trustee | Trusts (Regulation of Trust Business) Act 2001 | [ ] |
| Company formation / nominee / resident-rep / corporate admin **for profit** | Corporate Service Provider Business Act 2012 (s.2(2)) | [ ] |
| Is itself a collective investment vehicle | Investment Funds Act 2006 | [ ] |
| Administers funds for others | Fund Administration Provider Business Act 2019 | [ ] |
| Deals / arranges / manages / advises / safeguards / promotes investments | Investment Business Act 2003 | [ ] |
| Money transmission / FX / cheque-cashing / payment services | Money Service Business Act 2016 | [ ] |
| Issues / exchanges / custodies digital assets | Digital Asset Business Act 2018 | [ ] |

**Multiple activities?** [ ] Yes → resolve each as a separate licensing question. [ ] No → single sector.

## 3. Licence class within the sector (the load-bearing sub-determination)

| Sector | Licence class options | This entity's class | Basis |
|---|---|---|---|
| Banking | banking / deposit company / restricted banking (s.14) | [ ] | [reasoning] |
| Trust | unlimited / limited (s.11) | [ ] | [limited = no sole-trustee + US$30m cap] |
| CSP | unlimited / limited | [ ] | [reasoning] |
| Investment fund | Authorised (Institutional/Administered/Specified-Jurisdiction/Standard) or Registered (Prof. Class A s.6A / Class B s.7 / Private / Prof. Closed) | [ ] | [qualified-participant test?] |
| Investment business | Licensed / Class A Registered / Class B Registered / Non-Registrable | [ ] | [Bermuda place of business? recognised foreign regulator?] |
| Digital assets | Class T / M / F | [ ] | [reasoning] |

## 4. Capital / net-asset position (per the class fixed above)

- **Applicable floor:** [figure + citation, e.g. "Trust corporate trustee US$250,000; Investment Business principal US$250,000 / agent US$100,000; DAB Class M/F US$100,000"]
- **Marked `[unverified]`?** [yes/no — if a figure carries `[unverified]` in the sector file, confirm against the Act PDF before relying]
- **Entity's current position vs floor:** [assessment]

## 5. AML/ATF determination

- [ ] Carries on a relevant financial-business activity → **AML/ATF-regulated financial institution** (POCA 1997 + AMLR 2008; BMA supervises under SE Act 2008).
- **Any licensing exemption (e.g. private trust company, CSP carve-out)?** [yes/no] — **if yes, note it does NOT remove AML/ATF obligations** (exempt PTCs are still AML/ATF-regulated FIs).
- **MLRO / Reporting Officer appointed?** [name / gap]
- **Business-wide + customer risk assessments documented?** [yes/gap]
- **Beneficial-ownership:** gatekeeper fitness check at **10%**; statutory BO definition at **25%** (BO Act 2025; register held by the RoC). [findings]

## 6. Filing & supervisory obligations

- **Periodic filing(s):** [per [`../knowledge/bma/supervision-and-filings.md`](../knowledge/bma/supervision-and-filings.md), e.g. quarterly prudential return (bank), annual Certificate of Compliance + audited financials (trust/IB/fund)]
- **Annual fee:** [figure if known — many non-insurance figures are `[unverified]`]; due **on/before 31 March**.
- **Change-of-control regime:** shareholder-controller bands 10/20/33/50%; notification within 45 days (recognised-exchange exception).
- **OpRes/cyber codes in scope?** [banks comply by 1 Jan 2027; other registrants 31 Mar 2028]

## 7. Conclusion

- **Sector + licence class:** [statement]
- **AML/ATF status:** [regulated / exempt-licence-but-still-AML / out-of-scope-with-basis]
- **Open questions for counsel:** [licence eligibility, statutory interpretation, structuring]
- **Citations relied on:** [Act + section for each; flag every `[unverified]` pin]

---

**Sources:** the BMA sector files under [`../knowledge/bma/`](../knowledge/bma/) and the classification trees in [`../knowledge/bma/decision-trees.md`](../knowledge/bma/decision-trees.md). Confirm every `[unverified]` section/figure against the Act PDF before this workpaper gates a live decision.
