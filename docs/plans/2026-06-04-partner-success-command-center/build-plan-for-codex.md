# Build plan for Codex — Partner Success Command Center, Tier 0 (v2)

**Audience:** a fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace with RavenClaude installed. Codex is the engineer; this file is the engineer's brief. **Self-contained — do not ask Matt to clarify what's already in here.**

**Scope:** Tier 0 of [`plan.md`](./plan.md) — JSON schema + synthetic fixture + seeded generator + cross-entity integrity gate + two knowledge files. **Zero render changes, zero version bump, zero new agent, zero CLAUDE.md milestone.** Tier 1 ships those.

**Version note (v2 vs v1):** v1 of this brief had **17 P0 issues** found by a 4-panel cold review (security/FERPA, PSM-operational, data-engineering, architect). v2 is the rewrite that closes them. Highlights of what changed from v1 to v2 are inline in §"What v2 fixes" — do NOT search for v1; this file IS the spec.

---

## 0. What v2 fixes (so you know which v1 assumptions to drop)

- **Partner-shape collision:** v1 said "extend, never replace" but then redefined `partners[]` with `additionalProperties: false` AND a 4-key `health_components` that omitted the existing fixture's `champion` + `usage`. v2 merges (superset) — every existing key stays; the existing 6-key component taxonomy is preserved; new fields are **added alongside**.
- **Priority-score math:** v1's `priority_breakdown` was simultaneously "per-signal contribution percent summing to 100" AND "the score is the weighted sum" — unsatisfiable. v2: `priority_breakdown[k]` = raw 0–100 signal value; `priority_score` = `sum(weights[k] * breakdown[k]) / 100`; the "per-signal contribution percent" is **derived at render time**, never stored.
- **FERPA grep:** v1's grep had `\|` (literal pipe in ERE, not alternation) and `; echo "exit=$?"` (always exit 0 — no gate). v2 ships a hardened denylist as a real CI gate, exit-coded.
- **`account_uid` format:** v1 allowed UUID-or-SFDC-shape — unenforceable. v2: strict UUIDv4 only; real SFDC ID lives in `bridge_account_xref.salesforce_id`.
- **Prettier byte-equality clash:** v1 ran `prettier --write .` before `diff` against `synthesize.py` output → silent drift. v2 adds `plugins/edtech-partner-success/bi-report/data.json` to `.prettierignore` so `synthesize.py` is the canonical formatter.
- **Cross-entity integrity:** v1 only asserted at generation time. v2 ships `scripts/check-psm-data-integrity.py` and registers it as a CI gate so hand-edits are caught.
- **`priority_weights` sum-to-100:** v1 mandated it in prose; JSON Schema can't express sum constraints. v2 enforces in the integrity check script.
- **Schema versioning:** v1 had `$id` but no `schema_version`. v2 adds `schema_version: 1` as required.
- **Tier 0.5 drop-in contract:** v1's "transparently swaps to real data" had no test. v2 ships `data.export.schema.json` profile (looser; Tier 0.5 production-required minimum).
- **Lifecycle stage:** v1 collapsed the spec's 2-level (phase × 12 substates) into a 4-value flat enum. v2 splits into `lifecycle_phase` + `lifecycle_substage`.
- **Renewal-timing formula:** v1 linear (`max(0, 100 - days)`) mis-ranks. v2 uses the spec's bucket model (≤30→100, ≤60→85, ≤90→65, ≤120→40, ≤180→20, else 0).
- **`days_since_touchpoint` cadence-aware:** v1 ignored the cadence file. v2 uses `days_overdue_vs_cadence`, with `cadence_tier` on `partners[]` + dead-zone suppression.
- **ARR signal:** v1 hardcoded `arr / 5000`. v2 uses portfolio-percentile rank.
- **Top 15:** v1 was a bare bool. v2 is `top15: {is_member, reason, owner, designated_at} | null`.
- **PII leak via URL fields:** v1 left `doc_url` and `source_ref_url` as free-text URIs. v2 uses an opaque internal scheme (`salesforce://<account_uid>/event/<event_uid>`) until Tier 0.5, with a schema regex blocking `https://` querystrings.
- **`additionalProperties: false` discipline:** v2 makes it explicit on every nested object subschema, with the integrity script asserting closed-object structure across the whole compiled schema.
- **`org_uid` everywhere:** v2 carries `org_uid` on every entity record (not just top level), so multi-tenant doesn't require a backfill.
- **MUST-NOT list extended:** v2 adds the Codex traps the review panels surfaced.

---

## 1. Pre-flight (5 min)

