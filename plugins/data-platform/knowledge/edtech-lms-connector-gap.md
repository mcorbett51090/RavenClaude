# EdTech LMS connector gap

> **Last reviewed:** 2026-05-21. **This is the highest-leverage proprietary claim in this plugin** per the expert verdicts on the v0.1.0 plan. Sources: Canvas, Moodle, Schoology, Blackboard, D2L Brightspace developer docs; Fivetran / Airbyte connector catalog searches (negative result confirmed via multiple passes). Refresh when: (a) Fivetran or Airbyte ships a first-class LMS connector (would materially rewrite this file), (b) a new LMS gains meaningful US K-12 / higher-ed market share, (c) OneRoster v1.3 ships and changes roster-sync norms.

## The headline finding

**Native ELT-vendor connector coverage for K-12 / higher-ed LMS is thin to nonexistent as of mid-2026.** Canvas / Moodle / Schoology / Blackboard / D2L Brightspace all have documented REST APIs — but none of them have first-class Fivetran or Airbyte connectors that ship out of the box.

**This is the consulting differentiator** for an EdTech-focused practice. Custom Airbyte connector authoring fills the gap; the work product is a real consulting deliverable that ELT vendors don't replicate at the SaaS layer.

## Why the gap exists

1. **LMS market fragmentation.** No single LMS holds >50% market share. Vendor focus goes to higher-volume B2B SaaS sources (Salesforce, HubSpot, Stripe, NetSuite, etc.).
2. **Per-institution deployment variation.** Moodle in particular is highly customized per institution (plugins, custom field definitions, schema variations) — a one-size-fits-all connector is hard.
3. **Education-vertical buyer is smaller.** Fivetran/Airbyte revenue is concentrated in mid-market and enterprise SaaS; EdTech ELT spend is genuinely smaller per customer.
4. **OneRoster solves the *roster* problem.** OneRoster (1EdTech standard) handles roster sync between SIS and LMS — but it's a *roster* protocol, not an LMS *engagement-data* protocol. ELT vendors focus on the broader-applicable rostering pattern.

## The LMS landscape (the five US-dominant systems)

