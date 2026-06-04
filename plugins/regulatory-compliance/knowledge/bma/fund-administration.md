# BMA Investment Funds & Fund Administration — Investment Funds Act 2006 / Fund Administration Provider Business Act 2019

> **Last reviewed:** 2026-06-04. Primary-source map of the Bermuda Monetary Authority's (BMA) **investment-funds** and **fund-administration** regimes for the `bma-financial-institutions-specialist`. **Refresh when** (a) the IFA fund classes, thresholds, or "qualified participant" tests change; (b) a new Code of Conduct or fee schedule is issued; (c) any `[unverified]` marker is resolved against the Act/Guidance PDF.
>
> **Sourcing caveat:** every BMA PDF returned **HTTP 403 to direct fetch** during the build sweep, so the substance below is triangulated from BMA search-indexed content + multiple independent law-firm compendiums (Conyers, Appleby, Harneys, Carey Olsen). **Exact section numbers and current-year monetary thresholds must be confirmed against the source PDFs** before a cite gates live advice. Code-of-Conduct dates are inferred from `cdn.bma.bm` filename timestamps and should be confirmed on the document cover page.

One of five BMA sector files; see [`overview.md`](overview.md) for the cross-sectoral AML/sanctions/enforcement frame.

---

## A) Investment Funds

### Governing instruments

| Instrument | Year | Role | URL |
|---|---|---|---|
| **Investment Funds Act 2006** (2006:37) | 2006 | Primary fund statute ("IFA") | https://cdn.bma.bm/documents/2023-12-05-15-25-13-Investment-Funds-Act-2006.pdf |
| **Investment Funds Amendment Act 2019** | 2019 | Operative **1 Jan 2020**; brought closed-ended & overseas funds into scope | https://bermudalaws.bm |
| **Incorporated Segregated Accounts Companies Act 2019 (ISAC Act)** | 2019 | Separate-legal-personality segregated-account vehicle `[unverified statute URL]` | — |
| **Guidance Notes — Professional Class A and B Investment Funds** | 2019 | Class A/B registration detail | https://cdn.bma.bm/documents/2019-04-09-04-20-40-Guidance-Notes---Professional-Class-A-and-Professional-Class-B-Investment-Funds.pdf |

### Fund classification

A vehicle (company, partnership, LLC, unit trust) meeting the IFA "investment fund" definition is either **Authorised** or **Registered**.

**Authorised funds (four classes):**
- **Institutional Fund** — qualified participants or participants investing **≥ US$100,000**; needs a Bermuda officer/trustee/resident representative with access to books and records.
- **Administered Fund** — must appoint a **Part III**-licensed fund administrator and either require **≥ US$50,000** minimum investment **or** list on a BMA-recognised exchange.
- **Specified Jurisdiction Fund** — the Minister of Finance, by Order, recognises the non-Bermuda jurisdiction/applicable law.
- **Standard Fund** — residual class; may include retail; most comprehensive supervision.

**Registered funds:**
- **Professional Class A Fund** — registration under **s.6A(2) `[unverified]`**; qualified participants only; **investment manager must be licensed under the Investment Business Act 2003 or authorised by a BMA-recognised foreign regulator** (this manager-status test is what distinguishes A from B).
- **Professional Class B Fund** — registration under **s.7(2) `[unverified]`**; qualified participants; lighter manager test.
- **Private Fund** — **fewer than 20 investors**, no public promotion.
- **Professional Closed Fund** — closed-ended class added by the 2019 reform.

**"Qualified participant" (s.9(2)/(3) `[unverified]`):** income **> US$200,000** (individual) in each of the two preceding years, or **> US$300,000** jointly with spouse; **or** net worth **> US$1m**; **or** a sophisticated private investor. [verified via BMA Guidance Notes excerpt]

### 2020 reform (Amendment Act 2019)

- **Closed-ended funds** brought into scope — must be authorised/registered in an existing class or registered as **Professional Closed Fund** (six-month transition for existing funds).
- **Overseas funds** managed/promoted in or from Bermuda must be **designated as an Overseas Fund** by the BMA.
- **ISAC Act 2019** lets open- and closed-ended strategies sit in one vehicle with statutory ring-fencing and **separate legal personality** per account.

