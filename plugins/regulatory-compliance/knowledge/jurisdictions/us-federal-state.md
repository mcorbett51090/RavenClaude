# United States — Federal & State Financial-Regulatory Framework

> **Last reviewed:** 2026-06-04. Primary-source map of the US "alphabet soup" for the `us-financial-regulation-specialist`. **Time-sensitive:** the **CTA/BOI** position rests on an *interim* final rule + active litigation — re-verify before relying. **Refresh when** the BOI final rule lands, a FATF plenary changes lists, or any `[unverified — training knowledge]` statute pin is confirmed.
>
> **Sourcing note:** consequential thresholds were verified this session; statute citations marked `[unverified — training knowledge]` are high-confidence standard references not independently re-fetched.

The US is the most **fragmented** regime in this plugin — functional + dual federal/state, no single integrated regulator (the opposite of the BMA/CIMA model). **Identify the charter and activity first**, then the regulator follows.

---

## US regulator directory

| Regulator | Supervises | Primary statute | URL |
|---|---|---|---|
| **Federal Reserve (FRB)** | Bank holding companies, savings-&-loan holding cos, state member banks, US ops of foreign banks, designated nonbank SIFIs; enhanced prudential standards | Bank Holding Company Act 1956 (12 USC 1841 et seq.); Federal Reserve Act 1913; Dodd-Frank Title I. Regs **K** (12 CFR 211), **YY** (12 CFR 252) | federalreserve.gov |
| **OCC** | National banks, federal savings associations (thrifts), federal branches of foreign banks | National Bank Act 1864 (12 USC 1 et seq.) | occ.gov |
| **FDIC** | Deposit insurance (DIF); state non-member banks; failed-bank resolution; OLA backup | Federal Deposit Insurance Act (12 USC 1811 et seq.); Dodd-Frank Title II | fdic.gov |
| **NCUA** | Federal credit unions; share-insurance fund | Federal Credit Union Act (12 USC 1751 et seq.) | ncua.gov |
| **CFPB** | Consumer financial products; UDAAP | Dodd-Frank Title X (12 USC 5481 et seq.) | consumerfinance.gov |
| **FinCEN** (Treasury) | AML/CFT administrator; BSA rules; SAR/CTR receipt; BOI registry | Bank Secrecy Act (31 USC 5311 et seq.); USA PATRIOT Act; Corporate Transparency Act (31 USC 5336) | fincen.gov |
| **OFAC** (Treasury) | Economic & trade sanctions; SDN List; blocking; licensing | IEEPA (50 USC 1701 et seq., §1702); TWEA | ofac.treasury.gov |
| **SEC** | Securities issuers, exchanges, broker-dealers, investment advisers, funds | Securities Act 1933; Securities Exchange Act 1934; Investment Advisers Act 1940; Investment Company Act 1940 `[unverified — training knowledge]` | sec.gov |
| **FINRA** | SRO for broker-dealers (under SEC oversight) | Securities Exchange Act 1934 §15A; **Rule 3310** (AML), **Rule 2111** (suitability); **Reg BI** is SEC rule 17 CFR 240.15l-1 | finra.org |
| **CFTC** | Derivatives — futures, options, swaps | Commodity Exchange Act (7 USC 1 et seq.); Dodd-Frank Title VII. SRO: **NFA** | cftc.gov |
| **NYDFS** (state) | NY-chartered banks, insurers, virtual-currency firms; AML monitoring certification; BitLicense | NY Financial Services Law; **23 NYCRR Part 200** (BitLicense); **3 NYCRR Part 504** (transaction monitoring) | dfs.ny.gov |
| **State securities / NASAA** | State securities registration & enforcement | State blue-sky laws; Uniform Securities Act; NSMIA 1996 preemption | nasaa.org |
| **FSOC** | Systemic-risk monitoring; SIFI / FMU designation | Dodd-Frank Title I (12 USC 5321 et seq.) | treasury.gov (FSOC) |

---

## The BSA/AML stack

