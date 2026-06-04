# US GAAP ASC 805 — Business Combinations (M&A Purchase Accounting): A Practitioner Synthesis

> Audience: controllers, FP&A, valuation analysts. This is a judgment-and-error-mode reference, not an introduction. Confidence tags are inline: `[high]` = codification itself or ≥2 independent authoritative sources; `[med]` = single authoritative source, direction corroborated; `[unverified — training knowledge]` = stated from prior knowledge, not confirmed against this session's sources.

## Method note

Twelve WebSearch queries were fanned out across all sub-topics (acquirer identification incl. VIE/reverse, measurement period, PPA/intangible valuation, goodwill vs. bargain purchase, contingent consideration, deferred-tax step-up, the screen test, goodwill subsequent accounting, IFRS divergence, and common errors). Source quality was strong: results surfaced the Big-4 / large-firm technical guides repeatedly (Deloitte DART Roadmap, PwC Viewpoint, KPMG Business Combinations Handbook, EY FRD, RSM, BDO Blueprint, Grant Thornton Viewpoint), the FASB ASU full texts, plus valuation specialists for the intangible methods. **All WebFetch attempts returned HTTP 403 Forbidden** — PwC Viewpoint, GAAP Dynamics, CPA Journal, Weaver, and Centri all block the fetch user-agent. That is a route/host restriction (a 403 on one access path), not an absence of the source; I therefore relied on the search-engine excerpts of those same authoritative pages and **cross-corroborated every load-bearing claim across ≥2 independent sources** before tagging it `[high]`. Section numbers stated below were confirmed in at least one authoritative excerpt; where only prior knowledge supports a number it is tagged `[unverified]`. **Notable currency update found this session: ASU 2025-03 (issued May 12, 2025) revised the VIE accounting-acquirer guidance** — covered in §2.

---

## 1. Acquisition method — the spine

ASC 805 defines a **business combination** as a transaction or event in which an acquirer **obtains control of one or more businesses**, and requires the **acquisition method** `[high]` (BDO, Deloitte, PwC, Weaver). The method has four steps:

1. Identify the acquirer.
2. Determine the acquisition date (date control transfers — usually closing).
3. Recognize and measure the identifiable assets acquired, liabilities assumed, and any noncontrolling interest (NCI), generally at **acquisition-date fair value** `[high]`.
4. Recognize and measure **goodwill** (residual) **or a bargain-purchase gain**.

Goodwill = consideration transferred + fair value of any previously held equity interest + NCI − fair value of identifiable net assets acquired `[high]`. Acquisition-related (transaction) costs in a **business combination are expensed as incurred** `[high]` (CBIZ, Deloitte DART, CPA Journal) — contrast with asset acquisitions in §8.

## 2. Identifying the acquirer (and the traps)

- **Default rule:** the entity that transfers consideration (cash, assets, equity) and obtains control is the acquirer; primary control guidance is **ASC 810 (Consolidation)** `[high]` (BDO, Grant Thornton). ASC 805 then layers additional factors (relative voting rights, large minority interest, governing-body/management composition, terms of the equity exchange, relative size) when consideration is solely equity `[med]`.
- **Reverse acquisition:** when the **legal acquiree is the accounting acquirer** — common when a private operating company merges into a public shell and the shell issues shares. The accounting acquirer is the operating company; financial statements are a continuation of the legal acquiree, with consideration deemed issued by it `[high]` (BDO, Grant Thornton). Watch this in SPAC/de-SPAC and reverse-merger fact patterns.
- **VIE primary beneficiary — important currency note:** Under legacy ASC 805-10-25-5, in a combination in which the legal acquiree is a **VIE, the primary beneficiary is always the accounting acquirer** `[high]`. **ASU 2025-03 (issued May 12, 2025) revised this** so that the accounting-acquirer determination for a VIE legal acquiree aligns more closely with the general (non-VIE) factors, improving comparability `[high]` (BDO/ARCH, EY FRD Aug-2025). Practitioners must check adoption timing before assuming the legacy "primary-beneficiary-is-always-acquirer" rule still governs.

## 3. The measurement period

- **What it is:** a window after the acquisition date during which the acquirer may adjust **provisional** amounts if new information about facts existing at the acquisition date comes to light `[high]`.
- **Hard cap:** it **cannot exceed one year from the acquisition date** (ASC 805-10-25-13 through 25-15 `[med — number from excerpts/prior knowledge]`; one-year limit itself `[high]`, PwC, Deloitte DART, GAAP Dynamics). It ends earlier once the acquirer obtains the information it was seeking — it is **not a one-year "blank check"** `[high]` (a flagged common misconception).
- **How adjustments are booked — CONFIRMED:** Under **ASU 2015-16**, measurement-period adjustments are recognized **prospectively, in the reporting period in which the adjustment is determined** (ASC 805-10-25-17), **not** by retrospectively restating prior periods `[high]` (PwC ASU full text, Deloitte DART, GAAP Dynamics, Armanino). The acquirer records the cumulative catch-up to depreciation/amortization/other income effects in the current period. The offsetting entry to a measurement-period adjustment of an identifiable asset/liability is **goodwill** `[high]`.
- After the period closes, further changes are **error corrections (restatement) or normal post-acquisition events** — they no longer touch goodwill `[high]`.

