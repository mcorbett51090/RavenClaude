# P0a pre-registration record (`decision_record` kind: `p0_preregistration`)

Per `plan.md` P0a item 1: this must be co-signed and locked **before any contract data is collected**.
Its whole purpose is to stop the analysis from being quietly reshaped around whatever data comes in —
the thresholds and rules below are fixed now, on paper, so nobody (including future-you) can move them
later without it being visible.

Fill in the bracketed fields, review with anyone else involved, sign and date, then treat this file as
frozen. If a rule genuinely needs to change after data collection starts, that's a new dated addendum
below the signature line — never a silent edit above it.

---

## 1. Products under test

Pick **2–3** SaaS products. Criteria for a good pick (per plan.md's own reasoning): high enough
adoption that 15–20 real contracts are gettable in the timeframe; genuinely comparable across
districts (not so customized that "unit price" is meaningless); a mix of at least one likely-high-
dispersion product and one likely-more-commoditized product, so the test isn't picking only favorable
cases.

1. **Product A: PowerSchool SIS** (student information system) — why chosen: the **high-dispersion
   candidate**, and not a guess — `incumbent-check-findings.md` already surfaced a direct, sourced data
   point (CiviCIQ, 2026-04-02) showing PowerSchool renewals averaging **$24,939 versus $10,604 at first
   purchase**, a >2x spread in real board-approval data. SIS is close to universal-adoption
   infrastructure (satisfies the 15–20-contract gettability bar), heavily represented in board packets
   (the fastest source-mix channel), and prices on a defensible per-student or per-district-enrollment
   basis.
2. **Product B: IXL Learning** (adaptive practice platform) — why chosen: the **more-commoditized
   candidate**, to avoid picking only favorable cases. IXL publishes comparatively standardized public
   per-student list pricing `[unverified — training knowledge, not re-checked this session]`, which makes
   it a good test of whether that list-price discipline actually holds once real contracts are examined,
   or masks the same kind of variance PowerSchool shows in the open. Broad, well-distributed adoption
   across elementary/middle grades; different vendor and category from A and C, which helps rule out a
   single-category artifact driving the result.
3. **Product C: Instructure Canvas** (LMS) — why chosen: a third product lifts statistical power
   meaningfully at this sample size (`plan.md`'s own power table: ~65% vs. ~34% at n=15–20 for 3 products
   vs. 2). Canvas surfaced incidentally in this session's own research as a board-packet example
   ("Contract Renewal – Infrastructure (Canvas)"), is a third distinct vendor and category (LMS, not SIS
   or adaptive-practice), and licenses per-student like the other two — genuinely comparable, and a
   further hedge against a category-specific result.

**Honest caveat:** these were selected by Claude at Matt's explicit direction (2026-09-24), reasoning
from what this session's research already established (PowerSchool) plus general category knowledge for
the other two (flagged `[unverified]` where not re-checked live). IXL and Canvas adoption/comparability
should get a quick sanity check against the first few contracts actually collected — if either turns out
to be badly customized per-district or too thin in the sample states, swap it before the noise-floor
double-normalization work starts, per the pre-registration's own addendum rule below.

## 2. Sampling frame

- **Target n per product:** 15–20 (45–60 total across all products).
- **Stratification:** by contract-size band. Define the bands now:
  - Sub-threshold band: **under $50,000, aggregated over 12 months** — Texas's competitive-bid threshold
    per `plan.md` (citation K7). `plan.md` also flags a possible SB 1173 threshold of $100,000
    `[unverified]` (U14) — if N1 counsel confirms SB 1173 is enacted before data collection starts, treat
    that as superseding this band via a dated addendum, not a silent edit.
  - Mid band: **$50,000–$250,000** — typical single-product annual spend for a mid-size district
    `[unverified — reasoned estimate, not independently sourced this session]`.
  - Large band: **above $250,000** — multi-year or multi-campus contracts (common for SIS/LMS at
    district scale) `[unverified — reasoned estimate, not independently sourced this session]`.
  - **Sub-threshold contracts must be deliberately included, not excluded as "hard to find."** This is
    the segment public records are weakest on and where price-gouging is most plausible — dropping it
    would bias the sample toward the cases least likely to show dispersion.
- **Geographic/state scope: Texas.** This is `plan.md` §4.1's own stated **default candidate**, not a
  new choice — the final launch-state selection is explicitly reserved for the founder at P0a exit,
  re-ranked on the §4.1 factors (seedability, co-op saturation, private-school population, records-egress
  posture). Using Texas for the pre-registration's data-collection push doesn't foreclose that re-rank;
  it just gives contract collection a starting state so work can begin. Records law is strong on prices
  (Tex. Gov't Code §552.0222); terms are `[unverified]` per the plan's own tracking (U15).
- **Source mix (in priority order, fastest/most-reliable first):**
  1. Check registers (actual totals)
  2. Board packets (fast, but often not-to-exceed totals only — flag these as such, don't treat as exact)
  3. Formal public-records requests (slow — budget for the timeline in `contract-collection-playbook.md`)
  4. Pilot-org-shared contracts under NDA, internal-analysis-only (requires counsel scoping to confirm
     this is safe — do not collect under this channel until N1 counsel has signed off)
  5. A GovSpend trial, for internal validation only, never resale (plan-A Alt 6)

## 3. Model specification (locked before data collection)

- **Outcome:** log(effective unit price)
- **Predictors:** log(volume), contract term length, contract year, acquisition channel (direct /
  reseller / co-op), product fixed effects
- **Sensitivity-only predictor (not primary):** purchase timing relative to fiscal-year end — run as a
  secondary check, not the headline result. More covariates cost power at this sample size.
- **Noise floor:** at least 10 contracts double-normalized independently by two different people, to
  estimate normalization-noise SD (σ_m). This is not optional — without it there's no way to tell real
  dispersion from normalization inconsistency.
- **Statistic:** noise-corrected residual P75/P25 = `exp(1.349 · sqrt(residual_variance − noise_variance))`
- **Confidence interval:** 90%, via bootstrap, stratified within product.
- **Also report:** the raw (uncorrected) P75/P25 ratio, so the size of the correction itself is visible.

Use `dispersion_test.py` in this same folder to run this exact model once data is collected — it
implements this specification directly so the analysis can't drift from what's pre-registered here.

## 4. Thresholds and exclusion rules (locked)

**Provisional GO** requires **all** of:

- (a) Pooled 90% CI lower bound of the noise-corrected statistic ≥ **1.10**, AND the point estimate is
  ≥ 1.10 in at least **2 of the products**.
- (b) Seedability: ≥ 40% of sampled **above-threshold** contracts yield quantity/metric/term from public
  records within 60 days; the sub-threshold yield rate is measured and reported separately (if < 20%,
  the day-one product flow changes — see plan.md).
- (c) Demand: ≥ 8 of ~15 public buyers name a specific renewal in the next 12 months where they'd use a
  benchmark; ≥ 5 non-binding pilot LOIs, ≥ 2 of them private (conditional on N1/L1 clearing).
- (d) TEC three-state result is not "failed for a demand-side cause that's now established."
- (e) No incumbent already serves normalized buyer-side price benchmarks in the launch state at
  comparable depth.
- (f) Runway budget covers P0b + P1 + N1/L1 + EK + P2 Stage 1, with a reserve.

**PIVOT to utilization-first** when the dispersion lower bound is below 1.10 **and** interviews show
strong unused-seat pain.

**STOP / PARTNER** when **any** of: (e) fails; TEC failed for an established demand-side cause;
dispersion is no larger than the noise floor **and** there's no utilization pain; or (f) fails.

**Exclusion rules (define now, not after seeing the data):**
- A contract is excluded if:
  1. it's bundled with unrelated products with no per-product price breakdown;
  2. it's missing volume, metric or term entirely;
  3. the price point is a known promotional, pilot, or first-year-discount rate;
  4. it's a **not-to-exceed-only total with no actual paid amount available** — `plan.md`'s own data-
     quality rule (line 380: not-to-exceed-only totals are excluded from unit-price cells, board-packet
     figures are flagged as such rather than treated as exact).
- Exclusions must be logged with a reason, not silently dropped.

## 5. Sign-off

| Role | Name | Date |
|---|---|---|
| Founder | Matt | 2026-09-24 |
| (anyone else co-deciding) | | |

**Provenance note (required by this repo's accuracy discipline, not part of the pre-registration
itself):** the product picks (§1), sampling-frame bands and state (§2), and exclusion rules (§4) above
were filled in by Claude at Matt's direct, explicit instruction ("Pick the target products and sign the
pre-registration template," 2026-09-24) — not inferred or assumed. The model specification (§3) and
GO/PIVOT/STOP thresholds (§4) were already locked by the FORGE plan itself and are unchanged. Matt should
review this record before contract collection begins and amend anything that doesn't match his intent —
per this file's own rule, any change after that review is a new dated addendum below this line, never a
silent edit above it.

*Once signed, this record is frozen. See `plan.md` P0a for the full acceptance-test text this
pre-registration implements, and `dispersion_test.py` for the statistical implementation.*