Before touching files, Codex MUST do all of these. They take seconds and avoid the failure modes that ate the overnight 2026-06-04 session (file-state drift, draft CI quirks, layout misses, regen side effects).

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is the latest main commit |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-0-foundation` | switched |
| 3 | Read this brief in full | `cat docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md` | every section, not just headers |
| 4 | Read the strategic plan | `cat docs/plans/2026-06-04-partner-success-command-center/plan.md` | full file |
| 5 | Read the SME spec | `cat docs/research/2026-06-04-partner-success-dashboard-requirements/spec.md` | full file |
| 6 | Read the **existing** fixture | `cat plugins/edtech-partner-success/bi-report/data.json \| head -200` | identify EXISTING `partners[]` shape — v2 merges, never replaces (§2 below) |

**Read also (priors that constrain design — internalize before writing code):**

- `plugins/edtech-partner-success/CLAUDE.md` — house rules 1 (partner profile = SoT), 4 (cite the signal), 8 (rostering = silent killer), 12 (provenance on every claim).
- `plugins/edtech-partner-success/knowledge/partner-health-score-drift.md` — health-score decay model.
- `plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md` — cadence tiers + dead zones (load-bearing for the `days_overdue_vs_cadence` signal).
- `plugins/edtech-partner-success/knowledge/partner-health-decline-which-play.md` — recommended_action source.
- `plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md` — identity-spine pattern. Tier 0 references; doesn't re-author.

---

## 2. The existing fixture — what v2 inherits and MUST preserve

The existing `bi-report/data.json` has these top-level keys (read it to confirm):

- `report{}`, `_README`, `bands{}`, `components[]`, `kpis[]`, `cohort{}`, `trend_weeks[]`, `portfolio_trend[]`, `partners[]`.

**Existing `partners[]` shape (11 partners today):**

```
{name, segment, psm, score, delta, band,
 components{adoption, touchpoint, outcome, sentiment, champion, usage},
 spark[], flags[], play, last_touch, next_qbr, renewal}
