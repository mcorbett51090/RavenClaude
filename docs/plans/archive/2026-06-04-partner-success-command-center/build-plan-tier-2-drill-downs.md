# Build plan for Codex — Partner Success Command Center, Tier 2 (drill-downs)

**Audience:** a fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace with RavenClaude installed. Codex is the engineer; this file is the engineer's brief. **Self-contained — do not ask Matt to clarify what's already in here.**

**Scope:** Tier 2 of [`plan.md`](./plan.md) — the **single canonical drill-down implementation** (Partner 360 panel) consumed by Tiers 1, 3, and 4; plus the four widgets the spec calls out for this tier: Account Timeline, Lifecycle Tracking, Renewal Command Center. **One drill-down, used everywhere.** Tiers 3 and 4 MUST reuse this implementation rather than re-author it.

**Pre-build gate:** Tier 1 ([`build-plan-tier-1-daily-os.md`](./build-plan-tier-1-daily-operating-system.md)) merged. The four Tier 1 widgets render against `data.json`. This tier hangs drill-downs off those widgets without changing them.

---

## 0. Dependencies

- **Tier 0** ([`build-plan-for-codex.md`](./build-plan-for-codex.md)) — schema, fixture, integrity script. **Frozen.** No additions to `data.schema.json` in this PR.
- **Tier 1** — `dashboard.html` skeleton + `scripts/generate-bi-report.py` renders Portfolio Summary, Health Snapshot, Daily Action Center, Calendar.
- **Knowledge files that constrain this tier** — re-read before writing code:
  - `plugins/edtech-partner-success/knowledge/k12-renewal-motion-90-60-30.md` — the 180/120/90/60/30 bucket model. **This is the source of truth for the Renewal Command Center 5-bucket layout.** The spec at §"Renewal Command Center" enumerates the buckets verbatim; the knowledge file supplies the per-bucket *meaning* (180-day = internal posture, 90-day = decisive EBR, 60-day = RM-owned, etc.).
  - `plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md` — the cadence-policy thresholds the Lifecycle Tracking badge consumes (e.g. "MOI > 90 days without substage progression → yellow").
  - `plugins/edtech-partner-success/knowledge/psm-dashboard-canon-2026.md` §1 (Account 360 archetype) + §5 (Stephen Few single-screen + 5-second rule). The drill-down is a **side panel**, not a modal, per `dashboard-ux.md` §5 ("side panel is the default for show-me-more-about-this-row; preserves spatial map; default modern pattern, NN/g + Pencil & Paper").
  - `docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md` §8 (URL state for shareable drill-down) + §5 (drill-down pattern selection rules).
- **Substrate (do NOT re-author):**
  - `bridge_account_xref` shape — owned by `plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md`. Read for the source_ref-resolution contract; do not edit.
  - `partners[].lifecycle_phase × lifecycle_substage` allowed-pair table — frozen in Tier 0.
  - `data.json` `timeline_events[]` schema (event types, source enum, source_ref opaque-URI scheme) — frozen in Tier 0.

---

## 1. Pre-flight

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is latest main |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-2-drill-downs` | switched |
| 3 | Verify Tier 0 fixture present | `test -f plugins/edtech-partner-success/bi-report/data.json && python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 |
| 4 | Verify Tier 1 renderer present | `grep -q 'renderDailyActionCenter\|render_action_center' plugins/edtech-partner-success/bi-report/dashboard.html scripts/generate-bi-report.py 2>/dev/null` | match found |
| 5 | Re-read the strategic plan §"Tier 2" | open [`plan.md`](./plan.md) | full section |
| 6 | Re-read the spec §"Partner 360 View", "Account Timeline", "Lifecycle Tracking", "Renewal Command Center" | open `docs/research/2026-06-04-partner-success-dashboard-requirements/spec.md` | full sections |
| 7 | Re-read `k12-renewal-motion-90-60-30.md` (knowledge file) | open file | full file |
| 8 | Re-read `k12-psm-operating-cadence.md` (knowledge file) | open file | full file |
| 9 | Re-read `dashboard-ux.md` §5 + §8 | open file | both sections |

**No new `data.json` fields. No schema bump.** If you find yourself reaching for a new top-level field, stop — Tier 2 reads what Tier 0 froze.

---

