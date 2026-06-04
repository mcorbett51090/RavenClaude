# US GAAP ASC 718 — Compensation–Stock Compensation: A Practitioner Synthesis

> Audience: controllers, FP&A leads, financial modelers, valuation analysts. This is a judgment-and-error-mode reference, not an introduction. Scope: equity-classified, employee and (post-ASU 2018-07) nonemployee share-based payments. Cash-settled (liability) awards are noted only where they change a decision rule.

## Method note

Research method: ~10 fanned WebSearch queries across grant-date measurement, condition taxonomy, attribution, forfeitures, modifications (Type I–IV), deferred tax / ASU 2016-09, ESPP, diluted EPS, 409A, nonemployees (ASU 2018-07), and IFRS 2 divergence. **Source quality was high but fetch access was poor:** the authoritative technical guides — PwC Viewpoint, Deloitte DART/Roadmap, Stout, Armanino, NASPP — all returned **HTTP 403** to WebFetch, so their content is cited from the search-engine excerpt (the engine surfaces a substantive snippet of each), not from a full-page fetch. That is flagged inline as `[med – excerpt]` where a single excerpt carries a claim. Where two independent firm excerpts (e.g., PwC + Deloitte, or PwC + Equity Methods) or an excerpt + codification citation agree, the claim is `[high]`. Codification subsection numbers (e.g., 718-10-35-3) are cited as recalled and corroborated by firm excerpts; treat the *number* as `[med]` unless you confirm against the live FASB ASC. Claims resting only on my training are tagged `[unverified — training knowledge]`. Blocked domains (403 on fetch, used via excerpt): viewpoint.pwc.com, dart.deloitte.com, stout.com, armanino.com, naspp.com.

---

## 1. The measurement objective and grant-date fair value

**The objective** is to recognize, as compensation cost, the **grant-date fair value of equity instruments the entity is obligated to issue when employees have rendered the requisite service and satisfied any other vesting conditions** — measured at the *fair value of the equity instrument*, not the value transferred to the employee. `[high]` (PwC 2.2; ASC 718-10-30). For equity-classified awards this grant-date measurement is **fixed and not remeasured** for subsequent share-price movement — the only events that change the per-unit measure are a **modification** or a change in classification. `[high]`

**Grant date** requires: (a) mutual understanding of key terms, (b) the employer is contingently obligated to issue, (c) board/required approvals obtained, and generally (d) the award has been communicated to the employee. A "service inception date" can precede grant date (e.g., service begins before terms are mutually understood), forcing an estimated-fair-value accrual until grant date is established. `[med – excerpt]` (PwC 2.6).

**Per-instrument measures:**
- **RSUs / restricted stock** — grant-date fair value is the **stock price on the grant date**, reduced by the present value of dividends the holder will *not* receive during vesting (i.e., if no dividend-equivalents accrue while unvested). `[high]` (PwC 2.2 + corroborating firm guidance). No option model needed; there is no exercise price.
- **Stock options / SARs** — require an **option-pricing model** because there is no observable market for employee options (long term, non-transferable, forfeitable, blackout/exercise restrictions). `[high]`

### Option-pricing model selection (ASC 718-10-55)

The model must (1) be consistent with the fair-value measurement objective, (2) rest on established financial-economics principles, and (3) reflect all substantive award characteristics. `[high]` (Deloitte 4.9; PwC 8.2).

| Award feature | Model of choice | Why |
|---|---|---|
| Plain-vanilla service-vested option | **Black-Scholes-Merton** (closed form) | Adequate when exercise behavior can be captured via a single "expected term" input | `[high]` |
| Option needing dynamic exercise/term modeling, graded exercise behavior | **Lattice / binomial** | Can embed suboptimal-exercise multiples and term structure of volatility (ASC 718-10-55-21) | `[high]` |
| **Market condition** (e.g., TSR-vested PSU, indexed strike, share-price hurdle) | **Monte Carlo simulation** (or lattice) | Closed-form Black-Scholes *cannot* value path-dependent share-price targets; simulation prices the condition directly into FV | `[high]` (Deloitte 4.9; PwC 8.5) |