- **Dual mandate:** FinCEN writes the rules under the BSA; the federal banking agencies (FRB/OCC/FDIC/NCUA) and FINRA/CFTC examine for compliance via the **FFIEC BSA/AML Examination Manual**.
- **Core filings:** **CTR** for cash transactions **> $10,000** (single or aggregated same-day), e-filed within **15 days**; **SAR** for known/suspected suspicious activity, incl. **structuring** to evade the CTR threshold (bank SAR threshold generally **$5,000** aggregate; **$25,000** with no suspect identified `[$25,000 tier = training knowledge]`).
- **2025 SAR guidance:** FinCEN + banking agencies clarified that activity merely *at or near* the $10,000 CTR line does **not** by itself require a SAR absent knowledge/suspicion of evasion.
- **Five pillars:** designated officer, internal controls, independent testing, training, and risk-based CDD/beneficial-ownership (the 2016 CDD Rule "5th pillar").
- **Sanctions overlay:** OFAC screening is separate from BSA but operationally bundled; the **50% Rule** blocks any entity **≥50%-owned** (aggregate, direct or indirect) by blocked persons even if **not itself on the SDN List**.

---

## Corporate Transparency Act / BOI status (⚠ verify before relying)

- **Statute:** CTA, **31 USC 5336**, enacted Jan 2021 (AML Act of 2020).
- **March 2025 interim final rule:** FinCEN **removed BOI reporting for all US-formed entities and US persons**; "reporting company" was **narrowed to foreign entities** registered to do business in the US (which report, but **need not report US-person beneficial owners**).
- **Litigation:** on **16 Dec 2025** the **Eleventh Circuit** held the CTA a constitutional exercise of the Commerce Clause, reversing the district court. **Practical effect unchanged:** the domestic-exemption interim rule remains in force; a final rule was delayed. **Net: most US companies currently have no BOI filing obligation; foreign reporting companies do — but this could shift.** [verified — re-verify each engagement]

## Key thresholds & numbers (confidence)

- **CTR:** currency transactions **> $10,000**, e-filed within **15 days** — [verified]
- **SAR (structuring/evasion):** file when transactions aggregating **$5,000+** designed to evade BSA reporting — [verified]
- SAR general bank threshold **$5,000** (suspect identifiable) / **$25,000** (no suspect) — [$5,000 verified; $25,000 training knowledge]
- **OFAC 50% Rule:** entity blocked if blocked persons own **≥50%** aggregate — [verified]
- **NYDFS Part 504 certification:** annual, due **15 Apr** for the prior calendar year — [verified]

## How the agent uses this file

`us-financial-regulation-specialist` reads this before any US answer. **Identify the charter (national/state, bank/CU/BD/IA) and the activity first** — the regulator follows from those, not the other way around. **The CTA/BOI position is live and litigation-shaped — never state the BOI obligation as settled without re-verifying.** AML supervision is split FinCEN-rules / functional-regulator-exams. International standard-setters that bind both the US and the offshore centres: [`global-regulator-directory.md`](global-regulator-directory.md).

## Primary-source URL list

- Federal Reserve — https://www.federalreserve.gov · OCC — https://www.occ.gov · FDIC — https://www.fdic.gov · NCUA — https://www.ncua.gov
- CFPB — https://www.consumerfinance.gov
- FinCEN — https://www.fincen.gov · BOI — https://www.fincen.gov/boi
- FinCEN BOI IFR (Mar 2025) — https://www.fincen.gov/news/news-releases/fincen-removes-beneficial-ownership-reporting-requirements-us-companies-and-us
- OFAC — https://ofac.treasury.gov · SEC — https://www.sec.gov · FINRA — https://www.finra.org · CFTC — https://www.cftc.gov
- NYDFS — https://www.dfs.ny.gov · Part 504 — https://www.dfs.ny.gov/industry_guidance/transaction_monitoring
- NASAA — https://www.nasaa.org · FSOC — https://home.treasury.gov/policy-issues/financial-markets-financial-institutions-and-fiscal-service/fsoc