## 4. Purchase price allocation (PPA) and intangibles

The acquirer recognizes **all** identifiable assets and liabilities — including ones the acquiree never booked — at fair value; everything not separately identifiable falls into **goodwill** as the residual `[high]` (Sofer, GAAP Dynamics, RSM). An intangible is **identifiable** if it is **separable** OR **arises from contractual/legal rights** `[high]`.

**Common identifiable intangibles and their standard valuation approaches:**

| Intangible | Typical method | Notes |
|---|---|---|
| Customer relationships | **MPEEM** (multi-period excess earnings) | Usually the **primary** asset; MPEEM applied **last**, after other intangibles valued; deduct **contributory asset charges (CACs)** for the fair return on all other contributing assets `[high]` (Alpha, Opagio, PCE) |
| Developed technology / patents | **Relief-from-royalty** (or MPEEM if primary) | Royalty saved by owning vs. licensing `[high]` |
| Trade names / brands | **Relief-from-royalty** | `[high]` |
| Non-compete agreements | **With-and-without** (DCF of cash flows with vs. without the agreement) | `[med]` |
| IPR&D | Income approach; capitalized as **indefinite-lived** until completion/abandonment | See §9 `[high]` |
| Workforce | **Not** recognized separately — subsumed into goodwill (but is a contributory asset in MPEEM) `[high]` |

**Reacquired rights** (e.g., a franchise right the acquirer had previously licensed to the target) are amortized over the **remaining contractual term, ignoring renewals**; if perpetual, assess whether indefinite-lived `[high]` (Deloitte DART, PwC).

## 5. Goodwill vs. bargain-purchase gain

When consideration + NCI + prior-held interest < fair value of identifiable net assets, the difference is a **bargain purchase**. **Before** recording any gain, ASC 805-30-25-4/30-30-4 `[med — number]` **requires a mandatory reassessment** that all assets/liabilities (including unrecognized intangibles) are correctly identified and all FV measurements (and the consideration) are correct `[high]` (Deloitte DART 5.2, PwC 2.6, datastudios). Only if the excess **persists after reassessment** is it recognized — as a **gain in earnings on the acquisition date** `[high]`. Typical legitimate causes: forced/distressed sales, regulatory divestitures, liquidity-constrained sellers `[high]`.

> **Decision tree — goodwill vs. bargain purchase**
> - Consideration+NCI+prior interest **>** FV of identifiable net assets → **record goodwill** (residual).
> - Consideration+NCI+prior interest **<** FV of identifiable net assets → **reassess** every recognized/unrecognized asset, liability, and FV input.
>   - Excess **disappears** after reassessment → no gain; revised goodwill/zero.
>   - Excess **persists** → **recognize bargain-purchase gain in current earnings** at acquisition date (US GAAP: always P&L, never OCI/equity).

## 6. Contingent consideration (earnouts)

Recognized at **acquisition-date fair value** as part of consideration transferred `[high]`. **Initial classification** is the fork that drives everything downstream — determined under **ASC 480** (and ASC 815-40), per **ASC 805-30-25-6** `[high]` (GAAP Dynamics, Deloitte DART 5.7 / 2.6, McLean).

> **Decision tree — contingent consideration classification & remeasurement**
> - Settled in **cash** or a **variable number of shares** / obligation indexed to something other than the acquirer's own stock → **LIABILITY** (or asset if it can swing the acquirer's way).
>   - → **Remeasure to fair value every period, changes through EARNINGS** until settled `[high]`. This is the P&L-volatility trap: a target that outperforms *increases* the earnout liability and *reduces* earnings, which surprises operators.
> - Settled in a **fixed number of the acquirer's own shares** and meets ASC 815-40 equity conditions → **EQUITY**.
>   - → **NOT remeasured**; fixed at acquisition-date fair value; settlement recognized within equity `[high]`.

Key nuance: because ASC 805 governs **subsequent measurement**, the subsequent-measurement guidance in ASC 480 does **not** apply to a liability-classified earnout — ASC 480 only drives the **initial classification** `[high]`.

## 7. Asset step-up and deferred taxes

