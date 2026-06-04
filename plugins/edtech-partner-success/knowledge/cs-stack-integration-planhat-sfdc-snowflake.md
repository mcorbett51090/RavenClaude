# CS stack integration — Planhat + Salesforce + Snowflake + Zapier + Granola

> **Last reviewed:** 2026-06-03. Sources: Planhat unified-data-model docs (https://www.planhat.com/features/unified-data-model — vendor, aspirational; retrieval 2026-05-21 per `psm-tools-landscape-2026.md`); Salesforce Standard Object Reference for Account / Opportunity / Contact (verified pattern, no specific URL needed); Snowflake dimensional modeling conventions (Kimball, applied); Zapier webhook + multi-step zap patterns (vendor docs, general); Granola product page (vendor source — flow not yet defined as of this writing). Refresh when: (a) Planhat's company-external-id semantics change, (b) Salesforce-to-Planhat sync product changes, (c) the Granola flow is designed and shipped, (d) a stale-source incident points to a threshold this file got wrong.
>
> **Not in scope:** the broader CSP vendor landscape — that's [`psm-tools-landscape-2026.md`](psm-tools-landscape-2026.md). This file is **narrower and operational**: the specific Planhat-Salesforce-Snowflake-Zapier(-Granola) pattern, written for an EdTech PSM team standing it up or diagnosing it.

The cross-cutting **contract** (which dashboard field comes from which system, at what cadence, with what fallback) lives in the [`cs-platform-integration`](../skills/cs-platform-integration/SKILL.md) skill. This file carries the **deeper operational reference**: identity-spine specifics, sync-cadence rationale, failure modes the team has run into (or is most likely to run into), and the Granola placeholder.

---

## 1. Which system owns what — and the decision rule when a field could live in two places

| Field family | System of record | Decision rule |
|---|---|---|
| Account / district identity, decision-makers, contract financials, renewal date | **Salesforce** | If a value gates a renewal or commercial conversation, SFDC owns it. CRM is the AE-team source of truth; never let it diverge from Planhat. |
| CS activities (touchpoints, calls, emails, success plans), health composite, NPS / CSAT | **Planhat** | If a value reflects the CS team's *operating* state, Planhat owns it. The PSM lives in Planhat day-to-day. |
| Product usage rollups, outcome KPIs, cohort baselines | **Snowflake** | If a value is computed from event-level product telemetry, Snowflake owns it. Planhat reads aggregates, not raw events. |
| Meeting content (Granola call summaries) | **Granola** (stubbed) | Capture surface only — content flows into Planhat as an activity. Granola is **not** the system of record once the call is closed; Planhat is. |
| The wiring itself | **Zapier** | Zapier is never the system of record for any field. If a value lives "in Zapier," that's a smell — re-route. |

**Anti-pattern: dual ownership.** Renewal date in both SFDC and Planhat with no sync → AEs and PSMs cite different dates at QBR. The renewal date lives in SFDC; Planhat shows a mirror. Same pattern for ARR, contract value, account-team ownership.

---

## 2. Identity spine — the SFDC Account ID is canonical

**Rule:** every record in every other system carries the SFDC Account ID as a join key. This is non-negotiable; without it, the dashboard's per-partner view cannot be assembled deterministically.

### How each system carries the SFDC Account ID

| System | Where the SFDC Account ID lives | Notes |
|---|---|---|
| **Planhat** | `company.external_id` | Planhat's native company ID is internal-only. The SFDC mirror **must** be `external_id`, not a custom field — many of Planhat's built-in connectors depend on it. |
| **Snowflake** | `dim_partner.sfdc_account_id` (PK is the natural key, not a surrogate) | Every fact table joins on this. Surrogate keys are fine for fact-table internals but the SFDC ID is the public face. |
| **Zapier** | Carried end-to-end as a payload field in every zap | **Never** look up a Planhat company or Snowflake row by partner name in a zap. Partner names collide (e.g., "Lincoln Schools" exists in multiple states); SFDC IDs don't. |
| **Granola** (when wired) | Resolved from the calendar invite's SFDC-mapped attendees before the zap fires | If no SFDC-mapped attendee is on the invite, the zap routes to an "unrouted" bucket and surfaces in the dashboard's source banner as an error rather than landing on the wrong account. |

### Validation pattern

Before the dashboard is trusted in production, run a one-off reconciliation:

1. Pull all SFDC Account IDs from SFDC (the ground-truth set).
2. Pull all `company.external_id` values from Planhat.
3. Pull all `dim_partner.sfdc_account_id` values from Snowflake.
4. Set-diff: every SFDC ID should appear in both Planhat and Snowflake. Investigate every mismatch — the most common causes are (a) a partner-renamed-after-Planhat-creation case (Planhat company name diverged, external_id was never set), (b) a Snowflake partner that hasn't been onboarded into Planhat yet, or (c) a Planhat partner that was created manually without the SFDC backfill.

---

## 3. Sync-cadence recommendations and the rationale

These thresholds feed `sources[].stale_after_hours` in the dashboard's source-freshness banner. The reasoning matters because a wrong threshold either (a) cries wolf and trains the team to ignore the banner, or (b) under-alerts and the team trusts stale data at QBR.

| Sync | Recommended cadence | `stale_after_hours` | Rationale |
|---|---|---|---|
| Planhat activity stream | continuous (per-event) | **2** during business hours | If activities aren't landing in 2 h during business hours, the Planhat API integration or the upstream calendar/email connector is broken. Outside business hours, the dead-zone overlay (§5) raises this. |
| SFDC → Planhat (account / opportunity / contact mirror) | hourly | **4** | Hourly is the Planhat-native sync; 4 h gives a 3 h grace before flagging. Faster than nightly because field changes (renewal date moves, sponsor leaves) need same-day visibility. |
| Snowflake → Planhat (custom-field upsert: usage, adoption, outcomes) | nightly (post-ELT) | **30** | Nightly is the warehouse rhythm. 30 h grace covers a one-day ELT delay (which happens) without immediate banner-red. |
| Planhat → SFDC (health-field write-back) | nightly | **30** | AE-facing; doesn't need to be live. Drift > 1 day means the AE is seeing yesterday's health, acceptable. |
| Zapier zaps (each) | per-event | **1** | Event-driven zaps that go silent > 1 h during business hours have almost certainly errored. Zapier's own dashboard is the diagnostic — the dashboard's banner is the alarm. |
| Granola → Planhat (stubbed) | per-call | **24** | Per-call is the natural cadence; 24 h covers an end-of-day batching pattern. Status stays `"stub"` until the zap is live. |

### Cadence-vs-event tradeoff

The team should resist the temptation to make everything real-time. Real-time syncs:

- Cost more (Planhat API rate limits, Snowflake warehouse credits if a small-warehouse runs continuously).
- Introduce more failure surface (every minute is a chance for a 5xx).
- Confuse the source-freshness banner — a 30-second silence on a real-time sync gets confused with a real outage.

The contract is **as fresh as the consuming surface needs**, not "as fresh as possible." A PSM glancing at the dashboard at 8 AM doesn't need overnight Snowflake data faster than overnight.

---

## 4. The Granola flow — placeholder until defined

**Status as of 2026-06-03:** the user has identified Granola as a likely capture surface for meeting notes but has not designed the handoff. This file carries the placeholder contract; the [`cs-platform-integration`](../skills/cs-platform-integration/SKILL.md) skill carries the dashboard-side stub status.

**The placeholder contract:**

```
Granola call          → AI summary       → Zapier zap        → Planhat activity
(captured on calendar)  (text + topics)    (resolve SFDC ID)   (activity type: meeting,
                                                                custom field: granola_call_id,
                                                                body: summary)
```

**Open questions to resolve before wiring:**

1. **Action-item structure.** Does Granola expose extracted action items in a structured field, or only inline in the summary text? If structured, `partners[].pickup.commitments[]` populates automatically. If inline-only, commitments stay PSM-curated and Granola is a read-only context surface.
2. **Sentiment / topic tags.** Are these available? Used signals should feed the sentiment component as corroborating evidence (not authoritative — NPS + survey remain authoritative). Unused signals stay in Granola.
3. **Attendee → SFDC contact resolution.** What's the matching rule? Email exact match is the safe default; fuzzy name matching is the failure surface (see §6).
4. **PII redaction.** Granola summaries may contain student names if the call discussed individual students. The Zapier zap must strip those before landing in Planhat (and definitely before any field flows to Snowflake or the dashboard). This is mandatory and gates the Granola integration going live — `ravenclaude-core/security-reviewer` reviews the redaction step before the zap is enabled.
5. **Override / opt-out.** Some calls (e.g., sensitive personnel conversations) shouldn't be auto-summarized into Planhat. The flow needs a per-call exclusion mechanism — at minimum a calendar-invite tag (`[no-granola]`) that the zap respects.

**When the flow is designed**, the change is local: the Granola row in `sources[]` flips from `"status": "stub"` to a real `last_sync` value, and (if action items are structured) the per-partner `pickup.commitments[]` gets an additional populator. The dashboard layout doesn't change.

---

## 5. Dead-zone overlay on sync alerts (calendar-aware freshness)

The dashboard's stale-source banner naively reads `now - last_sync > stale_after_hours`. That's wrong on:

- **Weekends** — touchpoint activity legitimately drops to zero. A Planhat activity stream that's "stale" at 8 AM Monday isn't broken; the partners weren't talking on Saturday.
- **K-12 calendar dead zones** from [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) §2 — late August setup window, Thanksgiving week, winter / spring break, state testing window, end-of-year wrap. Same dynamic.
- **Higher-ed finals weeks** (December, May) and **summer term gaps**.
- **Corporate L&D fiscal-year-end + 2-week wrap-ups** — varies per partner.

**Implementation:** the simplest pattern is a per-source `dead_zone_aware: true` flag on the `sources[]` entry; when set, the freshness check widens the threshold during the partner-segment's known dead zones. Touchpoint-activity-via-Planhat is the most important field to make dead-zone-aware; commercial-data-via-SFDC less so (account changes don't pause for spring break).

