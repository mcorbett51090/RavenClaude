# Basel Framework — Cross-Jurisdictional Prudential Reference (BCBS)

> **Last reviewed:** 2026-06-04. The **canonical Basel reference** for every banking-touching agent in this plugin (`bma-financial-institutions-specialist`, `cima-cayman-specialist`, `uk-pra-specialist`, `bahamas-financial-services-specialist`, `us-financial-regulation-specialist`, `risk-and-controls-specialist`, `regulatory-reporting-analyst`). The jurisdiction files state how each regulator **implements** Basel; this file is the **standard itself** so the per-jurisdiction files don't each re-derive it. **Time-sensitive:** the Basel III finalisation ("Basel 3.1 / endgame") implementation dates differ by jurisdiction and several are still moving — see §7, every date there is pinned.
>
> **Sourcing caveat:** this file is authored from **well-established, training-stable BCBS framework knowledge** (the three-pillar architecture, the capital stack, the Pillar-1 minimum ratios, the buffers, LCR/NSFR, the leverage ratio, the output floor) — these are foundational and corroborated across the BCBS consolidated framework, national rulebooks, and the jurisdiction files already in this plugin. **The jurisdiction-specific *implementation dates* in §7 are the fast-moving layer; they were verified 2026-06-04 against primary/authoritative sources** (EUR-Lex OJ for the EU FRTB postponement, Bank of England PS1/26 for the UK, the joint FRB/OCC/FDIC NPRs for the US re-proposal) and now carry `[verified 2026-06-04 …]` tags. The one genuinely open item is the **US final rule**, which was still at the proposal stage on that date — re-confirm before it gates advice to a US bank. Ratios and buffer levels in §2–§5 are the BCBS minimums and are stable.
>
> **The one rule that governs everything below:** **BCBS standards have no legal force.** They are *minimums* agreed by the Basel Committee; only **national implementation binds**, and national authorities routinely **go stricter** ("gold-plating") or apply a **proportionate / simplified** regime to smaller banks. Always cite the *implementing instrument* (PRA Rulebook, EU CRR, BMA Basel III for Bermuda Banks, CIMA rules, US Reg Q/Capital Rule), never "Basel says," when advising a specific firm.

---

## 1. Architecture — the three Pillars

| Pillar | Name | What it is | Where it bites |
|---|---|---|---|
| **Pillar 1** | Minimum capital requirements | The formula-driven **minimum capital and liquidity** a bank must hold against **credit, market, and operational risk** (RWA-based), plus the leverage ratio and LCR/NSFR | The hard ratios in §2–§5 |
| **Pillar 2** | Supervisory review | The bank's own **ICAAP/ILAAP** + the supervisor's **review** (SREP in the EU/UK) → bank-specific **add-ons** (P2R) and **guidance** (P2G) for risks Pillar 1 under-captures (IRRBB, concentration, model risk, pension, etc.) | §6 — the firm-specific layer |
| **Pillar 3** | Market discipline | Standardised **public disclosure** of capital, RWA, leverage, liquidity, and risk so the market can price the bank | Disclosure templates; cross-references Pillar 1 numbers |

The three pillars are **cumulative, not alternatives** — a bank meets Pillar 1, *then* carries any Pillar 2 add-on on top, *then* discloses both under Pillar 3.

---

## 2. The capital stack — what counts as capital

Capital is tiered by **loss-absorbing quality** (highest quality first):

| Tier | Component | Defining feature | Key instruments |
|---|---|---|---|
| **CET1** | Common Equity Tier 1 | Highest quality; absorbs losses **on a going-concern basis** first | Common shares, retained earnings, other comprehensive income, **minus regulatory deductions** (goodwill, intangibles, DTAs, etc.) |
| **AT1** | Additional Tier 1 | Going-concern; **perpetual**, discretionary coupons, **loss-absorbing** (write-down or equity-conversion trigger) | Perpetual non-cumulative instruments; "CoCos"/AT1 bonds |
| **T2** | Tier 2 | **Gone-concern** (absorbs losses in resolution/liquidation) | Subordinated debt ≥5y original maturity, amortising in the final 5 years |

- **Tier 1 = CET1 + AT1** (going-concern capital).
- **Total capital = Tier 1 + Tier 2.**
- **Regulatory deductions** (goodwill, intangibles, deferred-tax-assets reliant on future profitability, significant investments in financial entities, etc.) come **off CET1** — this is where "Basel III made the definition of capital much stricter than Basel II" actually bites.

---