In a **nontaxable** combination (typically a stock deal where tax basis carries over), book bases of acquired assets are stepped to fair value but **tax bases are not** → a **book-vs-tax basis difference** → a **deferred tax liability (DTL)** on the step-up (and DTAs on stepped-down items / acquired NOLs) `[high]` (PwC income-taxes guide, Bloomberg Tax, TaxOps).

- Recording the DTL **reduces net identifiable assets**, which **increases goodwill**, which... does **not** itself create more DTL on the *book* goodwill, but where there is **excess tax-deductible goodwill over book goodwill**, the DTA is computed via an **iterative / "simultaneous-equations" loop**: the DTA changes goodwill, which changes the temporary difference, which changes the DTA — iterate to convergence `[high]` (PwC 10.8, multiple).
- **No DTL is recorded for the excess of book goodwill over tax-deductible goodwill** (ASC 805-740-25-9) — a deliberate exception to avoid a circular grossing-up of goodwill `[high]`.
- A **valuation allowance** established in purchase accounting **increases goodwill**; later releases generally hit the income statement, not goodwill `[high]`.

## 8. Asset acquisition vs. business combination — the screen test

The threshold question, because the accounting diverges sharply. Introduced by **ASU 2017-01**, the **screen / concentration test (ASC 805-10-55-5A)**: if **substantially all of the fair value of the gross assets acquired is concentrated in a single identifiable asset or a group of similar identifiable assets, the set is NOT a business** → asset acquisition, and you skip the full analysis `[high]` (Deloitte DART 2.4, Weaver, CohnReznick, GAAP Dynamics). "**Substantially all**" is read as **~90%+**, but the FASB explicitly **did not make it a bright line** — apply judgment near the threshold `[high]`.

If the screen is **not** met, run the **inputs–processes–outputs framework**: to be a business, a set needs, at minimum, **an input and a substantive process** that together significantly contribute to the ability to create outputs `[high]`.

> **Decision tree — business combination vs. asset acquisition**
> - Is **substantially all (~90%+)** of the FV of gross assets acquired concentrated in **one identifiable asset or a group of similar assets**? (Goodwill, deferred taxes, and the asset being acquired are excluded from "gross assets" in the screen computation `[med]`.)
>   - **Yes** → **Asset acquisition.** Stop.
>   - **No** → Does the set include **an input + a substantive process** that significantly contributes to creating outputs?
>     - **Yes** → **Business combination** (acquisition method, §1).
>     - **No** → **Asset acquisition.**

**Why it matters — the four divergences `[high]`:**

| | Business combination | Asset acquisition |
|---|---|---|
| Model | **Fair-value** model | **Cost-accumulation** model |
| Transaction costs | **Expensed** as incurred | **Capitalized** into the asset cost |
| Goodwill | Recognized (residual) | **No goodwill**; any excess cost allocated to identifiable assets on a **relative-fair-value** basis |
| Contingent consideration | FV at acquisition; liability-classified remeasured **through earnings** | Generally recognized when **probable and estimable**; **capitalized** into asset cost when recognized |

## 9. IPR&D — subsequent accounting

Acquired **IPR&D** in a business combination is capitalized at fair value and treated as an **indefinite-lived intangible** (not amortized, tested for impairment) **until the project is completed or abandoned** `[high]` (PwC 8.2, Deloitte DART). On **completion**, it becomes **finite-lived** — amortized over the related product's useful life — and the reclassification **triggers a required impairment test** (ASC 350-30-35-17 `[med — number]`) `[high]`. On **abandonment**, it is written off.

## 10. Goodwill subsequent accounting (ASC 350)

- **Public / non-electing entities — simplified one-step test (ASU 2017-04):** Step 2 of the legacy test is **eliminated**. Compare a **reporting unit's fair value to its carrying amount**; impairment = **carrying amount − fair value, capped at the goodwill carrying amount** `[high]` (PwC ASU full text, CPA Journal, Centri, MPI). An **optional qualitative "Step 0" assessment** (ASC 350-20-35-3 `[med — number]`) precedes the quantitative test — if it's *more likely than not* that fair value exceeds carrying amount, skip the quantitative test `[high]`.
- **Effective dates (ASU 2017-04):** PBE **SEC filers** (other than smaller reporting companies) — fiscal years beginning **after Dec 15, 2019**; **all other entities** — fiscal years beginning **after Dec 15, 2022** `[high]` (RSM effective-date reminders).
- **Private-company alternative (ASU 2014-02):** eligible private companies may **amortize goodwill straight-line over 10 years or less**, and **test only on a triggering event** at the **entity level** (or reporting-unit level, by election), using the same single-step measurement `[high]` (CPA Journal, PCE, Sofer). (A parallel NFP alternative exists per ASU 2019-06 `[unverified — training knowledge]`.)
- **The amortization-for-all project is DEAD:** after ~4 years of deliberation leaning toward a **10-year-default / 25-year-cap amortization-with-impairment** model, the **FASB removed the goodwill subsequent-accounting project from its agenda in June 2022** `[high]` (Thomson Reuters, IAS Plus, KPMG, Accounting Today). Practical takeaway: **public companies continue under the ASU 2017-04 impairment-only model**; do not assume amortization is coming.

