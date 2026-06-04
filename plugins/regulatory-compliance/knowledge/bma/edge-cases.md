# BMA edge cases — the non-obvious determinations that get advisers wrong

> **Last reviewed:** 2026-06-04. A curated catalogue of the **tricky boundary conditions** in BMA non-insurance regulation — the situations where the obvious answer is wrong. Each entry: the **situation**, the **trap**, the **correct treatment**, and the **cite / source file**. The `bma-financial-institutions-specialist` scans this when a fact pattern feels like a corner case. Grounded entirely in the other `knowledge/bma/` files — every `[unverified]` marker there carries through here; confirm against the Act PDF before a corner-case call gates a live decision.

Use this **after** the [`decision-trees.md`](decision-trees.md) classification — these are the cases where the tree's clean leaf hides a gotcha.

---

## A. Scope & licensing edges

### A1 — One entity, multiple licences
**Situation:** a trust company that also provides corporate services; a fund manager that also deals as principal.
**Trap:** assuming a single licence covers the whole business.
**Correct:** each **licensable activity** is a separate licensing question — an entity can hold several BMA licences. A Non-Registrable-Person or exemption status under one Act does **not** transfer to another. *(See [`decision-trees.md`](decision-trees.md) STACK leaf.)*

### A2 — A fund is *not* an investment-business licensee, but its manager may be
**Situation:** classifying a Bermuda fund and its investment manager.
**Trap:** licensing the fund under the Investment Business Act.
**Correct:** an **investment fund is a Non-Registrable Person under the IBA 2003** (Order 2022). But a **Professional Class A fund's investment manager must be licensed under the IBA 2003 or authorised by a BMA-recognised foreign regulator** — that manager-status test is what distinguishes Class A from Class B. *(See [`fund-administration.md`](fund-administration.md), [`investment-business.md`](investment-business.md).)*

### A3 — Digital asset business doing ancillary investment business
**Situation:** a DABA licensee that also touches investment-business activities.
**Trap:** requiring a separate IBA licence.
**Correct:** a **DABA 2018 licensee is a Non-Registrable Person under the IBA** for ancillary investment business. *(See [`investment-business.md`](investment-business.md), [`msb-and-digital-assets.md`](msb-and-digital-assets.md).)*

### A4 — Restricted banking licence is not "no high-street, no customers"
**Situation:** a restricted bank's permitted client base.
**Trap:** assuming a restricted bank can serve anyone, or no one.
**Correct:** the restricted licence has **no high-street minimum-services obligation**, and the Banks Act Amendment Order extended permitted clients to **Casino Gaming Act 2014 casinos** and persons **"not ordinarily resident… in Bermuda."** Initial net assets **US$5m** (vs US$10m full bank) `[confirm vs Act]`. *(See [`banking.md`](banking.md).)*

### A5 — Money service business: the ancillary-service and bank carve-outs
**Situation:** a firm that incidentally provides a money-service-listed activity.
**Trap:** licensing every firm that touches FX or payments.
**Correct:** a listed service provided **ancillary without a separate charge** is "not likely" in scope; **banks licensed under the BDCA 1999 are exempt** from MSB licensing. *(See [`msb-and-digital-assets.md`](msb-and-digital-assets.md).)*

### A6 — Specified Jurisdiction Fund is Minister-recognised, not self-classified
**Situation:** an authorised-fund class for a recognised non-Bermuda regime.
**Trap:** treating it like the other authorised classes.
**Correct:** a **Specified Jurisdiction Fund** depends on the **Minister of Finance, by Order, recognising** the non-Bermuda jurisdiction and applicable law — it is not a self-selected class. *(See [`fund-administration.md`](fund-administration.md).)*

### A7 — Fund administration: IFA Part III vs FAPB Act 2019
**Situation:** licensing a fund administrator.
**Trap:** citing only one instrument.
**Correct:** the historical pathway sits in **Part III of the IFA 2006**, now framed by the **Fund Administration Provider Business Act 2019** (min net assets US$50,000). Cite the current framing. *(See [`fund-administration.md`](fund-administration.md).)*

---

## B. AML/ATF edges

### B1 — A licensing exemption is not an AML exemption
**Situation:** an exempt private trust company, or a CSP-Act carve-out.
**Trap:** "exempt from the licence → no AML obligations."
**Correct:** since 2018, **exempt PTCs are AML/ATF-regulated financial institutions**; full CDD/EDD/MLRO/FIA-reporting apply. *(Best-practice: `bma-a-licensing-exemption-is-not-an-aml-exemption`; [`aml-atf.md`](aml-atf.md), [`trust.md`](trust.md).)*