## 3. Pillar 1 minimum ratios + the buffer stack

All ratios are **capital ÷ risk-weighted assets (RWA)** unless stated otherwise. These are the **BCBS minimums** (stable):

| Requirement | Level | Quality required |
|---|---|---|
| **CET1 minimum** | **4.5%** | CET1 |
| **Tier 1 minimum** | **6.0%** | CET1 + AT1 |
| **Total capital minimum** | **8.0%** | CET1 + AT1 + T2 |
| **+ Capital Conservation Buffer (CCB)** | **2.5%** | **CET1** |
| **+ Countercyclical Buffer (CCyB)** | **0–2.5%** (national authority sets; can exceed) | **CET1** |
| **+ G-SIB / D-SIB surcharge** | **1.0–3.5%** G-SIB (buckets) / D-SIB set nationally | **CET1** |

**The numbers that matter in practice (minimum + CCB, the everyday "do not breach" line):**

- **CET1 ≥ 7.0%** (4.5% + 2.5% CCB)
- **Tier 1 ≥ 8.5%** (6.0% + 2.5% CCB)
- **Total capital ≥ 10.5%** (8.0% + 2.5% CCB)

…then **CCyB and any systemic surcharge stack on top of that**, all in CET1.

**Breaching the buffer (not the minimum) is not an immediate breach — it trips the MDA.** A bank operating **inside its combined buffer** faces **automatic distribution restrictions** via the **Maximum Distributable Amount (MDA)**: the deeper into the buffer, the larger the mandated cut to dividends, AT1 coupons, and bonuses (quartile-based scaling, 100% → 60% → 40% → 0% of earnings distributable across the four buffer quartiles). This is the mechanism that makes buffers "usable but expensive to use."

---

## 4. RWA — the denominator (where Basel 3.1 changes the most)

RWA is the sum of capital charges across three risk types, each with a **standardised** approach and (historically) an **internal-model** approach:

| Risk type | Standardised approach | Internal-model approach | Basel 3.1 change |
|---|---|---|---|
| **Credit risk** | SA — fixed/lookup risk weights | **IRB** (Foundation / Advanced) | A-IRB **removed for some portfolios** (banks/large corporates → F-IRB or SA); **input floors** on PD/LGD/EAD; revised SA risk weights |
| **Market risk** | Revised SA | Internal Models Approach (IMA) | **FRTB** (Fundamental Review of the Trading Book) — new SA + stricter IMA with the trading/banking-book boundary tightened |
| **Operational risk** | **SMA** (Standardised Measurement Approach) | — | **AMA and all prior op-risk approaches abolished**; single **SMA** based on a Business Indicator × an Internal Loss Multiplier |
| **CVA risk** | Revised SA-CVA / BA-CVA | — | Revised credit-valuation-adjustment framework |

**The output floor** is the headline Basel 3.1 constraint and the one to know cold:

> **A bank using internal models cannot report total RWA below 72.5% of what the standardised approaches would produce.** It caps the capital benefit a bank can extract from its own models at a 27.5% reduction vs. standardised.

The floor **phases in** (BCBS canonical schedule, post-COVID one-year deferral): **50% (2023) → 55% → 60% → 65% → 70% → 72.5% (2028)**. **Jurisdictions vary the start year and may run additional transitional reliefs** (the EU, for example, applies the FRTB-SA for the output-floor calc during its FRTB postponement — see §7) — confirm the applicable phase-in step in the implementing instrument before it gates a specific firm's number.

---

## 5. The non-RWA constraints — leverage + liquidity

These sit **alongside** the risk-weighted ratios as **backstops** (a bank must satisfy *all* of them — the binding constraint is whichever is tightest):

| Metric | Definition | Minimum | Purpose |
|---|---|---|---|
| **Leverage Ratio (LR)** | Tier 1 ÷ **total exposure measure** (on- + off-balance-sheet, **not** risk-weighted) | **3.0%** Tier 1 | Risk-insensitive backstop to the RWA ratios; catches model-driven RWA understatement. G-SIBs carry a **leverage buffer = 50% of their G-SIB risk-weighted surcharge** |
| **LCR** (Liquidity Coverage Ratio) | **HQLA ÷ net cash outflows over a 30-day stress** | **≥ 100%** | Short-term resilience — survive a 30-day acute stress on liquid assets alone |
| **NSFR** (Net Stable Funding Ratio) | **Available Stable Funding ÷ Required Stable Funding** (1-year horizon) | **≥ 100%** | Structural funding — discourage over-reliance on short-term wholesale funding |

