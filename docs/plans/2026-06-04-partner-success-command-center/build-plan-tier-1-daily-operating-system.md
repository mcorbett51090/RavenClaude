# Build plan for Codex — Partner Success Command Center, Tier 1 (Daily Operating System)

**Audience:** a fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace with RavenClaude installed. Codex is the engineer; this file is the engineer's brief. **Self-contained — do not ask Matt to clarify what's already in here.**

**Scope:** Tier 1 of [`plan.md`](./plan.md) — the four widgets that turn the existing `bi-report/report.html` into the wife's **daily operating system**. Renders against the Tier 0 synthetic fixture; updates seamlessly when Tier 0.5 swaps in real data. **Zero new connectors. Zero drill-downs. Zero new agent. Zero schema bump.** Tiers 2-4 ship those.

**Companion doc:** the strategic plan [`plan.md`](./plan.md) §"Tier 1 — Daily Operating System". The Tier 0 brief [`build-plan-for-codex.md`](./build-plan-for-codex.md) is the data contract you read against.

---

## 0. What Tier 1 ships (and what it doesn't)

### Ships (the four widgets, top-of-page, above the existing Portfolio Report)

| # | Widget | Source data | Renders |
|---|---|---|---|
| **W1** | **Portfolio Summary** card | `partners[]` counts | Total / Active / Top 15 / In renewal window / At risk / Open escalations / Need outreach this week |
| **W2** | **Portfolio Health Snapshot** card | `partners[]` averages + counts | Avg health · avg sentiment · avg engagement · count declining usage · count no touchpoint 90+ days |
| **W3** | **Daily Action Center** table | `partners[]` sorted by `priority_score` desc | partner_name · priority_score · reason · recommended_action · due_date · **per-signal contribution % rendered INLINE per row** (Rule 4) |
| **W4** | **Calendar / Upcoming Touchpoints** list | `partners[].next_touchpoints[]` (cadence_projection per type) | Countdowns per partner per type with **R5 tooltip** ("derived from contract.end + cadence policy; not a calendar invite") |

### Dependencies (read these from disk — they must already exist)

- The Tier 0 data spine must be on disk: `plugins/edtech-partner-success/bi-report/data.json` MUST be a strict superset of the existing fixture's keys AND carry the Tier 0 v3 additions (the 25-partner spine, `priority_weights{}`, `priority_breakdown{}` per partner, `next_touchpoints[]` with at least one `cadence_projection` per partner per type ∈ `{checkin, qbr, renewal_meeting}`, `lifecycle_phase` × `lifecycle_substage`, `top15` object, `open_escalations`, `open_tickets`, `last_touchpoint_at`, `engagement_score`, `sentiment_score`).
- The Tier 0 schema is on disk: `plugins/edtech-partner-success/bi-report/data.schema.json` (read-only here — Tier 1 does NOT modify it).
- The Tier 0 priority-score rubric is on disk: `plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md` (Tier 1 reads the 9 signal formulas + default weights from here).
- The K-12 cadence file is on disk: `plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md` (Tier 1 reads the cadence rules for the calendar widget).
- The play catalog is on disk: `plugins/edtech-partner-success/knowledge/partner-health-decline-which-play.md` (Tier 1 reads the reason → recommended_action lookup from here).
- The Tier 0 integrity gate is on disk: `scripts/check-psm-data-integrity.py` (Tier 1 does NOT modify it).

**If any of the above is missing, STOP.** Re-read [`build-plan-for-codex.md`](./build-plan-for-codex.md), confirm Tier 0 was merged, and only then proceed. **Tier 1 has no business advancing against an absent Tier 0.**

### Out of scope (explicitly deferred)

- **No real connectors.** Tier 0.5 owns Salesforce / Planhat / Snowflake / Support / Contracts / Calendar. Tier 1 ships against the synthetic fixture; the real-data swap is invisible to Tier 1.
- **No drill-downs / Partner 360 / Timeline / Lifecycle / Renewal Command Center.** Tier 2 owns those.
- **No segment lenses** (Top 15, Health, Sentiment, Family Engagement, School-Level, Support). Tier 3 owns those.
- **No business-motion lenses** (Success Plan, Expansion, PD Tracker, Contract Center, Relationship Mapping). Tier 4 owns those.
- **No AI features.** Spec drew the boundary; Tier 5 / never.
- **No JS framework.** Vanilla JS + inline SVG only (matches the existing `bi-report` pattern). No React, no Vue, no Tremor, no D3, no CDN.
- **No `data.json` shape changes.** Every Tier 1 number derives from fields Tier 0 already shipped. If a needed field doesn't exist, you misread Tier 0 — re-read first.
- **No real Calendar sync.** R5 governs: countdowns are derived from `contract.end + cadence`, never real invites.

---

