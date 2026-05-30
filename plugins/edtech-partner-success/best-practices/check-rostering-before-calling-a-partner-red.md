# Check rostering before you call a partner red on engagement

**Status:** Primary diagnostic

**Domain:** Learning analytics / Rostering data quality

**Applies to:** `edtech-partner-success`

---

## Why this exists

When a partner says "the data isn't right," it is almost never the analytics product and almost always a rostering / SIS / LMS / IdP sync issue. Engagement metrics computed against a stale or partial roster are noise — and a partner marked red on that noise is a relationship damaged for the wrong reason. House opinion #8 ("rostering is the silent killer") and #4 ("cite the signal") make this the first check, not the last: before the `learning-analytics-analyst` declares a partner red, it verifies the roster is flowing at all, flowing correctly, and flowing currently. The most dangerous case is the silent one — a direct-OneRoster district whose nightly cron failed three days ago, or a Clever sharing-scope set to 1 of 12 schools, where the sync "succeeds" but the dataset is wrong.

## How to apply

Run the diagnostic in order — cheapest, highest-yield checks first — and only open a vendor-side product ticket after all of them clear.

```
Rostering pre-flight (run BEFORE marking engagement red):
  1. Last successful sync timestamp — per upstream system (SIS → broker → vendor),
     not just "the broker is green"
  2. Row-count delta — yesterday vs today; a 10%+ drop is a sync issue, not attrition
  3. Sample 5 students the partner can verify — org, grade, section, active status correct?
  4. Broker sharing scope — did a district admin change which schools/grades are shared?
     (Clever/ClassLink: "added a school, kids not showing up" = sharing scope first)
  5. Encoding / required columns — CSV path: parse the file, compare row counts pre/post
  6. SIS change log — mid-year transfer/drop/schedule shift not yet propagated? (24-48h lag)
  7. ONLY after 1-6 — open a vendor product ticket
```

**Do:**
- Treat "sync ran successfully" and "sync contains the right data" as different claims — spot-check the data.
- Cite which of the six checks failed when you escalate (named signal + date/range, per the output contract's `Signals cited:` line).
- Coach the partner when the cause is broker scope, OneRoster encoding, a district cron, SCIM config, or LTI version; escalate to product when the vendor's parser silently drops rows or a metric definition disagrees with the partner's source of truth.

**Don't:**
- Mark a partner red while last-successful-sync is stale or a row-count cliff is unexplained.
- Tolerate "we'll look into it" for a week without coordinating a cross-party escalation thread.
- Try to debug the partner's SIS yourself — the PSM coordinates the fix, does not own the pipeline.

## Edge cases / when the rule does NOT apply

- **Roster is verified healthy** (all six checks pass, sample students correct, counts stable) — then a genuine engagement decline is real, and the red call stands. The rule is "check rostering first," not "blame rostering always."
- **Higher-ed add/drop window** — a 5-20% roster churn in the first 1-2 weeks of term is expected, not a sync failure; re-sync after the window before reading the numbers.
- **Corporate L&D** — the source of truth is the HRIS (Workday HCM, SuccessFactors, BambooHR) via SCIM 2.0; watch for `active=false` being hard-deleted (losing engagement history) rather than disabled.

## See also

- [`../knowledge/rostering-data-quality-typology.md`](../knowledge/rostering-data-quality-typology.md) — the full failure-mode typology, K-12/higher-ed/LMS/L&D stacks, diagnostic checklist, who-owns-what matrix
- [`../knowledge/sis-sso-rostering-integration-patterns.md`](../knowledge/sis-sso-rostering-integration-patterns.md) — implementation-time SIS/SSO/broker setup and integration failure modes
- [`../agents/learning-analytics-analyst.md`](../agents/learning-analytics-analyst.md) — the agent that owns the rostering-first diagnostic instinct

## Provenance

Distilled from `knowledge/rostering-data-quality-typology.md` (Last reviewed 2026-05-21) — the diagnostic instinct, the run-in-this-order checklist, and the escalate-to-product-vs-coach-the-partner rule — plus `edtech-partner-success/CLAUDE.md` house opinions #4 and #8 and the `sis-sso-rostering-integration-patterns.md` "sync ran successfully ≠ data is correct" anti-pattern. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