### B2 — Reinsurance is out of AML scope; long-term (life) insurance is in
**Situation:** AML scoping an insurance-adjacent entity.
**Trap:** treating all insurance the same for AML.
**Correct:** the BMA-supervised AML/ATF-regulated population includes **long-term (life) insurers, insurance managers and brokers carrying on long-term business — but NOT reinsurance.** A sharp scope line. *(See [`aml-atf.md`](aml-atf.md).)*

### B3 — Digital asset CDD triggers at a *lower* threshold
**Situation:** the occasional-transaction CDD trigger for a DAB.
**Trap:** applying the general occasional-transaction threshold.
**Correct:** the **digital asset business CDD trigger is USD 1,000** (single/linked) per the BMA DAB sectoral annex — lower than the general threshold (which is itself `[unverified]` for Bermuda). *(See [`aml-atf.md`](aml-atf.md).)*

### B4 — Which regulation numbers are actually confirmable
**Situation:** citing an AMLR 2008 regulation number.
**Trap:** quoting a precise reg number as settled because a law-firm guide used it.
**Correct:** only **POCA s.42A/46/47/49, SEA Act s.11A, and AMLR Reg 11 / Reg 11(1)(aa)** are verbatim-confirmed; the CDD/SDD/record-keeping cluster numbers are **indicative `[unverified]`** — cite them as such. *(See [`aml-atf.md`](aml-atf.md).)*

### B5 — Non-financial AML businesses aren't the BMA's
**Situation:** AML for real estate, gaming, high-value-goods dealers, lawyers/accountants.
**Trap:** routing them to the BMA.
**Correct:** those are supervised by the **Registrar of Companies / Superintendent of Real Estate / Casino Gaming Commission / Barristers & Accountants AML/ATF Board** — not the BMA. *(See [`aml-atf.md`](aml-atf.md), [`overview.md`](overview.md).)*

---

## C. Beneficial-ownership edges

### C1 — 10% gatekeeper vs 25% statutory
**Situation:** a holder between 10% and 25%.
**Trap:** using one number for both purposes.
**Correct:** **10%** triggers the CSP gatekeeper fitness check; **25%** is the statutory beneficial-owner definition (BO Act 2025). A 10–25% holder is screened but not (on the percentage test alone) a registrable beneficial owner. *(Best-practice: `bma-keep-the-10-and-25-percent-bo-thresholds-distinct`; [`corporate-services.md`](corporate-services.md).)*

### C2 — The BO register moved BMA → RoC in 2025
**Situation:** where the central beneficial-ownership register sits.
**Trap:** advising the BMA holds it.
**Correct:** the **Beneficial Ownership Act 2025** moved the central register to the **Registrar of Companies** (ROC enforcement from 1 Jun 2026); the BMA-held register is legacy. *(See [`overview.md`](overview.md), [`corporate-services.md`](corporate-services.md).)*

### C3 — "Control by other means" overrides the percentage
**Situation:** a sub-25% holder who nonetheless controls.
**Trap:** clearing them because they're under 25%.
**Correct:** the 25% test is the **first, not the only** route — control by other means, or the senior managing official fallback, can make someone a beneficial owner regardless of percentage.

---

## D. Capital / prudential edges

### D1 — Pillar 2 (CARP) can require capital above the Pillar 1 minimums
**Situation:** a bank that meets CET1/Tier1/Total minimums.
**Trap:** concluding it is adequately capitalised on Pillar 1 alone.
**Correct:** the BMA's **Capital Assessment and Risk Profile (CARP)** (Pillar 2) lets the BMA **prescribe capital above** the Pillar 1 minimums per the bank's risk profile; D-SIB buffers (0.5–3%) add further. *(See [`banking.md`](banking.md).)*

### D2 — Solvency II equivalence is insurance-only
**Situation:** a cross-border banking/funds group invoking "Bermuda equivalence."
**Trap:** transferring Solvency II equivalence to non-insurance capital reasoning.
**Correct:** **Solvency II equivalence is an insurance regime** (route to `bermuda-insurance-specialist`); it does not carry into banking, funds, or investment-business capital. *(See [`overview.md`](overview.md).)*

### D3 — Don't quote an `[unverified]` Bermuda figure as settled
**Situation:** any capital/net-asset/fee figure.
**Trap:** stating a number from a sector file that carries `[unverified]`.
**Correct:** confirm against the Act / Final Rule / 2025 Fees PDF first — many non-insurance fee figures and some section numbers are `[unverified]` (BMA sites 403 the fetch backend).