## 2. Deliverables — exactly these files

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `plugins/edtech-partner-success/bi-report/dashboard.html` | EDIT | Mount drill-down panel container + 4 widget sections. |
| 2 | `plugins/edtech-partner-success/bi-report/dashboard.js` | EDIT (or CREATE if Tier 1 inlined) | The canonical drill-down implementation + 4 widget renderers. **Vanilla JS only.** No React, no Vue, no frameworks. |
| 3 | `plugins/edtech-partner-success/bi-report/dashboard.css` | EDIT (or CREATE) | Side-panel styling, lifecycle badge color rules, renewal bucket cards. |
| 4 | `plugins/edtech-partner-success/bi-report/source-ref-resolver.js` | CREATE | Pure function `resolveSourceRef(opaqueUri, tenantConfig, bridgeXref) → realUrl`. **Resolution happens at render time, never stored in JSON.** |
| 5 | `plugins/edtech-partner-success/bi-report/tenant-config.json` | CREATE | Tenant URL-template config — `{salesforce_base, planhat_base, support_base, calendar_base}`. Synthetic tenant for Tier 0 fixture. |
| 6 | `scripts/generate-bi-report.py` | EDIT | Inline the four new widget templates + the drill-down panel HTML scaffold (server-side template; JS hydrates client-side). |
| 7 | `scripts/check-psm-cross-section-consistency.py` | CREATE | New CI gate (Gate 53). Verifies a 90-day-renewal partner appears in BOTH the Renewal Window count AND the Renewal Command Center 90-day bucket with the same numbers. |
| 8 | `scripts/audit-gates.sh` | EDIT (append) | Wire Gate 53 with must-pass + must-fail. |
| 9 | `plugins/edtech-partner-success/knowledge/dashboard-drill-down-contract.md` | CREATE | The single-implementation contract that Tiers 3 and 4 read. |
| 10 | `plugins/edtech-partner-success/CLAUDE.md` | EDIT (milestone entry only) | 5-line Tier 2 milestone per the project rule. |
| 11 | `plugins/edtech-partner-success/.claude-plugin/plugin.json` | EDIT (version bump) | Semver minor bump. |
| 12 | `.claude-plugin/marketplace.json` | EDIT (version mirror) | Lockstep with plugin.json. |

**Nothing else.** No new agents. No new skills. No `data.schema.json` changes. No `report.html` changes (legacy file stays untouched; new work lives in `dashboard.html`).

---

## 3. Widget specifications

### 3.1 Partner 360 — the canonical drill-down

**Pattern choice:** **side panel (drawer)** sliding from the right, 480px wide, overlaying the right ~30% of viewport. Closes via X button, Esc key, or click-outside. Per `dashboard-ux.md` §5: "Side panel is the default for show-me-more-about-this-row; preserves user spatial map; can stay open as user moves between items."

**MUST be a single implementation.** Concretely: ONE function `openPartner360(account_uid)` exported from `dashboard.js`. Every list/table/card that displays a partner (Daily Action Center row, Renewal Command Center card, Top 15 row in Tier 3, Success Plan row in Tier 4, etc.) MUST call this function on row-click. Tiers 3 and 4 are FORBIDDEN from authoring their own drill-down.