**Key model inputs and their judgment traps:** expected term, expected volatility, risk-free rate, expected dividend yield. Where a *range* of reasonable estimates exists and no point is more likely than another, use the expected value (average) of the range — explicit guidance for volatility, dividends, and term. `[high]` (Deloitte 4.9 excerpt). Common audit friction: using historical realized volatility uncritically for a newly public issuer (peer-group / implied volatility blends are often required), and an expected term that ignores actual exercise data.

---

## 2. Condition taxonomy — the single most consequential decision in ASC 718

This is the rule practitioners most often get wrong, and the error is **directional** (it overstates or understates expense, and it survives audit only by luck). Three condition types, two independent questions each:

- **Q1 — Is the condition baked into grant-date fair value?**
- **Q2 — Is previously recognized expense reversed if the condition is ultimately not met?**

### Decision tree: condition type → FV treatment & reversal

```
What kind of condition gates the award?
│
├─ SERVICE condition (time / continued employment)
│     • In grant-date FV?  NO
│     • Reverse expense if not met (employee leaves pre-vest)?  YES — true up to actual
│        → Recognize cost only for awards that ultimately vest.            [high]
│
├─ PERFORMANCE condition (revenue, EPS, FDA approval, IPO/CIC, non-market metric)
│     • In grant-date FV?  NO (FV ignores the metric; you assess probability instead)
│     • Recognition gate: accrue ONLY when achievement is "probable";
│        start/stop/catch-up as probability assessment changes each period.
│     • Reverse expense if not met?  YES — if never probable / fails, cumulative
│        expense is reversed to zero.                                      [high]
│
└─ MARKET condition (own or another entity's share price / TSR / share-price hurdle)
      • In grant-date FV?  YES — priced via Monte Carlo/lattice; the probability
         of hitting the target is embedded as a discount to FV.
      • Reverse expense if not met?  NO — once the requisite SERVICE is rendered,
         cost is NOT reversed even if the market target is never hit.       [high]
         (The "discount" for the chance of failure was already taken in FV.)
      • Special: requisite service period may be the DERIVED service period
         from the model if there is no explicit service requirement.        [med – excerpt]
```

**The load-bearing rule, stated twice because it is the #1 error:** *Market conditions are reflected in grant-date fair value and expense is NOT reversed if the condition fails (provided service is rendered). Performance and service conditions are NOT in fair value and expense IS trued up to actual vesting.* `[high]` — corroborated by PwC 2.5, Deloitte 3.4, and the BDO Blueprint excerpt, and consistent with ASC 718-10-30-14 / 35.

Practical corollaries:
- A TSR-based PSU that an executive *fully serves through* but that pays zero because relative TSR missed: **you still keep all the expense.** Reversing it is a restatement-grade error. `[high]`
- A revenue-target PSU that becomes improbable: **stop accruing and reverse to date.** `[high]`
- An award with *both* a market and a service/performance condition: the market condition lives in FV; the service/performance condition still gates recognition and can still reverse. The two operate independently. `[high]`
- Awards with a **market condition cannot use straight-line attribution** (see §3) and **cannot use the forfeitures-as-incurred reversal for the market condition itself** — only a forfeiture *rate* for failure to render service is applied. `[high]` (PwC 2.5/2.7 excerpts).

---

## 3. Attribution — graded vs straight-line

For an award with **graded (tranched) vesting and only a service condition**, ASC 718-10-35-8 gives an **accounting-policy election** `[high]` (PwC 2.8 excerpt):

| Method | Pattern | Note |
|---|---|---|
| **Graded / accelerated** (FIN 28 legacy) | Treat each tranche as a separate award and recognize each over *its own* shorter vesting period → **front-loaded** total expense | Always permissible | `[high]` |
| **Straight-line** | One even line over the **whole** requisite service period (through the last tranche) | Permitted **only for service-only graded awards** | `[high]` |