---

## E. Tax-transparency edges (non-BMA-administered)

### E1 — €750m appears in three regimes with *different* consolidation tests
**Situation:** a large group hitting €750m.
**Trap:** applying one threshold test to all three.
**Correct:** **CbCR** uses **prior single year**; **CIT** uses **≥2 of the preceding 4 years**; Pillar Two tracks the GloBE test. Same number, different gate. *(See [`economic-substance-and-tax.md`](economic-substance-and-tax.md).)*

### E2 — Economic substance: pure-equity-holding reduced test vs high-risk-IP heightened test
**Situation:** classifying an in-scope entity's substance burden.
**Trap:** applying the full five-limb test to everything.
**Correct:** a **pure equity holding entity** has a **reduced test** (adequate people + premises only); **high-risk IP** faces a **heightened test** + a rebuttable presumption of non-compliance + **spontaneous information exchange** with owner jurisdictions. *(See [`economic-substance-and-tax.md`](economic-substance-and-tax.md).)*

### E3 — The administering body is not the BMA
**Situation:** routing an economic-substance / CRS / CIT question.
**Trap:** treating these as BMA filings.
**Correct:** **economic substance → Registrar of Companies; CRS/FATCA/CbCR → Office of the Tax Commissioner; corporate income tax → Corporate Income Tax Agency.** A BMA licensee carries all of these in parallel with its BMA prudential obligations. *(See [`economic-substance-and-tax.md`](economic-substance-and-tax.md).)*

### E4 — FATCA reports direct to the IRS (Model 2)
**Situation:** a Bermuda FFI's FATCA route.
**Trap:** routing US-FATCA through the Bermuda portal.
**Correct:** Bermuda is a **US Model 2 IGA** — FFIs report **directly to the IRS**, not via the Bermuda portal (which handles CRS/CbCR/UK-FATCA). *(See [`economic-substance-and-tax.md`](economic-substance-and-tax.md).)*

---

## F. Procedural edges

### F1 — The conduct-of-business regime runs through sector codes, not a standalone instrument
**Situation:** citing a "Conduct of Business Rules" instrument.
**Trap:** asserting a standalone instrument exists.
**Correct:** the Aug-2022 conduct mandate is delivered via **per-sector codes of conduct**; **whether discrete standalone "Conduct of Business Rules" have been *made* is `[unverified]`** — don't assert it. *(See [`investment-business.md`](investment-business.md).)*

### F2 — The enforcement appeal forum is in transition
**Situation:** advising on appealing a BMA decision.
**Trap:** stating the Appeal Tribunal route as current.
**Correct:** the reform **removes the Tribunal and sends BMA decisions to the Supreme Court**; commencement date `[unverified]` — **confirm the current forum at time of use.** *(See [`supervision-and-filings.md`](supervision-and-filings.md).)*

### F3 — Don't apply a US MRA/MRIA ladder to a BMA communication
**Situation:** classifying the severity of a BMA supervisory letter.
**Trap:** mapping it to the US MRA/MRIA timeline.
**Correct:** the BMA's response expectations are set in its **letter + the underlying rule**; use [`../regulator-finding-severity-triage.md`](../regulator-finding-severity-triage.md), not a US ladder.

### F4 — Change-of-control: the 45-day clock is verified for insurance, inferred elsewhere
**Situation:** a non-insurance change-of-controller notification.
**Trap:** stating "45 days" as settled cross-sector.
**Correct:** the **45-day post-completion notification (recognised-exchange route) is firmly verified for insurance**; cross-sector application is a strong inference `[unverified]` — confirm against the sector Act. *(See [`supervision-and-filings.md`](supervision-and-filings.md).)*

---

## How the agent uses this file

When a fact pattern feels like a corner case, scan this catalogue **after** the classification trees. Each entry points to the source file carrying the full context + citation. **The recurring meta-lesson:** a BMA "edge case" is almost always (a) a scope boundary the obvious label crosses, (b) an exemption that doesn't extend to AML, (c) a threshold that means different things in different regimes, or (d) an `[unverified]` figure quoted as settled. When in doubt, confirm against the primary PDF and flag the uncertainty rather than guessing.

## See also

- [`decision-trees.md`](decision-trees.md) — the classification trees these edges sit on top of
- All `knowledge/bma/` sector + cross-cutting files (each edge cites its source)
- Best-practices: `bma-classify-the-sector-and-licence-before-you-advise`, `bma-a-licensing-exemption-is-not-an-aml-exemption`, `bma-keep-the-10-and-25-percent-bo-thresholds-distinct`
