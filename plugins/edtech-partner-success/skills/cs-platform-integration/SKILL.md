---
name: cs-platform-integration
description: The back-end integration contract for a centralized EdTech customer success dashboard sitting on top of Planhat (CS platform) + Salesforce (CRM) + Snowflake (warehouse / product usage) + Zapier (glue) + Granola (AI meeting notes, stubbed). Documents what each system contributes to the dashboard's `bi-report/data.json` shape, the sync-freshness thresholds that drive the source-freshness banner, the identity spine that joins records across systems, and the Granola-into-Planhat flow (currently a documented placeholder). Used by `learning-analytics-analyst` (primary), `partner-success-manager` (touchpoint and pickup-brief fields), `qbr-composer` (data-pull plan). FERPA / student PII routes through `ravenclaude-core/security-reviewer` (mandatory).
---

# Skill: cs-platform-integration

**Purpose:** turn a Planhat + Salesforce + Snowflake + Zapier + Granola stack into one centralized customer success dashboard for an EdTech PSM team — without buying another BI tool and without writing a server. This skill is the **contract** between those source systems and the dashboard's `bi-report/data.json` shape: which system owns which field, how often it syncs, what to fall back to when it's stale, and how a partner is identified end-to-end.

It pairs with:

- [`health-report-dashboard`](../health-report-dashboard/SKILL.md) — the rendering layer (the `report.html` you actually look at).
- [`partner-health-scoring`](../partner-health-scoring/SKILL.md) — the math behind the score components, which this skill maps to source systems.
- [`knowledge/cs-stack-integration-planhat-sfdc-snowflake.md`](../../knowledge/cs-stack-integration-planhat-sfdc-snowflake.md) — the deeper operational reference (identity spine, failure modes, dead-zone overlay on sync alerts).
- [`templates/partner-pickup-brief.md`](../../templates/partner-pickup-brief.md) — the markdown-export equivalent of the dashboard's per-partner pickup brief, so the dashboard view and the exportable doc carry the same shape.

## When to use

- Standing up the dashboard for the first time: which system feeds which field, what cadence, who owns the wiring.
- Diagnosing a stale source (the banner went red): which sync is broken and who fixes it.
- Adding a new field to the dashboard: where does it come from, what's the fallback, what's the refresh contract.
- Onboarding a new PSM team to the stack: this is the shape, this is what's authoritative for each value.
- Granola flow decisions: this skill carries the documented contract; the operational design is still open (see §"Granola — stubbed integration" below).

## The stack — who owns what