**Decision rule.** Service-only graded award → elect straight-line or graded, applied **consistently to awards with similar characteristics.** `[high]` Any award with a **performance or market condition** → graded/accelerated attribution is **required**; straight-line is not available (narrow exception: the only performance condition is an IPO/change-in-control that merely accelerates vesting). `[high]` (PwC 2.8 excerpt; corroborated by Deloitte 6.3 / IFRS-comparison excerpt).

**Straight-line floor.** Even under straight-line, cumulative expense recognized at any date must be **at least** the grant-date FV of the tranches that have *already vested* — you cannot be "behind" the vested portion. `[unverified — training knowledge]` (a well-established ASC 718-10-35-8 nuance; verify against codification before relying on it in a model).

---

## 4. Forfeiture accounting — the ASU 2016-09 election

ASU 2016-09 introduced an **entity-wide accounting-policy election** for *service-condition* forfeitures: `[high]`

- **Estimate forfeitures** (legacy default) — build an expected-forfeiture rate into expense from grant; **true up to actual** through the vesting date so cumulative cost equals grant-date FV of awards that actually vest (ASC 718-10-35-3). `[high]`
- **Account for forfeitures as they occur** — recognize the full expense as if no forfeitures, and **reverse** when an actual forfeiture happens. Simpler; produces *higher early expense* and lumpier reversals. `[high]`

**Critical scoping limits practitioners miss:**
- The election covers **only the service-condition** aspect. **Performance conditions are still assessed for probability every period regardless of the election** — you do not "wait for them to occur." `[high]` (PwC 2.7 excerpt).
- For **market-condition** awards, you still apply a forfeiture-rate assumption (or forfeit-as-incurred) to capture employees who *don't render service*, but — per §2 — **you never reverse for the market condition failing.** `[high]`
- Pre-vest forfeiture → reverse cost; **post-vest cancellation/expiration → do NOT reverse** (the service was rendered; the award was earned). `[high]` (PwC excerpt).

---

## 5. Modification accounting — the Type I–IV framework

A **modification** is any change to terms or conditions (repricing, extending exercise window, accelerating vesting, changing performance targets). Equity-to-equity modification accounting (ASC 718-20-35-3) layers an **incremental** measure on top of the original.

**Incremental fair value** = (FV of the **modified** award measured *immediately after* modification) − (FV of the **original** award measured *immediately before* modification), both at the **modification date**. `[high]` (PwC 4.3; Stout; Armanino excerpts).

The classification turns on the **probability of vesting before vs after** the change:

### Decision tree: modification Type I–IV

```
Was the ORIGINAL award expected to vest (probable) just BEFORE modification?
│
├─ PROBABLE before ──► Is it PROBABLE after?
│     │
│     ├─ YES → TYPE I (probable-to-probable)  — the common case (e.g., repricing
│     │        an in-the-money option to a still-vesting grantee)
│     │        TOTAL COST = original grant-date FV (the "floor" — never written down)
│     │                     + incremental FV (if any), recognized over remaining service.   [high]
│     │
│     └─ NO  → TYPE III* (probable-to-improbable)
│              TOTAL COST = original grant-date FV ONLY. Any incremental FV is
│              recognized ONLY IF the modified award ultimately vests; if it does
│              not vest, you still keep the original grant-date cost (service was
│              rendered under the original, probable terms).                          [med]
│
└─ IMPROBABLE before ──► Is it PROBABLE after?
      │
      ├─ YES → TYPE II* (improbable-to-probable)
      │        TOTAL COST = FV of the MODIFIED award (post-mod FV); none of the
      │        original (improbable) award's cost is a floor. Catch-up expense is
      │        booked immediately for service already rendered.                       [high]
      │
      └─ NO  → TYPE IV (improbable-to-improbable)
               No expense unless/until vesting becomes probable; if it never does,
               no cost. Accounted for like the improbable-origin case.                [high]
```

