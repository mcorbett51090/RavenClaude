---
target_path: plugins/ravenclaude-core/best-practices/operational-console-design.md
last_reviewed: 2026-06-04
status: rule — load-bearing for any operational dashboard or "single pane of glass" surface
audience: [dashboard-builder, frontend-coder, designer, learning-analytics-analyst]
refresh_triggers:
  - WCAG version bump (currently 2.2)
  - Major design-system update (Carbon, Material, Astro UXDS, SAP Fiori)
  - New alarm-fatigue / CVD research that revises ≥5% false-positive heuristic
  - A real shipped console exposes a recurring failure not in this doc
sources:
  - /tmp/research-dashboard-ux.md (research synthesis; 79 distinct URLs across 14 topical clusters)
---

# Operational console design — the floor for any "single pane of glass"

> **Status.** Authoritative reference for designing the dashboard a PSM / SRE / PM opens every morning. Synthesized from Stephen Few, Tufte, NN/g, IBCS, Carbon / Astro UXDS / SAP Fiori, the alarm-fatigue ICU literature, and 2025-2026 real-time-dashboard practice.

---

## 1. The 5-second test (NN/g + Few — load-bearing)

A PSM opening the console must be able to answer **"what needs my attention right now?"** in 5 seconds, **without scrolling, filtering, or hovering.**

- A single fixation: 200-600 ms (working range 200-300 ms for routine perception)
- 5 seconds = ~10-20 fixations = enough for a structural impression, not for reading body copy
- The "command-line of attention" — the single top row that says "3 items need your attention" — should resolve in 1-2 fixations (≈400-600 ms)

**Operational rule:** the top fold answers the attention question. Anything below the fold is the *next* layer of attention; it doesn't need to be 5-second-readable, just structurally legible.

[Few *Information Dashboard Design*; NN/g *5-Second Usability Test*]

---

## 2. Color discipline — ≥2 channels, WCAG 1.4.1 Level A

### The accessibility floor (non-negotiable)

- **~8% of men, 0.5% of women** have color-vision deficiency (CVD); red↔green and red↔orange are the most-confused pairs — **exactly** the colors most dashboards use for status.
- **WCAG 2.2 SC 1.4.1 (Use of Color), Level A:** color must NOT be the only means of conveying information.
- Status indicators must use **≥2 of** {color, shape, symbol/icon, text label}.

[Carbon Design System; Astro UXDS; SAP Fiori — all converge]

### When the green/yellow/red palette backfires

- CVD users see red and green as the same dull tan/brown — a dashboard tuned to "scan for red" silently fails them.
- **Alarm fatigue:** ICU literature reports **72-99% of alarms are false positives**; a single shift exposes a nurse to ~1,000 alarms; the trained response is to ignore them. **Once a dashboard's red threshold is mis-tuned, the human stops looking at red.**
- **Too much red habituates the eye** — Few's principle: red is the loudest signal in your palette; spend it sparingly so it retains meaning.

[PLOS One Drew et al. 2014; Atlassian Incident Management; Nature npj Digital Medicine s41746-019-0160-7]

### The seven mitigation patterns

1. **Default to neutral, escalate by exception.** Tiles render neutral gray/blue at rest; color appears only on `attention` or `critical`.
2. **Redundant encoding.** Color + icon + text label.
3. **Severity tiering with shape:** filled circle / hollow circle / triangle / square — distinguishable under CVD simulation.
4. **Border/background separation.** Colored border + neutral background + dark text — never colored text on colored background.
5. **Calibrate thresholds for ≤5% false-positive rate on `critical`.** Above ~5%, the team trains itself to ignore the highest severity. Design to PPV, not recall.
6. **Acknowledge / snooze affordances** for fired alerts being worked.
7. **Sound / motion sparingly** — motion is preattentive but exhausting; reserve for the single highest-severity tier.

---

## 3. Drill-down patterns — side-panel default

The field has converged on three patterns:

| Pattern | When it fits | When it hurts |
|---|---|---|
| **Modal dialog** | A single atomic next action: confirm, edit one field, see latest 3 events | Anything that needs cross-reference with the dashboard underneath; anything multi-step |
| **Side panel / drawer** *(default)* | Detail-on-demand for the row/tile just clicked; preserves spatial context; drawer can stay open between items | Content that genuinely needs full-screen (Gantt, long form) |
| **Route navigation** (dedicated URL) | A deep workflow lasting minutes; needs bookmarkable URL; needs shareability | A 30-second glance — full route nav costs context |

[UXPin 2025; Pencil & Paper; NN/g *Progressive Disclosure*]

### Practical rules (consensus)

- **Side panel is the default** for "show me more about this row." It preserves spatial map.
- **Modal only when blocking is the point** (destructive confirm, single-field edit). Avoid multi-step in modals.
- **Route navigation when the URL matters** — bookmark, share, return.
- **Breadcrumbs + visible close affordance** on every drill level. Drilling without a way back is a usability bug.
- **Predictable, consistent interactions.** Click-row-opens-panel everywhere, OR click-row-navigates everywhere — never mix.
- **Progressive disclosure beats permanent disclosure** — summary in table, full record on intent.

