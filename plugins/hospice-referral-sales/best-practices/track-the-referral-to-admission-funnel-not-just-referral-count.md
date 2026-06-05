# Track the referral-to-admission funnel, not just the referral count

**Status:** Absolute rule
**Domain:** Funnel / census
**Applies to:** `hospice-referral-sales`

---

## Why this exists

A referral is not census. A program can celebrate a rising referral count while admissions stall, because the conversion rate, time-to-admission, and length of stay all sit between a referral and a patient-day. Reporting referral volume as if it were results hides the leak — the ineligible referrals, the family-declined conversations, the ones lost to a faster competitor, the ones where the patient died before admission. Honest tracking measures the whole funnel, stage by stage, and connects activity to an average-daily-census target.

## How to apply

**Do:**
- Track referral → eligibility screen → information visit → election → admission, with conversion and elapsed time at each stage.
- Measure time-to-admission and the same-day-admit rate as conversion levers.
- Read average daily census and length of stay; flag a short LOS as a late-referral signal.
- Set activity targets by working back from a census target (use `hospice_calc.py funnel` + `census`).

**Don't:**
- Report referral volume as census.
- Set activity goals by habit instead of by the arithmetic to a census target.
- Ignore time-to-admission as "just logistics."

## Edge cases / when the rule does NOT apply

A brand-new territory with no conversion history may legitimately track top-of-funnel activity first while the funnel fills — but the moment conversion data exists, it governs.

## See also
- [`../agents/admissions-conversion-coach.md`](../agents/admissions-conversion-coach.md)
- [`a-declined-referral-has-a-root-cause-and-an-owner.md`](./a-declined-referral-has-a-root-cause-and-an-owner.md)

## Provenance

Codifies CLAUDE.md §3 #5. Standard B2B funnel discipline applied to hospice admissions.

---

_Last reviewed: 2026-06-05 by `claude`_