### Canvas (Instructure)
- **Market position:** Most-deployed LMS in US higher-ed; second-most in K-12 (post-Schoology acquisition)
- **API:** Well-documented REST API at the [Instructure Developer Documentation Portal](https://www.canvas.instructure.com/doc/api/). Comprehensive resource coverage.
- **Connector status:** No first-class Fivetran or Airbyte connector as of 2026-05-21. Custom Airbyte CDK is the canonical path.
- **OAuth:** OAuth 2.0
- **Common entities for analytics:** `courses`, `users`, `enrollments`, `assignments`, `submissions`, `grades`, `quizzes`, `quiz_submissions`, `discussion_topics`, `analytics` (Canvas-side aggregated)

### Schoology (Powerschool, formerly Instructure)
- **Market position:** Strong K-12 presence
- **API:** OAuth 2.0 + LTI 1.3 launch with NRPS extension for roster sync
- **Connector status:** No first-class ELT connector; custom Airbyte is the path

### Moodle
- **Market position:** Heaviest global open-source LMS deployment; thinner in US than Canvas
- **API:** REST API exists, but **per-deployment variation is real** — each institution can install plugins that change data shapes
- **Connector status:** No standard ELT connector; even custom Airbyte requires per-deployment tuning

### Blackboard (Anthology branding post-acquisition)
- **Market position:** Long-established in higher-ed
- **API:** Blackboard Learn REST API
- **Connector status:** No first-class ELT connector; custom Airbyte path

### D2L Brightspace
- **Market position:** Solid in higher-ed (less common in US K-12)
- **API:** Brightspace API with comprehensive documentation
- **Connector status:** No first-class ELT connector

## The custom-Airbyte-connector pattern

For a real EdTech engagement, the connector path is:

1. **Airbyte CDK (Python)** is the 2026 default for greenfield connector authoring
2. **Low-code `manifest.yaml`** approach handles most LMS REST APIs without custom Python code
3. **Schema declaration > schema discovery** — LMS APIs are stable enough to declare; discovery breaks on edge cases
4. **OAuth 2.0 + token-refresh handling** — every LMS uses OAuth; rotation discipline applies
5. **Cursor-based pagination + state checkpointing** — production tenants have millions of rows; resumable runs are non-negotiable
6. **Rate-limit-aware retry** — honor `Retry-After`, exponential backoff with ceiling

See [`../skills/connector-configuration/SKILL.md`](../skills/connector-configuration/SKILL.md) for the operational pattern, and route deeper custom-connector work to `connector-developer`.

## Cross-plugin handoff to `edtech-partner-success`

When the engagement is EdTech vertical, the work splits cleanly:

- **`data-platform` owns:** the LMS connector (custom Airbyte), the warehouse landing, the dimensional model in dbt, the dashboard
- **`edtech-partner-success` owns:** the partner-success motion above the data layer — renewal plays, QBR composition, health-score design, FERPA-aware parent comms, the partner-profile durable record

**Boundary:** if the question is "how do we get Canvas data into the warehouse?" → data-platform. If the question is "how do we use Canvas data to predict district renewal risk?" → edtech-partner-success (which consumes data-platform's output).

See the cross-plugin handoffs in [`../CLAUDE.md`](../CLAUDE.md) §10.

## OneRoster (1EdTech standard) — the roster layer

OneRoster is *not* an LMS connector — it's the **standard for SIS → LMS roster sync**. K-12 districts use OneRoster (often via Clever or ClassLink brokers) to sync rosters into LMS systems.

- **v1.1** is the wide install base
- **v1.2** adds gradebook scope
- **v1.3** (when it ships) will materially change roster-sync norms

For a consulting engagement focused on LMS *engagement data* (assignments, submissions, grades), OneRoster is irrelevant — the LMS API is the source. For a consulting engagement focused on *rostering health* (is the SIS-to-LMS sync working?), OneRoster is the protocol.

See [`../../edtech-partner-success/knowledge/rostering-data-quality-typology.md`](../../edtech-partner-success/knowledge/rostering-data-quality-typology.md) for the rostering-side deep dive.

## Why this is a consulting differentiator (not just a technical gap)

For a Matt-shaped solo consulting practice at $25-50k engagements:

1. **The gap is structural** — ELT vendors don't address it economically; not just "haven't gotten to it yet"
2. **The custom-connector work is reusable across engagements** — Canvas connector built for District A serves District B with minimal modification
3. **The handoff to partner-success is durable** — once the data is flowing, the consulting motion shifts to renewal / QBR / health scoring, which is repeat-engagement-friendly
4. **The methodology travels** — even if Airbyte ships a Canvas connector tomorrow, the dimensional-modeling layer + dashboard layer + partner-success motion still need the consultant
5. **It's marketing material** — the case study "we built the Canvas-to-Snowflake pipeline because Fivetran doesn't ship one" is exactly the kind of proof-of-craft the marketplace exists to produce

## Engagement template

For an EdTech LMS engagement:

1. **Stack-selection** (`ravenclaude-core/architect` invokes `stack-selection`): typically Case B (per-client deliverable) with EdTech vertical flag
2. **Custom Airbyte connector for the LMS** (`connector-developer`)
3. **Postgres or Supabase as the warehouse** (`database-setup-guide`)
4. **dbt modeling layer** with EdTech-specific marts (engagement, assignment-completion, grade-distribution, student-progress)
5. **Dashboard** — Apache Superset / Metabase for client deliverable; Cube + custom React if productizing across districts
6. **Multi-tenancy** via Postgres RLS + JWT-claim-driven tenant scoping
7. **Handoff to `edtech-partner-success`** for the renewal motion + QBR + partner-health-score on top

## Anti-patterns the plugin flags

- Trying to use a generic Fivetran/Airbyte LMS connector that doesn't exist (waste of evaluation time)
- Building a custom LMS connector without first checking if Airbyte's community-contributed catalog has one (the catalog grows quickly; the next release might fill the gap)
- Shipping a custom Canvas connector without a maintenance-posture plan (community contribution back to Airbyte? Matt-maintained fork? Client owns it post-engagement?)
- Treating OneRoster as an LMS connector (it's a roster protocol)
- Skipping the cross-plugin handoff to `edtech-partner-success` (leaves the engagement at the data layer when the consulting value is higher up)
- Building an LMS-engagement dashboard without consulting `edtech-partner-success/knowledge/rostering-data-quality-typology.md` (rostering issues frequently mask as engagement issues)

## Refresh triggers

- Fivetran or Airbyte ships a first-class Canvas / Moodle / Schoology / Blackboard / D2L connector (would materially rewrite this file)
- New LMS gains meaningful US market share (rare, but possible)
- OneRoster v1.3 ships
- Anthology (Blackboard) makes a material API change post-acquisition
- A major Canvas LMS API version-bump
- Federal student-privacy policy changes that affect LMS data flow (FERPA reinterpretation, state-level updates)
