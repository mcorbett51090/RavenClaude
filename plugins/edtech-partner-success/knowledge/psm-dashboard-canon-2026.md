---
name: psm-dashboard-canon-2026
description: The convergent "good operational PSM dashboard" pattern — Portfolio Summary → Daily Action Center → Account 360 → Timeline → Health Distribution — drawn from Gainsight, Planhat, ChurnZero, Catalyst, and Totango product canon. The single canonical spec the K-12 EdTech dashboard build kit reads from. Includes the 8-dashboard archetype list, the 5-second-rule layout test, and the Stephen Few / IBCS rules inherited.
last_reviewed: 2026-06-04
confidence: high
---

# PSM Dashboard Canon (2026)

> **Scope.** Operational design canon for a Partner Success Manager (PSM) home page in K-12 EdTech. **Non-goals:** analytical exploration tools (different design constraints — interactive depth, broad filter surface), executive roll-up decks (different design constraints — five KPIs max, monthly cadence). Conflating the three is the most common dashboard failure mode ([Improvado — Dashboard Design Guide](https://improvado.io/blog/dashboard-design-guide); [RIB Software — 25 Dashboard Design Principles](https://www.rib-software.com/en/blogs/bi-dashboard-design-principles-best-practices), accessed 2026-06-04).
>
> **Refresh trigger.** When any of the four major Customer Success Platforms (Gainsight, Planhat, ChurnZero, Totango) materially restructures their CSM home page; when IBCS revises Standards 1.2; when the PSM book shifts away from K-12 majority.

---

## 1. The convergent "home base" pattern (table stakes)

Every major Customer Success Platform now ships a CSM-centric home page that fuses the same four widgets. This is the strongest single signal in the research — independent product teams converged on the same layout from different starting points.

| Widget | Function | Per-vendor naming |
|---|---|---|
| **Portfolio Summary** | Book of business at a glance — segmented health distribution, totals, deltas. | Gainsight `My Portfolio` widget; Planhat dashboard "health trends across segments"; Catalyst "prioritized account lists"; Totango "manage their day in one screen" |
| **Daily Action Center (Cockpit)** | Today's prioritized CTAs / tasks, grouped by overdue / today / later. | Gainsight `Cockpit`; ChurnZero `Command Center` "single view of daily tasks"; Totango "tasks grouped by due date — overdue / today / later" |
| **Timeline** | Live touchpoint log + notes from the PSM and integrated systems. | Gainsight `Timeline` widget; ChurnZero "log tasks, view milestones and alerts"; Planhat journey timelines |
| **Health Distribution** | Red/Yellow/Green band counts with delta vs. prior week. | Gainsight `Open CTAs` + health charts; Planhat "health trends across teams, segments, lifecycle stages"; Catalyst "leadership dashboards tracking churn, NRR, health distribution" |

**Source citations:**
- Gainsight Home for CSMs: "centralized workspace … widgets that provide a holistic view of insights … My Portfolio … Cockpit … Timeline" — Gainsight Home for CSMs docs ([gainsight.com docs](https://support.gainsight.com/gainsight_nxt/Gainsight_Home/User_Guides/Gainsight_Home_for_CSMs), accessed 2026-06-04).
- ChurnZero Command Center: "Single view of daily tasks and detailed reporting on your book of business … log tasks, view milestones and alerts" ([churnzero.com/features/command-center](https://churnzero.com/features/command-center/), accessed 2026-06-04).
- Catalyst (now Totango): "CSM dashboards with prioritized account lists and daily task views, leadership dashboards tracking churn, NRR, health distribution" ([catalyst.io/product/playbooks](https://catalyst.io/product/playbooks); [help.catalyst.io](https://help.catalyst.io/hc/en-us/articles/28924671873556-Use-Catalyst-to-view-or-manage-customer-accounts), accessed 2026-06-04).
- Totango: "Intelligent workflow format that enables [CSMs] to manage their day in one screen … Tasks are grouped by their due date by default and have three categories: overdue tasks, today's tasks, and tasks for later" ([Totango CS Center](https://support.totango.com/hc/en-us/articles/204012969), accessed 2026-06-04).
- Planhat: "Custom dashboards track customer journeys, measure CSM efficiency … Dashboards display health trends across teams, segments, and lifecycle stages" ([planhat.com/customer-success/health](https://www.planhat.com/customer-success/health), accessed 2026-06-04).

---

## 2. The 5-section flow for a RavenClaude PSM home page

The convergent home-base pattern, sequenced left-to-right / top-to-bottom for K-12 EdTech:

1. **Portfolio Summary** (top-left, status indicator) — KPI strip + health-band distribution. **Most-urgent exception belongs here.**
2. **Daily Action Center** (left column, primary surface) — today's top-N accounts with NBA + confidence + rationale (see [`daily-action-queue` skill](../skills/daily-action-queue/SKILL.md)).
3. **Account 360** (drill-down on row click) — single-account view: per-component health, persona-segmented signals, last 90 days timeline, open CTAs, renewal/budget-cycle context. **K-12 overlay:** funding-source flag, leadership turnover flag, state-testing-window flag.
4. **Timeline** (right column, live feed) — chronological touchpoints + system events + flags fired in the last 7 days. Acts as the "what changed since I last looked" surface.
5. **Health Distribution** (bottom strip) — band donut + 12-week trend sparkline + cohort peer-range. The score-distribution sanity check.

**Layout test (from Stephen Few canon):** if a PSM can't answer "what's on fire today?" within 5 seconds of opening, the layout is too dense. ([Ethos3 — 5 Second Rule](https://ethos3.com/mastering-the-5-second-rule-elevate-your-presentation-design-for-maximum-impact/), accessed 2026-06-04.)

---

## 3. The Gainsight "8 dashboards" canon (full catalog)

Gainsight's widely-cited piece names eight dashboard archetypes that top-performing CS teams maintain. The K-12 PSM home page maps onto archetypes 1-3 + selectively 5/6. The remaining archetypes live on separate surfaces (manager view, executive view) — they are **not** part of the operational PSM home.

| # | Archetype | Audience | Operational / Analytical / Executive | On the PSM home page? |
|---|---|---|---|---|
| 1 | CSM Daily / Operational | PSM (self) | Operational | **Yes** — the daily action center + portfolio summary |
| 2 | Book-of-Business / Portfolio | PSM (self) + CS leader | Operational | **Yes** — the portfolio summary + health distribution |
| 3 | Health Distribution | PSM + CS leader | Operational | **Yes** — bottom-strip widget |
| 4 | Renewal Pipeline | CS leader, RevOps, finance | Analytical / Executive | **No** — separate surface; K-12 needs *budget-decision-date* axis, not contract-end-date |
| 5 | Adoption / Product Usage | PSM + product | Analytical | **Drill-down only** — surfaces inside Account 360, not on home |
| 6 | NPS / Sentiment | PSM + product + CS leader | Analytical | **Drill-down only** — surfaces inside Account 360 |
| 7 | CTA / Task Performance (manager view) | CS leader | Operational (for the manager, not PSM) | **No** — manager surface |
| 8 | Executive / NRR & GRR | Exec team | Executive | **No** — exec surface |

Source: [Gainsight — 8 Dashboards Top Performing CS Teams Can't Live Without](https://www.gainsight.com/blog/8-dashboards-top-performing-customer-success-teams-cant-live-without/) (accessed 2026-06-04 — WebFetch 403, citation per SERP summary content; the 8-archetype list itself is corroborated by multiple practitioner blogs including [Velaris CS Dashboard Examples](https://www.velaris.io/articles/customer-success-dashboard-examples) and [Customer Success Collective — Building a CS Dashboard](https://www.customersuccesscollective.com/building-a-customer-success-dashboard/), so the *catalog* is well-attested even though the canonical Gainsight piece is paywalled to WebFetch).

---

## 4. KPI top strip (convergent across sources)

The KPI cards at the top of the portfolio summary. K-12 additions tagged.

| KPI | Format | Source |
|---|---|---|
| Health-band distribution (R/Y/G counts) | KPI card + sparkline | Vendor convergence (Gainsight, Planhat, ChurnZero, Totango) |
| Renewal pipeline next 90d (count + $ ARR) | KPI card | Vendor convergence |
| Overdue CTAs (count, color-coded) | KPI card | Gainsight Cockpit; ChurnZero Command Center |
| At-risk ARR ($) | KPI card | Practitioner consensus (Customer Success Collective, Velaris) |
| Today's touches scheduled (count) | KPI card | Totango "today's tasks" canonical grouping |
| **State-testing-window flag** (count of accounts in blackout) — **K-12** | KPI card | Frontline education (state testing trends); K-12 signal taxonomy |
| **Rostering errors active** (count of incidents) — **K-12** | KPI card | Clever / ClassLink / OneRoster operational practice |

**IBCS semantic notation rule:** the color used for "at risk" must be the **same** across every widget on the page (same red = same meaning, not "negative variance" red in one widget and "missing data" red in another). IBCS improves analysis speed 46% and accuracy 61% when applied consistently ([IBCS Standards 1.2](https://www.ibcs.com/ibcs-standards-1-2/); [Wikipedia — IBCS](https://en.wikipedia.org/wiki/International_Business_Communication_Standards), accessed 2026-06-04).

---

## 5. Inherited design rules (Stephen Few + IBCS + NOC research)

These are non-negotiable. The build kit's validation gate rejects dashboards that violate them.

### 5.1 Stephen Few — at-a-glance constraint
- "Dashboards are usually required to display a great deal of somewhat disparate information in a limited amount of space (a single screen) … information must be organized into meaningful groups in a way that features what's most important." ([Stephen Few — Formatting and Layout Matter](https://www.perceptualedge.com/articles/Whitepapers/Formatting_and_Layout_Matter.pdf), accessed 2026-06-04.)
- **Inherited rule:** single screen, no scrolling. The PSM home page is one viewport.

### 5.2 The 5-second rule
- "The 5 second rule measures how effectively information is communicated to viewers within the initial 5 seconds … Cognitive Load Theory" ([Ethos3](https://ethos3.com/mastering-the-5-second-rule-elevate-your-presentation-design-for-maximum-impact/); [DEV — 5 Second Rule](https://dev.to/deyrupak/are-you-aware-of-the-5-second-rule-398a), accessed 2026-06-04).
- **Inherited rule:** "What's on fire today?" must be answerable in 5 seconds. If it isn't, the layout is too dense.

### 5.3 IBCS SUCCESS principles
- **S**ay (convey a message), **U**nify (same color = same meaning), **C**ondense (high info density), **C**heck (visual integrity), **E**xpress (right chart type), **S**implify (no clutter), **S**tructure (organize content). ([IBCS Standards 1.2](https://www.ibcs.com/ibcs-standards-1-2/), accessed 2026-06-04.)
- **Inherited rules:**
  - Same color always = same meaning (red is "at risk" everywhere; never "negative variance" in one place and "missing data" elsewhere).
  - Variance shown alongside the value with fixed-position delta indicator.
  - Time series go left-to-right; categorical comparisons top-to-bottom.

### 5.4 Top-left = current status / most-urgent exception
- "The most important signal in the top-left is the current status or the most urgent exception." ([Stephen Few — Dashboard Design Course](https://www.perceptualedge.com/files/Dashboard_Design_Course.pdf); convergent with [Domo — Sparklines](https://www.domo.com/learn/charts/sparkline-chart) on placement, accessed 2026-06-04.)
- **Inherited rule:** the highest-severity at-risk account or the count of red-band partners goes in the top-left KPI card.

### 5.5 Sparklines + small multiples for density
- Sparklines: "small, inline line charts placed next to a KPI value that show the recent trend without requiring a full chart" ([Domo — Sparklines](https://www.domo.com/learn/charts/sparkline-chart); [Stephen Few — Sparkline Best Practices](https://www.perceptualedge.com/articles/visual_business_intelligence/best_practices_for_scaling_sparklines.pdf), accessed 2026-06-04).
- Small multiples: same chart per category, same scale + size + shape ([Omni Analytics — Data Viz Best Practices](https://omni.co/articles/data-visualization-best-practices-for-better-decision-making); [DataCamp — Dashboard Design](https://www.datacamp.com/tutorial/dashboard-design-tutorial), accessed 2026-06-04).
- **Inherited rule:** the per-partner row in Daily Action Center carries a 12-week sparkline; the cohort comparison uses small multiples, not one stacked chart.

### 5.6 NOC / situational-awareness research
- "All information should be color coded to classify the severity of issues. Filtering, suppression, and categorization prevent alarm fatigue." ([Activu — SOC Best Practices](https://www.activu.com/security-operations-center-dashboard-best-practices-a-checklist-for-critical-situational-awareness/), accessed 2026-06-04.)
- Energy-grid control-room research using eye-tracking found that layout *across* screens correlated strongly with cognitive load via subjective + physiological probes ([PMC — Control Room Cognitive Load](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8995508/), accessed 2026-06-04).
- **Inherited rules:**
  - Suppression beats noise: signals fired during K-12 dead zones (Aug, winter break, state testing) are suppressed on the home view — they aren't *missing*, they're *deferred until the dead zone ends*. See [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md).
  - 9-widget cap on the home view (practitioner consensus, [Velaris — CS Dashboard Examples](https://www.velaris.io/articles/customer-success-dashboard-examples), accessed 2026-06-04). 15+ widgets is analytical, not operational.

---

## 6. K-12 overlay (where the canonical pattern needs translation)

The vendor templates are tuned for horizontal B2B SaaS (seat-based, monthly billing, single buyer/user). K-12-specific signals — leadership turnover, state-testing-window-suppressed usage, ESSER tail, multi-stakeholder buyer (curriculum / IT / superintendent) — are not in the out-of-box widgets ([User Intuition — Education Churn Playbook](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04).

| Generic widget | K-12 overlay |
|---|---|
| Renewal pipeline by *contract end date* | Re-axis to **budget-decision date** (typically Feb 15 for July-1 fiscal-year districts) — the real renewal window is Sep-Mar, not Apr-Jun. See [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md). |
| At-risk ARR by health band | Add **funding-source flag** — districts whose initial purchase was ESSER-funded carry structural renewal risk through at least 2027 [verify-at-use — 2026-06-04]. |
| Sentiment NPS card | **Persona-segmented sentiment** — teacher / admin / decision-maker. NPS aggregated across personas hides the buyer-user-decision-maker mismatch ([User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04). See [`k12-signal-taxonomy.md`](k12-signal-taxonomy.md). |
| Usage 90-day trend | **Seasonality-adjusted** — overlay state-testing-window bands per state. Without adjustment, every district fires a false at-risk alert every spring. |
| Account 360 | Add **Leadership Watch** row — districts where superintendent / CTO / curriculum director changed in the last 12 months. 23% superintendent turnover in 500 largest districts in 2024-25 (up from pre-pandemic 14-16%) ([K-12 Dive — Superintendent Turnover](https://www.k12dive.com/news/high-superintendent-turnover-staffed-up/804337/), accessed 2026-06-04 — single-source flag in research ledger). |
| (none) | **Activation Watch** widget active Aug 1 – Sep 30 only. Tracks license-claim rate, first-class-completion rate, roster-sync error count. Outside that window, collapses. |

---

## 7. Explicit non-goals (what this surface is NOT)

- **Not analytical.** No free-form filter surface, no cross-tab pivots, no ad-hoc segmentation. Those live on a separate analytics surface owned by `learning-analytics-analyst`.
- **Not executive.** No NRR/GRR roll-up, no cohort-cohort comparison, no exec-narrative sparklines. Those live on a separate executive surface.
- **Not a CRM.** No edit-account-in-place, no inline contact editing. The dashboard reads; the source-of-truth systems (SFDC, profile docs) write.
- **Not the manager view.** No "team load by PSM," no "CTAs completed per PSM per week." Those are CS-leader operational surfaces.

Conflating these is the #1 dashboard design failure mode ([Improvado — Dashboard Design Guide](https://improvado.io/blog/dashboard-design-guide); [RIB Software](https://www.rib-software.com/en/blogs/bi-dashboard-design-principles-best-practices), accessed 2026-06-04).

---

## 8. Refresh triggers for this document

- A major CSP (Gainsight, Planhat, ChurnZero, Totango) materially restructures their CSM home page widget canon.
- IBCS publishes Standards 1.3+ with revised semantic-notation rules.
- The PSM book shifts away from K-12 majority (the K-12 overlay in §6 stops being the dominant translation).
- The 5-second-rule layout test starts failing on the build kit's generated dashboards in audit.

---

## 9. References (existing plugin artifacts)

- [`k12-signal-taxonomy.md`](k12-signal-taxonomy.md) — the K-12-specific signal catalog that powers §6's overlay.
- [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) — calendar dead zones the home view must suppress.
- [`partner-health-score-drift.md`](partner-health-score-drift.md) — the score that powers the health-distribution widget needs decay discipline or the widget decorates instead of predicts.
- [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) — the K-12 120-180-day renewal clock that re-axes the renewal pipeline widget.
- [`../templates/health-score-dashboard.md`](../templates/health-score-dashboard.md) — the existing spec the build kit reads from.
- [`../bi-report/data.json`](../bi-report/data.json) — the data shape the BI report consumes; the schema this canon implies.
- [`ferpa-dashboard-boundaries.md`](ferpa-dashboard-boundaries.md) — the compliance gate every widget must pass.