- **HQLA** is tiered: **Level 1** (cash, central-bank reserves, high-quality sovereigns — no haircut, no cap), **Level 2A** (≤40% of HQLA, 15% haircut), **Level 2B** (≤15% of HQLA, 25–50% haircut).
- LCR and NSFR are **separate tests** — passing one says nothing about the other (LCR = 30-day acute; NSFR = 1-year structural).

---

## 6. Pillar 2 — the firm-specific layer (ICAAP / ILAAP / SREP)

Pillar 1 is one-size-fits-all; **Pillar 2 is where the supervisor tailors capital to the individual firm's risk profile.**

- **ICAAP** (Internal Capital Adequacy Assessment Process) — the **bank's own** assessment of *all* material risks and the capital it judges it needs, including risks Pillar 1 under- or doesn't capture: **IRRBB** (interest-rate risk in the banking book), **concentration risk**, **model risk**, **pension risk**, **strategic/reputational risk**, **stress-testing** outcomes.
- **ILAAP** — the liquidity-side equivalent (the bank's own liquidity-adequacy assessment).
- **SREP** (Supervisory Review and Evaluation Process — EU/UK term) — the **supervisor's** challenge of the ICAAP/ILAAP, producing firm-specific add-ons:
  - **P2R** (Pillar 2 Requirement) — **binding** add-on for risks under-captured by Pillar 1; a breach is a breach.
  - **P2G** (Pillar 2 Guidance) — **non-binding** buffer expectation above the combined buffer; sits **above** the MDA trigger so using it doesn't mechanically restrict distributions, but the supervisor expects it held.

> **Stacking order (the "capital stack" a CFO actually manages to):** Pillar 1 minimum → **P2R** → Combined buffer (CCB + CCyB + systemic) → **P2G**. The **MDA trigger sits at the top of the combined buffer** — i.e., P2R and Pillar 1 breaches are hard breaches; eating into the combined buffer trips the MDA; P2G is the soft top layer.

---

## 7. Basel III finalisation ("Basel 3.1" / "Basel IV" / "endgame") — implementation by jurisdiction

The BCBS finalised the post-crisis reforms in **Dec 2017** (FRTB market-risk piece **Jan 2019**). "Basel IV" is market shorthand — the BCBS calls it the **finalisation of Basel III**. The substance is in §4 (revised credit SA, IRB constraints, SMA op-risk, FRTB, revised CVA, **output floor**). **Implementation is national and the dates diverge** — this is the time-sensitive layer:

| Jurisdiction | Local name / instrument | Implementation date | Status |
|---|---|---|---|
| **BCBS standard** | "Basel III: Finalising post-crisis reforms" | Framework **1 Jan 2023**; output floor phase-in **to 2028** | The minimum the others implement `[stable]` |
| **EU** | **CRR3 / CRD6** | Bulk **1 Jan 2025**; **FRTB own-funds piece now 1 Jan 2027** | The FRTB market-risk go-live was postponed **a second time** — from 1 Jan 2026 to **1 Jan 2027** — by **Commission Delegated Regulation (EU) 2025/1496 (12 Jun 2025)**. In the interim, banks use pre-FRTB methodologies for own funds but the **FRTB-SA for the output-floor calc**; a draft delegated act adds 3-year targeted FRTB relief from 2027. `[verified 2026-06-04 — EUR-Lex OJ L 2025/1496]` |
| **UK** | **Basel 3.1** (PRA — **PS1/26**) | **1 Jan 2027** | **Confirmed** in **PS1/26 — *Implementation of Basel 3.1: Final rules*, published 20 Jan 2026** (delayed one year from 2026 by the PRA's 17 Jan 2025 announcement). Lands together with the **Strong & Simple SDDT** regime. `[verified 2026-06-04 — Bank of England PS1/26]` |
| **US** | **"Basel III Endgame"** (re-proposal) | **Re-proposed 19 Mar 2026; still at proposal stage — no final date** | The agencies (FRB/OCC/FDIC) issued **three NPRs** on **19 Mar 2026** — Basel III Endgame (Cat I/II), Standardised Approach amendments, and the Fed's G-SIB surcharge revamp — **comments due 18 Jun 2026**. Net effect is **capital-light vs. the 2023 version** (CET1 down ~4.8% Cat I/II, ~5.2% Cat III/IV, ~7.8% smaller banks); FRB advanced them 6–1. **No final rule or implementation date yet** — confirm status before advising a US bank. `[verified to 2026-06-04 — joint agency NPRs; final rule pending]` |
| **Offshore (BMA / CIMA / Bahamas)** | Local Basel adoption (often a **simplified / proportionate** Basel II or III) | Per local code | E.g. **Basel III for Bermuda Banks** (BMA); **Basel II** baseline at **CIMA** with higher CARs (12%/15%); **simplified Basel II/III** at the CBOB (Bahamas). See the jurisdiction files. |

> **Why this table earns the verify tags:** the *substance* of Basel 3.1 is stable, but **which year a given bank actually adopts which piece** is the single most error-prone fact in this domain — jurisdictions defer, phase, and carve out differently (the EU FRTB go-live alone has now slipped **twice**). The dates above were verified 2026-06-04, but they keep moving — **never quote an implementation date to a specific firm without re-confirming it against that jurisdiction's current policy statement / rulebook**, especially the **US final rule** (proposal-stage only as of 2026-06-04, comments due 18 Jun 2026).

---

## 8. Related standards that travel with Basel (don't conflate them)

| Standard | Body | What it is | Relationship to Basel |
|---|---|---|---|
| **Core Principles for Effective Banking Supervision** | BCBS | **29 principles** for *how a supervisor should supervise* (not capital levels) | Assessed in **IMF/World Bank FSAPs**; the yardstick for whether a *regulator* (BMA, CIMA, …) is credible |
| **Large Exposures framework** | BCBS | A bank's exposure to **one counterparty/group ≤ 25% of Tier 1**; **15%** between G-SIBs | A Pillar-1-adjacent concentration backstop — separate from the CET1 ratios |
| **TLAC** (Total Loss-Absorbing Capacity) | **FSB** (not BCBS) | G-SIBs hold **≥18% RWA / ≥6.75% leverage** of loss-absorbing instruments (since 2022) | **Resolution** standard, sits **above** regulatory capital; the EU/UK analogue is **MREL** |
| **G-SIB / D-SIB methodology** | BCBS / national | Size, interconnectedness, complexity, cross-jurisdictional activity, substitutability → systemic surcharge bucket | Sets the CET1 surcharge in §3 |
| **IRRBB** | BCBS | Interest-rate risk in the banking book — **a Pillar 2 risk** (standardised outlier test, not a Pillar 1 charge) | Handled in ICAAP/SREP, not the §3 minimums |

---

## 9. Quick-reference — the numbers to know cold

- **Pillar-1 minimums:** CET1 **4.5%** / Tier 1 **6%** / Total **8%** of RWA.
- **+ CCB 2.5% CET1** → everyday floors **CET1 7% / Tier 1 8.5% / Total 10.5%**.
- **+ CCyB 0–2.5%** and **+ G-SIB 1–3.5% / D-SIB national**, all CET1, on top.
- **Leverage ratio 3%** Tier 1 / exposure (backstop, not risk-weighted).
- **LCR ≥ 100%** (30-day) and **NSFR ≥ 100%** (1-year) — separate tests.
- **Output floor 72.5%** of standardised RWA (Basel 3.1, phasing to 2028).
- **Large exposures ≤ 25% Tier 1** (15% G-SIB-to-G-SIB).
- **Breaching a *buffer* (not a minimum) trips the MDA** → automatic distribution restrictions.
- **BCBS sets minimums; only national implementation binds — cite the implementing instrument, never "Basel says."**

---

## Cross-references (graceful degradation — these resolve only if the file/plugin is present)

- **In-plugin jurisdiction implementations:** [`jurisdictions/uk-pra.md`](jurisdictions/uk-pra.md) (Basel 3.1 / SDDT), [`bma/banking.md`](bma/banking.md) (Basel III for Bermuda Banks), [`jurisdictions/cima-cayman.md`](jurisdictions/cima-cayman.md) (Basel II + CIMA CARs), [`jurisdictions/bahamas.md`](jurisdictions/bahamas.md) (simplified Basel II/III), [`jurisdictions/global-regulator-directory.md`](jurisdictions/global-regulator-directory.md) (BCBS in the standard-setter map).
- **Pillar 2 tooling:** the `risk-register-build` skill consumes ICAAP/ILAAP risk identification (§6). The `risk-and-controls-specialist` owns the control mapping.
- **If the `finance` plugin is installed alongside:** its `controller` / `audit-prep-specialist` pair with capital-adequacy work where the *source data* (the RWA inputs, the capital reconciliation) needs close/controls assurance — but this file stands alone and assumes nothing about that plugin's presence.
