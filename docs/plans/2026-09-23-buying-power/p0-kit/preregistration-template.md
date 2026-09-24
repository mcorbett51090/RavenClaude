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

1. **Product A:** `[ NAME ]` — why chosen: `[ ]`
2. **Product B:** `[ NAME ]` — why chosen: `[ ]`
3. **Product C (optional):** `[ NAME ]` — why chosen: `[ ]`

## 2. Sampling frame

- **Target n per product:** 15–20 (45–60 total across all products).
- **Stratification:** by contract-size band. Define the bands now:
  - Sub-threshold band: `[ e.g. under the launch state's competitive-bid threshold ]`
  - Mid band: `[ ]`
  - Large band: `[ ]`
  - **Sub-threshold contracts must be deliberately included, not excluded as "hard to find."** This is
    the segment public records are weakest on and where price-gouging is most plausible — dropping it
    would bias the sample toward the cases least likely to show dispersion.
- **Geographic/state scope:** `[ which state(s) — affects which public-records law applies ]`
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
- A contract is excluded if: `[ e.g. bundled with unrelated products with no per-product breakdown,
  missing volume/term entirely, price point is a known promotional/pilot rate, ... ]`
- Exclusions must be logged with a reason, not silently dropped.

## 5. Sign-off

| Role | Name | Date |
|---|---|---|
| Founder | | |
| (anyone else co-deciding) | | |

*Once signed, this record is frozen. See `plan.md` P0a for the full acceptance-test text this
pre-registration implements, and `dispersion_test.py` for the statistical implementation.*