**Anti-pattern:** ignoring the banner because it's red half the year due to weekend false positives. If the banner trains the team to ignore it, the banner is worse than no banner.

---

## 6. Failure modes (what's broken when something's broken)

### 6.1 Zapier silent zap failure

**Shape:** a zap stops firing, but Zapier doesn't surface the failure prominently — only in the per-zap history.

**Symptoms in the dashboard:**

- The affected source row goes red on the banner (correct — the threshold caught it).
- Per-partner timeline entries from that zap stop showing up.
- Downstream fields (e.g., Snowflake → Planhat custom-field upsert silently failing means health-score components drift toward stale).

**Diagnosis:** check Zapier's zap-history page for the specific zap; look for 4xx / 5xx from the destination API. The most common causes are:

- API token rotated / expired (Planhat or SFDC) → re-auth the zap.
- Destination object renamed / deleted (e.g., a Planhat custom field renamed) → fix the field mapping.
- Rate-limit window hit (rare; Zapier paces itself) → reduce zap frequency.

**Fix discipline:** when re-enabling a failed zap, replay the missed events if Zapier supports it for that zap type. If not, expect a gap in the timeline — note the gap on the partner's pickup brief so a backfill PSM knows.

### 6.2 SFDC ID mismatch (partner renamed mid-flight)

