---
name: k12-signal-taxonomy
description: The K-12-specific signal catalog beyond generic B2B customer success — buyer/user/decision-maker separation, leadership turnover as renewal-risk event, ESSER cliff aftermath, state-testing-window blackout, back-to-school surge, family activation gap, rostering health, and LearnPlatform external benchmark. Each signal entry carries persona / leading-or-lagging / default weight / half-life / FERPA class.
last_reviewed: 2026-06-04
confidence: high
---

# K-12 Signal Taxonomy

> **Scope.** Catalog of the signals that horizontal B2B customer-success platforms don't ship out of the box but that a K-12 EdTech PSM dashboard requires. Read as a complement to the existing [`psm-metrics-glossary.md`](psm-metrics-glossary.md) (the segment-neutral metric definitions) — this file is where the K-12 overlay lives.
>
> **Refresh trigger.** When ESSER tail effectively ends (post-2027 [verify-at-use — 2026-06-04]); when a national K-12 statute changes the rostering or buyer landscape (e.g., COPPA full enforcement post-April 2026); when superintendent turnover normalizes to pre-pandemic baseline; when LearnPlatform's methodology shifts away from Chrome-extension panel.

---

## 1. Why K-12 health is different from generic B2B

The single most important K-12 gap in horizontal customer-success platforms:

> "Standard SaaS retention tools like NPS surveys and login-based health scores mislead in education because the buyer, user, and budget decision-maker are almost never the same person. A teacher can love the platform while a curriculum director questions alignment and a CFO cuts the line item, creating three distinct churn mechanisms within a single account." — [User Intuition — Education Churn Playbook](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/) (accessed 2026-06-04).

**Operational consequence:** every adoption / sentiment / champion signal in a K-12 health score must be **tagged per persona** (teacher / admin / decision-maker / family). A composite that averages them across personas hides the dominant churn mechanism. The dashboard needs a persona-segmented sentiment view per partner.

This file catalogs the signals. The [`health-score-v2-extension.md`](health-score-v2-extension.md) defines how they roll into the composite.

---

## 2. Persona-segmented adoption signals

The buyer / user / decision-maker separation, made operational. Each row is a separable signal — never roll up across personas before showing them on the home view.