```

**v2 superset rule:** every existing per-partner key STAYS. New Tier 0 fields are ADDED ALONGSIDE. `health_components` in v1 was a 4-key subset — **v2 drops `health_components` entirely** and uses the existing `components` block (already 6 keys). New name fields use new names, not name-collisions with old ones.

**Existing top-level blocks STAY.** v2 schema enumerates ALL of them as known top-level properties so the compiled `additionalProperties: false` doesn't reject the existing fixture.

---

## 3. The deliverable — exactly these files

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `plugins/edtech-partner-success/bi-report/data.schema.json` | **CREATE** | Authoritative JSON Schema. |
| 2 | `plugins/edtech-partner-success/bi-report/data.export.schema.json` | **CREATE** | Looser export profile for Tier 0.5 real-data drop-in (closes architect P0-4). |
| 3 | `plugins/edtech-partner-success/bi-report/data.json` | **EDIT** (superset, do not replace) | Extend with the new Tier 0 blocks. Every existing key stays. |
| 4 | `plugins/edtech-partner-success/bi-report/synthesize.py` | **CREATE** | Seeded generator; reproducible; FERPA self-check at end. |
| 5 | `scripts/check-psm-data-integrity.py` | **CREATE** | Cross-entity refs + sum-to-100 + FERPA + closed-object gate. |
| 6 | `plugins/edtech-partner-success/knowledge/dashboard-identity-spine.md` | **CREATE** | bridge_account_xref shape; references the SKILL. |
| 7 | `plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md` | **CREATE** | The rubric: signal formulas + weights + sum-to-100 invariant + Tier 0.5 export contract. |
| 8 | `plugins/edtech-partner-success/knowledge/dashboard-schema-evolution.md` | **CREATE** | `schema_version` evolution policy. |
| 9 | `.prettierignore` | **EDIT** (append) | Add `plugins/edtech-partner-success/bi-report/data.json` so synthesize.py is the canonical formatter (closes data-eng P0-4). |
| 10 | `scripts/audit-gates.sh` | **EDIT** (append) | Wire `check-psm-data-integrity.py` as a gate with a must-fail half. |
| 11 | `.repo-layout.json` | **VERIFY ONLY** | Both `bi-report/**` and `knowledge/**` already covered. Confirm via the snippet in §6. |

**Nothing else.** No `report.html`, no agent, no version bump, no CLAUDE.md milestone.

---

## 4. Step-by-step build order

### Step 1 — `data.schema.json` (the contract)

JSON Schema draft 2020-12.

**Top-level required fields** (this is the union of existing + new — failure to include the legacy keys = closed-schema rejection of the existing fixture):

```
schema_version, $id, report, _README, bands, components, kpis, cohort,
trend_weeks, portfolio_trend, org_uid, as_of, priority_weights,
partners, contacts, timeline_events, usage_daily, success_plans,
contracts, tickets, calendar_events, bridge_account_xref
```

Top-level `additionalProperties: false`. Every nested object schema (one level deep, two levels deep, …) ALSO carries `additionalProperties: false` — the integrity script (§Step 5) asserts this recursively.

**`$id`:** `"urn:ravenclaude:psm-dashboard-data"` (opaque URN — avoid the `https://ravenpower.net/...` v1 trap; no resolver expectation).

**`schema_version`:** integer, `const: 1`. Renderers refuse to render an unrecognized version. Evolution policy lives in `dashboard-schema-evolution.md` (§Step 8).

**`org_uid`:** strict UUIDv4 — `pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"`. Meaningful-string `org_uid` fails CI.

**`as_of`:** date-time (UTC). Note: every datetime field in the schema is UTC; date-only fields (`renewal_date`, `contract_start`, `contract_end`) are calendar dates with no time component but interpreted as 00:00 UTC for math.

**Per-entity schemas — REQUIRED fields:**

#### `partners[]` (superset of existing + new)

Existing keys (preserve exactly):
- `name` · `segment` · `psm` · `score` · `delta` · `band` · `components{adoption, touchpoint, outcome, sentiment, champion, usage}` · `spark[]` · `flags[]` · `play` · `last_touch` · `next_qbr` · `renewal`

New v2 keys:
- `account_uid` (strict UUIDv4)
- `org_uid` (UUIDv4 — every entity record carries it; closes security P1-4, data-eng P1-4)
- `state` (US-state 2-char enum: `["AL","AK","AZ", ... "WY"]`)
- `arr` (number ≥ 0)
- `enrollment` (integer | null — public-record district enrollment; closes PSM P2-5)
- `contract_start`, `contract_end`, `renewal_date` (dates)
- `funding_source` (enum: `general_fund | esser | title_i | title_iv | iii_eia | state_grant | foundation_grant | mixed | other` — PSM P1-8)
- `owner_psm`, `sfdc_owner` (string)
- `top15` (object `{is_member: bool, reason: enum(community_size|strategic_logo|expansion_potential|reference_account|other), owner: string, designated_at: date} | null` — PSM P0-5)
- `lifecycle_phase` (enum: `deployment | boi | moi | renewal`)
- `lifecycle_substage` (enum, allowed values depend on phase per the table below — PSM P0-1)
- `stage_entered_at` (date-time)
- `last_touchpoint_at` (date-time | null)
- `cadence_tier` (enum: `weekly | monthly | quarterly` — PSM P0-3)
- `next_touchpoints` (array of `{type: enum(checkin|qbr|renewal_meeting|strategic|pd_session|success_plan_review|sentiment_update|health_check), due_at: date-time, derived_from: enum(calendar_event|cadence_projection)}` — PSM P1-7; replaces v1's single `next_required_touchpoint_at`)
- `sentiment_score` (number 0–100)
- `engagement_score` (number 0–100 — defined as `100 * percentile_rank(messages_sent_30d_per_active_user, all_partners)`, computed in synthesize.py and documented in rubric file)
- `usage_trend_30d_pct` (number — precomputed in synthesize.py; rubric depends on it; closes data-eng P1-8)
- `priority_score` (number 0–100)
- `priority_breakdown` (object: required keys = exactly the 9 signal names; values 0–100 raw signal values; `additionalProperties: false`)
- `open_escalations` (integer ≥ 0)
- `open_tickets` (integer ≥ 0)

**Allowed `lifecycle_phase` × `lifecycle_substage` pairs** (closes PSM P0-1; the schema does this with `if/then/else` per phase, OR — easier — the integrity script asserts the allowed-pairs table):

| phase | allowed substages |
|---|---|
| `deployment` | `needs_assessment`, `data_mapping`, `data_upload`, `validation`, `configuration` |
| `boi` | `training`, `go_live`, `adoption` |
| `moi` | `data_review`, `insights_and_analysis` |
| `renewal` | `strategic_planning`, `success_and_growth` |

#### `contacts[]`

`contact_uid` · `account_uid` · `org_uid` · `name` · `title` · `role` (enum: `champion | exec_sponsor | superintendent | tech_lead | family_engagement | stakeholder`) · `influence_level` (enum: `high | medium | low`) · `sentiment` (enum: `green | yellow | red`) · `last_interaction_at` (date-time | null).

**Required role coverage** (synthesize.py asserts): every partner has exactly one `champion` and one `exec_sponsor`.

#### `timeline_events[]`

`event_uid` · `account_uid` · `org_uid` · `type` (enum of 13 values: `closed_won | kickoff | data_mapping | go_live | training | qbr | checkin | success_plan_review | escalation | sentiment_change | renewal_conversation | expansion_conversation | success_plan_milestone`) · `ts` (date-time) · `source` (enum: `salesforce | planhat | support | snowflake | calendar | manual`) · `summary` (string ≤ 1000 chars — data-eng P2-3) · `source_ref` (string matching `^(salesforce|planhat|support|calendar)://[A-Za-z0-9._:/-]+$` — opaque internal scheme, NO `https://`; closes security P0-1 + P0-2) · `payload` (object, type-dependent — for `sentiment_change`: `{prior_score, new_score, reason, notes, action_plan}`; for `escalation`: `{severity, opened_at, owner}`; PSM P1-6).

#### `usage_daily[]`

District-level only (v2 — security P1-2 + data-eng P1-3 split): `{account_uid, org_uid, date, active_users, active_teachers, active_admins, messages_sent, messages_received, family_invited, family_activated, family_engagement_rate}`.

#### `usage_daily_school[]` (NEW v2 — split from v1)

`{account_uid, org_uid, school_uid, school_name, date, active_users, usage_level}`. School-level rows live here; the district fact stays clean.

#### `success_plans[]`

`{plan_uid, account_uid, org_uid, name, owner, status (enum: on_track | at_risk | complete | overdue), goals: [{goal_uid, description, owner, due_date, progress_pct (0–100), status (same enum)}]}` — closes data-eng P1-2 (plan-level rolls up from goals).

#### `contracts[]` (1-to-many — closes data-eng P1-1)

`{contract_uid, account_uid, org_uid, kind (enum: current | previous | amendment | renewal_quote | order_form), doc_ref (string matching the opaque scheme regex above; NOT a public URL), start, end, arr, multi_year (bool), schools_included (int), licensed_users (int), products_purchased (string[]), pd_purchased_sessions (int), pd_completed_sessions (int), pd_expiration_date (date | null) — PSM P1-5}`.

Synthesize.py asserts: exactly one `kind: "current"` per partner; can have 0 or more of every other kind.

#### `tickets[]`

`{ticket_uid, account_uid, org_uid, opened_at, status (enum: open | in_progress | resolved | closed), severity (enum: p1 | p2 | p3 | p4), theme (enum: adoption | data_quality | permissions | rostering | outage | feature_request | integration | training — PSM P2-1), age_days, is_escalation (bool)}`.

#### `calendar_events[]`

`{event_uid, account_uid, org_uid, type (enum: qbr | checkin | renewal_meeting | strategic | pd_session | success_plan_review | sentiment_update | health_check), scheduled_at, duration_min, status (enum: scheduled | completed | missed | cancelled | rescheduled — PSM P2-3)}`.

#### `bridge_account_xref[]` (NEW v2 — closes data-eng P1-6)

Modeled in `data.json`, not just docs: `{account_uid, salesforce_id, planhat_id, support_tool_id, snowflake_partner_key, match_method (enum from the SKILL: external_id | email_domain | name_fuzzy | manual | unresolved — closes data-eng P1-7), confidence (number 0–1), manual_override_reason (string | null), overridden_by (string | null), last_verified_at (date-time)}`.

In the synthetic fixture every row has `match_method: "external_id"`, `confidence: 1.0` (single-org single-source-of-truth posture). Real Tier 0.5 connectors populate the other methods.

#### `priority_weights{}`

```json
{
  "renewal_timing": 20,
  "health_decline": 18,
  "sentiment_decline": 12,
  "days_overdue_vs_cadence": 12,
  "open_escalations": 15,
  "ticket_volume": 5,
  "arr_percentile": 5,
  "top15_bonus": 5,
  "usage_decline": 8
}
```

**Sum: 100.** Closes PSM P1-4 (bumped escalations, reduced renewal_timing). Required keys exactly these 9; `additionalProperties: false`.

Sum-to-100 is **not schema-enforceable**; integrity script (§Step 5) asserts it.

### Step 2 — `data.export.schema.json` (Tier 0.5 drop-in contract)

A second, looser schema that defines what a real Tier 0.5 export MUST produce. Closes architect P0-4.

- All fields synthesize.py would mark `synthetic_only` are OPTIONAL here (e.g., `priority_breakdown` — Tier 0.5 may not compute it; renderer computes from raw signals if absent).
- `org_uid` strict UUIDv4 still required.
- Cross-entity referential integrity still required (the integrity script also takes a `--export-mode` flag that runs against this schema).

Document explicitly in this file's comments which fields are `synthetic_only` (renderer-safe to default), which are `production_required` (Tier 0.5 MUST produce), and which are `derived_at_render` (Tier 1 computes from inputs).

### Step 3 — `data.json` (extend the existing fixture as superset)

Read current `data.json` first. The existing top-level keys (`report`, `_README`, `bands`, `components`, `kpis`, `cohort`, `trend_weeks`, `portfolio_trend`, `partners`) STAY. The existing 11 partners get their NEW v2 fields added alongside their existing 13 fields.

**Then ADD top-level:** `schema_version: 1`, `$id: "urn:ravenclaude:psm-dashboard-data"`, `org_uid: "<a valid UUIDv4>"`, `as_of: "2026-06-04T00:00:00Z"`, `priority_weights: {...}`, then the new entity arrays.

**Synthetic content shape (canonical source is synthesize.py — see Step 4):**

- **Partner count:** v2 grows from 11 (existing) to **25 total** — keep the 11 existing names + add 14 more. Distribution per PSM P1-3:
  - **~14 green** (`band: "g"` for existing + `score ≥ 70` for new)
  - **~7 yellow** (`band: "y"`, score 50–69)
  - **~4 red** (`band: "r"`, score < 50)
  - **~7 inside a renewal bucket**, weighted toward 120/180 days (NOT 30/60 — only 1 partner at 30-day is realistic for a healthy book)
  - ≥ 1 partner with `last_touchpoint_at` set to today (test no-false-alarm path of cadence decay)
- **Fictional name list — use ONLY these** (closes security P0-4 + data-eng P2-7):
  - For new partners: `Quokka Valley Schools`, `Stonebridge Unified`, `Glassmere ISD`, `Wendelhart Public Schools`, `Pellington County Schools`, `Brindleford School District`, `Marmotview Unified`, `Tussocksprings ISD`, `Kelpforest Public Schools`, `Norrwhisper Schools`, `Beigewood Unified`, `Cobblefern School District`, `Murmuring Pines ISD`, `Thistlebrook Unified`. These are deliberately implausible (no real-district collision risk; verified by web-search spot-check).
- **Synthetic contact names:** prefix with `Demo:` so a leaked screenshot reads as synthetic on sight (closes security P0-4): `Demo: Riley Carter`, `Demo: Morgan Singh`, etc. Generator MUST use these.
- **Top 15 flag:** 8 of the 25 partners are top15 members. Each has `top15.reason` populated (mix of community_size / strategic_logo / expansion_potential / reference_account).
- **`enrollment`:** synthesize from 800 (small) to 28,000 (large), log-distributed.
- **`bridge_account_xref`:** 25 rows (1 per partner), all `match_method: "external_id"`, `confidence: 1.0`.
- **`timeline_events`:** 8–20 per partner, mix of all 13 types, ≥ 3 sources represented per partner.
- **`success_plans`:** 1–3 per partner, each with 2–5 nested goals.
- **`contracts`:** ≥ 1 `kind: "current"` per partner; 30% of partners also have 1 `previous` contract.
- **`tickets`:** 0–5 per partner; 70% closed, 20% open, 10% in_progress; severity p2 dominant.
- **`calendar_events`:** 2–6 per partner.
- **`usage_daily`:** 90 days × 25 partners (district level).
- **`usage_daily_school`:** for the 8 multi-school partners, school-level rows.

### Step 4 — `synthesize.py` (the reproducible generator)

```python
#!/usr/bin/env python3
"""synthesize.py — reproducible synthetic-data generator for the PSM dashboard.

Tested on Python 3.12.x. Stdlib only — NO third-party deps (faker, pydantic, etc).

USAGE
  python3 plugins/edtech-partner-success/bi-report/synthesize.py \
      [--seed 42] [--partners 25] [--as-of 2026-06-04] \
      [--out plugins/edtech-partner-success/bi-report/data.json] [--check]

CANONICAL INVOCATION (closes architect P2-4):
  python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 \
      --out plugins/edtech-partner-success/bi-report/data.json

DETERMINISM DISCIPLINE (closes architect P1-1):
  - All randomness via `rng = random.Random(seed)`, NEVER module-level `random`.
  - No `set()` over user-visible values; iterate sorted lists.
  - Verify step must `export PYTHONHASHSEED=0` for defense in depth.
  - All datetimes derived from `--as-of`, never `datetime.now()`.
  - UUIDs via `uuid.UUID(int=rng.getrandbits(128))`, NEVER `uuid.uuid4()`.
  - `json.dumps(..., indent=2, sort_keys=False, ensure_ascii=False)` — match existing data.json style.
  - Floats rounded to 2 decimals at construction.

FERPA SELF-CHECK (closes security P1-3):
  - End-of-generation: `assert_no_pii(generated_dict)` runs the same denylist as the CI
    integrity script against every string VALUE in the structure.
  - Exits 1 on hit.

OUTPUT DISCIPLINE (closes security P1-6):
  - No per-entity prints to stderr/stdout. Only summary counts.
"""
```

**Cross-entity assertions (synthesize.py runs these before writing):**

- Every non-`partners` `account_uid` exists in `partners[].account_uid`.
- Every `account_uid` is a strict UUIDv4.
- Every contract has exactly one `kind: "current"` per partner.
- Every partner has exactly one champion + one exec_sponsor in `contacts[]`.
- `priority_weights` keys are exactly the 9 names AND values sum to 100.
- For each partner: `lifecycle_substage` ∈ allowed set for `lifecycle_phase`.
- For each partner: `priority_score == round(sum(weights[k] * breakdown[k]) / 100, 2)`.

Exit 1 on any failure with the row that violated.

**Reproducibility verify (canonical):**

```sh
PYTHONHASHSEED=0 python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/run1.json
PYTHONHASHSEED=0 python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/run2.json
diff /tmp/run1.json /tmp/run2.json   # exit 0; no diff
PYTHONHASHSEED=0 python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/canon.json
diff /tmp/canon.json plugins/edtech-partner-success/bi-report/data.json   # exit 0
```

### Step 5 — `scripts/check-psm-data-integrity.py` (the CI gate)

Standalone Python validator that runs against the COMMITTED `data.json` — catches hand-edits the seeded-diff loop misses (closes data-eng P0-5, P0-6, P0-7 + architect P1-2, P1-7 + security P1-1).

**Checks (each exits 1 with the violating row on failure):**

1. **JSON Schema validation** — `python3 -m jsonschema -i data.json data.schema.json`. (Subprocess; if the module isn't installed locally, emit a clear `[skip — install jsonschema]` and exit 0 with a warning — but ALWAYS hard-fail in CI where the module is installed.)
2. **Cross-entity refs** — every non-`partners` `account_uid` ∈ `partners[].account_uid`.
3. **Closed-object recursive** — walk every object subschema, fail if any has implicit `additionalProperties: true`.
4. **Sum-to-100** — `priority_weights` values sum to exactly 100.
5. **Phase × substage** — every `lifecycle_substage` ∈ allowed set for `lifecycle_phase`.
6. **Priority math** — every `priority_score == round(sum(weights[k] * breakdown[k]) / 100, 2)`.
7. **FERPA grep — HARDENED** (closes data-eng P0-7, P1-5 + security P0-3):
   - **Pattern (file-content scan):** matches any of `ssn`, `social.security`, `student[_ ]?name`, `student[_ ]?id`, `pupil`, `learner[_ ]?id`, `child[_ ]?name`, `parent[_ ]?name`, `parent[_ ]?email`, `guardian`, `iep[_ ]?details`, `504[_ ]?plan`, `race[_ ]?code`, `ethnicity[_ ]?code`, `dob`, `birth[_ ]?date`, `frpl`, `free[_ ]?and[_ ]?reduced`, or any email-shape (`@.*\.(com|org|edu|net|gov)`), or any phone-shape (`\d{3}-\d{3}-\d{4}`).
   - Match → exit 1.
8. **URL discipline** — every `doc_ref` and `source_ref` matches the opaque scheme regex; explicit fail on any `https://` or `http://` in those fields (closes security P0-1, P0-2).
9. **Real-district-name guard** — load a small embedded denylist of well-known real US districts (LAUSD, NYCDOE, CPS Chicago, Houston ISD, Dade County Schools, Clark County School District, Broward, Hillsborough, Cobb County, Cedar Falls, etc.) — fail if any synthetic partner name fuzzy-matches (case-insensitive substring) any of them. Closes security P0-4.
10. **`org_uid` UUIDv4** — every entity record's `org_uid` matches the strict UUIDv4 pattern.

Each check has a `--check N` runner for per-check debug, mirroring `audit-gates.sh` Gate 50/60/70 convention.

### Step 6 — `dashboard-identity-spine.md`

Documents `bridge_account_xref` shape, references `cross-system-identity-resolution/SKILL.md`. **Uses the SKILL's `match_method` enum verbatim** (closes data-eng P1-7). Includes the manual_override audit-trail requirement (closes security P2-3).

Sections: §1 what this is, §2 `account_uid` choice (strict UUIDv4 internal), §3 `bridge_account_xref` shape with full per-column doc, §4 match_method tiers + < 0.9 dashboard banner rule, §5 anti-patterns, §6 references.

### Step 7 — `dashboard-priority-score-rubric.md`

Documents the 9-signal rubric.

**Signal formulas (v2 — all addressed P0/P1 fixes):**

| Signal | Formula |
|---|---|
| `renewal_timing` | `100 if d ≤ 30 else 85 if d ≤ 60 else 65 if d ≤ 90 else 40 if d ≤ 120 else 20 if d ≤ 180 else 0` where `d = days_to_renewal` (PSM P0-2 bucket model) |
| `health_decline` | `max(0, 100 - health_score)` |
| `sentiment_decline` | `max(0, 100 - sentiment_score)` |
| `days_overdue_vs_cadence` | `max(0, days_since_touchpoint - expected_cadence_days[cadence_tier])`, suppressed (→0) during dead zones from `k12-psm-operating-cadence.md` (PSM P0-3) |
| `open_escalations` | `min(100, open_escalations * 25)` |
| `ticket_volume` | `min(100, open_tickets * 10)` |
| `arr_percentile` | `100 * percentile_rank(arr, all_partner_arrs)` (PSM P0-4 portfolio-relative, not absolute cap) |
| `top15_bonus` | `100 if top15.is_member else 0` |
| `usage_decline` | `max(0, 100 - usage_trend_30d_pct)` where `usage_trend_30d_pct` is the precomputed 30-day percent change in `active_users` (data-eng P1-8 — precomputed in synthesize.py, read at render time) |

**Default weights** (sum to 100): copy from §Step 1 `priority_weights` block.

**Composition (closes architect P0-3):**

- `priority_breakdown[k]` = raw 0–100 signal value (output of the formula above).
- `priority_score` = `round(sum(weights[k] * breakdown[k]) / 100, 2)`.
- "Per-signal contribution percent" rendered at Tier 1 = `(weights[k] * breakdown[k]) / priority_score / 100`. **Derived, never stored.**

**Cadence dead-zone suppression (PSM P0-3):** during dates in the `k12-psm-operating-cadence.md` dead-zone list (late August, Thanksgiving week, Winter Break, Spring Break, state testing windows), `days_overdue_vs_cadence` returns 0 regardless of actual days. The rubric file lists the exact date ranges keyed off `as_of`'s year.

**Tier 0.5 export contract** — the export schema marks `priority_breakdown` and `priority_score` as `synthetic_only` (Tier 0.5 may not produce them; Tier 1 renderer computes from raw signals when absent).

### Step 8 — `dashboard-schema-evolution.md` (closes architect P0-2)

Short knowledge file documenting:

- `schema_version` is required + `const: 1` today.
- Backward-incompatible bump = MAJOR version (v1 → v2): renderer refuses to load.
- Backward-compatible extension = patch version stays at 1 (add new optional top-level keys; nothing existing changes).
- Tier 0.5 may NOT bump `schema_version` independently — it must match the canonical schema.
- Pattern: any schema bump ships in a single PR with both the schema AND a synthesize.py regen.

### Step 9 — `.prettierignore` (append)

Add the line:

```
plugins/edtech-partner-success/bi-report/data.json
```

Closes data-eng P0-4 — synthesize.py's `json.dumps(indent=2, sort_keys=False, ensure_ascii=False)` becomes the canonical formatter; prettier no longer touches the fixture.

### Step 10 — `scripts/audit-gates.sh` (append a new gate)

After Gate 47/48 (the validate-schemas / sanitizer area), add:

```bash
echo "── Gate 52: PSM dashboard data integrity ─────────────────────────────"
# must-pass: real tree
rc=0; python3 scripts/check-psm-data-integrity.py >/dev/null 2>&1 || rc=$?
gate "psm-data-integrity (real tree)" must_pass "$rc"
# must-fail: a fixture with an orphan account_uid in contacts[]
DI_BAD="$TMP/data-orphan.json"
python3 - <<PY > "$DI_BAD"
import json
d = json.load(open("plugins/edtech-partner-success/bi-report/data.json"))
d["contacts"].append({**d["contacts"][0], "contact_uid": "test-orphan",
                     "account_uid": "00000000-0000-0000-0000-deadbeefcafe"})
print(json.dumps(d))
PY
rc=0; python3 scripts/check-psm-data-integrity.py --data "$DI_BAD" >/dev/null 2>&1 || rc=$?
gate "psm-data-integrity (orphan account_uid detected)" must_fail "$rc"
```

### Step 11 — `.repo-layout.json` (verify only)

Run §6 below. Expected: "Layout OK". If violations, extend `allowed_globs` with the missing pattern (NOT per-file).

---

## 5. Verification — exactly what Codex runs before pushing

In order. Run independent steps in parallel via `&` + `wait`. ALL must pass before `git push`.

| # | Command | Expected |
|---|---|---|
| 1 | `npx --yes prettier --write . --log-level warn` then `npx --yes prettier --check . --log-level warn` | exit 0 |
| 2 | `python3 -m json.tool plugins/edtech-partner-success/bi-report/data.json > /dev/null` | exit 0 |
| 3 | `python3 -m json.tool plugins/edtech-partner-success/bi-report/data.schema.json > /dev/null` | exit 0 |
| 4 | `python3 -m json.tool plugins/edtech-partner-success/bi-report/data.export.schema.json > /dev/null` | exit 0 |
| 5 | `python3 -m jsonschema -i data.json data.schema.json` | exit 0 |
| 6 | `PYTHONHASHSEED=0 python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/gen.json && diff /tmp/gen.json plugins/edtech-partner-success/bi-report/data.json` | exit 0 |
| 7 | `python3 scripts/check-psm-data-integrity.py` | exit 0 (all 10 checks pass) |
| 8 | `python3 scripts/check-frontmatter.py plugins/edtech-partner-success/knowledge/` | exit 0 |
| 9 | `bash scripts/audit-gates.sh` | clean (modulo local-env jsonschema gap; CI has the module) |
| 10 | Layout snippet from §6 below | "Layout OK" |

---

## 6. Layout snippet (verify)

```sh
python3 - <<'PY'
import fnmatch, json, subprocess
allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
new = subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=A", "main"],
    capture_output=True, text=True,
).stdout.splitlines()
violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
if violations:
    print("VIOLATIONS — extend .repo-layout.json:")
    for v in violations: print(" ", v)
else:
    print("Layout OK")
PY
```

Expected: "Layout OK" (the new `data.export.schema.json` + the new `dashboard-schema-evolution.md` are covered by existing globs). New `scripts/check-psm-data-integrity.py` is covered by `scripts/**`.

---

## 7. PR shape — exact format

```sh
git add plugins/edtech-partner-success/bi-report/data.schema.json \
        plugins/edtech-partner-success/bi-report/data.export.schema.json \
        plugins/edtech-partner-success/bi-report/data.json \
        plugins/edtech-partner-success/bi-report/synthesize.py \
        plugins/edtech-partner-success/knowledge/dashboard-identity-spine.md \
        plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md \
        plugins/edtech-partner-success/knowledge/dashboard-schema-evolution.md \
        scripts/check-psm-data-integrity.py \
        scripts/audit-gates.sh \
        .prettierignore

git commit -m "feat(edtech-partner-success): PSM dashboard Tier 0 — schema + synthetic fixture + integrity gate"
git push -u origin feat/psm-dashboard-tier-0-foundation
```

Open as a draft PR via `mcp__github__create_pull_request` with `draft: true`. PR body summary mirrors the commit subject + a bulleted "what ships" + "deliberately does NOT do" + test plan.

---

## 8. Wall-handling (if Codex gets stuck)

The wall pattern Codex MUST follow:

1. **Re-read the relevant prior** in §1 — the constraint is almost always already documented.
2. **If silent but a default exists per the strategic plan's Alternatives**, take it; note as inline code comment (`# Default per plan.md A4: config-driven priority_weights`).
3. **If silent AND no default**, stop and `AskUserQuestion` Matt.
4. **Walls where step 3 is mandatory** (Q1–Q6 from the strategic plan affect Tier 0.5, NOT Tier 0 — Tier 0 is synthetic + contract + knowledge):
   - Tier 0 should NOT hit any of Q1–Q6 if it follows this brief literally.

---

## 9. What Codex MUST NOT do (extended in v2)

- **Do not** add Tier 1 / 2 / 3 / 4 / 5 work to this PR.
- **Do not** version-bump `plugin.json` or `marketplace.json`. Wait for Tier 1.
- **Do not** add a CLAUDE.md milestone. Wait for Tier 1.
- **Do not** edit `report.html`. Wait for Tier 1.
- **Do not** re-author content that already lives in the four "do not re-author" priors from §1.
- **Do not** introduce a per-student field, ever. FERPA hard rule.
- **Do not** use any of the real US district names from the embedded denylist in the integrity script.
- **Do not** force-push, amend, or rewrite history on a pushed branch. New commits only.
- **Do not** mark the PR ready-for-review without Matt's say-so. Draft only.
- **(v2 ADDITION)** **Do not** change the existing `data.json` top-level blocks (`report`, `_README`, `bands`, `components`, `kpis`, `cohort`, `trend_weeks`, `portfolio_trend`). v2 is strictly additive.
- **(v2 ADDITION)** **Do not** drop any existing `partners[]` per-row key from the existing 11 partners (`name`, `segment`, `psm`, `score`, `delta`, `band`, `components{6 keys}`, `spark`, `flags`, `play`, `last_touch`, `next_qbr`, `renewal`). v2 adds alongside.
- **(v2 ADDITION)** **Do not** introduce a new health-component key beyond the existing 6 (`adoption`, `touchpoint`, `outcome`, `sentiment`, `champion`, `usage`). v1's mistake was dropping `champion` + `usage`.
- **(v2 ADDITION)** **Do not** use module-level `random`. Only `rng = random.Random(seed)`.
- **(v2 ADDITION)** **Do not** move `synthesize.py` to `plugins/data-platform/`. The dashboard's canonical contract is owned by `edtech-partner-success`.
- **(v2 ADDITION)** **Do not** introduce third-party Python dependencies (faker, pydantic, polars, etc.). Stdlib only.
- **(v2 ADDITION)** **Do not** use `https://` or `http://` in `doc_ref` or `source_ref` values. Opaque scheme only until Tier 0.5.
- **(v2 ADDITION)** **Do not** use any of the v1 brief's example synthetic names ("Cedar Falls Public Schools" is a REAL Iowa district). Use only the v2 list in §3 Step 3.
- **(v2 ADDITION)** **Do not** add prints to stderr/stdout in `synthesize.py` that include per-entity values. Summary counts only.

End of v2 brief.