> *Naming caution — verify before quoting in a memo.* Firms label these consistently by the **probable→improbable matrix**, but the **Roman-numeral mapping is NOT uniform across guides.** The PwC/most-common convention is **I = probable→probable, II = probable→improbable, III = improbable→probable, IV = improbable→improbable.** One search excerpt (LegalClarity/Stout) labeled "Type II = probable-to-improbable" and "Type III = improbable-to-probable," which matches that convention; another mapping circulates that swaps II/III. `[med — naming conflicts across sources]` **The economics (which row you are in) is what matters and is `[high]`; do not let the numeral drive the accounting.** Always describe the modification by its probability transition in workpapers.

**The two durable rules underneath the matrix** `[high]`:
1. **Original grant-date FV is a floor when the original award was probable** (Types I & probable-to-improbable). You can add incremental cost; you cannot claw back the original.
2. **When the original was improbable, there is no floor** — total cost is rebuilt on the *modified* award's FV, recognized only as/when vesting becomes probable.

Special modifications: **repricing** (classic Type I incremental), **acceleration of vesting** at termination (often triggers a probable-to-improbable assessment — if the award *would have been forfeited* absent acceleration, the modification recognizes the previously-unrecognized cost as incremental), and **equity-to-liability** reclassification (re-measure as a liability). `[med – excerpt]`

---

## 6. Deferred tax and the ASU 2016-09 income-statement change

**Book/tax timing.** ASC 718 expense generally creates a **deferred tax asset (DTA)** as book compensation cost is recognized (for awards that will generate a future tax deduction — NQSOs, RSUs, SARs). The DTA accretes over the service period at the expected statutory rate applied to cumulative book expense. ISOs and most ESPPs are **non-deductible** absent a disqualifying disposition, so generally **no DTA** is built. `[high]` (ASC 718-740; Bloomberg Tax / PwC excerpts).

**The settlement difference — the volatility source.** The eventual **tax deduction** equals the award's intrinsic value at exercise/vest (NQSO spread; RSU FMV at vest), which rarely equals cumulative book expense.

- **Pre-ASU 2016-09:** the difference ran through the **APIC pool** — excess tax benefits credited APIC; shortfalls debited the pool (then earnings once exhausted). Smoothed the P&L; required pool tracking. `[high]`
- **Post-ASU 2016-09 (effective PBEs FY beginning after 12/15/2016):** the **APIC pool is eliminated.** All **excess tax benefits and tax deficiencies flow through income tax expense/benefit on the income statement** at settlement/vesting, as **discrete items** in the period. `[high]` (Deloitte Heads Up; PwC ASU full text; TaxAdviser; CPA Journal — multi-source).

**Modeling consequence — flag this loudly for FP&A:** the **effective tax rate is now structurally volatile** and correlated with the **share price** (high stock price → big RSU/option deductions → excess benefits → ETR *drops*; a falling stock → shortfalls → ETR *rises*). This couples a financing-flavored event to operating EPS and is a frequent source of analyst-estimate misses. `[high]`

**Cash-flow-statement classification:** post-ASU 2016-09, **excess tax benefits are presented in operating activities** (previously a financing inflow with an offsetting operating outflow). `[high]` (Deloitte 7.3; PwC excerpt). Separately, **cash paid to taxing authorities for shares withheld to cover an employee's tax** (net-share settlement) is a **financing outflow** — treated as a reacquisition of equity. `[high]` (Deloitte excerpt). ASU 2016-09 also raised the **net-share-settlement withholding threshold** from minimum statutory to up to the **maximum statutory rate** in the employee's jurisdiction without triggering liability classification. `[med]`

**SBC on the cash flow statement (indirect method):** the period's stock-comp **expense is a non-cash add-back** to reconcile net income to operating cash flow. `[high]`

---

## 7. Award-type mechanics: RSUs vs options vs ESPP

