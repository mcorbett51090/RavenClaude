# Treat "the sync ran successfully" and "the data is correct" as two different claims

**Status:** Primary diagnostic

**Domain:** Rostering / SIS-SSO integration hygiene

**Applies to:** `edtech-partner-success`

---

## Why this exists

The most dangerous rostering failure is the silent one: the broker shows green, the cron exited 0, the integration "succeeded" — and the dataset is still wrong. A district admin narrowed the Clever sharing scope to 1 of 12 schools, a OneRoster CSV arrived with a UTF-8 BOM that dropped a column, a nightly job failed three days ago but the last *good* file is still being served, or SSO works for admins (who log in via AD) but not for students (who route through Clever Instant Login). In every case "sync ran successfully" is true and "the data is correct" is false. Rostering is the silent killer (house opinion §3 #8), and engagement metrics computed on a wrong roster are noise — a partner marked red on that noise is a relationship damaged for the wrong reason. The fix is to never let a green sync status stand in for verified data: spot-check the rows.

## How to apply

Validate the *content* of the roster, not just the status of the job — sample real users across roles and schools before trusting any engagement number built on it.

```
Integration-hygiene validation (treat sync-status and data-correctness separately):
  1. Last SUCCESSFUL sync timestamp per upstream HOP (SIS → broker → vendor),
     not just "the broker is green".
  2. Row-count delta day-over-day — a 10%+ drop is a sync issue, not attrition.
  3. Spot-check 10 users ACROSS roles AND schools — org, grade, section, active status
     correct? Admins working but students failing = SSO per-role routing gap, not "low usage".
  4. Broker sharing scope — did a district admin change which schools/grades are shared?
     ("added a school, kids not showing up" → sharing scope first).
  5. Encoding / required columns on CSV paths (UTF-8 BOM / Windows-1252, v1.1 ↔ v1.2 mismatch).
  6. SIS change log — mid-year transfer/drop/schedule shift not yet propagated (24-48h lag).
  → ONLY after 1-6 clear, the data is trustworthy. A vendor product ticket is the LAST step,
    not the first.
```

**Do:**
- Coach the partner when the cause is broker scope, OneRoster encoding, a district cron, SCIM config, or LTI version; escalate to *product* only when the vendor's parser silently drops rows or a metric definition disagrees with the partner's source of truth.
- Prefer LTI 1.3 / Advantage with NRPS over LTI 1.1; check pagination on direct Canvas API pulls.
- Escalate a noticed rostering smell to product/engineering proactively — not waiting for the partner to complain is the named §4 anti-pattern.

**Don't:**
- Let a green broker dashboard substitute for spot-checking the rows.
- Debug the partner's SIS yourself — the PSM coordinates the cross-party fix, does not own the pipeline.

## Edge cases / when the rule does NOT apply

- **Roster verified healthy** — all checks pass, sample users correct, counts stable — then a genuine engagement decline is real and the red call stands. The rule is "verify first," not "blame rostering always."
- **Higher-ed add/drop window** — 5-20% roster churn in the first 1-2 weeks of term is expected (Banner especially); re-sync after the window before reading numbers.
- **Corporate L&D** — source of truth is the HRIS via SCIM 2.0; watch for `active=false` being hard-deleted (losing engagement history) rather than disabled.

## See also

- [`./check-rostering-before-calling-a-partner-red.md`](./check-rostering-before-calling-a-partner-red.md) — the diagnostic-order sibling rule (run rostering check before the red call)
- [`../knowledge/sis-sso-rostering-integration-patterns.md`](../knowledge/sis-sso-rostering-integration-patterns.md) — SIS landscape, broker routing, SSO per-role, validation patterns, "sync ran successfully ≠ data is correct"
- [`../knowledge/rostering-data-quality-typology.md`](../knowledge/rostering-data-quality-typology.md) — the full failure-mode typology + who-owns-what matrix
- [`../agents/learning-analytics-analyst.md`](../agents/learning-analytics-analyst.md) — owns the validation instinct

## Provenance

Distilled from `knowledge/sis-sso-rostering-integration-patterns.md` ("sync ran successfully ≠ data is correct", spot-check 10 users across roles+schools, SSO per-role routing), `knowledge/rostering-data-quality-typology.md` (vendor-specific tells, who-owns-what), and house opinion §3 #8 + §4 (un-escalated rostering smell). Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