## 1. Pre-flight

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is latest main |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-1-daily-operating-system` | switched |
| 3 | Read this brief in full | (open the file) | every section |
| 4 | Read the strategic plan §Tier 1 | `cat docs/plans/2026-06-04-partner-success-command-center/plan.md` | §"Tier 1 — Daily Operating System" |
| 5 | Read Tier 0 v3 brief in full | `cat docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md` | every section |
| 6 | Confirm the Tier 0 data spine on disk | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 |
| 7 | Confirm the Tier 0 integrity gate is clean | `python3 scripts/check-psm-data-integrity.py` | exit 0 |
| 8 | Read the verbatim spec (Home, Daily Action, Calendar, Health Snapshot) | `cat docs/research/2026-06-04-partner-success-dashboard-requirements/spec.md` | §Home Dashboard, §Daily Action Center, §Calendar View, §Portfolio Health Snapshot |
| 9 | Read the dashboard canon | `cat plugins/edtech-partner-success/knowledge/psm-dashboard-canon-2026.md` | §1-§5 |
| 10 | Read the daily-action-queue SKILL | `cat plugins/edtech-partner-success/skills/daily-action-queue/SKILL.md` | §1-§4 |
| 11 | Read the operational-console-design best-practice | `cat plugins/ravenclaude-core/best-practices/operational-console-design.md` | §1-§10 |
| 12 | Read the Tier 0 rubric | `cat plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md` | full file |
| 13 | Read the cadence file | `cat plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md` | §2 (dead zones) + §3 (per-partner defaults) |
| 14 | Read the existing generator | `cat scripts/generate-bi-report.py` | full file — Tier 1 EXTENDS it; does NOT rewrite |
| 15 | Read the existing rendered report | `cat plugins/edtech-partner-success/report.html \| head -80` | confirm the file is auto-generated (the foot says so) — **never hand-edit** |
| 16 | Read the Mímir render gate (the template Tier 1's render gate mirrors) | `cat scripts/check-mimir-render.mjs` | full file |

**Priors that constrain design (no re-authoring):**

- `plugins/edtech-partner-success/CLAUDE.md` — house rules 3 (decay), 4 (cite the signal), 12 (provenance on every claim).
- `plugins/edtech-partner-success/knowledge/partner-health-decline-which-play.md` — reason → recommended_action mapping. **Read at render time** (Tier 1 does NOT hardcode it; per Risk R9).
- `plugins/edtech-partner-success/knowledge/psm-dashboard-canon-2026.md` §2 (5-section flow) + §5 (Stephen Few / IBCS / NOC rules).
- `plugins/ravenclaude-core/best-practices/operational-console-design.md` — the 5-second test, color discipline, empty states, sparklines.

---

## 2. The deliverable — exactly these 8 files

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `scripts/generate-bi-report.py` | **EDIT** | Render four new top sections (W1-W4) into `report.html` from the extended `data.json`. Additive — every existing Portfolio Report path stays. |
| 2 | `plugins/edtech-partner-success/report.html` | **EDIT (auto-regenerated)** | The output of (1). **NEVER hand-edit.** Re-run the generator. |
| 3 | `plugins/edtech-partner-success/knowledge/dashboard-tier-1-rendering-contract.md` | **CREATE** | The shape of the four widgets + the per-signal contribution-percent derivation + the R5 tooltip text + the honest-empty-state contract. The single source of truth Tier 2-4 read against. |
| 4 | `scripts/check-bi-report-render.mjs` | **CREATE** | Node behavioral render gate mirroring `check-mimir-render.mjs`. Extracts the real W1-W4 render functions from the regenerated `report.html` and drives them against 4 fixtures (populated / empty / honest-empty-fields / drift). |
| 5 | `scripts/audit-gates.sh` | **EDIT (append)** | Wire **Gate 53** with the must-fail half (Gate 51 is the unified-dashboard shell router; Gate 52 is the Tier 0 PSM data-integrity gate). |
| 6 | `plugins/edtech-partner-success/.claude-plugin/plugin.json` | **EDIT** | Bump `version` (minor — user-visible feature; `0.10.0` → `0.11.0`). |
| 7 | `.claude-plugin/marketplace.json` | **EDIT** | Mirror the version bump on the `edtech-partner-success` entry (CI gates the lockstep). |
| 8 | `plugins/edtech-partner-success/CLAUDE.md` | **EDIT (append)** | 5-line milestone entry under §Layout / milestones — the "Tier 1 daily operating system shipped" marker. Plain prose. No emoji. |

**Nothing else.** No new skills, no new agents, no new templates, no schema changes, no `bi-report/data.json` edits.

---

## 3. Per-widget specs

The wife's success criterion (spec §"Success Criteria"): **open the dashboard → know in ≤15 seconds who needs attention today, why, what to do, when the next required touchpoint is, and what the portfolio's health looks like.**

The four widgets render in this exact top-to-bottom order, above the existing Portfolio Report. The layout test (operational-console-design §1) governs: the top fold answers "what needs my attention?" without scrolling, filtering, or hovering.

### W1 — Portfolio Summary card

**Spec source:** spec.md §"Home Dashboard / Portfolio Summary".

**Counts (each derived deterministically from `partners[]`):**

| Count | Derivation |
|---|---|
| **Total partners** | `len(partners)` |
| **Active partners** | `len([p for p in partners if p.lifecycle_phase != 'renewal' or (p.lifecycle_substage in ['strategic_planning','success_and_growth'])])` — i.e. partners not in a churned state. Tier 0 has no `churned` substate, so this equals Total in v0; future Tier 0.5 may add one. Render as a separate line anyway (honest empty contract — never hide a count because it equals another). |
| **Top 15 partners** | `len([p for p in partners if p.top15 and p.top15.is_member])` |
| **In renewal window** | `len([p for p in partners if 0 <= (p.renewal_date - as_of).days <= 180])` — anyone with a renewal in the next 180 days. Spec calls this out generically; the 180-day clock matches the K-12 renewal motion in `renewal-pricing-conversations-edtech.md`. |
| **At-risk partners** | `len([p for p in partners if p.band == 'red'])` — the existing band classification (green 70+ / yellow 50-69 / red <50, from `bands{}`). |
| **Open escalations** | `sum(p.open_escalations for p in partners)` — total count of escalations across the book (NOT count of partners with escalations; spec is ambiguous, surface the count interpretation that makes the wife's morning useful). Tooltip names which interpretation per Rule 12. |
| **Need outreach this week** | `len([p for p in partners if p.last_touchpoint_at is None or (as_of - p.last_touchpoint_at).days >= 7])` — anyone the wife hasn't touched in 7+ calendar days. Suppress during dead zones for the *affected* partner per the cadence file (the count is still emitted; the per-row reason is annotated `suppressed: dead zone`). |

**Rendering:**

- A single card with 7 KPI tiles inside (existing KPI tile pattern from `bi-report` generator — `.kpi` class). Each tile is `{label, value, delta(optional), info-tooltip}`.
- The `info` tooltip per tile names the source query + last refresh (Rule 12 — every number names its source). Source for Tier 1 is always `partners[]` + `as_of`; the tooltip says so verbatim.
- Color discipline: counts are neutral text (the existing `.kpi .v` style). The **At-risk** tile uses the danger color **PLUS the warning icon class** (≥2 channels per WCAG 1.4.1; never color-only).

### W2 — Portfolio Health Snapshot card

**Spec source:** spec.md §"Portfolio Health Snapshot".

**Averages and counts:**

| Metric | Derivation |
|---|---|
| **Average health score** | `round(mean(p.score for p in partners), 1)` — the existing top-level `score` field. |
| **Average sentiment score** | `round(mean(p.sentiment_score for p in partners), 1)` — Tier 0 v3 added `sentiment_score`. |
| **Average engagement score** | `round(mean(p.engagement_score for p in partners), 1)` — Tier 0 v3 added `engagement_score`. **field-classifications.json marks this `synthetic_only`** — render an honest "computed from synthetic data — see field-classifications.json" tooltip on this tile (Rule 12 + the honest-empty-state contract from operational-console-design §7). |
| **Accounts with declining usage** | `len([p for p in partners if p.usage_trend_30d_pct < 0])` — Tier 0 v3 added the signed percent. |
| **Accounts with no touchpoint 90+ days** | `len([p for p in partners if p.last_touchpoint_at is None or (as_of - p.last_touchpoint_at).days >= 90])` — does NOT subtract dead zones (the wife wants the raw count for portfolio hygiene; per-row dead-zone suppression is W3's job). |

**Rendering:**

- A second card next to W1 (use the existing `.grid2` layout), 5 KPI tiles inside.
- Each average tile carries a hover tooltip naming the formula AND the source field AND the last refresh (`as_of` from `data.json`). Rule 12.
- The **declining usage** and **no touchpoint 90+** tiles use the warning icon class (≥2 channels) when their count is > 0.
- Color discipline: averages are neutral text; if `avg_health < 50` the tile carries the warning icon (NOT color-only) — habituated-green-tile failure mode is avoided per operational-console-design §2.

### W3 — Daily Action Center

**Spec source:** spec.md §"Daily Action Center" + §"Dashboard Priority Ranking Logic" + the `daily-action-queue/SKILL.md` rationale-string anatomy.

**Construction:**

1. **Sort `partners[]` by `priority_score` descending.** (Tier 0 v3 emits `priority_score` per partner; Tier 0 v3 derives `priority_breakdown{}` per partner with the 9 signal values.)
2. **Take the top N where N = min(15, len(partners)).** Wife's "Top 15" framing matches the Top 15 segment; the table caps at 15 rows so the 5-second test holds.
3. **Per row, render exactly five columns** (spec is explicit; no extras): `partner_name | priority_score | reason | recommended_action | due_date`.
4. **`reason` is a deterministic enum derived from the signal that drove the score.** Logic: pick the signal `k` that maximizes `weights[k] * breakdown[k]` (i.e. the largest contribution). Map to the reason enum:

   | Dominant signal | Reason enum |
   |---|---|
   | `renewal_timing` | `renewal_approaching` |
   | `health_decline` | `health_score_decline` |
   | `sentiment_decline` | `sentiment_decline` |
   | `days_overdue_vs_cadence` | `no_recent_touchpoint` |
   | `open_escalations` | `open_escalation` |
   | `ticket_volume` | `support_ticket_aging` |
   | `arr_percentile` | `high_arr_attention` |
   | `top15_bonus` | `top15_attention` |
   | `usage_decline` | `usage_decline` |

   The spec's example list ("Renewal approaching", "Health score decline", "Usage decline", "No recent touchpoint", "Open escalation", "Support ticket aging", "Success plan overdue") matches this enum 1-to-1 except `success_plan_overdue` which Tier 1 does NOT compute (the success-plan signal lives in Tier 4); skip it cleanly.

5. **`recommended_action` reads from `partner-health-decline-which-play.md` AT RENDER TIME.** The generator parses the play catalog markdown for a reason → play lookup table; the lookup is keyed on the reason enum from (4). **Do NOT hardcode the mapping inside the generator** — per Risk R9 (the catalog evolves; the dashboard must read it live). If the lookup misses, render `"see playbook"` and surface the unmapped reason on stderr so the rubric can be tightened.

6. **`due_date` is computed deterministically per reason:**

   | Reason | due_date formula |
   |---|---|
   | `renewal_approaching` | `min(p.renewal_date - 14 days, today + 3 days)` — give the renewal motion lead time; never less than 3 days out. |
   | `health_score_decline` | `today + 3 days` |
   | `sentiment_decline` | `today + 2 days` |
   | `no_recent_touchpoint` | `today + 1 day` |
   | `open_escalation` | `today` |
   | `support_ticket_aging` | `today + 1 day` |
   | `high_arr_attention` / `top15_attention` | `today + 5 days` |
   | `usage_decline` | `today + 3 days` |

7. **Per-signal contribution percent rendered INLINE per row (Rule 4 — by construction, not discipline).** Below the row's reason cell, render a single line:

   > `Drivers: renewal_timing 48% · health_decline 22% · open_escalations 18% · top15_bonus 12%`

   The contribution percent is the renderer derivation (NEVER stored — `field-classifications.json` marks `priority_breakdown` `derived_at_render` for Tier 1's purposes):

   ```
   contribution[k]% = (weights[k] * breakdown[k]) / sum(weights[j] * breakdown[j] for j) * 100
   ```

   Round to integer percent. Show only signals contributing ≥10%, sorted desc. If exactly one signal dominates (≥80%), show only that one. Honest empty: if `priority_score == 0` show `"No drivers above threshold"` — never a blank line.

8. **Honest empty state.** If `len(partners) == 0`, render the panel with an honest diagnostic-headline + supporting-copy + CTA per operational-console-design §7 — `"No partners in the book yet. Drop a real export at plugins/edtech-partner-success/bi-report/data.json and re-run the generator."` — NOT a blank table.

**Column color discipline:**

- `priority_score` cell uses the existing `.scorebadge` style with `BAND_VAR[band_of(score, bands)]` — same color scale as the Portfolio Report below. **+ status icon class** for ≥2 channels.
- Every row carries an `aria-label` summarizing the reason for screen readers.
- The reason cell is text-only (NEVER color-only).

### W4 — Calendar / Upcoming Touchpoints

**Spec source:** spec.md §"Calendar View" — the **Upcoming tasks view** sub-view, NOT Monthly/Weekly (those are deferred to Tier 2+; spec calls them out but Tier 1's job is the countdown list).

**Construction:**

1. **Iterate `partners[]` and project `next_touchpoints[]` per partner.** Tier 0 v3 guarantees AT LEAST ONE `cadence_projection` entry per partner per type ∈ `{checkin, qbr, renewal_meeting}`. (Tier 0 integrity check #15 enforces this — if it ever drifts, the wife sees an empty calendar list for the affected partner, which the render gate catches.)
2. **Sort the projected entries by `due_at` ascending across the whole portfolio.** First-due first.
3. **Render as a flat list (not a calendar grid — that's Tier 2):**

   ```
   15 days until next check-in — Brightpath Charter (cadence_projection)
   30 days until QBR — Quokka Valley Schools (cadence_projection)
   45 days until QBR — Harbor District (cadence_projection)
   90 days until renewal planning — Pinecrest ISD (cadence_projection)
   120 days until renewal outreach — Wendelhart Public Schools (cadence_projection)
   ```

   Format the countdown phrase per the spec's literal examples: "15 days until next check-in" / "45 days until QBR" / "90 days until renewal planning" / "120 days until renewal outreach". Map by `type`:

   | type | phrase template |
   |---|---|
   | `checkin` | `{n} days until next check-in` |
   | `qbr` | `{n} days until QBR` |
   | `renewal_meeting` | `{n} days until renewal {planning,outreach}` — `planning` if 60 ≤ n ≤ 120, `outreach` if 120 < n ≤ 180, `prep` if n < 60. Spec lists both `planning` and `outreach` as examples — use the n-band. |

4. **The R5 tooltip is MANDATORY per entry.** Every row carries a hover-tooltip with the verbatim text:

   > "derived from contract.end + cadence policy; not a calendar invite"

   Render via `title="..."` on each row. **The render gate asserts every row has this tooltip; a row missing it is a hard fail** (Risk R5 — the calendar countdowns look authoritative; the tooltip is what keeps the wife from trusting them as real invites).

5. **Cap the list at 25 entries.** Past 25 the wife is scrolling, which violates the 5-second test. Tier 2 ships the full calendar grid + filters; Tier 1 surfaces "what's nearest."

6. **Honest empty state.** If a partner has no `next_touchpoints[]` (should not happen because Tier 0 enforces coverage, but defend anyway), the partner is skipped silently and the per-partner count is emitted on stderr by the generator. If the whole portfolio has none, render `"No upcoming touchpoints projected. Verify the cadence rules in data.json."` per the §7 empty-state contract.

7. **Dead-zone suppression annotation.** If a touchpoint's `due_at` falls inside a dead zone from `k12-psm-operating-cadence.md` §2 (universal dead zones — Tier 1 does NOT load state-keyed windows from `dashboard-dead-zones.md`; that's a Tier 2 enrichment), append `· dead zone — defer 1 week` to the row. The countdown stays accurate; the suggestion is advisory.

---

## 4. UX discipline — apply `operational-console-design.md`

Tier 1 is the wife's **operational console**, not a report. Every choice below is enforced by the render gate where mechanically possible; the rest is discipline the build commits to.

### 4.1 The 5-second test (operational-console-design §1)

The wife opening the dashboard must answer **"which partners need attention today?"** in ≤ 5 seconds (1-2 fixations = ~400-600 ms for the headline number; ≤ 15 fixations = ~5 seconds for the structural impression). The four widgets achieve this because:

- W1's **At-risk** count is one of the seven KPI tiles in the top-left card.
- W3's first row IS the highest-priority account; the wife reads "name + reason + recommended_action" in one fixation.
- W4's first row IS the most-imminent touchpoint.

**Acceptance criterion** (the wife's verification): opening `report.html`, time-to-answer for "who needs attention today" is ≤ 15 seconds without scrolling, filtering, or hovering. Document this in the milestone entry (§7 — the milestone references the 5-second-test outcome).

### 4.2 Color discipline (operational-console-design §2 + WCAG 1.4.1)

**Required:**

- Bands: green ≥ 70 / yellow 50-69 / red < 50, read from `data.json` `bands{}` (do NOT hardcode the cutoffs — Tier 0 ships them).
- **Status uses ≥ 2 channels: color + icon class + (where space allows) text label.** Never color-only. The render gate asserts the at-risk tile carries the warning icon class.
- Defaults to neutral (the existing `.kpi` style); escalates by exception. A sea-of-green tile pattern is the alarm-fatigue failure mode (§2.5 + the ICU literature) — quiet tiles at rest, color reserved for "needs attention."
- **CVD floor:** every status indicator that uses color also uses the existing `var(--rc-ok-fg)` / `var(--rc-warn-fg)` / `var(--rc-danger-fg)` foreground + icon class so red/green confusion (~8% of men) doesn't silently break the morning routine.

### 4.3 Provenance tooltips (operational-console-design §6 + plugin CLAUDE.md Rule 12)

**Every number renders with a hover tooltip naming:**

1. The source field path (`partners[].open_escalations`, `partners[].sentiment_score`, …).
2. The derivation in one phrase (`sum across portfolio`, `mean across portfolio`, …).
3. The last refresh timestamp (the top-level `as_of` from `data.json`).

The tooltip text is constructed once by a helper (`_provenance_tooltip(field, derivation, as_of)`) and reused — DRY. The render gate asserts presence on every KPI tile.

### 4.4 Per-signal contribution rendered inline (Rule 4 — by construction)

W3 §7 above governs. The render gate asserts every Daily Action Center row carries either (a) a `Drivers: ...` line OR (b) the honest `"No drivers above threshold"` line. **A row with neither is a hard fail** — that's the Rule 4 regression mode.

### 4.5 Honest empty states (operational-console-design §7)

| Surface | Empty case | Honest text |
|---|---|---|
| W1 At-risk = 0 | The portfolio is healthy | `"0 — all partners above the at-risk band"` (celebratory per §7, NOT a dash) |
| W2 Avg engagement (synthetic-only field) | Always present | Tooltip names the synthetic-only marker per `field-classifications.json` |
| W3 No partners | Pre-import state | Diagnostic-headline + CTA per §7 |
| W4 No projected touchpoints | Drift from Tier 0 | `"No upcoming touchpoints projected. Verify the cadence rules in data.json."` |
| W3 `priority_score == 0` row | Edge case | `"No drivers above threshold"` (never a blank line) |

**The "in-process-only fields" discipline:** every field marked `synthetic_only` OR `derived_at_render` in `field-classifications.json` renders with an explainer tooltip naming WHY (synthetic vs computed at render time). This is the Tier 1 equivalent of the Mímir tab's in-process pill — render gate must assert the explainer exists or it silently degrades to a dash.

### 4.6 Layout (operational-console-design §1)

Top-to-bottom order on `report.html`, above the existing Portfolio Report:

```
┌─────────────────────────────────────────────────────────────┐
│ Existing report header (title, subtitle, refreshed, owner)  │
├──────────────────────────────┬──────────────────────────────┤
│ W1 Portfolio Summary card    │ W2 Portfolio Health Snapshot │
├──────────────────────────────┴──────────────────────────────┤
│ W3 Daily Action Center table (top 15 by priority_score)     │
├─────────────────────────────────────────────────────────────┤
│ W4 Upcoming Touchpoints list (≤25 entries)                  │
├─────────────────────────────────────────────────────────────┤
│ <existing Portfolio Report — UNCHANGED below this line>     │
└─────────────────────────────────────────────────────────────┘
```

Reuse the existing `.grid2` for W1+W2, `.panel` for W3+W4. Do NOT introduce a new layout primitive.

---

## 5. Render gate — mirroring Heimdall / Norns / Mímir

The render gate is `scripts/check-bi-report-render.mjs` — pure-text-based assertions over the regenerated `report.html`'s script bodies. Extracts the real W1-W4 render helpers (`renderPortfolioSummary`, `renderHealthSnapshot`, `renderDailyActionCenter`, `renderUpcomingTouchpoints` + shared helpers `provenanceTooltip`, `driversLine`, `cadenceTooltip`) from the generated HTML via the same brace-balanced extraction pattern Mímir uses.

### Four fixtures (per the Mímir / Heimdall / Norns convention)

1. **POPULATED** — a 25-partner spine matching the Tier 0 fixture distribution (14 green / 7 yellow / 4 red, 7 in renewal buckets, 8 Top 15, ≥1 partner with `last_touchpoint_at = today`). Every widget renders every field; the contribution-percent line is present per row; the R5 tooltip is on every calendar row; the provenance tooltip is on every KPI tile.
2. **EMPTY** — `partners: []`. Every widget renders its honest-empty-state per §4.5; no thrown errors; no dashes where the in-process explainer should appear.
3. **HONEST-EMPTY-FIELDS** — every partner has `engagement_score: null` AND `usage_trend_30d_pct: null` (the Tier 0.5 production-data swap where the synthetic-only fields aren't available). The widgets render the `field-classifications.json` explainer tooltip per affected tile; NEVER a dash without explanation; never a thrown error.
4. **DRIFT** — a fixture identical to POPULATED except every partner's `next_touchpoints[]` is empty. The W4 widget renders the honest `"No upcoming touchpoints projected..."` empty state (proving the Tier 0 integrity-check-#15 coverage assumption is verified at the render layer too).

### Must-fail half (bidirectional — required for Gate 53 to have teeth)

The must-fail half drifts `report.html` so the **R5 tooltip is silently stripped from W4 rows.** The render gate's "every calendar row carries the R5 tooltip" assertion MUST fire — otherwise the gate is audit theater.

The drift patch (Python `re.sub` on `report.html`):

```python
import re, sys
src = open("plugins/edtech-partner-success/report.html", "r", encoding="utf-8").read()
# Strip the R5 tooltip from cadenceTooltip(): rewrite the body to return "".
patched = re.sub(
    r"function cadenceTooltip\(\) \{[\s\S]*?return [\s\S]*?;\s*\}",
    'function cadenceTooltip() { return ""; }',
    src,
    count=1,
)
sys.stdout.write(patched)
```

Running the render gate against the patched fixture MUST exit nonzero. If it exits 0, the gate is broken — fix the gate, not the drift.

### Also assert (per the Mímir / Heimdall parity discipline)

- The render gate confirms the four render helpers exist in `report.html` by header name.
- The render gate confirms the generator (`scripts/generate-bi-report.py`) carries a function for each widget (a string-grep is sufficient — the helpers run server-side in Python, but the render gate is JS-driven on the rendered HTML, so the parity check is a separate string-grep on the Python source).
- The render gate prints `BI-report render: ALL ASSERTIONS PASS` on success; `BI-report render: N assertion(s) FAILED` with the count on failure.

---

## 6. Verification + PR shape

### 6.1 Verification commands

| # | Command | Expected |
|---|---|---|
| 1 | `python3 scripts/generate-bi-report.py --plugin edtech-partner-success` | exit 0; "[ok] wrote plugins/edtech-partner-success/report.html (... KB, 25 partners)" |
| 2 | `python3 scripts/generate-bi-report.py --check` | exit 0 (the regenerated report.html matches what's committed) |
| 3 | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 |
| 4 | `python3 scripts/check-psm-data-integrity.py` | exit 0 (Tier 0 gate still clean — Tier 1 didn't drift it) |
| 5 | `node scripts/check-bi-report-render.mjs` | exit 0; "BI-report render: ALL ASSERTIONS PASS" |
| 6 | `npx prettier --write . && npx prettier --check .` | exit 0 |
| 7 | `bash scripts/audit-gates.sh` | exit 0 (Gate 53 passes both halves) |
| 8 | Layout snippet | "Layout OK" |
| 9 | `python3 -m json.tool plugins/edtech-partner-success/.claude-plugin/plugin.json > /dev/null` | exit 0 |
| 10 | `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null` | exit 0 |
| 11 | `grep -E '"version": "0.11.0"' plugins/edtech-partner-success/.claude-plugin/plugin.json` | matches |
| 12 | Visual: open `report.html` in a browser, time the 5-second test | ≤ 15 seconds to identify the top-priority partner + reason + recommended action |

### 6.2 Layout snippet

```sh
python3 - <<'PY'
import fnmatch, json, subprocess
allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
new = subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=A", "main"],
    capture_output=True, text=True,
).stdout.splitlines()
violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
print("VIOLATIONS:" if violations else "Layout OK")
for v in violations: print(" ", v)
PY
```

### 6.3 PR shape

```sh
git add scripts/generate-bi-report.py \
        plugins/edtech-partner-success/report.html \
        plugins/edtech-partner-success/knowledge/dashboard-tier-1-rendering-contract.md \
        scripts/check-bi-report-render.mjs \
        scripts/audit-gates.sh \
        plugins/edtech-partner-success/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json \
        plugins/edtech-partner-success/CLAUDE.md