| Feature | Stock options / SARs | RSUs / restricted stock | ESPP (compensatory) |
|---|---|---|---|
| Grant-date FV basis | Option model (BSM/lattice/MC) | Stock price less PV of forgone dividends | Discount + look-back value (option-like) |
| Exercise price | Yes | None | Purchase price = discounted (often look-back) price |
| Typical tax deduction | NQSO: spread at exercise (DTA). ISO: none unless disqualifying disp. | FMV at vest (DTA) | Generally none (qualified §423) |

**ESPP — the compensatory vs. noncompensatory test (ASC 718-50).** An ESPP is **noncompensatory (no expense)** only if it meets *all* the safe-harbor criteria, the key one being a purchase **discount of 5% or less** *and* **no option-like features (no look-back, no other beneficial terms)**, plus substantially-all-employee participation and limited subscription/cancellation rights. `[high]` (Deloitte 8.2; PwC 5.2).

```
Is the ESPP compensatory? (does it require ASC 718 expense?)
│
├─ Discount ≤ 5% AND no look-back AND other safe-harbor criteria met
│      → NONCOMPENSATORY — no expense.                                  [high]
│
├─ Discount > 5% (e.g., the typical 15%) OR has a LOOK-BACK feature
│      → COMPENSATORY — expense the FULL fair value of the benefit:
│         the discount PLUS the value of the look-back (an option on the
│         lower of grant-date/purchase-date price), modeled BSM-style.   [high]
│      • A >5% discount can still be partly noncompensatory ONLY to the
│        extent it equals avoided share-issuance costs of a public
│        offering — but if it exceeds that justified amount, the ENTIRE
│        discount (not just the excess) is compensation.                 [high]
```
Practitioner trap: a 15%-discount-with-look-back ESPP is **fully compensatory** and the look-back materially increases per-share FV; **omitting ESPP expense entirely is a common error**, especially at newly public companies. `[high]` (NASPP; Infinite Equity excerpts).

---

## 8. Diluted-EPS impact (ASC 260)

Options, SARs, RSUs, and nonvested shares enter diluted EPS via the **treasury-stock method (TSM)**: assume exercise/vesting, then assume the **assumed proceeds** repurchase shares at the **average market price** for the period; the net (issued − repurchased) is the incremental dilutive share count. `[high]` (Deloitte 4.2; PwC 7.5).

**Assumed proceeds = ** `[high]`:
1. **Exercise price** the holder would pay (zero for RSUs/RSAs — they have no strike, so they are highly dilutive); **plus**
2. **Average unrecognized compensation cost** still to be expensed (often computed as the average of beginning and ending unamortized expense); **plus**
3. (Pre-ASU 2016-09 only) the **windfall tax benefit** — **this third component was removed by ASU 2016-09**, which *increased* diluted share counts modestly because proceeds fell. `[high]` (SOS-Team; Equity Methods excerpts).

**Mechanics that bite modelers** `[high]`:
- TSM is applied **award-by-award** and only when **dilutive** (option in the money: avg price > strike). Out-of-the-money options are **antidilutive → excluded**.
- **Performance/market awards** are included in diluted EPS only to the extent the **contingency would be met if the reporting date were the end of the contingency period** (contingently issuable share rules, ASC 260-10-45) — *not* simply because they are outstanding. `[high]`
- Year-to-date diluted EPS uses **weighted-average** quarterly incremental shares, **not** a fresh full-year TSM — a recurring reconciliation error. `[med]` (Deloitte 4.9).

---

## 9. Nonemployees — ASU 2018-07 alignment

ASU 2018-07 **superseded ASC 505-50** and pulled nonemployee (vendor/contractor) share-based payments **into ASC 718**, largely aligning them with employee accounting. `[high]` (Moss Adams; Deloitte Heads Up; RSM excerpts).

- **Measurement date is now the GRANT DATE** (previously the earlier of a performance commitment or completion of performance — which forced remeasurement through vesting). `[high]`
- Nonemployee awards with **performance conditions** are now measured on the **probable outcome** (replacing the old "lowest aggregate fair value" approach). `[high]`
- Effective: PBEs FY beginning after 12/15/2018; nonpublic FY beginning after 12/15/2019. `[high]`