**Shape:** an SFDC account is renamed (e.g., "Lincoln Schools" → "Lincoln Public Schools District 5"). Planhat's company name is now stale. If Planhat's `external_id` was never set, a fresh sync may create a *second* Planhat company because the name no longer matches.

**Symptoms:** two partners with the same SFDC Account ID in the dashboard view (or one partner appearing twice with different scores).

**Prevention:** the `external_id` discipline from §2 is the prevention. The retroactive fix is a Planhat company merge keyed on the SFDC ID. Mark the merge in `templates/partner-profile.md` for the durable record.

### 6.3 Snowflake nightly job late (or runs against stale source)

**Shape:** the warehouse ELT ran but the upstream connector to the product database was behind, so Snowflake's "nightly" rollup is yesterday's data, not today's.

**Symptoms:** adoption / usage / outcome scores look fine on the surface (Snowflake reported a recent sync) but lag a day behind reality.

**Detection:** carry a `data_max_date` field in the Snowflake rollup table that the dashboard's source-freshness check uses *in addition to* the sync timestamp. The banner should flag when `data_max_date` is older than expected even if `last_sync` is fresh.

### 6.4 Planhat dedupe collision

**Shape:** two partners get merged in Planhat because the dedupe heuristics matched on a near-identical name (the `external_id` would have prevented this; absent it, Planhat falls back to name matching).