---

## 4. Filter persistence — URL is the source of truth

### Two-tier persistence

- **URL state** (query string) is the source of truth for *view state* — filters, sort, pagination, drill location, time-range. Bookmarkable, shareable in Slack, restorable after refresh, back-button-friendly.
- **Local-storage** is for *user preference* state — theme, sidebar collapsed, default time-range. **Not** for view state — preferences shouldn't travel in a shared URL.

[LogRocket; TanStack Router discussion; dev.to *Persisting and Sharing Application State*]

### Operational-console specifics

- **Active filters surfaced as chips at the top of the view**, each with an individual `×` and a `Clear all` link.
- **Saved views.** Named URL presets ("My morning view," "Pre-standup view") — the UI lets the user name, save, and share the current URL state.
- **URL-state hygiene.** Only UI-relevant state in the URL. Never secrets, never internal IDs that mean nothing to humans, never transient form input.
- **Back / forward navigation must work.** A surprising number of dashboards break this by using client-side router state instead of real URL state.

---

## 5. Time-zone discipline

The settled answer across enterprise practice and timezone literature:

1. **Store everything in UTC server-side.** Non-negotiable. DST-immune, audit-friendly.
2. **Convert at the edge** (UI / export layer), never in storage or business logic.
3. **Display strategy depends on portfolio shape:**

| Portfolio shape | Display rule |
|---|---|
| Single-site, single-region | Local time only; UTC offset in footnote |
| Multi-site, single-region | Local time of *site*; viewer's local time in tooltip |
| Truly multi-region (cross-continental) | Show **both**: site-local + viewer-local, with timezone abbrev explicit |

### UX rules

- **Always show the timezone label** next to wall-clock times. "14:32" alone is ambiguous; "14:32 PST" or "14:32 (your time)" is not.
- **Users think in cities, not UTC offsets.** Selector accepts "New York" or "London."
- **Detect viewer's TZ** from browser; always allow override; remember the override.
- **DST transitions.** Use zone names (`America/Los_Angeles`) not offsets (`UTC-8`).
- **Libraries:** `Intl.DateTimeFormat`, `Luxon`, `date-fns-tz`, `Temporal`. Never roll your own.

[Smart Interface Design Patterns; Vitaly Friedman LinkedIn]

---

## 6. Data-freshness — non-negotiable

1. **Always show "Last updated N min ago"** — footer / corner badge / chip per tile. Without it, the user cannot tell stale from broken.
2. **Three-state staleness indicator:** Live / Stale / Paused.
3. **Manual refresh button** beside the freshness indicator.
4. **Pause / snapshot on user demand.** A dashboard that re-paints while the user is *reading* a row is hostile.
5. **Visual diff on update** — briefly highlight the changed value (subtle border flash, fade-from-yellow).
6. **Latency budgets:** sub-second query response for click-driven refresh. 200ms vs 2s is the difference between "tool" and "slow tool."
7. **Sane defaults:** most PSM use cases are **near-real-time** (1-5 minute lag is invisible). True streaming rarely justified at portfolio altitude.
8. **Degradation transparency:** "data paused — last live point 14:32" not silent freeze.

[Smashing Magazine *UX Strategies for Real-Time Dashboards* 2025; Raw.Studio]

---

## 7. Empty states — diagnose, then prescribe

The default "No data" empty state is the single biggest credibility leak in an ops dashboard.

### Best-practice structure (Carbon / SAP Fiori / Setproduct / Pencil & Paper / Eleken / NN/g)

1. **Diagnostic headline.** "No active risks in this portfolio" or "Connect your project source to start" — state *why* it's empty.
2. **One-line supporting copy** — what would cause data to appear.
3. **Primary CTA** — the one action that resolves the empty state.
4. **Subtle visual** — icon or illustration, never decorative-only.
5. **Distinguish three categories:**
   - **First-run** — "you haven't set this up yet" → guide to setup
   - **Filter-emptied** — "your filter excludes everything" → offer "clear filters"
   - **Truly empty / healthy** — "no items need your attention" → celebrate, don't apologize

### Operational-tool specifics

- **Distinguish "no data" from "data hasn't arrived yet" from "service is degraded."** A 5-minute staleness should NOT look identical to a 5-day staleness which should NOT look identical to a never-connected source.
- **The all-clear empty state is celebratory, not blank.** "0 issues — last checked 2 min ago" beats `—` or `N/A`.
- **Multi-widget consistency.** When several tiles can be independently empty, the empty states must share visual structure — or the dashboard looks broken.

---

## 8. Top-10 UX principles (the §11 list, normalized)

In priority order:

1. **The 5-second rule governs the top fold.** A PSM opening the console must answer "what needs my attention?" in 5 seconds, no scrolling/filtering/hovering. [Few + NN/g]
2. **Status uses ≥2 redundant channels.** Color + icon (+ text when space allows). Never color-only. [WCAG 1.4.1; Carbon; Astro UXDS]
3. **Default to neutral; escalate by exception.** Tiles at rest are quiet, not green. Color reserved for "needs attention" and "critical." [Few + alarm-fatigue lit]
4. **Calibrate thresholds for ≤5% false-positive rate on `critical`.** Above ~5%, the team trains itself to ignore the highest severity. [PLOS One; Nature npj DM]
5. **Side-panel is the default drill pattern; modal for blocking only; route for shareable destinations.** Predictable across the app. [Pencil & Paper; NN/g; UXPin]
6. **Borrow IBCS semantic notation, skip IBCS reporting structure.** Adopt actual/plan/forecast/prior fills + variance colors as house style; don't try to be IBCS-compliant. [IBCS v1.2]
7. **Always show data freshness.** "Updated 2 min ago" + Live/Stale/Paused indicator + manual refresh button on every primary tile. [Smashing 2025]
8. **URL is the source of truth for view state.** Filters, sort, drill, time-range in the query string. Back button must work. Sharing a view = sharing a URL. [LogRocket; TanStack]
9. **Empty states diagnose, then prescribe.** Each empty tile explains *why* and offers the *one* action that fills it. Distinguish first-run / filter-emptied / healthy-empty. [Eleken; Setproduct; Carbon]
10. **Store UTC, display local — always labeled.** Wall-clock times carry a zone label. Multi-region tiles show both site-local and viewer-local. [enterprise practice + Smart Interface Design Patterns]

---

## 9. Anti-patterns (explicit avoid list)

1. **Gauges, dials, speedometers, traffic-light tiles** — Few's foundational critique [Few]
2. **3D pie charts, 3D bars, drop shadows, gradients on data marks** — chartjunk [Tufte, Few]
3. **Color-only status** — fails 8% of users by default; fails the whole team after alarm fatigue [WCAG 1.4.1]
4. **A sea of green tiles** — habituates the eye to ignore color; one turning red is *less* visible than from neutral
5. **No staleness indicator** — frozen dashboard that looks live is worse than no dashboard [Smashing 2025]
6. **Auto-refresh that re-paints while user is reading** — always offer pause/snapshot [Smashing 2025]
7. **Drill via modal for multi-step workflows** — modals are for atomic confirmations [Design Studio; NN/g]
8. **Filter state in client memory only** — refresh must not lose filters; Slack-link must reproduce the view [LogRocket]
9. **Wall-clock times without timezone labels** — ambiguous in any multi-region context
10. **Empty state = "No data"** — replace with diagnostic + CTA [Eleken; Setproduct]
11. **Sparklines without an endpoint value or label** — decorative noise [Tufte]
12. **Mobile-responsive everything** — make alert/detail responsive (people read those on phones), don't waste effort on portfolio-table responsiveness [Tableau Mobile BI]
13. **A dashboard that doubles as a report** — if it's a snapshot for scheduled review, it's a report. Keep the console scoped to monitoring [Few + Knaflic]
14. **IBCS overcompliance** — all 98 rules applied rigidly becomes a discipline tax [derived]

---

## 10. Sparklines + small multiples (Tufte + Few)

When sparklines help in an ops console:

- A portfolio table where each row needs both a current value (KPI) *and* a 30-day trajectory.
- "Status over last 7 days" per project — one row per project, one sparkline showing on-track/at-risk/off-track transitions.
- Anywhere the question is "is this getting better or worse?"

### Design checklist

- **Always show the current value as a number adjacent to the sparkline.** Sparkline is context for the number, not a replacement.
- **Endpoint dot** for current value; second dot color for extrema if relevant.
- **Consistent y-scale within a column** — different scales across rows of a "same metric" column is an IBCS Check violation.
- **Hover for full chart, click for drill.** Sparkline is the preview, not the artifact.

When sparklines add noise: tiles already encoding current status via color/icon; series too short to show shape (<~7 points); variance dominated by noise; mixed-axis columns (one dollars, next percent).

---

## Sources

Full ledger (79 URLs across 14 clusters): `/tmp/research-dashboard-ux.md` §Sources ledger.

Key anchors:
- Stephen Few — *Information Dashboard Design* + *Common Pitfalls in Dashboard Design*
- Edward Tufte — *Sparkline theory and practice*; *Beautiful Evidence*
- NN/g — *Dashboards: preattentive*; *5-Second Usability Test*; *Progressive Disclosure*
- IBCS v1.2 (Creative Commons; ISO/AWI 24896 in progress)
- WCAG 2.2 SC 1.4.1 — Use of Color
- Carbon Design System — Status Indicator + Empty States patterns
- PLOS One Drew et al. 2014 — alarm fatigue baseline
- Smashing Magazine — *UX Strategies for Real-Time Dashboards* (Sep 2025)
- LogRocket — *Query strings are underrated*
- Smart Interface Design Patterns — *Designing A Time Zone Selection UX*