Practitioner consequence: pre-2018-07 nonemployee awards remeasured each period (P&L noise tracking the share price); post-2018-07 they are fixed at grant-date FV like employee awards — much less volatility, simpler bookkeeping.

---

## 10. 409A and the private-company FV input

**409A and ASC 718 are different regimes that share an input.** `[high]`
- **IRC §409A** governs the **strike price** of options: NQSOs/ISOs must be struck at or above the common stock's **FMV at grant** to avoid punitive 409A income inclusion + 20% penalty. `[high]`
- **ASC 718** governs the **book expense** measure (grant-date fair value of the *option*, not the underlying common).

In **theory** they are not the same number — 409A measures the **fair market value of the underlying common stock**; ASC 718 needs the **fair value of the award** (which runs the common-stock value through an option model and adds time value). `[high]` In **practice**, private companies use the **409A common-stock FMV as the spot-price input** to the ASC 718 option model, and auditors scrutinize that 409A as the support for the ASC 718 measure. `[high]` (Eqvista; IPOHub excerpts).

**Safe harbor.** A 409A performed by a qualified independent appraiser (or, narrowly, the illiquid-startup or binding-formula methods) creates a **rebuttable presumption of reasonableness** — the IRS bears the burden to show it was *grossly unreasonable*. The valuation is good for **12 months** or until a material event (financing round, M&A, major performance change), whichever is first. `[high]` (Sofer; AcumenSphere; BPM excerpts).

**Audit hot spot — cheap-stock / pre-IPO:** the SEC and auditors challenge **stale or low 409A values** used for grants in the months before an IPO; the retrospective gap between a low grant-date 409A and the IPO price drives a **cheap-stock charge** (extra ASC 718 expense). Refreshing the 409A near financings is a defensive necessity. `[high]`

---

## 11. US GAAP vs IFRS 2 — the divergences that change numbers

| Topic | ASC 718 (US GAAP) | IFRS 2 | Materiality |
|---|---|---|---|
| **Graded-vesting attribution** | **Policy choice** straight-line vs graded for service-only awards | **Always graded/accelerated** (each tranche valued & attributed separately; no single weighted-average life) | High — IFRS 2 always front-loads `[high]` |
| **Forfeitures** | **Election:** estimate OR account-as-incurred (ASU 2016-09) | **Must estimate** at grant and true up | Med `[high]` |
| **Deferred tax** | DTA on cumulative book expense; **all excess/shortfall to P&L at settlement** (post-2016-09), no remeasurement of the DTA for share price | DTA **remeasured each period** to current intrinsic value (tax deduction estimate); excess over book expense booked to **equity**, deficiency to P&L | High — different P&L volatility & equity vs P&L split `[high]` |
| **Valuation model** | Model-agnostic (BSM acceptable) | Stated preference for **binomial/lattice**; per-tranche valuation | Med `[med – excerpt]` |
| **Awards scope** | Employee + nonemployee (post-2018-07) | All share-based payments for goods/services | Low (converged) `[high]` |

---

## 12. The practitioner error catalog (ranked by frequency × severity)

1. **Reversing expense for a failed MARKET condition.** The cardinal sin. Market conditions are in FV; a fully-served TSR-PSU that pays zero keeps 100% of its expense. Restatement-grade. `[high]`
2. **Wrong attribution method** — using straight-line on a performance/market award (only graded is allowed), or flip-flopping the policy election across similar awards. `[high]`
3. **Forgetting the DTA/excess-benefit ETR volatility** — modeling a flat statutory tax rate and missing that share-price-driven windfalls/shortfalls now whipsaw the effective rate and EPS through the P&L (post-2016-09). `[high]`
4. **Mishandling modifications** — netting incremental FV against a decline instead of recognizing a *floor* on the original (probable) grant-date cost; misclassifying an acceleration-at-termination; or chasing the wrong Roman numeral instead of the probability transition. `[high]` / `[med]`
5. **Omitting ESPP expense** — treating a 15%-discount-with-look-back ESPP as noncompensatory; the look-back's option value is routinely understated or ignored. `[high]`
6. **Not assessing performance-condition probability each period** — wrongly assuming the forfeiture-as-incurred election lets you defer performance assessment; it does not. `[high]`
7. **Stale 409A / cheap-stock** — using a >12-month-old or pre-financing 409A for pre-IPO grants, inviting a cheap-stock charge. `[high]`
8. **Diluted-EPS misses** — including out-of-the-money options, omitting unrecognized comp from assumed proceeds, including performance shares whose contingency isn't met as of the reporting date, or doing a full-year TSM instead of weighting quarterly increments. `[high]` / `[med]`
9. **Service-inception vs grant-date** — failing to accrue from a service-inception date that precedes a later grant date. `[med]`
10. **Dividend treatment on RSUs** — not reducing grant-date FV by forgone dividends when unvested RSUs don't accrue dividend-equivalents. `[high]`