**Symptoms:** a partner's score, activities, or commitments suddenly include data from a different partner.

**Prevention:** same as §6.2 — strict `external_id` discipline.

**Recovery:** Planhat company unmerge if available; otherwise a manual rebuild from the SFDC + Snowflake sources. Always retain the partner profile markdown as the canon — it's the only place the unmerged state still exists in full.

### 6.5 Granola attendee not SFDC-mapped (when wired)

**Shape:** a call happens with a partner contact who isn't in SFDC (e.g., a new district hire). Granola captures the call; the Zapier zap can't resolve the attendee to an SFDC Account ID; the call lands in the "unrouted" Planhat bucket.

**Symptoms:** the dashboard's source banner flags Granola with an "unrouted" count > 0; the partner's timeline is missing the call entry until the PSM resolves it.

**Fix:** add the contact to SFDC (mapped to the right Account), then re-route the unrouted Planhat activity. The fix has to happen in SFDC first — otherwise the route is still ambiguous.

---

## 7. What this means for the dashboard

The dashboard's surfaces (source-freshness banner, school-year arc, pickup brief, multi-year history, source chips per field) are **read-only views** of the contract this file documents. The contract is what makes the dashboard trustworthy:

- **Source-freshness banner** = §3 thresholds + §5 dead-zone overlay + §6 failure-mode detection.
- **Source chip per field** = §1 ownership rules made visible — the reader can see which system is authoritative for each value.
- **Multi-year history** = the SFDC opportunity history + Snowflake year-end snapshots, joined on the SFDC Account ID.
- **Pickup brief** = the operational synthesis a PSM (or backfill PSM, or CS leader) needs to act, drawn from the right system per field.

If any of those surfaces is wrong on the dashboard, the diagnostic starts here, not in the rendering layer.

---

## References

- Contract / dashboard read-path: [`../skills/cs-platform-integration/SKILL.md`](../skills/cs-platform-integration/SKILL.md)
- Rendering / theming: [`../skills/health-report-dashboard/SKILL.md`](../skills/health-report-dashboard/SKILL.md)
- Markdown pickup-brief: [`../templates/partner-pickup-brief.md`](../templates/partner-pickup-brief.md)
- Score math + half-lives: [`../skills/partner-health-scoring/SKILL.md`](../skills/partner-health-scoring/SKILL.md)
- Broader CSP landscape (for context only): [`psm-tools-landscape-2026.md`](psm-tools-landscape-2026.md)
- Calendar dead zones: [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) §2
- Rostering data-quality typology: [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md)
- Health-score drift: [`partner-health-score-drift.md`](partner-health-score-drift.md)
