# Building WACC / Cost of Capital from Primary Sources, Defensibly

_A practitioner synthesis for DCF valuation — valuation analysts, financial modelers, FP&A. As-of 2026-06-04. Authored for a professional audience; not an introduction to CAPM._

## Method note

Research proceeded by a web-search fan-out across each WACC input (risk-free rate, ERP, beta, size premium, cost of debt, capital-structure weights, country-risk premium, and common errors), prioritizing primary/authoritative sources: Aswath Damodaran (NYU Stern data pages, SSRN ERP paper, Substack "Data Update" series), Kroll/Duff & Phelps (Cost of Capital Navigator, recommended-ERP reports, corroborated via Business Valuation Resources / BVWire), the AQR "Fact, Fiction, and the Size Effect" white paper, academic work on the size effect (Asness et al.; van Dijk's "Is Size Dead?"; McLean & Pontiff on post-publication decay), and valuation-firm/practitioner references (NACVA, ValuSource, QuickRead, Wall Street Prep, Macabacus, AnalystPrep). **Two domains hard-block WebFetch (HTTP 403): `kroll.com` and `pages.stern.nyu.edu` (and `aqr.com`).** For those, figures rest on search-result excerpts and secondary corroboration (BVResources for Kroll; multiple mirrors for Damodaran) and are tagged accordingly. **Every recommended figure here is as-of-dated and moves over time** — Damodaran re-computes the ERP monthly; Kroll re-issues ERP/risk-free guidance several times a year. Re-pull the source page on the valuation date; do not carry these numbers forward without refresh. Confidence tags: `[high]` = ≥2 independent authoritative sources; `[med]` = single authoritative source; `[unverified — training knowledge]`.

---

## 1. Risk-free rate

**The core rule: match the risk-free maturity to the duration of the cash flows you are discounting, then hold it constant across the model for internal consistency.** `[high]` (Damodaran riskfree.pdf; Wall Street Prep; StableBread). Because a going-concern DCF produces a long-dated (effectively perpetual) cash-flow stream, the relevant rate is a long government-bond yield, not a T-bill.

**Tenor — the practical fork:**

- **10-year US Treasury constant maturity** is the modal practitioner choice and Damodaran's stated default "if you don't want to compute cash-flow duration." `[high]` Rationale: it is the most liquid/efficiently-priced long bond, and it keeps the risk-free consistent with the 10-year horizon already embedded in other inputs (e.g., the maturity assumption commonly used for cost of debt). `[med]`
- **20-year US Treasury** is the tenor Kroll pairs with its recommended ERP and normalized risk-free guidance, and is defensible when the cash-flow duration is longer (most going concerns). `[high]` (Kroll recommended-ERP report, via BVResources.) Using the 20Y also avoids the modest liquidity distortions some attribute to the 30Y.
- **Avoid the 30-year** as a default — less liquid, and the on-the-run/off-the-run premium muddies it. `[med]`

**Source:** US Treasury daily par-yield (constant-maturity) curve, mirrored in the Federal Reserve H.15 release. `[high]` Use the spot yield on the valuation date.

**Spot vs. normalized — an active divergence:**

| View | Position | As-of / source |
|---|---|---|
| **Damodaran** | Use the **current spot** long-bond rate. The risk-free rate must reflect the actual opportunity cost available today; "normalizing" injects an analyst forecast and breaks internal consistency (spot rates already sit inside the observed ERP and market prices). | Ongoing; riskfree.pdf, Substack `[med]` |
| **Kroll / Duff & Phelps** | Use the **higher of** a **normalized** risk-free rate (currently **3.5%**) **or** the **spot 20-year Treasury** as of the valuation date. Normalization smooths central-bank-distorted/transient-low-rate regimes so the discount rate isn't artificially depressed. | Reaffirmed **2025-09-02** `[high]` (Kroll report via BVResources) |

**Practitioner judgment:** the spot-vs-normalized choice is *not* free — it must be paired consistently with the ERP. Kroll's 3.5% normalized rate is *designed* to be used with Kroll's 5.0% recommended ERP; mixing a Kroll normalized rate with a Damodaran implied ERP (which is built off spot rates) double-distorts. Pick a school and stay inside it (see §2).

---

## 2. Equity risk premium (ERP)

This is the single most consequential and most contested WACC input. Three schools, three philosophies:

### Consensus

All three schools agree the ERP is the expected return on equities over the risk-free rate, that it is not directly observable, and that the historical *arithmetic* mean of long realized excess returns is the naive anchor. They diverge on whether to trust history, smooth it, or back it out of today's prices.

### Divergent — the three schools

| School | Method | Current figure (as-of) | Confidence |
|---|---|---|---|
| **Damodaran — implied / forward** | Solve for the IRR that equates the S&P 500 level to expected future cash flows (dividends + buybacks + projected growth). Model-agnostic, re-computed monthly, reflects *today's* pricing. | **~4.23%** at the start of **2026** (over the US T-bond rate) | `[med]` (Damodaran "Data Update 2 for 2026"; histimpl page 403-blocked) |
| **Kroll / Duff & Phelps — recommended** | A reconciliation of multiple models (historical, supply-side, implied, surveys) plus judgment; published as a single "recommended" number to pair with their risk-free rate. | **5.0%** (USD discount rates), reaffirmed **2025-09-02**. Had been raised to **5.5%** on **2025-04-15** (tariff/trade volatility) then cut back to 5.0% in Sept 2025. | `[high]` (Kroll via BVResources/BVWire, two corroborating items) |
| **Historical / Ibbotson (now Kroll CRSP/SBBI)** | Long-run (1926–present) realized arithmetic mean of stock-minus-bond returns. The legacy Ibbotson/Morningstar SBBI number, now licensed and maintained by Kroll. | Long-run historical large-stock equity premium historically quoted **~6.5–7%** arithmetic vs. income return on long govts; **supply-side** adjustment trims it ~1–1.5pp. | `[unverified — training knowledge]` for the exact current print; methodology `[high]` |

**Why they differ:**
- **Historical** assumes the future mean-reverts to the past; it is *backward*-looking and sensitive to the start date, the averaging window, and arithmetic-vs-geometric choice (arithmetic for single-period discount-rate building; geometric understates a forward expected return).
- **Supply-side (Ibbotson-Chen)** decomposes the historical premium into fundamental drivers (inflation, real EPS growth, payout, P/E change) and strips out the unrepeatable P/E-expansion component — typically yielding a premium ~1pp below the raw historical.
- **Implied (Damodaran)** is purely *forward* and dynamic: it rises automatically when prices fall or expected cash flows climb, so it self-corrects to the current market — but it inherits the analyst's cash-flow/growth assumptions and is noisy month-to-month.

**ERP decision tree — which source for which engagement:**

```
Is this a USGAAP/IFRS fair-value or litigation/tax engagement needing a citable, defensible standard?
├── YES → Kroll recommended ERP (+ Kroll's matched risk-free). Most-cited, audit/court-friendly. Pair 5.0% + (max(3.5% normalized, spot 20Y)).
└── NO → Is the goal a market-consistent, point-in-time intrinsic valuation (investing / corporate intrinsic DCF)?
         ├── YES → Damodaran implied ERP (with current spot risk-free). Forward-looking, internally consistent with today's prices.
         └── NO (long-horizon strategic / capital-budgeting, want stability) → Historical or supply-side mean (Kroll CRSP/SBBI). Smooth, defensible, but stale near regime shifts.
```

**Cardinal rule:** never mix an ERP from one school with a risk-free convention from another (see §1). Document the as-of date of the ERP print used.

---

## 3. Beta

**Two estimation philosophies:**

- **Regression (top-down) beta** — OLS of the stock's returns on a market index (commonly 2–5 years of weekly/monthly data). High standard error, sensitive to index choice, return interval, and the look-back window; reflects the *historical* leverage and business mix of the single firm. `[high]`
- **Bottom-up / peer (fundamental) beta** — the preferred professional method. `[high]` (Damodaran "Ten Questions about Bottom-up Betas"; analyst references.)

**Bottom-up mechanics (the defensible path):**
1. Identify a clean peer set (the pure-play business[es] the subject operates in). Peer-set discipline is the load-bearing judgment: enough names to cut noise, narrow enough to stay comparable; screen out firms with anomalous leverage, distressed status, or off-business segments.
2. Pull each peer's **regression (levered) beta**, then **unlever** each: `βU = βL / [1 + (1 − t)(D/E)]` (Hamada, debt beta = 0). `[high]`
3. **Average the unlevered betas** — *average first, then relever.* Averaging across peers cuts the standard error roughly by √n; unlevering noisy individual betas first only compounds noise. `[high]` (Damodaran "Ten Qs".)
4. **Relever** the peer-average unlevered beta at the **subject's target** capital structure: `βL = βU [1 + (1 − t)(D/E_target)]`. `[high]`
5. Optionally adjust for the subject's operating leverage / cash holdings.

**Raw vs. adjusted (Blume):** the Blume adjustment shrinks a raw beta toward the market mean of 1.0: `β_adj = (2/3)·β_raw + (1/3)·1.0`. `[high]` (Multiple sources; this is what Bloomberg's "adjusted beta" applies by default.) Rationale: betas empirically mean-revert toward 1.0 over time, so a raw historical beta is a biased forecast of the future beta. Use adjusted when the beta feeds a forward discount rate. **Caveat:** the ⅔/⅓ weights are an empirical convention, not a law; bottom-up betas built from peer averages are already low-noise and need not be Blume-adjusted on top — doing both can over-shrink.

**Key levering/relevering caveats:**
- Use the **target** (not necessarily current) D/E to relever — consistent with the capital-structure weights in §6.
- The marginal tax rate `t` must be the same one used in the after-tax cost of debt (§5) and in unlevering.
- If a peer's debt is itself risky, the debt-beta-zero assumption overstates the unlevered beta slightly; some practitioners assume a small positive debt beta for highly levered comps.

---

## 4. Size premium — the live debate

### Where it sits in the model
The size premium (SP) is an *additive* term — an excess return over what CAPM-beta predicts — appended to the cost of equity, most commonly inside the **build-up method** or as an add-on to a "modified CAPM." Data source in practice: the **Kroll CRSP Deciles Size Study** (the licensed continuation of the Ibbotson/Morningstar SBBI Valuation Yearbook data, updated with CRSP data). `[high]` (NACVA; ValuSource; Kroll.) Kroll reports premia by decile, with the smallest decile (10) further split into **10z/10y/10x/10w** (10z smallest), plus a "risk-premium-over-CAPM" series. `[high]`

### Consensus
- A *raw* size effect existed in the historical US data, especially in microcaps and concentrated in January. `[high]`
- The effect has **weakened materially** since its early-1980s discovery, particularly in liquid US large-caps; some studies find it vanishes after ~1981. `[high]` (van Dijk "Is Size Dead?"; multiple reviews.)
- Anomalies decay ~half their Sharpe ratio post-publication (McLean & Pontiff 2016) — the size effect is a textbook candidate for arbitraging-away. `[high]`

### Divergent

| Camp | Claim |
|---|---|
| **Size premium is a data artifact / dead** | The premium is fragile: it's driven by tiny illiquid microcaps, a January seasonal, survivorship/delisting bias, and look-ahead bias; out-of-sample and post-1981 it largely disappears. Practitioners who add a 3–5% SP to a small-company cost of equity may be pricing a phantom. `[high]` |
| **AQR — "size is fine once you control for junk"** (Asness, Frazzini, Israel, Moskowitz, Pedersen, "Fact, Fiction, and the Size Effect") | The standard critiques (weak, time-varying, microcap-only, January-only) all *dissolve* when you control for **quality/junk**: small + low-quality ("junk") stocks are distressed and illiquid and drag the raw factor; control for quality and a **stable, robust, international** size premium emerges across 30 industries and 24 markets. Asness's nuance: there is a "decidedly non-simple" size effect, but **no "simple" standalone size premium**. `[high]` (AQR white paper via search excerpt; Institutional Investor; Advisor Perspectives.) |
| **Valuation-practice camp (Kroll users)** | Continue to apply an SP for genuinely small private companies, citing the CRSP/SBBI data, because the *subject* small private firm is illiquid and low-quality — exactly the profile where even the critics concede excess return exists. `[med]` |

### Practitioner judgment & decision tree
```
Is the subject a large, liquid public company?
├── YES → Do NOT add a separate size premium. (Effect absent in large-caps; CAPM/bottom-up beta suffices.)
└── NO (small/micro, often private) →
     ├── Using build-up or modified CAPM for a valuation/tax/litigation engagement?
     │    └── Apply Kroll CRSP-decile / risk-premium-over-CAPM SP, matched to the subject's size measure
     │       (revenue/assets/equity), and DOCUMENT the decile + as-of year. Most defensible in court.
     └── Investment/intrinsic context → treat SP skeptically; if applied, justify via illiquidity/quality,
          not size alone, and avoid stacking it on top of a beta that already captures small-cap risk.
```
**The double-counting trap (see §8):** if you use a bottom-up beta from *small* peers (already high), then *also* add a full SP, *and* a company-specific risk premium, you triple-count small-company risk.

---

## 5. Cost of debt

**Always pre-tax first, then tax-affect:** `after-tax Kd = pre-tax Kd × (1 − t)`, where `t` is the marginal tax rate (must match §3/§6). `[high]`

**Pre-tax cost of debt — decision tree:**
```
Does the company have liquid, publicly traded straight (option-free) bonds?
├── YES → Use the YTM on a long-dated straight bond. Most precise: it's a live, market-clearing rate. [high]
│         (Strip out convertibles/callables; use a representative long maturity, not a single odd CUSIP.)
└── NO →
     ├── Does it have a current issuer credit rating (S&P/Moody's/Fitch)?
     │    └── YES → risk-free + the market default spread for that rating (rating-implied). [high]
     └── NO (private / unrated / multiple conflicting ratings) →
          → Synthetic rating (Damodaran): compute the interest-coverage ratio (EBIT / interest expense),
            map it to a synthetic rating via Damodaran's coverage→rating→spread table (separate tables for
            large vs. small/<$5bn firms), read off the default spread, add to the risk-free. [high]
            Pre-tax Kd = risk-free + synthetic default spread. (Table re-published annually; coverage page 403-blocked — refetch.)
```

**Current vs. target debt:**
- The cost of debt should reflect the company's **current marginal** borrowing cost (what it would pay to issue debt *today*), not the historical coupon on legacy debt. `[high]`
- But the *weight* on debt (§6) should reflect the **target** structure. So a firm deleveraging toward a target uses today's marginal Kd at the *target* leverage — and if the rating changes at the target leverage, the synthetic-rating spread should be re-estimated at that target coverage.
- Do **not** use book interest-expense / book-debt as the cost of debt for a firm whose credit profile has shifted — it's stale.

---

## 6. Capital-structure weights

**Rules:**
1. **Equity weight: always market value.** Book equity is an accounting residual (historical cost minus depreciation/buybacks); it bears no relation to the market's claim and can be tiny or negative for profitable firms. Using book equity systematically mis-weights WACC. `[high]`
2. **Debt weight: market value preferred; book value is an acceptable proxy** when debt is not traded and is near par (short-dated, investment-grade, floating). For distressed or deeply discounted debt, mark to market. `[high]`
3. **Target vs. current:** use the **target** (long-run sustainable) capital structure, not a transient current mix, especially if the firm is mid-recapitalization or the current structure is anomalous. `[high]` Industry-median leverage of mature peers is the usual proxy for "target."
4. **Iterate to resolve circularity:** market-value equity weight depends on the equity value, which depends on WACC, which depends on the weight — circular. Resolve by iteration: assume a structure → compute WACC → run the DCF → re-derive implied equity value/weights → recompute → repeat to convergence. `[high]` (Or simply adopt a fixed target structure and avoid the loop, which most practitioners do for tractability.)

**Common error:** mixing a *target* beta/relevering (§3) with *current* book-value weights — the levering assumption and the weights must describe the *same* capital structure.

---

## 7. Country-risk premium (CRP) — cross-border valuation

Damodaran's framework offers **three** CRP estimators, in increasing sophistication: `[high]` (Damodaran "Measuring Company Exposure to Country Risk"; "Data Update 4 for 2026"; ctryprem page.)

1. **Sovereign default spread** — the spread of the country's USD sovereign bond (or sovereign CDS) over the US Treasury, or a rating-implied spread (Damodaran averages CDS by sovereign rating for the ~80 countries with traded CDS). Floor estimate.
2. **Relative equity-volatility approach** — scale the US ERP by `σ(country equity index) / σ(US equity index)`. Captures that equity is riskier than debt but ignores the default-spread anchor.
3. **Melded / default-spread × relative-vol (Damodaran's preferred)** — `CRP = sovereign default spread × [σ(country equity) / σ(country bond)]`. Anchors on the bond market's default pricing, then scales up for equity's higher volatility. This is the number in his country-risk data tables. `[high]`

**How to attach CRP to a company — add-to-ERP vs. lambda:**
```
How exposed is THIS company to the country's risk?
├── Uniformly exposed (default assumption) → add the full CRP to the ERP for every company in that market:
│      Ke = Rf + β·(mature-market ERP) + CRP   ("add-to-ERP" / constant-exposure method)
└── Differentially exposed (e.g., an exporter earning hard currency vs. a domestic utility) →
       Lambda (λ) method: Ke = Rf + β·(mature ERP) + λ·CRP, where λ scales by the share of revenue/
       operations actually exposed to the country (a Brazilian exporter selling globally has λ < 1;
       a purely domestic firm λ ≈ 1, possibly >1 if hyper-exposed). [high]
```
**Judgment:** the add-to-ERP method overcharges hard-currency exporters and undercharges concentrated domestic firms; lambda is more correct but harder to defend with precise inputs. Match the CRP currency to the cash-flow currency, and never apply a CRP to cash flows already modeled in a risk-adjusted (e.g., scenario-weighted) way — that double-counts.

---

## 8. Common practitioner errors (the defensibility checklist)

| Error | Why it's wrong | Fix |
|---|---|---|
| **Mismatched risk-free tenor** | Using a T-bill or 2Y rate to discount perpetual cash flows understates Rf. | Match maturity to cash-flow duration; default to 10Y or 20Y govt. |
| **Mixing ERP schools with risk-free conventions** | Kroll normalized Rf with Damodaran implied ERP (built on spot) double-distorts. | Pick one school (Kroll-normalized *or* Damodaran-spot) and stay inside it. |
| **Double-counting small-company risk** | Small-peer bottom-up beta + full size premium + company-specific risk premium can triple-count the same illiquidity/distress risk. | Decide where small-company risk lives — beta *or* SP *or* CSRP — and don't stack. |
| **Book-value equity weights** | Book equity is an accounting residual unrelated to the market claim; mis-weights WACC. | Market value for equity, always. |
| **Stale / unadjusted beta** | A single noisy 5-year regression beta is a poor forward estimate. | Bottom-up peer beta, averaged-then-relevered; Blume-adjust raw betas. |
| **Current-structure beta with target-structure weights (or vice-versa)** | The relevering D/E and the WACC weights describe different capital structures — internally inconsistent. | Use the *same* target structure for relevering, weights, and the rating used for Kd. |
| **Legacy-coupon cost of debt** | Book interest/book debt reflects past borrowing, not today's marginal cost. | Use current marginal Kd (YTM, rating spread, or synthetic spread). |
| **Mixing nominal and real** | Nominal cash flows discounted at a real rate (or vice-versa) double-counts/omits inflation. | Keep both nominal (govt-yield Rf already nominal) or both real, consistently. |
| **Inconsistent marginal tax rate** | Different `t` in unlevering, after-tax Kd, and FCF tax-affecting. | One marginal rate everywhere. |
| **CRP applied to already-risk-adjusted cash flows** | Adds country risk twice. | CRP in the discount rate XOR scenario-weighted cash flows, not both. |

---

## Source-quality note

Primary/authoritative sources dominate this synthesis: Damodaran (NYU Stern) for risk-free, implied ERP, beta, synthetic ratings, and CRP; Kroll/Duff & Phelps for recommended ERP, normalized risk-free, and the CRSP/SBBI size data; AQR + peer-reviewed reviews for the size-effect debate. **Caveat:** `kroll.com`, `pages.stern.nyu.edu`, and `aqr.com` returned HTTP 403 to direct fetch, so several primary numbers rest on search-result excerpts plus secondary corroboration (BVResources/BVWire for Kroll's 5.0% ERP / 3.5% normalized Rf; multiple mirrors for Damodaran's ~4.23% 2026 implied ERP). All recommended figures are point-in-time and move — Damodaran re-computes monthly, Kroll several times yearly — so re-pull on the valuation date.

## Sources

- [Damodaran — Historical Implied Equity Risk Premiums](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histimpl.html)
- [Damodaran — Data Update 2 for 2026: A Testing Year (2025) for US Equities](https://aswathdamodaran.substack.com/p/data-update-2-for-2026-a-testing)
- [Damodaran — Equity Risk Premiums (ERP): The 2026 Edition (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6361419)
- [Damodaran — Estimating Risk-free Rates (paper)](https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/riskfree.pdf)
- [Damodaran — Ten Questions about Bottom-up Betas](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/TenQs/TenQsBottomupBetas.htm)
- [Damodaran — Estimating Risk Parameters (beta paper)](https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/beta.pdf)
- [Damodaran — Ratings, Interest Coverage Ratios and Default Spread](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ratings.html)
- [Damodaran — Estimating a synthetic rating and cost of debt](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/syntrating.htm)
- [Damodaran — Country Default Spreads and Risk Premiums](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html)
- [Damodaran — Measuring Company Exposure to Country Risk](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/CountryRisk.htm)
- [Damodaran — Data Update 4 for 2026: A Risk Journey around the World](https://aswathdamodaran.substack.com/p/data-update-4-for-2026-a-risk-journey)
- [Kroll — Recommended U.S. Equity Risk Premium and Corresponding Risk-Free Rates](https://www.kroll.com/en/reports/cost-of-capital/recommended-us-equity-risk-premium-and-corresponding-risk-free-rates)
- [BVResources — Kroll lowers recommended U.S. ERP to 5.0%](https://www.bvresources.com/articles/bvwire/kroll-lowers-recommended-us-erp-to-50)
- [BVResources — Kroll increases recommended ERP to 5.5%](https://www.bvresources.com/articles/bvwire/kroll-increases-recommended-erp-to-55)
- [Kroll — U.S. Cost of Capital (Navigator)](https://www.kroll.com/en/tools-and-platforms/cost-of-capital/us-cost-of-capital)
- [AQR — Fact, Fiction, and the Size Effect (white paper)](https://www.aqr.com/-/media/AQR/Documents/Whitepapers/Fact-Fiction-and-the-Size-Effect.pdf)
- [Asness et al. — Size matters, if you control your junk (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S0304405X18301326)
- [Institutional Investor — AQR Attacked the Size Factor; Scientific Beta Hits Back](https://www.institutionalinvestor.com/article/2bswzoz7x91fqhtkuwo3k/portfolio/aqr-attacked-the-size-factor-scientific-beta-is-hitting-back)
- [Advisor Perspectives — The Size Premium is Alive and Well](https://www.advisorperspectives.com/articles/2019/10/16/the-size-premium-is-alive-and-well)
- [van Dijk — Is Size Dead? A Review of the Size Effect (ResearchGate)](https://www.researchgate.net/publication/228302459_Is_Size_Dead_A_Review_of_the_Size_Effect_in_Equity_Returns)
- [NACVA — Case Study Using the Revamped Kroll Cost of Capital Navigator Datasets](https://www.nacva.com/navigatorweb)
- [ValuSource — Leveraging Kroll Cost of Capital Data](https://www.valusource.com/case-study-leveraging-kroll-cost-of-capital-data-to-support-and-enhance-your-valuation-analysis/)
- [QuickRead — Best Practices for Estimating the Company-Specific Risk Premium](https://quickreadbuzz.com/2020/12/30/business-valuation-reilly-thurman-best-practices-for-estimating-the-company-specific-risk-premium-3/)
- [Wall Street Prep — Risk-Free Rate](https://www.wallstreetprep.com/knowledge/risk-free-rate/)
- [Macabacus — Weighted-Average Cost of Capital (WACC)](https://macabacus.com/valuation/dcf-wacc)
- [AnalystPrep — Target Capital Structure & WACC](https://analystprep.com/cfa-level-1-exam/corporate-issuers/target-capital-structure-and-wacc/)
- [StableBread — Cost of Debt](https://stablebread.com/cost-of-debt/)
- [IESE — Levered and Unlevered Beta](https://www.iese.edu/media/research/pdfs/DI-0488-E.pdf)