## 11. US GAAP vs. IFRS 3 — where they diverge

| Topic | US GAAP (ASC 805/350) | IFRS 3 / IAS 36 |
|---|---|---|
| **NCI / goodwill** | **Partial method only** — NCI at proportionate share of identifiable net assets; full-goodwill method **not** available `[high]` | **Policy choice per transaction:** full-goodwill (NCI at FV) **or** partial (NCI at proportionate share) `[high]` (Opagio, US GAAP Buddy) |
| **Goodwill subsequent** | **Impairment-only**, single-step at the reporting-unit level (private cos. may amortize) `[high]` | Impairment-only (no amortization), but **one-step at CGU/group-of-CGUs** level, with a different (recoverable-amount) mechanic `[med]` |
| **Bargain purchase** | Gain **always in earnings** `[high]` | Gain in **profit or loss** after reassessment (substance similar) `[med]` |
| **Contingent consideration (subsequent)** | Liability-classified → **FV through earnings** every period `[high]` | Liability-classified financial instrument → typically FV through P&L; but classification/scoping differs `[med]` |
| **Measurement period** | Max **one year**, adjustments **prospective** (ASU 2015-16) `[high]` | Max **one year**; adjustments applied **retrospectively** to the acquisition-date accounting `[med — IFRS retrospective vs. US prospective is the key divergence]` |

## 12. Most common practitioner errors

1. **"Everything into goodwill."** Failing to identify separable/contractual intangibles (customer relationships, technology, trade names, backlog) — overstates goodwill, understates amortization, and invites restatement `[high]`.
2. **Mis-classifying contingent consideration.** Defaulting an earnout to equity (no remeasurement) when it's cash-settled/variable → should be a **liability remeasured through earnings**; or being blindsided by the earnings hit when a target outperforms `[high]`.
3. **Ignoring the deferred-tax step-up.** Omitting the **DTL on the book-vs-tax basis difference** in a nontaxable deal — which both misstates the balance sheet **and** understates goodwill (the DTL is part of the residual math); plus failing to run the **iterative goodwill/DTA loop** when tax-deductible goodwill exists `[high]`.
4. **Treating an asset acquisition like a business combination (or vice versa).** Skipping the **screen test** → wrongly expensing capitalizable transaction costs, recognizing goodwill that shouldn't exist, or mishandling contingent consideration `[high]`.
5. **Treating the measurement period as a one-year blank check.** Pushing routine post-close estimate changes through goodwill instead of through earnings, or restating retrospectively (pre-ASU-2015-16 muscle memory) `[high]`.
6. **Wrong valuation method for the asset class** (e.g., MPEEM on a non-primary intangible, or omitting contributory asset charges) → audit findings `[med]`.
7. **Skipping the bargain-purchase reassessment** — booking a "gain" that is actually an unrecognized liability or a missed intangible `[high]`.

---

## Sources (authoritative; WebFetch blocked by 403 on several, so excerpts relied upon)

- FASB ASU 2015-16 full text (measurement-period adjustments) — PwC Viewpoint mirror
- FASB ASU 2017-04 full text (goodwill impairment simplification) — PwC Viewpoint mirror
- FASB ASU 2017-01 (definition of a business / screen test); ASU 2025-03 (VIE accounting acquirer)
- Deloitte DART — Roadmap: Business Combinations (chs. 2, 5, 6, App. C) and Roadmap: Goodwill (ASC 350-20)
- PwC Viewpoint — Business Combinations guide (chs. 1, 2, 8) and Income Taxes guide (ch. 10)
- KPMG — Accounting for Business Combinations and Noncontrolling Interests Handbook (Feb 2023)
- EY — FRD: Business Combinations (Aug 2025); RSM — Guide to Accounting for Business Combinations (Dec 2024) and Effective-Date Reminders
- BDO ARCH — Business Combinations Under ASC 805 (Blueprint, Aug 2025); Grant Thornton Viewpoint — Identifying the Acquirer / Identifying a Business Combination
- CBIZ, Weaver, CohnReznick, GAAP Dynamics, CPA Journal, Centri, MPI — practitioner corroboration
- Alpha Valuations, Opagio, PCE Companies, Sofer Advisors — intangible valuation methods (MPEEM, CACs, relief-from-royalty)
- Thomson Reuters, IAS Plus, KPMG, Accounting Today, BVResources — FASB June-2022 goodwill-project termination
- Opagio, US GAAP Buddy, datastudios.org — IFRS 3 vs. ASC 805 divergence
