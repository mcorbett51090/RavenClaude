# Measure Portfolio Concentration at the Peril-Location Level

**Status:** Absolute rule
**Domain:** Underwriting / accumulation management
**Applies to:** `insurance-pc`

---

## Why this exists

A carrier that tracks total insured value (TIV) by state or by account but not by peril-zone or geographic cluster underestimates its catastrophe exposure. Multiple policies covering adjacent buildings in the same wind or quake zone accumulate to a concentration risk that does not appear in any single account's profile. The 2011 Christchurch earthquake, the 2017 Irma season, and multiple US hail and convective storm events demonstrated that seemingly uncorrelated local accounts aggregate into massive per-event losses when the peril zone covers a dense cluster of insured locations. Accumulation management is a portfolio discipline; it cannot be done account by account.

## How to apply

Run portfolio accumulation analysis at the peril-location level, not just at the account or state level.

```
Accumulation Report — Minimum Requirements (quarterly for CAT-exposed lines)
──────────────────────────────────────────────────────────────────────────────
Segmentation:
  - Peril: wind, earthquake, flood, hail, wildfire (separately)
  - Zone: CRESTA zone / county / zip code / latitude-longitude grid
    (use the finest resolution your data supports; zip-code minimum for property)

For each peril-zone combination:
  Total TIV bound ($M)
  Count of locations
  Maximum per-location TIV
  Estimated PML at 100-year / 250-year (from cat model, loaded per cat-model-outputs-are-inputs-not-answers.md)

Accumulation limits by peril-zone (set by underwriting management):
  Report whether any zone is ≥ 80% of the limit (amber) or ≥ 100% (red — block bind)

New-business impact tracking:
  When quoting a new risk in a zone near its limit, flag the accumulation status
  to the underwriter before binding.
```

**Do:**
- Set accumulation limits by peril and zone — not just by state — and enforce them at the point of quoting, not at the point of the quarterly report.
- Update the accumulation report within 5 business days of any large single-risk binding that materially changes a zone's concentration.
- Report accumulation to the board or executive committee alongside the combined ratio; it is a risk metric, not just an operational one.

**Don't:**
- Report accumulation only by state or territory; state-level aggregation is too coarse for meaningful CAT concentration management except as a summary.
- Assume that policies in different lines of business (commercial property and commercial auto, for example) don't accumulate at the same physical location — they do.
- Allow the accumulation limit to function as a soft guideline rather than a hard underwriting control; once a zone hits its limit, new binds require explicit senior underwriter approval.

## Edge cases / when the rule does NOT apply

- **Casualty-only lines** (general liability, commercial auto liability without property exposure) — geographic accumulation at the peril level is not directly applicable; however, industry-concentration risk (multiple accounts in the same sector, e.g., construction) is the casualty analogue and should be monitored similarly.
- **Very small books** (fewer than 100 locations) — a formal zone-level accumulation system may be overhead-intensive; a spreadsheet-based tracking tool with manual updates is sufficient, but the zone-level discipline is the same.

## See also

- [`../agents/pc-underwriter.md`](../agents/pc-underwriter.md) — owns accumulation management at the account level and the zone-limit enforcement gate.
- [`./isolate-the-catastrophe-load.md`](./isolate-the-catastrophe-load.md) — the combined-ratio-level discipline; this doc is the underwriting/accumulation discipline that controls the cat load before it appears in the loss ratio.

## Provenance

Codifies the pc-underwriter and underwriting-lead accumulation management discipline from the insurance-pc plugin's CLAUDE.md §3 #4 (isolate the catastrophe load) and §3 #6 (line-of-business mix drives the portfolio result). The CRESTA-zone granularity and quarterly reporting cadence reflect standard Lloyd's, BMA Bermuda insurer, and US carrier accumulation management practice.

---

_Last reviewed: 2026-06-05 by `claude`_