**Panel content — three stacked sections (the canon's Account 360 archetype per `psm-dashboard-canon-2026.md` §1):**

1. **Account header** (always visible at top):
   - District name (from `partners[].name`)
   - Segment + State + ARR (formatted `$X,XXX,XXX`)
   - Owner PSM + Salesforce Account Owner
   - Renewal date + days-until countdown
   - Contract start/end + funding_source (rendered as human label, e.g. `title_iii` → "Title III")
   - **Provenance tooltip on every number** (per CLAUDE.md house rule 12 + Tier 1 discipline): hover shows `source_query + last_refresh_timestamp` from `as_of` + tenant config.

2. **Contacts grid** — table of `contacts[]` filtered to this `account_uid`. Columns: name (with `Demo:` prefix from Tier 0 fixture, **un-prefixed at render time only if `tenant_config.strip_demo_prefix=true`**) · title · role badge · influence_level · sentiment dot (green/yellow/red filled circle) · last_interaction_at (formatted, with relative-time tooltip "12 days ago"). Sort: role priority (champion → exec_sponsor → superintendent → tech_lead → family_engagement → stakeholder), then influence_level high→low.

3. **Open escalations** — `tickets[].is_escalation = true AND status != closed` for this account. If zero, render the celebratory empty state per `dashboard-ux.md` §6: "0 open escalations — last checked HH:MM" (NOT "—" or "N/A").

**Below the three Account-360 sections, the panel displays the three Tier 2 in-context views as a tabbed strip:** [Timeline] [Lifecycle] [Renewal]. Default tab: Timeline.

**URL state for shareable drill-down (per `dashboard-ux.md` §8):**
- Opening the panel pushes `?partner=<account_uid>&tab=<timeline|lifecycle|renewal>` to the URL via `history.pushState`.
- On page load, if `?partner=...` is present, auto-open the panel.
- Closing the panel pops the param via `history.pushState`.
- Back/forward buttons restore panel state correctly.
- The URL is shareable in Slack — a teammate pasting `dashboard.html?partner=<uuid>&tab=renewal` lands on the same view.

### 3.2 Account Timeline (drill-down tab #1)

**Source:** `timeline_events[]` filtered by `account_uid`, sorted by `ts` descending.

**Layout:** vertical chronological list. Each event renders as a row: `<source icon> <type badge> <ts (formatted local time)> <summary (truncated to 120 char, full on hover)> <"open in source" link>`.

**Source icons (per `timeline_events[].source` enum):**
- `salesforce` → SFDC cloud icon
- `planhat` → Planhat octahedron icon
- `support` → headset icon
- `snowflake` → snowflake icon
- `calendar` → calendar icon
- `manual` → pencil icon

Inline-SVG icons only (matches the existing `bi-report/report.html` pattern — no external icon-font dependencies).

**Filter controls** at the top of the tab:
- Source multi-select (checkboxes for the 6 source enum values)
- Type multi-select (checkboxes for the 13 type enum values)
- Date range (from / to date inputs; default = all)

Filter state lives in the URL: `?partner=<uuid>&tab=timeline&src=salesforce,planhat&type=renewal_conversation,qbr&from=2026-01-01`. Per `dashboard-ux.md` §8 ("URL state is the source of truth for shareable view state").

**The "open in source" link** resolves the `source_ref` opaque URI via `resolveSourceRef(...)` (§3.5). If resolution fails (tenant_config missing the relevant base URL, or `bridge_account_xref` row missing the SFDC ID), render the link as disabled with tooltip: "Source URL not configured for this tenant — see `tenant-config.json`."

### 3.3 Lifecycle Tracking (drill-down tab #2)

**Layout:** single-column status card.

- **Current phase badge** — large pill with phase name (`Deployment | BOI | MOI | Renewal`). Color: gray/neutral.
- **Current substage badge** — smaller pill below, colored per the days-in-stage policy below.
- **Date entered stage** — `stage_entered_at` formatted.
- **Days in stage** — `(as_of - stage_entered_at).days`.
- **Next milestone** — derived deterministically from the allowed-substage progression order per Tier 0's allowed table:
  - `deployment.needs_assessment` → next: `data_mapping`
  - `deployment.data_mapping` → next: `data_upload`
  - `deployment.data_upload` → next: `validation`
  - `deployment.validation` → next: `configuration`
  - `deployment.configuration` → next: `boi.training`
  - `boi.training` → next: `go_live`
  - `boi.go_live` → next: `adoption`
  - `boi.adoption` → next: `moi.data_review`
  - `moi.data_review` → next: `insights_and_analysis`
  - `moi.insights_and_analysis` → next: `renewal.strategic_planning`
  - `renewal.strategic_planning` → next: `success_and_growth`
  - `renewal.success_and_growth` → next: (next-year cycle; render "Next year-2 success plan kickoff")
- **Next required activity** — looks up `next_touchpoints[]` for this partner, picks the earliest `due_at`. If a `calendar_event` covers it, link to the event; otherwise render `"derived from cadence projection — not a calendar invite"` per Tier 1 tooltip discipline (R5 of the strategic plan).

**Substage badge color (days-in-stage vs cadence policy):**

Per `k12-psm-operating-cadence.md` cadence rules + spec §"Lifecycle Tracking":

| Phase | Substage | Green threshold | Yellow threshold | Red threshold |
|---|---|---|---|---|
| deployment | * | ≤ 14 days | 15–30 days | > 30 days |
| boi | training | ≤ 21 days | 22–45 days | > 45 days |
| boi | go_live | ≤ 30 days | 31–60 days | > 60 days |
| boi | adoption | ≤ 60 days | 61–120 days | > 120 days |
| moi | * | ≤ 60 days | 61–90 days | > 90 days |
| renewal | strategic_planning | ≤ 30 days | 31–60 days | > 60 days |
| renewal | success_and_growth | ≤ 90 days | 91–180 days | > 180 days |

Thresholds live in a CONST table in `dashboard.js` (NOT hardcoded inline). Documented in `dashboard-drill-down-contract.md`. **MUST suppress red badge during dead zones** from `dashboard-dead-zones.md` (the Tier 0 file) — a partner in deployment.training that hit day 45 during winter break gets a yellow with tooltip "in dead zone (Dec 22 – Jan 5); not flagged red," NOT a red.

### 3.4 Renewal Command Center (drill-down tab #3 + also a top-level widget)

**Two surfaces, ONE data computation.** The same per-partner renewal-bucket calculation that powers the drill-down tab #3 also powers the standalone Renewal Command Center widget on the home dashboard.

**5-bucket layout** per spec §"Renewal Command Center" verbatim (180 / 120 / 90 / 60 / 30 days). Each bucket is a column / card group.

**Bucket assignment rule:** partner falls into bucket `B` if `(renewal_date - as_of).days <= B AND (renewal_date - as_of).days > next_smaller_bucket`. E.g. 95-day partner → 120-day bucket (between 90 and 120); 65-day partner → 90-day bucket (between 60 and 90); 25-day partner → 30-day bucket.

**Per-partner card content per spec:**
- Partner name (click → opens drill-down with `tab=renewal`)
- Renewal amount (= `arr`; deal-extension uplift NOT modeled here — that's Tier 4 Expansion)
- Health score (with band color dot)
- Sentiment (with band color dot)
- Renewal risk — derived: `red if health_score < 50 OR sentiment_score < 50; yellow if 50-69; green if ≥ 70`. (Same band thresholds as Tier 1 — no new bands.)
- Expansion opportunity — boolean derived from Tier 4 logic (PUNT: render "—" in Tier 2; Tier 4 fills this in when it ships)
- Renewal owner (= `owner_psm` in Tier 0; in Tier 4 Contract Center, this gets re-resolved to RM-of-record)
- Status — derived: `pending if (renewal_date - as_of).days > 0 AND no closed_won event in timeline_events; closed_won if event present; lost if event of type=closed_lost present`

**Per-bucket meaning labels** (consumed from `k12-renewal-motion-90-60-30.md` §3 — render as a small italic header above each column):
- **180 Days** — "Internal review; refresh champion map; YTD usage pull; expansion go/no-go"
- **120 Days** — "Year-end impact deck drafting; SETDA-aligned evidence"
- **90 Days** — "Decisive EBR / value-realization meeting with exec sponsor"
- **60 Days** — "Proposal delivered; procurement starts; RM owns from here"
- **30 Days** — "Commercial execution only; PSM in support mode"

Cite the knowledge file inline as a tooltip on each header: hover → "Source: `knowledge/k12-renewal-motion-90-60-30.md` §3 (Planhat 90/60/30 model extended to K-12 180/120/90/60/30)."

### 3.5 `source-ref-resolver.js` — opaque URI → real URL at render time

**Contract (the single function this file exports):**

```javascript
// resolveSourceRef
//   opaqueUri: e.g. "salesforce://Account/synthetic-account-001"
//   tenantConfig: loaded from tenant-config.json
//   bridgeXref: data.json bridge_account_xref[] (used when SFDC ID needs lookup)
//   account_uid: passed through for bridgeXref lookup
// Returns: { url: string|null, reason: string|null }
//   On success: { url: "https://yourorg.salesforce.com/Account/0011x00000abcde", reason: null }
//   On failure: { url: null, reason: "tenant config missing salesforce_base" | "bridge_xref has no SFDC ID for this account" | "scheme unknown" }
function resolveSourceRef(opaqueUri, tenantConfig, bridgeXref, account_uid) { ... }
```

**Resolution rules per scheme:**

| Scheme | Pattern | Resolved URL |
|---|---|---|
| `salesforce://Account/<sfid>` | direct | `${tenant.salesforce_base}/lightning/r/Account/${sfid}/view` |
| `salesforce://Opportunity/<sfid>` | direct | `${tenant.salesforce_base}/lightning/r/Opportunity/${sfid}/view` |
| `salesforce://Contact/<sfid>` | direct | `${tenant.salesforce_base}/lightning/r/Contact/${sfid}/view` |
| `planhat://company/<phid>` | direct | `${tenant.planhat_base}/profile/${phid}` |
| `support://ticket/<tid>` | direct | `${tenant.support_base}/agent/tickets/${tid}` |
| `calendar://event/<cid>` | direct | `${tenant.calendar_base}/event?eid=${cid}` |

**The `<sfid>` segment in synthetic data is `synthetic-account-001` etc.** When the resolver sees a `synthetic-` prefix and `tenantConfig.tier === 'synthetic'`, it returns `{ url: '#synthetic', reason: 'synthetic ID — no real URL in Tier 0 fixture' }` so the dashboard renders the link as disabled-with-tooltip, NOT broken.

**MUST NOT store resolved URLs in `data.json`.** Resolution happens at render time. The opaque URI in `data.json` is FERPA-safe (no leaking real org URLs into a committed fixture); the resolution against `tenant-config.json` happens entirely client-side.

### 3.6 `tenant-config.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "tenant_id": "synthetic-tier-0",
  "tier": "synthetic",
  "salesforce_base": "https://example-synthetic.my.salesforce.com",
  "planhat_base": "https://app.planhat.com",
  "support_base": "https://example-synthetic.zendesk.com",
  "calendar_base": "https://calendar.google.com",
  "strip_demo_prefix": false,
  "comment": "When Tier 0.5 swaps in real connectors, replace this file with the tenant-specific config. Never commit a real tenant's config to the repo — gitignore the production path."
}
```

Append `tenant-config.production.json` to `.gitignore` (NOT `tenant-config.json` itself — the synthetic file IS committed).

---

## 4. Cross-section consistency invariants

**The single most important property of Tier 2 + 3 + 4: the same number on N pages renders identical bytes.**

| # | Invariant | How enforced |
|---|---|---|
| C1 | A partner whose `renewal_date - as_of` is between 60 and 90 days appears in BOTH the Tier 1 Portfolio Summary "Partners in renewal window" count AND the Renewal Command Center 90-day bucket. | `scripts/check-psm-cross-section-consistency.py` enumerates partners-in-renewal-window from `partners[]`, computes the Renewal Command Center bucket assignment, asserts each renewal-window partner is in exactly one bucket. |
| C2 | A partner appears in EXACTLY ONE Renewal Command Center bucket (no double-counting). | Same script: assert each partner with `renewal_date - as_of <= 180` is in exactly one bucket via the §3.4 bucket-assignment rule. |
| C3 | The Daily Action Center top-5 (Tier 1) and the Renewal Command Center 30/60/90 buckets (Tier 2) reference the same partner ARR + health + sentiment values. | Script asserts: for every partner with `renewal_date - as_of <= 90`, the `arr`, `health_score`, `sentiment_score` rendered in both surfaces matches byte-for-byte. |
| C4 | The Partner 360 panel opened from ANY entry point (Action Center, Renewal Command Center, eventually Top 15 / Health / Sentiment / Family / School / Support / etc.) renders IDENTICAL content for the same `account_uid`. | Architectural — single `openPartner360(account_uid)` function. Script grep asserts only ONE definition of this function exists across `dashboard.js` and any future Tier 3/4 JS files. |
| C5 | Timeline filter state survives a back-button navigation. | Manual verification step in §5. |
| C6 | Lifecycle phase × substage badge color matches the threshold table for the partner's stage AND respects dead-zone suppression. | Unit assertion in `synthesize.py`-side fixture (one partner in winter-break dead zone with > red threshold days-in-stage; integrity script verifies the badge color rule via the renderer's CONST table). |

---

## 5. Verification

| # | Command | Expected |
|---|---|---|
| 1 | `npx prettier --write . && npx prettier --check .` | exit 0 |
| 2 | `python3 -m json.tool plugins/edtech-partner-success/bi-report/tenant-config.json` | exit 0 |
| 3 | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 (data.json unchanged — Tier 0 invariant) |
| 4 | `python3 scripts/check-psm-data-integrity.py` | exit 0 (Tier 0 gate still passes) |
| 5 | `python3 scripts/check-psm-cross-section-consistency.py` | exit 0 (all 6 invariants C1–C6 pass against the Tier 0 fixture) |
| 6 | `bash scripts/audit-gates.sh` | clean (Gate 53 must-pass + must-fail both succeed) |
| 7 | `grep -c 'function openPartner360' plugins/edtech-partner-success/bi-report/dashboard.js` | exactly `1` (single implementation invariant C4) |
| 8 | Open `plugins/edtech-partner-success/bi-report/dashboard.html` in a browser, click a Daily Action Center partner row → drawer slides in from right → URL updates to `?partner=<uuid>&tab=timeline` → switch to Lifecycle tab → URL updates → back button restores Timeline tab → Esc closes drawer → URL clears `?partner=`. | All transitions work; no console errors. |
| 9 | Open the same dashboard with `?partner=<uuid>&tab=renewal` in URL on cold load. | Drawer auto-opens on Renewal tab. |
| 10 | Click "open in source" on a timeline event whose `source_ref` resolves to a synthetic-prefix URL. | Link disabled with tooltip "synthetic ID — no real URL in Tier 0 fixture." |
| 11 | Visual diff against pre-PR dashboard.html: 4 new widgets render; Tier 1 widgets unchanged. | Confirmed. |
| 12 | Layout snippet (§7 of Tier 0 brief) | "Layout OK" |

---

## 6. PR shape

```sh
git add plugins/edtech-partner-success/bi-report/dashboard.html \
        plugins/edtech-partner-success/bi-report/dashboard.js \
        plugins/edtech-partner-success/bi-report/dashboard.css \
        plugins/edtech-partner-success/bi-report/source-ref-resolver.js \
        plugins/edtech-partner-success/bi-report/tenant-config.json \
        scripts/generate-bi-report.py \
        scripts/check-psm-cross-section-consistency.py \
        scripts/audit-gates.sh \
        plugins/edtech-partner-success/knowledge/dashboard-drill-down-contract.md \
        plugins/edtech-partner-success/CLAUDE.md \
        plugins/edtech-partner-success/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json \
        .gitignore

git commit -m "feat(edtech-partner-success): PSM dashboard Tier 2 — Partner 360 drill-down + Timeline + Lifecycle + Renewal Command Center"
git push -u origin feat/psm-dashboard-tier-2-drill-downs
```

Open as draft PR.

---

## 7. Wall-handling

1. Re-read priors in §1 + the four knowledge files in §0.
2. If a behavior is silent in this brief but documented in `dashboard-ux.md` or `k12-renewal-motion-90-60-30.md`, take that as the answer with an inline citation in the code comment.
3. If silent AND no default, `AskUserQuestion`. Tier 2 should NOT hit any of the strategic plan's Q1–Q6.
4. If the existing fixture lacks coverage to test an invariant (e.g. no partner is in the 30-day bucket), STOP and propose extending the Tier 0 fixture in a *separate* PR — do NOT change `data.json` or `synthesize.py` in this PR.

---

## 8. What Codex MUST NOT do

- Add new fields to `data.schema.json` or `data.json`. Tier 0's schema is frozen.
- Introduce React, Vue, Svelte, htmx, Alpine, Tailwind, or any client framework. Vanilla JS + inline SVG matches the existing `bi-report/report.html` pattern.
- Author a SECOND drill-down implementation. There is exactly one `openPartner360(account_uid)` function. Tiers 3 and 4 reuse it.
- Store resolved URLs (real Salesforce URLs, real Planhat URLs) in `data.json`. Opaque URIs stay opaque in the committed fixture.
- Commit a real-tenant `tenant-config.production.json`. That file is gitignored.
- Reuse the Tier 1 modal pattern (if Tier 1 used one) — Tier 2 drill-down is a side panel per `dashboard-ux.md` §5.
- Re-author bucket thresholds (renewal 180/120/90/60/30 or lifecycle days-in-stage). They come from `k12-renewal-motion-90-60-30.md` and `k12-psm-operating-cadence.md`. Single source of truth.
- Strip the `Demo:` prefix from contact names in the committed fixture. Render-time stripping only, gated on `tenant_config.strip_demo_prefix`.
- Render a red lifecycle badge during a dead-zone window. Suppression → yellow + tooltip.
- Hardcode tenant URLs (`yourorg.salesforce.com`, real Planhat instance) anywhere. They live in `tenant-config.json`.
- Add a `confidence_threshold_banner` for `bridge_account_xref` rows with `confidence < 0.9` — that's strategic-plan R3 territory but ships in Tier 0.5 alongside real connectors, not here.
- Modify the legacy `report.html`. New work lives in `dashboard.html`.
- Skip the cross-section consistency script (Gate 53). The invariants are load-bearing.
- Add a CLAUDE.md milestone entry longer than 5 lines per project rule.
- Open the PR as ready-for-review without Matt's say-so.
- Force-push, amend, or rewrite history.
- Introduce a Tier 3 or Tier 4 widget in this PR. Drill-down + the 4 named widgets only.
- Re-implement `bridge_account_xref` matching logic. That SKILL lives in `plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md`. This tier CONSUMES the xref table; it does not produce or revise it.
- Add per-entity `console.log` debug paths in `dashboard.js`. PII leak vector even with synthetic data.

End of Tier 2 brief.
