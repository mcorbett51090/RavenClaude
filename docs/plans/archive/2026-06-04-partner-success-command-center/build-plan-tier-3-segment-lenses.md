# Build plan for Codex — Partner Success Command Center, Tier 3 (segment lenses)

**Audience:** a fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace with RavenClaude installed. Codex is the engineer; this file is the engineer's brief. **Self-contained — do not ask Matt to clarify what's already in here.**

**Scope:** Tier 3 of [`plan.md`](./plan.md) — the **6 segment-lens pages** that re-slice the same `data.json` partners[] under different filters. Each lens REUSES Tier 2's `openPartner360(account_uid)` drill-down; no new drill-downs. Each lens is a dedicated route page mounted in the same `dashboard.html` shell.

**Pre-build gate:** Tier 2 ([`build-plan-tier-2-drill-downs.md`](./build-plan-tier-2-drill-downs.md)) merged. The canonical `openPartner360`, `resolveSourceRef`, and `tenant-config.json` plumbing are present. Cross-section consistency gate (Gate 53) passes.

**Pattern-replication tier.** This brief is shorter than Tiers 0/1/2 because the 6 lenses share a common structure: a top KPI strip + a filter chip row + a sortable per-partner table + (where relevant) one secondary chart. The work is *replication of one well-defined pattern across 6 audience-specific filters*, not 6 different patterns.

---

## 0. Dependencies