| Signal ID | Name | Persona | Leading / Lagging | Default weight | Half-life | FERPA class | Source |
|---|---|---|---|---|---|---|---|
| `teacher_adoption` | Per-teacher login frequency + lesson-completion rate | teacher | leading | 15% | 7d | district-aggregate | [User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/) |
| `admin_engagement` | Admin-panel session count, settings-changes per month | admin | leading | 10% | 14d | district-aggregate | [User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/) |
| `decision_maker_touch_recency` | Days since last touchpoint with named decision-maker (curriculum dir / superintendent / CTO) | decision-maker | leading | 10% | 30d | district-aggregate | Convergent — Gainsight executive-engagement 20%, Vitally exec-engagement 15% ([Vitally 4 metrics](https://www.vitally.io/post/how-to-create-a-customer-health-score-with-four-metrics)) |
| `champion_status` | Named champion alive in role; named successor identified | decision-maker | leading | 10% | 30d | district-aggregate | [`partner-health-score-drift.md`](partner-health-score-drift.md) §"Champion change not captured" |

**Implementation note.** When the dashboard surfaces a yellow/red state, it must name the persona whose signal dropped. "Cedar Valley is yellow — teacher_adoption holding at 78, admin_engagement -22 over 30d" is decision-grade. "Cedar Valley is yellow" is not. House opinion §3 #4 in [`../CLAUDE.md`](../CLAUDE.md): "Cite the signal."

---

## 3. Family activation gap (parent-comms vendors specifically)

For partner-portal / family-comms products (ParentSquare, ClassDojo, Remind, SchoolStatus, Seesaw), the **activation rate plateau** is the dominant signal — not DAU/MAU.

- "Only 39% of schools report that they reach 90% to 100% of families, and another 27% estimate that they reach 75% to 90% of families." ([Edsby — Parent Engagement K-12 Data](https://www.edsby.com/school-apps-for-parent-engagement-k12-data/commentary/), accessed 2026-06-04.)
- "93% of families report feeling more connected and supported when schools use real-time communication platforms like ClassDojo, Remind, or Seesaw." ([edCircuit — Family Engagement Tools](https://edcircuit.com/how-family-engagement-tools-are-transforming-k-12-education/), accessed 2026-06-04.)

| Signal ID | Name | Persona | Leading / Lagging | Default weight | Half-life | FERPA class |
|---|---|---|---|---|---|---|
| `family_coverage_pct` | % of enrolled families with activated account | family | lagging | 8% (parent-comms vendors only) | 90d | school-n≥10 with suppression |
| `family_message_open_rate` | Avg open rate on broadcast messages, last 30d | family | leading | 5% | 30d | school-n≥10 |
| `family_reply_rate` | % of messages that generate a reply, last 30d | family | leading | 3% | 30d | school-n≥10 |
| `family_translation_coverage` | % of families with primary language other than English receiving translated comms | family | leading | (binary flag) | n/a | district-aggregate |

**Operational note.** Generic DAU/MAU doesn't capture the *coverage gap* that drives administrator dissatisfaction. A school with 99% engaged families on 60% coverage looks healthier on DAU than a school with 70% engagement on 95% coverage — but the second is the one the principal is happy with.

---

## 4. Leadership turnover signals (renewal-risk events)

### 4.1 Why this is a K-12-specific signal class

- **2024-25 superintendent turnover: 23% in the 500 largest districts**, up from 20% prior year, vs. pre-pandemic 14-16% ([K-12 Dive — Superintendent Turnover](https://www.k12dive.com/news/high-superintendent-turnover-staffed-up/804337/), accessed 2026-06-04 — flagged as single-source in research ledger; cross-check before slide use).
- "For EdTech vendors, each leadership transition is a renewal risk event. The incoming superintendent or principal arrives with their own vendor relationships … A platform that was championed by their predecessor may be evaluated from scratch — or simply not evaluated at all, replaced by a default preference for familiar tools." ([User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04.)
- **Detection asymmetry:** admin/decision-maker engagement drops while teacher usage continues. "This often means that the account administrator may be evaluating alternatives" ([User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04). This is the diagnostic pattern that distinguishes leadership-turnover risk from generic disengagement.

### 4.2 The signals

| Signal ID | Name | Persona | Leading / Lagging | Default weight | Half-life | FERPA class |
|---|---|---|---|---|---|---|
| `superintendent_change_12mo` | Boolean: superintendent changed in last 12 months [verify-at-use — 2026-06-04] | decision-maker | leading | 8% (binary multiplier on champion subscore) | 365d | district-aggregate |
| `cto_change_12mo` | Boolean: CTO / IT director changed in last 12 months | decision-maker | leading | 5% | 365d | district-aggregate |
| `curriculum_director_change_12mo` | Boolean: curriculum director changed in last 12 months | decision-maker | leading | 5% | 365d | district-aggregate |
| `admin_disengagement_with_teacher_usage_holding` | Diagnostic flag: admin_engagement -30% over 60d while teacher_adoption flat or up | decision-maker | leading | (alert flag — not a score component) | n/a | district-aggregate |

**Source for the change events:** state press releases, BoardDocs scraping, EdSurge / K-12 Dive feeds, EdWeek Marketbrief alerts. The `partner-profile-curator` agent is the owner of the named-role-in-seat record.

---

## 5. Funding-source signals (ESSER cliff aftermath)

### 5.1 Why this is a live signal in 2026 [verify-at-use — 2026-06-04]

- ESSER provided ~$190B; "30% to 40% of a typical district's discretionary spending over the life of the funding" ([K-12 Dive — ESSER Legacy](https://www.k12dive.com/news/esser-pandemic-COVID-K-12-spending-what-will-its-legacy-be/815999/); [Oliver Wyman](https://www.oliverwyman.com/our-expertise/insights/2025/mar/k-12-investment-strategies-stimulus-funds-end-2025.html), accessed 2026-06-04).
- "92% of school districts had used ESSER funds for educational technology" but "only 27% of states have plans to sustain funding for technology initiatives previously supported by federal relief programs" ([SETDA 2025 State EdTech Trends](https://www.setda.org/resource/2025-state-edtech-trends-report/), accessed 2026-06-04).
- In March 2025, "the U.S. Department of Education unexpectedly rescinded its extension for spending more than $2.5 billion of American Rescue Plan (ARP) ESSER funds" ([GovTech](https://www.govtech.com/education/k-12/experts-push-student-focused-budgeting-as-esser-winds-down), accessed 2026-06-04).

**Operational consequence:** districts whose initial purchase was ESSER-funded carry structural renewal risk through at least 2027 [verify-at-use — 2026-06-04]. These accounts deserve over-weighting in the at-risk queue regardless of current health-band.

### 5.2 The signals

| Signal ID | Name | Persona | Leading / Lagging | Default weight | Half-life | FERPA class |
|---|---|---|---|---|---|---|
| `esser_funded_flag` | Boolean: original purchase was ESSER-funded | decision-maker | lagging | (priority multiplier ×1.3 on the action queue) | 365d | district-aggregate |
| `funding_source_confirmed` | Status: confirmed / unconfirmed / sustainable (general fund / state line item / Title I) | decision-maker | leading | (gate — required field for any expansion play) | n/a | district-aggregate |

**Cross-reference:** [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) for the K-12 budget-build cycle that ESSER replacement conversations must hit.

---

## 6. State-testing-window blackout (seasonality adjustment)

### 6.1 Why this matters

State testing windows (typically Apr-May for spring summative assessments; Florida and others now run fall + spring under FAST) **structurally suppress edtech usage for 4-8 weeks** ([Frontline — Standardized State Testing Trends](https://www.frontlineeducation.com/blog/standardized-state-testing-in-education-changes-and-future-trends/), accessed 2026-06-04).

Without seasonality adjustment, every district fires a false at-risk alert every spring. The dashboard either suppresses usage signals during the window or overlays a "testing window" band on usage sparklines.

### 6.2 The signals

| Signal ID | Name | Persona | Leading / Lagging | Default weight | Half-life | FERPA class |
|---|---|---|---|---|---|---|
| `state_testing_window_active` | Boolean: account's state is currently in testing window (per state calendar) | n/a | n/a | (signal suppressor — disables `teacher_adoption` decay during window) | n/a | district-aggregate |
| `testing_window_usage_recovery_rate` | % return-to-baseline usage in the 14 days post-window | teacher | leading | 5% | 90d | district-aggregate |

The `testing_window_usage_recovery_rate` is the actually-predictive signal — a district whose usage recovers fast post-testing is engaged; one whose usage stays low post-testing has a deeper problem the testing window was hiding.

**Cross-reference:** [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) §2 for the dead-zone signal-suppression rules this signal participates in.

---

## 7. Back-to-school surge (the operational stress test)

### 7.1 Why this is a separate signal class

- "Back-to-school in August brings a tsunami of new student enrollments, roster uploads, and schedule changes." ([Dromo — EdTech Data Onboarding](https://dromo.io/blog/data-onboarding-for-edtech-student-records-rosters-and-compliance), accessed 2026-06-04.)
- "Digital on Day One" is a recognized industry concept; the first 2 weeks of school are the highest-leverage CS intervention period of the year.

### 7.2 The Activation Watch widget

Active **only Aug 1 - Sep 30** ([verify-at-use — 2026-06-04] — varies by state-by-state school-start date; the widget should consume per-state academic calendars not a hard-coded window). Outside that window, the widget collapses.

| Signal ID | Name | Persona | Leading / Lagging | Default weight (in-window) | Half-life | FERPA class |
|---|---|---|---|---|---|---|
| `license_claim_rate` | % of provisioned licenses activated by Day 14 of school | teacher | leading | 10% | 7d | district-aggregate |
| `first_class_completion_rate` | % of provisioned classes with ≥1 completed assignment by Day 14 | teacher | leading | 8% | 7d | school-n≥10 |
| `roster_sync_error_count` | Count of active rostering errors / sync incidents | admin | leading | 7% | 7d | district-aggregate |
| `digital_on_day_one_status` | Status: ready / partial / blocked, per school | admin | leading | 5% | 14d | school-aggregate |

**Reference:** [`k12-adoption-arc-fall-spring-summer.md`](k12-adoption-arc-fall-spring-summer.md) for the 9-phase adoption calendar these signals participate in.

---

## 8. Rostering health signals

Rostering is "the silent killer" (house opinion §3 #8 in [`../CLAUDE.md`](../CLAUDE.md)) — when the data isn't right, it's almost always a rostering issue the PSM has to coordinate without owning the fix.

| Signal ID | Name | Persona | Leading / Lagging | Default weight | Half-life | FERPA class |
|---|---|---|---|---|---|---|
| `roster_sync_last_success_hours` | Hours since last successful sync (Clever / ClassLink / OneRoster direct) | admin | leading | 5% | 7d | district-aggregate |
| `roster_sync_success_rate_30d` | % of attempted syncs in last 30d that completed cleanly | admin | leading | 5% | 30d | district-aggregate |
| `roster_completeness_pct` | % of expected students / teachers actually present in the rostered set | admin | lagging | 5% | 30d | district-aggregate |
| `roster_id_drift_count` | Count of IDs that changed identity across the last 2 sync cycles | admin | leading | 3% | 14d | district-aggregate |

**Cross-reference:** [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) for the full diagnostic framework these signals plug into. [`sis-sso-rostering-integration-patterns.md`](sis-sso-rostering-integration-patterns.md) for SSO-specific extensions.

**FERPA note.** `roster_completeness_pct` and `roster_id_drift_count` are district-aggregate and FERPA-safe. The discrete student-level data backing them is not exposed on the dashboard.

---

## 9. LearnPlatform external benchmark (optional widget)

### 9.1 What it is

LearnPlatform's EdTech Top 40 + EdTech300 indexes provide an *external* engagement benchmark — page-load events per 1000 users, normalized across 10,000+ products, collected via Chrome extension ([Instructure — EdTech Top 40](https://www.instructure.com/edtech-top40); [LearnPlatform Equity Dashboard](https://www.prnewswire.com/news-releases/learnplatform-launches-national-edtech-equity-dashboard-to-improve-visibility-of-digital-k-12-engagement-and-gaps-across-us-301277353.html), accessed 2026-06-04).

### 9.2 The signal

| Signal ID | Name | Persona | Leading / Lagging | Default weight | Half-life | FERPA class |
|---|---|---|---|---|---|---|
| `learnplatform_rank_percentile` | Vendor's usage percentile vs. EdTech300 national benchmark | n/a (product-level, not partner-level) | lagging | (context widget — not a score component) | 90d | n/a (vendor-aggregate, not student-level) |

### 9.3 Caveat (flagged in research ledger)

LearnPlatform's Chrome-extension methodology is **panel-based, not census** — confidence intervals apply ([LearnPlatform Engagement Dataset (ICPSR)](https://www.icpsr.umich.edu/web/ICPSR/studies/38426), single-source flag in research ledger, accessed 2026-06-04). The widget should display "percentile ± uncertainty band" not a bare rank. Treat as directional context for QBR narrative, not as a decision input.

---

## 10. Signal taxonomy at a glance

| Signal class | Lives where on dashboard | Persona | Owner agent |
|---|---|---|---|
| Persona-segmented adoption (§2) | Portfolio summary + Account 360 drill-down | teacher / admin / decision-maker | `learning-analytics-analyst` |
| Family activation (§3) | Account 360, parent-comms vendors only | family | `learning-analytics-analyst` + `ferpa-comms-translator` |
| Leadership turnover (§4) | Leadership Watch widget + Account 360 flag row | decision-maker | `partner-profile-curator` |
| Funding source (§5) | Account 360 flag + at-risk-ARR multiplier | decision-maker | `partner-profile-curator` + `learning-analytics-analyst` |
| State testing window (§6) | Usage sparkline overlay + signal suppressor | n/a | `learning-analytics-analyst` |
| Back-to-school surge (§7) | Activation Watch widget (Aug-Sep only) | teacher + admin | `partner-success-manager` |
| Rostering health (§8) | KPI card + Account 360 + alert flags | admin | `learning-analytics-analyst` |
| LearnPlatform benchmark (§9) | Account 360 context widget | n/a | `learning-analytics-analyst` |

---

## 11. Refresh triggers

- ESSER tail effectively ends (post-2027 [verify-at-use — 2026-06-04]) → §5 weights drop.
- Superintendent turnover normalizes to pre-pandemic baseline (~14-16% [verify-at-use — 2026-06-04]) → §4 priority multiplier reduces.
- A national K-12 statute changes the buyer / rostering landscape (e.g., COPPA full-enforcement post-April 2026 [verify-at-use — 2026-06-04]; FERPA reform).
- LearnPlatform changes methodology away from Chrome-extension panel → §9 caveat changes.
- A new K-12-specific signal class surfaces (e.g., chronic-absenteeism integration, IEP-compliance flags) — add a section.

---

## 12. References (existing plugin artifacts)

- [`psm-dashboard-canon-2026.md`](psm-dashboard-canon-2026.md) — the canonical PSM dashboard layout these signals populate.
- [`health-score-v2-extension.md`](health-score-v2-extension.md) — how these signals roll into the composite health score.
- [`ferpa-dashboard-boundaries.md`](ferpa-dashboard-boundaries.md) — the compliance gate every signal's FERPA-class field must clear.
- [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) — the dead-zone calendar that suppresses these signals during testing windows / breaks.
- [`partner-health-score-drift.md`](partner-health-score-drift.md) — the drift symptoms that retire signals from this catalog.
- [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) — the K-12 budget-build window that funding-source signals feed.
- [`k12-adoption-arc-fall-spring-summer.md`](k12-adoption-arc-fall-spring-summer.md) — the 9-phase calendar overlay for adoption signal interpretation.
- [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) — the full diagnostic framework for §8 rostering signals.
- [`psm-metrics-glossary.md`](psm-metrics-glossary.md) — the segment-neutral metric definitions this file extends.