git commit -m "$(cat <<'EOF'
feat(edtech-partner-success): PSM dashboard Tier 1 — daily operating system (4 widgets + Gate 53)

Renders Portfolio Summary + Portfolio Health Snapshot + Daily Action Center +
Upcoming Touchpoints from the Tier 0 fixture. Per-signal contribution percent
inline per Rule 4. R5 cadence_projection tooltip on every calendar row.
WCAG 1.4.1 secondary-channel discipline. Gate 53 render gate with must-fail.
EOF
)"

git push -u origin feat/psm-dashboard-tier-1-daily-operating-system
```

**Open as draft PR with `draft: true`.** Draft until Matt confirms the 5-second test against real eyes.

### 6.4 PR body shape

Include in the PR body:

- **A screenshot of `report.html`** (the top-fold — W1+W2+W3-first-3-rows+W4-first-3-rows). The 5-second-test eye-track is what the wife actually evaluates.
- **The render gate output paste.** Copy the `node scripts/check-bi-report-render.mjs` console output verbatim into a fenced code block in the PR body. Reviewers see the assertion list at a glance.
- **The Tier 0 integrity-check paste.** `python3 scripts/check-psm-data-integrity.py` output, proving Tier 1 didn't drift the data spine.
- **A "Migration" section.** If a consumer runs `/plugin marketplace update` after this PR, what changes? Answer: the rendered `report.html` adds four sections above their existing Portfolio Report. The existing Portfolio Report is byte-identical. The `data.json` shape is unchanged. No consumer breaks.

---

## 7. Wall-handling — Tier 1 should NOT hit Q1-Q6

The strategic plan §"Settling steps for the open spec questions" lists six questions (Q1: support tool / Q2: contract system / Q3: calendar tool / Q4: Top 15 list source / Q5: PSM team scope / Q6: sentiment source). **Tier 1 does NOT touch any of these surfaces** — the calendar widget reads derived `cadence_projection` (Q3 deferred); sentiment is read from `partners[].sentiment_score` which Tier 0 already shipped (Q6 deferred); Top 15 reads from `partners[].top15.is_member` which Tier 0 already shipped (Q4 deferred). If you find yourself reaching for one of Q1-Q6, **stop** — you're outside Tier 1's scope; re-read §0.

If a true wall hits:

1. Re-read priors per §1 step 6-15. Most "walls" are unread priors.
2. **Apply the capability-claim discipline from `ravenclaude-core/CLAUDE.md` §"Claim Grounding & Source Honesty":** before declaring blocked, name the specific mechanical cause (command output, file:line, exit code). Don't infer "can't" from one route's failure.
3. If silent and no documented default, `AskUserQuestion` per the tribunal routing rules — but Tier 1 SHOULD NOT hit this path. If you're asking, it's evidence the brief missed something; document it inline.
4. **Never falsely concede on a correction.** If Matt says "Tier 1 needs widget X" and X is outside §0's list, push back once with the brief's scope citation before adopting. Verify before yielding.

---

## 8. What Codex MUST NOT do

(About 20 hard nos. The render gate enforces what it can; this section catches the rest at brief time.)

1. **Never hand-edit `plugins/edtech-partner-success/report.html` directly.** It is generated by `scripts/generate-bi-report.py`. Re-run the generator. The freshness gate (Gate 46) WILL catch a hand-edit.
2. **Never edit Tier 0 artifacts** — `data.json`, `data.schema.json`, `data.export.schema.json`, `field-classifications.json`, `synthesize.py`, `check-psm-data-integrity.py`. Tier 1 is RENDER-ONLY. If you find yourself reaching for one, you're misreading the contract.
3. **Never bump `schema_version`.** Tier 0.5+ owns schema evolution. Tier 1 reads the existing schema.
4. **Never introduce a JS framework** — no React, Vue, Svelte, Tremor, D3, ECharts. Vanilla JS + inline SVG only. Matches the existing `bi-report` pattern.
5. **Never introduce a CDN.** Everything ships inline. The report opens by double-clicking the file.
6. **Never add filters / drill-down / Partner 360 in Tier 1.** Tier 2 owns those.
7. **Never use color-only status indicators.** WCAG 1.4.1 floor — color + icon class (+ text where space allows). The render gate asserts the at-risk tile carries the warning icon class.
8. **Never skip the R5 cadence_projection tooltip.** Every W4 row carries the verbatim `"derived from contract.end + cadence policy; not a calendar invite"` tooltip. The render gate's must-fail half exists precisely for this.
9. **Never hardcode the reason → recommended_action mapping inside the generator.** Read `partner-health-decline-which-play.md` at render time. Risk R9 is the precedent.
10. **Never store `priority_breakdown` contribution percents in `data.json`.** They are `derived_at_render` per `field-classifications.json`. Compute in the renderer; never persist.
11. **Never introduce a per-student field, anywhere.** FERPA floor — Tier 0 v3's `check-psm-data-integrity.py` will catch you; don't try.
12. **Never use a real US district name from Tier 0's denylist.** The Tier 0 fixture is the only fixture you write against; the render gate's fixtures are synthetic identifiers prefixed `Demo:` per Tier 0 discipline.
13. **Never write to `bi-report/data.json`.** Tier 0 owns it; Tier 1 renders against it. If the schema is wrong, Tier 0 ships a fix; not Tier 1.
14. **Never use `print(json.dumps(failing_row))` debug paths** in the generator. The FERPA-scrub discipline from Tier 0 §Step 5 applies here too — no row content reaches stderr/stdout.
15. **Never cache the rendered report across runs.** Each `--check` invocation regenerates and byte-compares. Don't introduce an intermediate cache.
16. **Never force-push, amend, or rewrite history.** The branch-archive skill is the sanctioned escape hatch for any branch lifecycle issue.
17. **Never mark PR ready-for-review without Matt's say-so.** Open as draft.
18. **Never re-author the four "do not re-author" priors** (the play catalog, the cadence file, the rubric file, the dashboard canon). Read them; cite them; do not modify them.
19. **Never introduce a third-party Python dependency** to `generate-bi-report.py`. Stdlib only — matches the Tier 0 `synthesize.py` discipline.
20. **Never use module-level `random` / non-deterministic output** in the generator. Every render is reproducible from the same `data.json` byte-for-byte.
21. **Never bump `marketplace.json` `metadata.version`** in this PR. That's the marketplace-level version (currently `0.44.0` per top-level metadata); only the per-plugin `version` field on the `edtech-partner-success` entry bumps.
22. **Never add Tier 2+ work to this PR.** The Tier 2 PR (Partner 360 + Timeline + Lifecycle + Renewal Command Center) is the next branch, after Tier 1 merges. Scope creep here delays both.
23. **Never add the spec's "Monthly view" or "Weekly view" calendar grid.** Tier 1 ships ONLY the "Upcoming tasks view" sub-view per §3 W4. Tier 2 ships the grid.
24. **Never compute `engagement_score` or `usage_trend_30d_pct` in the renderer.** They are `synthetic_only` Tier 0 fields. If they're absent in a Tier 0.5 export, the honest-empty contract fires; the renderer does NOT fabricate them.
25. **Never compute the priority score in the renderer.** Tier 0 emits it; Tier 1 renders it. The contribution-percent inline is the ONLY math the renderer does on the rubric.

---

## 9. Acceptance — Definition of Done

Tier 1 is done when:

- [ ] Four widgets render against the Tier 0 synthetic fixture, in the layout of §4.6.
- [ ] Render gate (Gate 53) passes both halves clean.
- [ ] Tier 0 integrity gate (Gate 52) still clean — Tier 1 did not drift the data spine.
- [ ] Prettier clean on the whole tree.
- [ ] Layout snippet returns "Layout OK".
- [ ] Per-signal contribution renders inline on every Daily Action Center row (Rule 4 by construction).
- [ ] R5 tooltip renders on every Upcoming Touchpoint row (verified by the render gate's must-fail half).
- [ ] Cross-section consistency holds: a 90-day-renewal partner appears in BOTH the W1 "In renewal window" count AND the W3 top-5 (manual check on the synthetic fixture).
- [ ] WCAG 1.4.1 secondary-channel discipline: the at-risk tile + the high-priority score badges carry icon classes alongside color.
- [ ] Honest empty states render per §4.5 for the four cases.
- [ ] Plugin version bumped to `0.11.0` in BOTH plugin.json AND marketplace.json (mirror).
- [ ] CLAUDE.md milestone entry appended.
- [ ] PR opened as draft with 5-second-test screenshot + render-gate paste + integrity-check paste + Migration note.
- [ ] Wife (or Matt as proxy) confirms the 5-second test in ≤ 15 seconds.

When the wife says "yes, this is what I open every morning" — Tier 1 is done. Until then, it's draft.

End of Tier 1 brief.