- **Tier 0** ([`build-plan-for-codex.md`](./build-plan-for-codex.md)) — schema + fixture. Frozen. No additions.
- **Tier 1** — Portfolio Summary, Health Snapshot, Action Center, Calendar. **Not edited here.**
- **Tier 2** — `openPartner360`, `resolveSourceRef`, `tenant-config.json`, lifecycle threshold CONST table, Renewal Command Center bucket logic. **Reused. Never re-authored.**
- **Knowledge files that constrain this tier** — re-read before writing code:
  - `plugins/edtech-partner-success/knowledge/psm-dashboard-canon-2026.md` §1 (table-stakes widgets) + §3 (Gainsight 8-dashboard catalog — Tier 3's lenses map onto archetypes 1, 2, 3, 5, 6) + §6 (K-12 overlay rules).
  - `plugins/edtech-partner-success/knowledge/k12-signal-taxonomy.md` (referenced by §6 of the canon) — family-engagement signal categories drive the Family Engagement Dashboard column choice.
  - `plugins/edtech-partner-success/knowledge/partner-health-score-drift.md` — the Health Dashboard "historical trend" view consumes the 6 health components per the existing `data.json` `components` block. Decay-discipline rule applies.
  - `plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md` §"Dead zones" — sentiment "no update in N days" alerts MUST suppress during dead zones.
  - `docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md` §3 (5-second rule), §4 (color discipline + alarm fatigue — "default to neutral, escalate by exception"), §6 (empty states — three categories: first-run / filter-emptied / truly-empty/healthy), §8 (URL state for shareable filters).

---

## 1. Pre-flight

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is latest main |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-3-segment-lenses` | switched |
| 3 | Verify Tier 2 surface present | `grep -q 'function openPartner360' plugins/edtech-partner-success/bi-report/dashboard.js` | match found |
| 4 | Verify Tier 0 fixture | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 |
| 5 | Verify Gate 53 (cross-section consistency from Tier 2) | `python3 scripts/check-psm-cross-section-consistency.py` | exit 0 |
| 6 | Read spec §"Top 15 Dashboard", "Health Dashboard", "Sentiment Dashboard", "Family Engagement Dashboard", "School Level Adoption View", "Support & Escalation Dashboard" | open file | all six |
| 7 | Read `psm-dashboard-canon-2026.md` §3 + §6 | open file | both |

---

## 2. Deliverables — exactly these files

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `plugins/edtech-partner-success/bi-report/dashboard.html` | EDIT | Add 6 new route mount-points (left-nav sidebar pattern). |
| 2 | `plugins/edtech-partner-success/bi-report/lenses/top15.js` | CREATE | Top 15 Dashboard renderer. |
| 3 | `plugins/edtech-partner-success/bi-report/lenses/health.js` | CREATE | Health Dashboard renderer. |
| 4 | `plugins/edtech-partner-success/bi-report/lenses/sentiment.js` | CREATE | Sentiment Dashboard renderer. |
| 5 | `plugins/edtech-partner-success/bi-report/lenses/family-engagement.js` | CREATE | Family Engagement Dashboard renderer. |
| 6 | `plugins/edtech-partner-success/bi-report/lenses/school-level.js` | CREATE | School Level Adoption View renderer. |
| 7 | `plugins/edtech-partner-success/bi-report/lenses/support-escalation.js` | CREATE | Support & Escalation Dashboard renderer. |
| 8 | `plugins/edtech-partner-success/bi-report/lenses/lens-shared.js` | CREATE | The common pattern: `renderLens({lensId, kpis[], filters[], table})`. Every lens calls into this. |
| 9 | `plugins/edtech-partner-success/bi-report/dashboard.css` | EDIT (append) | Lens layout, left-nav, KPI strip rules. |
| 10 | `scripts/generate-bi-report.py` | EDIT | Mount the 6 lens HTML scaffolds (server-side); JS hydrates client-side. |
| 11 | `scripts/check-psm-cross-section-consistency.py` | EDIT (extend) | Add cross-lens invariant assertions per §4 below. |
| 12 | `plugins/edtech-partner-success/.claude-plugin/plugin.json` | EDIT (version bump) | Semver minor. |
| 13 | `.claude-plugin/marketplace.json` | EDIT (version mirror) | Lockstep. |
| 14 | `plugins/edtech-partner-success/CLAUDE.md` | EDIT | 5-line Tier 3 milestone. |

**Nothing else.** No new schema, no new fixture data, no new drill-down.

---

## 3. The shared lens pattern (`lens-shared.js`)

Every Tier 3 lens calls into ONE rendering primitive. The lens-specific file (e.g. `top15.js`) selects the right partners, computes the right KPIs, and configures the right columns; `lens-shared.js` does the actual DOM rendering.

```javascript
// renderLens(config)
//   lensId: 'top15' | 'health' | 'sentiment' | 'family-engagement' | 'school-level' | 'support-escalation'
//   title: string — page header
//   kpis: [{label, value, format, sparkline?, deltaVsPriorPeriod?, tooltip}]
//   filters: [{id, label, type: 'multiselect'|'range'|'toggle', options, defaultValue}]
//   table: {
//     rows: [{account_uid, ...cells}],
//     columns: [{id, label, type, sortable, render(row): string|HTMLElement}],
//     defaultSort: {column, direction},
//     emptyState: {category: 'first-run'|'filter-emptied'|'truly-empty', headline, body, cta?},
//   },
//   secondary?: {type: 'bar'|'line'|'sparkline-grid', data, ...}  // optional second visual
function renderLens(config) { ... }
```

**Three contract properties of `renderLens` (load-bearing — Gate 54 asserts these):**

1. **Table row click → `openPartner360(row.account_uid)`** — single drill-down reused everywhere. The lens NEVER authors its own drill-down.
2. **Filter state → URL** — every filter persists to `?lens=<lensId>&<filterId>=<value>&sort=<col>:<dir>` per `dashboard-ux.md` §8. Pasting the URL into Slack reproduces the view exactly.
3. **Empty state → categorize** — if filters exclude every row, render `category: 'filter-emptied'` with a "Clear filters" CTA. If `data.json` has no matching partners at all (e.g. no top-15 designated), render `category: 'truly-empty'` with celebratory copy per `dashboard-ux.md` §6. If `data.json` is missing the source block (Tier 0.5 swap-in scenario where one connector failed), render `category: 'first-run'` with a "Source not configured" message.

**Color discipline (consumed from `dashboard-ux.md` §4 — non-negotiable):**

- Default tile state = neutral gray/blue at rest. Status color (red/yellow/green) appears ONLY when the tile is `attention` or `critical`.
- Status badges always = color + icon + text label (≥2 of 3 channels). Never color-alone — WCAG 1.4.1 Level A floor.
- Same meaning = same color across all 6 lenses (red is "at risk" everywhere; never "missing data" in one lens and "at risk" in another).

---

## 4. The 6 lens specifications

### 4.1 Top 15 Dashboard (`lenses/top15.js`)

**Spec §"Top 15 Dashboard"** — Community Top 15 partners only.

**Filter rule:** `partners[].top15.is_member === true`. (Per Tier 0 schema, `top15` is `{is_member, reason, owner, designated_at} | null`.)

**KPI strip (top 4 cards):**
- Top 15 partner count (= count of `top15.is_member`)
- ARR sum across Top 15
- Top 15 partners with health < 70 (count + color band)
- Top 15 partners with renewal in next 90 days

**Table columns per spec:**
- Partner name (click → `openPartner360`)
- Health score (with band color dot + sparkline of `spark[]` from existing `data.json`)
- Sentiment score (with band color dot)
- Renewal date (with countdown chip)
- Usage trend (`usage_trend_30d_pct` signed; up arrow if positive, down arrow if negative)
- Last touchpoint (relative time)
- Next touchpoint (from `next_touchpoints[]` earliest entry)
- Open risks (count of `is_escalation OR red-band-health OR red-band-sentiment`)
- Success plan status (from `success_plans[].status` aggregated — `on_track | at_risk | overdue` rolled up by worst-case)

**Color coding per spec:** "Green = Healthy, Yellow = Monitor, Red = Risk." Apply at the row level via a left-border color rule (per `dashboard-ux.md` §4 mitigation pattern #4 — colored border + neutral background + dark text).

**Default sort:** worst-health first (health_score ascending), so the partners who need attention land at the top.

### 4.2 Health Dashboard (`lenses/health.js`)

**Spec §"Health Dashboard"** — all partners, drillable into the 7 health input categories.

**KPI strip:**
- Average health score across portfolio (with sparkline of `portfolio_trend[]`)
- Green band count / Yellow band count / Red band count (3 separate KPI cards — color-coded per IBCS § U: same color = same meaning)
- Partners with health drop > 10 points in last 30 days (derived from `spark[]` first vs last value)

**Table columns per spec:**
- Partner name
- Current health score + band color
- Historical trend (sparkline of `spark[]`)
- 6 component scores (the existing `components{adoption, touchpoint, outcome, sentiment, champion, usage}` block from `data.json` — render as horizontal mini bars or stacked chips)
- Usage (from `partners[].components.usage`)
- Adoption (from `partners[].components.adoption`)
- Engagement (= `engagement_score`)
- Support activity (count of open `tickets[]` per partner)
- Escalations (= `open_escalations`)
- Renewal risk (red if `renewal_date - as_of <= 90 AND health_score < 70`; else yellow if < 70; else green)
- Product utilization (= `contracts[].pd_completed_sessions / pd_purchased_sessions` for current contract; render as percentage)

**Secondary visual:** distribution donut showing green/yellow/red counts (per the canon's §1 "Health Distribution" widget pattern).

**Filter chips:** band (multi-select), segment (multi-select), state (multi-select).

**Cite the knowledge file** in a help-icon tooltip on the page header: "Health scoring rules: `knowledge/partner-health-score-drift.md` — components decay per the half-life rules in §3."

### 4.3 Sentiment Dashboard (`lenses/sentiment.js`)

**Spec §"Sentiment Dashboard"** — focus on sentiment scoring + reasons + action plans.

**KPI strip:**
- Average sentiment score
- Green / Yellow / Red band counts (3 cards)
- Partners with sentiment drop in last 30 days (count, derived from `timeline_events[]` of type `sentiment_change` filtered to last 30 days where `payload.new_score < payload.prior_score`)

**Table columns per spec:**
- Partner name
- Current sentiment (band dot + numeric)
- Last sentiment update (`ts` of latest `sentiment_change` event)
- Sentiment trend (sparkline derived from sentiment_change events)
- Reason for score (= latest `sentiment_change` event's `payload.reason`)
- Notes (= latest `sentiment_change` event's `payload.notes`, truncated)
- Action plan (= latest `sentiment_change` event's `payload.action_plan`)

**Dead-zone suppression rule (consumed from `k12-psm-operating-cadence.md`):**

A partner with `last sentiment_change > N days ago` should NORMALLY get a "sentiment stale" warning chip. **But suppress that chip if the partner's `state` has an active dead zone per `dashboard-dead-zones.md`.** A district in winter break is expected to have stale sentiment; flagging them yellow is alarm fatigue per `dashboard-ux.md` §4. Tooltip on the suppressed-chip slot: "in dead zone (e.g., winter break); not flagged stale."

**Filter chips:** band, segment, "stale > N days" (toggle).

### 4.4 Family Engagement Dashboard (`lenses/family-engagement.js`)

**Spec §"Family Engagement Dashboard"** — pulls from `usage_daily[]` (district-level) family-engagement fields.

**KPI strip:**
- Total families invited (sum of latest `usage_daily.family_invited` per partner)
- Total families activated (sum of latest `usage_daily.family_activated`)
- Activation percentage (= activated / invited)
- Families reached (= active family-engagement users; derived field — render `—` if not present in Tier 0 fixture; that's an empty-state condition handled in `renderLens`)

**Table columns per spec:**
- Partner name
- Families invited
- Families activated
- Activation %
- Languages translated (count distinct from a derived field; render `—` in Tier 0 — the field isn't in the Tier 0 schema; flag as "Tier 0.5 connector dependency")
- Read rate (derived from messaging metrics; same — Tier 0.5 dependency)
- Response rate (same)
- Two-way conversation rate (same)

**Secondary visual:** Current-year vs previous-year side-by-side bar (small multiple). Current-quarter vs previous-quarter alongside.

**Filter chips:** segment, state.

**Per `dashboard-ux.md` §6 empty-state discipline:** if Tier 0.5 connectors haven't been wired (typical for Tier 3 ship time), the "Languages / Read rate / Response rate / Two-way" columns render as `—` with a footer note "Data from Tier 0.5 Snowflake connector — see `plugins/data-platform/scripts/export-partner-success-data.py`."

### 4.5 School Level Adoption View (`lenses/school-level.js`)

**Spec §"School Level Adoption View"** — only for multi-school districts.

**Filter rule:** partners where `usage_daily_school[]` has entries (i.e. multi-school per Tier 0 fixture's 8-of-25 partners).

**KPI strip:**
- Multi-school district count
- Total schools across portfolio (sum of distinct `school_uid` per partner)
- Schools with usage_level = "low" (count)
- Schools with no activity in last 14 days (count)

**Table:** **two-tier** — collapsible district rows with expandable school detail underneath. Default: districts collapsed.

District-row columns: partner name, school count, district avg health, district usage trend.

Expanded school-row columns per spec:
- School name (with `Demo School:` prefix from Tier 0 fixture, render-stripped per `tenant_config.strip_demo_prefix` rule from Tier 2)
- Usage level (from `usage_daily_school[].usage_level`)
- Health score (derived — punt to `—` in Tier 0; Tier 0.5 enrichment populates)
- Last activity date (= max `date` per school in `usage_daily_school[]`)
- Adoption trend (sparkline of `active_users` per school over time)

**Highlight per spec:** highest-performing schools (top-quartile of usage_level), lowest-performing (bottom-quartile), schools requiring intervention (usage_level = "low" AND no activity in last 14 days). Apply via row-level color border.

### 4.6 Support & Escalation Dashboard (`lenses/support-escalation.js`)

**Spec §"Support & Escalation Dashboard"** — pulls from `tickets[]`.

**KPI strip:**
- Open tickets (sum across portfolio)
- Open escalations (sum of `is_escalation = true AND status != closed`)
- Average ticket age (mean `age_days` of open tickets)
- Partners with > 3 open tickets (count)

**Table columns per spec:**
- Partner name
- Open tickets count
- Open escalations count
- Ticket aging (longest-open ticket's `age_days` per partner)
- Themes (top 2 `theme` values for this partner's open tickets, as chips)
- Resolution history (count of closed tickets in last 30 days)

**Highlight per spec:** accounts with multiple tickets (>= 3), high-risk escalations (`is_escalation = true AND severity = high`), unresolved (oldest age > 14 days).

**Secondary visual:** ticket-theme breakdown bar chart (count by `theme` enum across portfolio).

**Filter chips:** segment, severity, theme, status (open/closed toggle).

---

## 5. Cross-section invariants (Gate 53 extension)

`scripts/check-psm-cross-section-consistency.py` gets new assertions for the 6 lenses. **Same number on N pages renders identical bytes.**

| # | Invariant | How enforced |
|---|---|---|
| C7 | A Top-15 partner with declining health (band = red) appears in BOTH the Top 15 Dashboard AND the Health Dashboard's red-band partner list, with IDENTICAL `health_score`, `sentiment_score`, `arr`. | Script: enumerate `top15.is_member AND band == 'red'`; compare per-field values from both lenses' computed inputs. |
| C8 | The Sentiment Dashboard's "Green band count" KPI equals the Health Dashboard's "Sentiment component green" count for partners where the sentiment_score band derivation matches. | Same band-threshold table (Tier 1 `bands{}` block) used everywhere. Script asserts both lens KPI computations call the same `bandFor(score, bands)` function. |
| C9 | The Family Engagement Dashboard's "Total families activated" equals the sum of latest `usage_daily.family_activated` per partner — same number as would render on the Portfolio Health Snapshot (Tier 1) if that widget surfaced it. | Script computes from `data.json`, asserts byte-equality across both surfaces. |
| C10 | The Support & Escalation Dashboard's "Open escalations" KPI equals the Tier 1 Portfolio Summary "Partners with open escalations" KPI when both are computed against the same fixture. | Both pull from `partners[].open_escalations` — script asserts the same aggregation function is used. |
| C11 | The School Level Adoption View's "Schools requiring intervention" count for a given partner matches the Partner 360 panel's open-risks count for that same partner (when school-level risk is part of open risks). | Script asserts the intervention criteria are consistent across the two surfaces. |
| C12 | A partner appears in EXACTLY ONE row of each lens's main table (no duplicates). | Script asserts row-count == unique `account_uid` count per lens. |

**Cross-lens drill-down invariant (already enforced from Tier 2 via Gate 53 C4):** every row-click anywhere across the 6 lenses calls `openPartner360(account_uid)` — script greps for any local `panel`/`drawer`/`modal` function definitions inside `lenses/*.js`; finding one fails the gate.

---

## 6. Verification

| # | Command | Expected |
|---|---|---|
| 1 | `npx prettier --write . && npx prettier --check .` | exit 0 |
| 2 | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 |
| 3 | `python3 scripts/check-psm-data-integrity.py` | exit 0 |
| 4 | `python3 scripts/check-psm-cross-section-consistency.py` | exit 0 (C1–C12 all pass) |
| 5 | `grep -rE 'function (open\|render)Partner360' plugins/edtech-partner-success/bi-report/lenses/` | empty (no lens authors its own drill-down) |
| 6 | `grep -rE 'function .*(Panel\|Drawer\|Modal)' plugins/edtech-partner-success/bi-report/lenses/` | empty (no lens authors any drill-down primitive) |
| 7 | `bash scripts/audit-gates.sh` | clean |
| 8 | Open `dashboard.html?lens=top15` → Top 15 lens renders; click partner → drawer opens via `openPartner360`; URL updates to `?lens=top15&partner=<uuid>`; back button restores lens-only view. | All transitions work. |
| 9 | Open `dashboard.html?lens=health&band=red,yellow&sort=score:asc` → Health lens loads with filters applied. | Filter chips reflect URL state. |
| 10 | Open `dashboard.html?lens=family-engagement` with Tier 0 fixture (no connector data) → "Languages / Read rate / Response rate" columns render as `—` with footer note. | Empty-state copy correct per `dashboard-ux.md` §6. |
| 11 | Resize window to mobile width → lenses scroll horizontally but don't crash. (Desktop-first; mobile-acceptable.) | No console errors. |
| 12 | Visual diff: Tier 0/1/2 widgets unchanged. | Confirmed. |
| 13 | Layout snippet (Tier 0 brief §6) | "Layout OK" |

---

## 7. PR shape

```sh
git add plugins/edtech-partner-success/bi-report/dashboard.html \
        plugins/edtech-partner-success/bi-report/dashboard.css \
        plugins/edtech-partner-success/bi-report/lenses/top15.js \
        plugins/edtech-partner-success/bi-report/lenses/health.js \
        plugins/edtech-partner-success/bi-report/lenses/sentiment.js \
        plugins/edtech-partner-success/bi-report/lenses/family-engagement.js \
        plugins/edtech-partner-success/bi-report/lenses/school-level.js \
        plugins/edtech-partner-success/bi-report/lenses/support-escalation.js \
        plugins/edtech-partner-success/bi-report/lenses/lens-shared.js \
        scripts/generate-bi-report.py \
        scripts/check-psm-cross-section-consistency.py \
        plugins/edtech-partner-success/CLAUDE.md \
        plugins/edtech-partner-success/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json

git commit -m "feat(edtech-partner-success): PSM dashboard Tier 3 — 6 segment lenses reusing Tier 2 drill-down"
git push -u origin feat/psm-dashboard-tier-3-segment-lenses
```

Open as draft PR.

---

## 8. Wall-handling

1. Re-read priors in §1.
2. If a column or KPI mentioned in the spec isn't present in Tier 0's `data.json` (e.g. "Languages translated" on Family Engagement), render `—` + footer note "Data from Tier 0.5 connector — not in synthetic fixture." Do NOT extend `data.schema.json` to add it. Tier 0.5 ships the real connector + populates the field.
3. If silent AND no documented default, `AskUserQuestion`.

---

## 9. What Codex MUST NOT do

- Add new fields to `data.schema.json` or `data.json`. Tier 0's schema is frozen.
- Author a per-lens drill-down. Every lens reuses `openPartner360(account_uid)`. Architectural invariant C4.
- Author per-lens filter URL conventions. The URL pattern `?lens=<id>&<filter>=<value>&sort=<col>:<dir>` is shared via `lens-shared.js`.
- Introduce React / Vue / any framework. Vanilla JS.
- Use a band color for any meaning other than "Green = Healthy, Yellow = Monitor, Red = Risk." Same color = same meaning across all 6 lenses (IBCS §U; canon §1).
- Render red KPI cards by default. Default = neutral; escalate by exception per `dashboard-ux.md` §4 (alarm fatigue).
- Skip the empty-state categorization (first-run / filter-emptied / truly-empty). Each is a different copy + CTA per `dashboard-ux.md` §6.
- Fire a "sentiment stale" or "no touchpoint" warning chip when the partner's state is in an active dead zone. Suppression per `k12-psm-operating-cadence.md`.
- Render a lens with NO filter chip row. Every lens has at minimum a segment filter chip.
- Re-implement the lifecycle-badge color logic or the renewal-bucket assignment. Both come from Tier 2.
- Add per-entity `console.log` debug paths. PII vector.
- Skip the Demo: / Demo School: prefix stripping rule. Render-time stripping only, gated on `tenant_config.strip_demo_prefix`.
- Open the PR as ready-for-review without Matt's say-so.
- Force-push, amend, or rewrite history.
- Author a 7th lens. Six lenses, no more. Tier 4 covers motion lenses (5 different ones).
- Change Tier 1 or Tier 2 surfaces. Additive only.
- Add a CLAUDE.md milestone entry longer than 5 lines.
- Skip Gate 53 invariants C7–C12. They are load-bearing — they prove the dashboard doesn't lie by rendering the same number differently in different lenses.

End of Tier 3 brief.