### Key obligations

Operators appoint an **officer/operator/resident representative** with book-and-record access plus required service providers — **fund administrator, custodian/prime broker, auditor**, and (for Professional funds) an **investment manager**. Offering document/**prospectus**, **NAV/valuation** policy, annual **audited financials**, and ongoing BMA **reporting** are required `[unverified — exact IFA section numbers]`. Annual fees (per BMA schedule): Professional Class A **≈ US$1,500/yr**, Class B **≈ US$1,000/yr** `[verify against 2025 fee schedule]`.

---

## B) Fund Administration

| Instrument | Year | Role | URL |
|---|---|---|---|
| **Fund Administration Provider Business Act 2019** | 2019 | Licensing of fund administrators ("FAPB Act") | https://www.bma.bm/viewPDF/documents/2023-11-14-13-25-01-Fund-Administration-Provider-Business-Act-2019.pdf |
| **Code of Conduct for Fund Administrators** | publ. **29 Dec 2018** `[date inferred from filename]` | Binding code on licensed administrators | https://cdn.bma.bm/documents/2018-12-29-04-26-03-Code-of-Conduct-for-Fund-Administrators.pdf |

- Entities carrying on **fund administration in or from Bermuda must be licensed**; the historical licensing pathway sits in **Part III ("Fund Administrators") of the IFA**, now framed by the FAPB Act 2019.
- **Minimum licensing criterion** includes corporate-governance policies, **AML/ATF policies compliant with the Proceeds of Crime (AML/ATF) Regulations 2008**, and a **minimum net asset requirement of US$50,000**. Licence application fee **≈ US$8,270** `[verify against 2025 schedule]`.
- The BMA may issue **codes of conduct** binding on licensed administrators; every licensed administrator must comply.

---

## Supervision & powers

The BMA runs a **risk-rated** supervisory programme (onsite + offsite), can impose conditions, issue directions, vary/cancel authorisation or licences, and issue statements of principles and codes.

## Key thresholds & numbers (confidence)

- Authorised classes: Institutional / Administered / Specified-Jurisdiction / Standard — [verified]
- Registered classes: Professional Class A (s.6A) / Class B (s.7) / Private / Professional Closed — [verified; section #s `[unverified]`]
- Institutional Fund min investment **US$100,000**; Administered Fund **US$50,000** (or recognised-exchange listing) — [verified]
- Private Fund **< 20 investors**, no public promotion — [verified]
- Qualified participant: income > US$200k single / > US$300k joint; net worth > US$1m — [verified via Guidance Notes]
- Fund administrator min net assets **US$50,000** — [verified]
- Professional Class A annual fee ≈ US$1,500; Class B ≈ US$1,000 — `[verify 2025 schedule]`

## How the agent uses this file

`bma-financial-institutions-specialist` reads this before any funds / fund-admin answer. **Fund class drives obligation** — an Institutional Fund's officer/resident-rep requirement ≠ an Administered Fund's licensed-administrator requirement ≠ a Standard Fund's full supervision. Never quote a threshold or section number marked `[unverified]` as settled. Investment-manager licensing of a Professional Class A fund's manager hands to [`investment-business.md`](investment-business.md). AML/sanctions frame: [`overview.md`](overview.md).

## Primary-source URL list

- https://cdn.bma.bm/documents/2023-12-05-15-25-13-Investment-Funds-Act-2006.pdf
- https://www.bma.bm/viewPDF/documents/2023-11-14-13-25-01-Fund-Administration-Provider-Business-Act-2019.pdf
- https://cdn.bma.bm/documents/2018-12-29-04-26-03-Code-of-Conduct-for-Fund-Administrators.pdf
- https://cdn.bma.bm/documents/2019-04-09-04-20-40-Guidance-Notes---Professional-Class-A-and-Professional-Class-B-Investment-Funds.pdf
- https://www.bma.bm/investment-funds-supervision-regulation
- https://www.bma.bm/fund-administration-supervision-regulation
- https://cdn.bma.bm/documents/2025-01-13-09-37-05-2025-Bermuda-Monetary-Authority-Fees.pdf