---

## Sources

Search-engine excerpts (full-page fetch returned HTTP 403 for pwc, deloitte/dart, stout, armanino, naspp — cited as excerpts):

- [PwC Viewpoint — Stock-based compensation guide: 2.2 measurement objective](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_2_measuremen_US/22_measurement_basis_US.html), [2.5 vesting conditions](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_2_measuremen_US/25_vesting_condition_US.html), [2.6 grant date / attribution](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_2_measuremen_US/26_grant_date_requis_US.html), [2.7 forfeitures](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_2_measuremen_US/27_estimates_and_adj_US.html), [2.8 graded vesting](https://viewpoint.pwc.com/content/pwc-madison/ditaroot/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_2_measuremen_US/28_awards_with_grade_US.html), [4.3 modifications](https://viewpoint.pwc.com/content/pwc-madison/ditaroot/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_4_modificati_US/43_modifications_of__US.html), [5.2 ESPP comp vs noncomp](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_5_employee_s_US/52_compensatory_vs_n_US.html), [8.2 selecting a model](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_8_estimating_US/82_selecting_an_opti_US.html), [8.5 lattice models](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/stockbased_compensat/stockbased_compensat__3_US/chapter_8_estimating_US/85_lattice_models_US.html), [7.5 diluted EPS](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/financial_statement_/financial_statement___18_US/chapter_7_earnings_p_US/75_diluted_eps_US.html)
- [Deloitte DART Roadmap — 3.4 vesting conditions](https://dart.deloitte.com/USDART/home/codification/expenses/71x/asc718-10/roadmap-share-based-payments/chapter-3-recognition/3-4-vesting-conditions), [4.9 option-pricing models](https://dart.deloitte.com/USDART/home/codification/expenses/71x/asc718-10/roadmap-share-based-payments/chapter-4-measurement/4-9-option-pricing-models), [6.3 modifications & vesting conditions](https://dart.deloitte.com/USDART/home/codification/expenses/71x/asc718-10/roadmap-share-based-payments/chapter-6-modifications/6-3-impact-vesting-conditions), [8.2 noncompensatory ESPPs](https://dart.deloitte.com/USDART/home/codification/expenses/71x/asc718-10/roadmap-share-based-payments/chapter-8-employee-stock-purchase-plans/8-2-noncompensatory-plans), [ASC 260 4.2 treasury-stock method](https://dart.deloitte.com/USDART/home/codification/presentation/asc260-10/roadmap-earnings-per-share/chapter-4-diluted-eps/4-2-treasury-stock-method), [ASC 230 7.3 stock comp cash flows](https://dart.deloitte.com/USDART/home/codification/presentation/asc230-10/roadmap-statement-cash-flow/chapter-7-common-issues-related-cash/7-3-stock-compensation), [Heads Up — ASU 2016-09 FAQ](https://dart.deloitte.com/USDART/home/publications/archive/deloitte-publications/heads-up/2016/frequently-asked-questions-about-asu-2016), [Heads Up — nonemployee ASU 2018-07](https://dart.deloitte.com/USDART/home/publications/archive/deloitte-publications/heads-up/2018/fasb-simplifies-accounting-for-share-based), [Appendix A US GAAP vs IFRS](https://dart.deloitte.com/USDART/home/codification/expenses/71x/asc718-10/roadmap-share-based-payments/appendix-a-comparison-us-gaap-ifrs)
- [PwC — ASU 2016-09 full text](https://viewpoint.pwc.com/dt/us/en/fasb_financial_accou/asus_fulltext/2016/asu_201609compensati/asu_201609compensati_US/asu_201609compensati_US.html)
- [BDO Blueprint — Share-Based Payments Under ASC 718 (Jan 2026)](https://arch.bdo.com/getContentAsset/84e1cb94-ef77-45c2-aaea-743cb5701dc1/bb620d56-5e9c-4774-8d17-fb9323eefdf4/Share-Based-Payments-Under-ASC-718-BDO-Blueprint-01-2026.pdf?language=en)
- [Grant Thornton — Share-based payments: Navigating ASC 718](https://www.grantthornton.com/content/dam/grantthornton/website/assets/content-page-files/audit/pdfs/2019/share-based-payments-navigating-guidance-ASC-718/share-based-payments-navigating-guidance-asc-718.pdf)
- [Stout — Primer for Equity Award Modifications](https://www.stout.com/en/insights/article/primer-equity-award-modifications) · [Armanino — Decoding Modifications](https://www.armanino.com/articles/decoding-modifications-for-stock-based-compensation/) · [NASPP — 5 Things About Award Modifications](https://www.naspp.com/blog/5-Things-to-Know-About-Award-Modifications)
- [Equity Methods — EPS Hot Topics](https://www.equitymethods.com/articles/eps-hot-topics-for-equity-compensation/) · [10-Step ASU 2016-09 Checklist](https://www.equitymethods.com/articles/10-step-checklist-asu-2016-09-preparation/) · [Nonemployee awards after ASU 2018-07](https://www.equitymethods.com/articles/nonemployee-awards-subject-to-asc-718-after-asu-2018-07/) · [IFRS 2 vs ASC 718](https://www.equitymethods.com/white-papers/ifrs-2-and-asc-718-comparison/)
- [The Tax Adviser — Improvements to employee share-based payment accounting](https://www.thetaxadviser.com/issues/2017/jul/employee-share-based-payment-accounting/) · [CPA Journal — Changes to Accounting for Employee Share-Based Payment](https://www.cpajournal.com/2018/04/04/changes-accounting-employee-share-based-payment/) · [Bloomberg Tax — ASC 740 stock-based comp](https://pro.bloombergtax.com/insights/provision/asc-740-stock-based-compensation/)
- [SOS-Team — Treasury Stock Method overview](https://sos-team.com/pdfs/Treasury_Stock_Overview.pdf) · [Diluted EPS FAQs](https://www.sos-team.com/pdfs/Accounting_Answers_Diluted_EPS_FAQs.pdf)
- [Moss Adams — Nonemployee share-based payments (ASU 2018-07)](https://www.mossadams.com/articles/2018/july/nonemployee-share-based-payments-guidance) · [RSM — Nonemployee share-based payment changes](https://rsmus.com/insights/financial-reporting/substantial-accounting-changes-for-nonemployee-share-based-payme.html)
- [Eqvista — ASC 718 vs 409A](https://eqvista.com/tax-guides-compliance/asc-718/asc-718-vs-409a/) · [Sofer Advisors — 409A requirements 2026](https://soferadvisors.com/insights/blog/409a-valuation-requirements-complete-compliance-guide-2025/) · [BPM — What is a 409A](https://www.bpm.com/insights/409a-valuation/) · [IPOHub — 409A Valuations](https://www.ipohub.org/article/409a-valuations)
- [NASPP — Why 15% for ESPP](https://www.naspp.com/blog/why-15-percent-for-espp) · [Infinite Equity — ESPP Accounting 101](https://infiniteequity.com/espp/espp-accounting-101/)
