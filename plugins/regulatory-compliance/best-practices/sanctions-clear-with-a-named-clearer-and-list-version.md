# Record the Named Clearer and List Version on Every Sanctions Clearance

**Status:** Absolute rule
**Domain:** AML / sanctions
**Applies to:** `regulatory-compliance`

---

## Why this exists

A sanctions clearance is only as defensible as the audit trail behind it. Examiners reviewing sanctions-screening logs do not accept "we reviewed it and it was fine" — they ask who cleared it, on what date, against which list version, and on what rationale. A clearance without a named individual is an institutional assertion that no one can be held accountable for; a clearance without the list version cannot demonstrate that the screening happened against a current list. Both gaps are findings in themselves, independent of whether the underlying determination was correct.

## How to apply

Every sanctions-alert disposition — whether the result is "clear" or "escalate" — produces a structured record.

```
Sanctions Clearance Record — Required Fields
──────────────────────────────────────────────
Alert ID:                <system-generated or sequential>
Alert date/time:         <YYYY-MM-DD HH:MM>
Screened name/entity:    <as submitted to screening — not sanitized>
Screening system:        <vendor + version, e.g. "Acuity 3.2" or "World-Check One">
List(s) searched:        <OFAC SDN, EU Consolidated, HM Treasury, UN, etc.>
List version / date:     <e.g., "OFAC SDN as of 2026-05-30" — pull from system log>
Match type:              <Exact / Fuzzy - score XX% / Name-only / DOB match / etc.>
Disposition:             <Cleared | Escalated>
Rationale (if cleared):  <Reason the match is a false positive — DOB/nationality/address
                          mismatch; common name with no corroborating identifiers; etc.
                          Must be a positive finding, not "looks different enough.">
Cleared by:              <Full name — not a team account>
Clearance date:          <YYYY-MM-DD>
Supervisor review:       <Required if score > threshold — name + date>
```

**Do:**
- Configure the screening system to auto-capture the list version at the time of the search — do not reconstruct it after the fact.
- Use individual named accounts for clearances, not shared logins; the "cleared by" field is valueless on a shared account.
- Require a second-level approval for near-exact matches (score ≥ 85% or name-only with partial identifier match).
- Retain the record for the full retention period required by the applicable AML regime (minimum 5 years under most FATF-member regimes — verify for the specific jurisdiction).

**Don't:**
- Write "not a match" as the entire rationale; state the specific differentiating criterion.
- Clear an alert and then re-open the customer record without creating a new screening event.
- Allow a clearance rationale to say "approved by compliance" without a named individual.

## Edge cases / when the rule does NOT apply

- **Automated true-negative rules** (e.g., a watchlist rule that auto-excludes known-clean internal accounts) — the automation log substitutes for the manual record, provided it captures the list version and rule name; review the automation log in periodic QA.
- **Batch re-screening of the entire customer base** — the record-keeping requirement is the same; the format may be a batch log rather than individual disposition records, but the list version and QA sign-off are still required at the batch level.

## See also

- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — owns the sanctions-hit disposition playbook.
- [`./aml-sanctions-screening-hygiene.md`](./aml-sanctions-screening-hygiene.md) — the upstream rule on list coverage, fuzzy-match thresholds, and frequency of screening; this doc governs the clearance record once a hit occurs.

## Provenance

Codifies the plugin's sanctions screening discipline from CLAUDE.md §3 #8 ("sanctions screening is binary — a hit is either cleared with documented rationale, named clearer, source-list version, or escalated") and the `sanctions-hit-disposition` skill. The list-version capture requirement reflects FATF Recommendation 10 and standard BSA examiner expectations.

---

_Last reviewed: 2026-06-05 by `claude`_