| System | Role in the stack | What it's the source of truth for | What it's NOT the source of truth for |
|---|---|---|---|
| **Planhat** | CS platform | Activities (touchpoints, calls, emails, in-app messages), health-score composite, NPS / CSAT survey responses, success plans, custom-field rollups synced from Snowflake | Account / opportunity / contract financials (those live in SFDC); raw product-usage telemetry (that lives in Snowflake) |
| **Salesforce** | CRM | Account (district / institution), opportunity, renewal date, ARR / MRR, contract value, named contacts + roles, account-team ownership, multi-year history | Touchpoint diary (that's Planhat); product usage (that's Snowflake) |
| **Snowflake** | Warehouse | Product-usage rollups (DAU / WAU / MAU, feature adoption, rostering completeness, outcome KPIs), historical engagement series, cohort baselines | Real-time activity (that's Planhat); contract / commercial fields (that's SFDC); meeting content (that's Granola) |
| **Zapier** | Glue | No fields of its own — it's the wiring. Owns the canonical zaps that move data between the four others. Its **freshness** is what the dashboard's source-banner reports per zap. | Anything as a system of record. If Zapier is the "source" of a field, that's a smell — re-route. |
| **Granola** | AI meeting notes | (Stubbed.) Meeting transcripts + AI-generated summaries. When wired, flows into Planhat as activities with a `granola_call_id` tag. | Anything else — Granola is a capture surface, not a record. |

**House rule:** the partner profile (`templates/partner-profile.md`) remains the canon, and Planhat / SFDC are sync targets, per the plugin's CLAUDE.md §3 #1. This skill describes the **dashboard's** read path; the durable record lives in the markdown templates.

## Identity spine — how a partner is joined across systems

**Salesforce Account ID is canonical.** Every other system carries it as the join key:

- **Planhat** — `company.external_id` mirrors the SFDC Account ID. Planhat's native company ID is internal only.
- **Snowflake** — `dim_partner.sfdc_account_id` is the join column. All product-usage fact tables key off this.
- **Zapier** — every zap passes the SFDC Account ID end-to-end as a payload field (never as a lookup-by-name; partner names collide).
- **Granola** — when wired, the calendar-invite-attendees-to-account mapping resolves to the SFDC Account ID before the Zapier zap fires.

**`data.json` partner key.** The dashboard's `partners[].name` is human-readable; an additional `partners[].sfdc_account_id` (added when wiring real data) is the actual key. Until then, name-based matching is acceptable for the synthetic demo only.

**Failure mode if this is wrong:** the deeper failure-modes catalog (Zapier name-lookup zaps, mid-rename SFDC accounts, Planhat dedupe collisions) lives in [`knowledge/cs-stack-integration-planhat-sfdc-snowflake.md`](../../knowledge/cs-stack-integration-planhat-sfdc-snowflake.md) §"Failure modes."

## Field-to-source map (the dashboard read contract)

This is the field-by-field contract that an implementer wires up. Each row: dashboard field → source system → refresh cadence → fallback when missing.

### Top-level fields

| `data.json` path | Source system | Refresh cadence | Fallback when missing | Notes |
|---|---|---|---|---|
| `report.refreshed` | (build time) | every generator run | "—" | Set by the script writing `data.json`, not a source system |
| `kpis[].value` (NRR, GRR) | **Salesforce** (ARR rollup) | nightly | hold prior value + flag stale | Compute upstream of Snowflake or in Snowflake — not in Planhat |
| `kpis[].value` (avg_health, red_count) | **Planhat** (health-score rollup) | hourly | compute from `partners[].score` in the page | Cross-check against Snowflake-derived score before publishing |
| `cohort.median`, `cohort.p25`, `cohort.p75` | **Snowflake** (cohort table) | daily | hide the cohort panel | Cohort segmentation rules live in Snowflake, not Planhat |
| `portfolio_trend[]` (12 weeks) | **Snowflake** | weekly | last published value | One row per ISO week |
| `school_year.*` | (config) | static / per-year | use prior year + warn | Phase calendar from `knowledge/k12-adoption-arc-fall-spring-summer.md`; today's date from build environment |
| `sources[].last_sync` | each system's own monitoring | per system (see below) | render dot red + tooltip "no sync data" | The dashboard's freshness banner is driven by this |

### Per-partner fields

| `data.json` path | Source system | Refresh cadence | Fallback | Notes |
|---|---|---|---|---|
| `partners[].name`, `.segment`, `.psm` | **Salesforce** | hourly | hold prior | PSM = account owner |
| `partners[].score`, `.band`, `.delta` | **Planhat** | hourly | recompute from components | Composite per `partner-health-scoring` |
| `partners[].components.adoption` | **Snowflake** (usage depth rollup) | daily | last published + flag stale | Half-life decay per `partner-health-scoring` |
| `partners[].components.touchpoint` | **Planhat** (activity recency) | hourly | last published + flag stale | Substantive touchpoints only — the plugin's anti-pattern hook catches "synced with X" entries |
| `partners[].components.outcome` | **Snowflake** (outcome KPI series) | weekly | last published | Outcome definition is partner-specific — confirm with curator |
| `partners[].components.sentiment` | **Planhat** (NPS + survey + tagged call sentiment) | per-survey + per-call | last published | Decay 60 days |
| `partners[].components.champion` | **Salesforce** (named-contact-confirmed-in-role) | per-change | last published | Decay 60 days; "confirmed alive in role" is the signal |
| `partners[].components.usage` | **Snowflake** (feature-adoption breadth) | daily | last published | Counts distinct features touched in trailing window |
| `partners[].spark[]` (12-week composite) | **Planhat** (snapshot table) | weekly | derive from `score` deltas | Hold the series even when partner is dormant |
| `partners[].flags[]` | **Planhat** (rule engine) + **Snowflake** (threshold alerts) + **Zapier** (rostering-sync stalls) | per-event | omit | Six red-flag triggers per `partner-health-scoring` |
| `partners[].play` | **Planhat** (success-plan field) | per-PSM-edit | "—" | The play the PSM is currently running |
| `partners[].last_touch`, `.next_qbr` | **Planhat** | hourly / per-calendar-sync | "—" | Next QBR is a Planhat success-plan field, not a calendar event |
| `partners[].renewal` | **Salesforce** (opportunity close date) | hourly | "—" | Authoritative — Planhat mirrors this, doesn't own it |
| `partners[].history[]` (multi-year) | **Salesforce** + **Snowflake** | per-year-close | omit | Year-end score from Snowflake; renewal outcome + ARR from SFDC |
| `partners[].timeline[]` | **Planhat** (activities) + **Salesforce** (contact changes) + **Snowflake** (metric alerts) + **Granola** (when wired) | per-event | empty array | Each entry carries `source` for the dashboard's source chip |
| `partners[].pickup.where_we_are` | **Planhat** (derived: phase + last-touch) | hourly | compute on the page from `last_touch` + `school_year.current_phase` | Plain-language one-liner |
| `partners[].pickup.commitments[]` | **Planhat** (success-plan action items) | per-PSM-edit | empty | Each item needs owner + due date (hook §3 #13) |
| `partners[].pickup.next_actions[]` | **Planhat** + **Salesforce** (the next 3 things due) | derived | empty | Mix of CS activities and SFDC tasks |
| `partners[].pickup.dont_push[]` | **Planhat** (PSM-curated) + dead-zone calendar from `knowledge/k12-psm-operating-cadence.md` | derived | empty | What a backfill PSM would otherwise step on |
| `partners[].pickup.who_is_who[]` | **Salesforce** (Contact + Account Team) | hourly | empty | Carries `confirmed_in_role` date — see plugin §3 #4 |

## Sync-freshness thresholds (what makes the banner go red)

The dashboard's source-freshness banner is driven by `sources[].stale_after_hours`. Recommended thresholds:

| System | Recommended `stale_after_hours` | Why |
|---|---|---|
| Planhat | **2** | The high-volume activity stream — if it's stale > 2 h during business hours, something is broken |
| Salesforce | **30** | Nightly sync is the norm; 30 h gives a one-day grace |
| Snowflake | **30** | Nightly ELT; same grace |
| Zapier | **1** | Per-event; > 1 h silence on an event-driven zap usually means it errored |
| Granola | **24** | (stubbed) Per-call; > 24 h is end-of-day boundary |

**Dead-zone overlay.** During K-12 calendar dead zones from [`knowledge/k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md) §2 (weekends, late August, Thanksgiving week, winter / spring break, state testing window, end-of-year wrap), the touchpoint-freshness threshold should be widened or suppressed — a quiet Planhat at noon on a federal holiday is not a broken zap. Implementation note: the simplest pattern is a per-source `dead_zone_aware` flag on the `sources[]` entry that the renderer respects.

## Granola — stubbed integration

The Granola flow is a **documented placeholder** as of 2026-06: the user has named the tool but has not yet defined the exact handoff. The contract this skill writes is:

- **Capture:** Granola captures calls during the meeting; AI-generated summaries land in Granola immediately after the call.
- **Sync (via Zapier):** a Zapier zap reads the Granola call, transforms it to a Planhat activity (the activity body is the summary; the activity type is `meeting`; a custom field carries the `granola_call_id` so the activity can deep-link back to the Granola call).
- **Identity:** the call's calendar invite must include at least one attendee mapped to a Salesforce contact, which resolves to an SFDC Account ID. If no SFDC-mapped attendee is on the invite, the zap routes to an "unrouted" Planhat bucket and surfaces in the dashboard's source-banner as an error.
- **TODO when the flow is final:**
  1. Action-item extraction. If Granola's summary structure exposes action items, a downstream Zapier step should populate `partners[].pickup.commitments[]` automatically (owner + due date from the summary). Until that's confirmed, commitments stay PSM-curated.
  2. Sentiment / topic tags. If Granola exposes these, they can feed the sentiment component as a corroborating signal; until then, NPS + survey are authoritative.
  3. The Granola source row stays `"status": "stub"` in `sources[]` until the zap is live.

Reasoning: the user said "possibly Granola — flow not yet defined." The contract is here so that when the flow is designed, the implementation is a fill-in not a redesign.

## Recommended day-1 implementation order

For a team standing this up from scratch, the dependency order:

1. **Salesforce Account ID propagation** — confirm every Planhat company carries it as `external_id`; confirm every Snowflake fact table carries it. Nothing downstream is stable without this.
2. **Snowflake → Planhat custom-field upsert** (nightly Zapier zap) — pushes adoption / usage / outcome rollups into Planhat so they're available to the health score.
3. **Planhat health-score config** — wire components per `partner-health-scoring` with the half-lives this skill documents.
4. **Planhat → SFDC health-field write-back** (nightly Zapier zap) — so the AE / sales side can see health without logging into Planhat.
5. **`bi-report/data.json` export** — a script (Snowflake-resident or Python-side) that joins the four sources and writes the file per `health-report-dashboard`'s contract.
6. **Generator + report.html** — `python3 scripts/generate-bi-report.py --plugin edtech-partner-success`.
7. **Granola wiring** — when the flow is defined.

## Hand-offs

- **Score design / weights / decay** → [`partner-health-scoring`](../partner-health-scoring/SKILL.md) (`learning-analytics-analyst`).
- **Rendering / theming the dashboard** → [`health-report-dashboard`](../health-report-dashboard/SKILL.md) (`learning-analytics-analyst`, `partner-success-manager`).
- **Pickup-brief markdown export** → [`templates/partner-pickup-brief.md`](../../templates/partner-pickup-brief.md) (`partner-success-manager`).
- **Rostering / SIS data-quality concerns** → [`rostering-data-quality`](../rostering-data-quality/SKILL.md) (`learning-analytics-analyst`, `partner-success-manager`).
- **Anything student-level** → `ravenclaude-core/security-reviewer` (mandatory per plugin §2).
- **Identity-resolution across non-CS systems** (if Intercom, Slack, HubSpot enter scope) → `data-platform/cross-system-identity-resolution` skill, when that plugin is installed.

## FERPA / privacy

- `data.json` carries **partner-level** values only, never student-level. The plugin's existing discipline (`health-report-dashboard` SKILL.md §FERPA) applies unchanged.
- Granola transcripts may contain student names in conversation. The Zapier zap that lands Granola summaries into Planhat must not propagate student PII to Snowflake or the dashboard. Strip student identifiers in the zap step; if the summary structure makes that infeasible, the Granola integration must NOT be wired until `ravenclaude-core/security-reviewer` has reviewed the redaction step.
- Real exports replace synthetic identifiers in `data.json`. The committed demo stays synthetic (`report.synthetic: true`).

## References

- Rendering / theming: [`skills/health-report-dashboard/SKILL.md`](../health-report-dashboard/SKILL.md)
- Score math: [`skills/partner-health-scoring/SKILL.md`](../partner-health-scoring/SKILL.md)
- Operational reference: [`knowledge/cs-stack-integration-planhat-sfdc-snowflake.md`](../../knowledge/cs-stack-integration-planhat-sfdc-snowflake.md)
- Broader CSP landscape (for context only): [`knowledge/psm-tools-landscape-2026.md`](../../knowledge/psm-tools-landscape-2026.md)
- Dead-zone calendar: [`knowledge/k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md) §2
- School-year phase model: [`knowledge/k12-adoption-arc-fall-spring-summer.md`](../../knowledge/k12-adoption-arc-fall-spring-summer.md)
- Markdown pickup-brief: [`templates/partner-pickup-brief.md`](../../templates/partner-pickup-brief.md)
