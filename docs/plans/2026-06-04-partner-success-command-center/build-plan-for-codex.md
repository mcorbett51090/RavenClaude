# Build plan for Codex — Partner Success Command Center, Tier 0 (v3)

**Audience:** a fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace with RavenClaude installed. Codex is the engineer; this file is the engineer's brief. **Self-contained — do not ask Matt to clarify what's already in here.**

**Scope:** Tier 0 of [`plan.md`](./plan.md) — JSON schema + field-classifications + synthetic fixture + seeded generator + cross-entity integrity gate + three knowledge files. **Zero render changes, zero version bump, zero new agent, zero CLAUDE.md milestone.** Tier 1 ships those.

**Version note:** v1 had 17 P0 issues found by a 4-panel cold review. v2 closed most v1 P0s but introduced ~10 NEW P0s (a rewrite-introduces-regressions trap). v3 closes the v1 + v2 P0s together. The cumulative changelog below is what you, Codex, need to know — do NOT look for v1 or v2; this file IS the spec.

---

## 0. What v3 closes (cumulative since v1)

### From the v1 round (closed in v2, verified in v3):

- Partner-shape collision: `partners[]` is now a strict superset of the existing fixture's 11-field shape. The existing 6-key `components` block is preserved verbatim; new fields are added alongside under new names.
- Priority math: `priority_breakdown[k]` = raw 0–100 signal value (clamped); `priority_score` = `sum(weights[k] * breakdown[k]) / 100`; per-signal contribution percent is derived at render time, never stored.
- FERPA grep: hardened denylist as an exit-coded CI gate.
- `account_uid` format: strict UUIDv4 only; real SFDC ID lives in `bridge_account_xref.salesforce_id`.
- Prettier byte-equality clash: `data.json` added to `.prettierignore`.
- Cross-entity integrity: `scripts/check-psm-data-integrity.py` registered as a CI gate.
- `priority_weights` sum-to-100 enforced in the integrity script.
- `schema_version` required field + evolution policy.
- `lifecycle_phase` × `lifecycle_substage` split per spec's 12 substates.
- `top15` structured object.
- URL fields use opaque scheme.

### NEW v3 closures (issues v2 left or introduced):

- **band enum:** v2 said `"g"/"y"/"r"` in §Step 3 — that was a typo. v3 forces `"green"/"yellow"/"red"` everywhere (matches existing fixture).
- **`priority_breakdown.days_overdue_vs_cadence` was unbounded** (could exceed 100 → schema collision). v3 uses a bucket model parallel to `renewal_timing`, capped at 100.
- **`usage_decline` was directionally wrong + unbounded** (growth scored as high decline; declining partners scored >100). v3 uses a corrected formula with explicit cap.
- **Gate 52 must-fail was audit theater** (invalid UUIDv4 made jsonschema check fail first, not orphan check). v3 uses a valid-but-orphan UUIDv4.
- **Opaque URI regex allowed `:` and `/` → URL smuggling possible.** v3 tightens to forbid `:` after the scheme separator and forbid `//` anywhere in the body.
- **Exception traceback leaked failing PII row to CI logs.** v3 wraps `assert_no_pii` in try/except + scrubs to field path only + sets `sys.tracebacklimit = 0` before the check.
- **`bridge_account_xref.salesforce_id` had no synthetic-only constraint** (Tier 0.5 could ship real production IDs). v3 mandates `synthetic-` prefix in Tier 0; integrity check rejects committed rows missing the prefix.
- **Dead-zone dates were "state-variable" with no concrete data.** v3 ships a `dashboard-dead-zones.md` table keyed on US state.
- **`next_touchpoints[]` didn't guarantee one `cadence_projection` per type per partner** → some partners would show empty countdown lists. v3 requires per-partner coverage.
- **`funding_source` enum:** `iii_eia` was a typo + `esser` is past liquidation. v3 uses the correct 2026 enum.
- **Existing 11 partner names include real US collisions** (Riverside Unified, Mesa Community College, Granite State University, Cedar Valley Schools, Northshore Academy). v3 audits + renames as part of Tier 0.
- **`enrollment` was scope creep** (not in spec, plus a quasi-identifier risk at Tier 0.5). v3 drops it.
- **`cadence_tier` leaks PSM judgment.** v3 marks it `synthetic_only` in `field-classifications.json`; Tier 1 recomputes from ARR + segment + lifecycle.
- **Legacy block subschemas not enumerated.** v3 mandates Codex enumerates the inner shape of `report{}`, `bands{}`, `components[]`, `kpis[]`, `cohort{}`, `trend_weeks[]`, `portfolio_trend[]`, `_README` from the existing fixture so `additionalProperties: false` doesn't reject them at a level deeper than top-level.
- **Integrity script missed contract-cardinality + role-coverage checks.** v3 adds checks #11 (exactly one `kind: current` per partner) and #12 (exactly one champion + one exec_sponsor per partner).
- **jsonschema silent-skip on dev box could mask a stale gate-audit.** v3 makes check #1 LOUD-skip with explicit "THIS IS NOT A PASS" when `${CI:-}` is empty.
- **Synth/prod boundary lived only in comments.** v3 ships `bi-report/field-classifications.json` as a third artifact; integrity script enforces it.

---

## 1. Pre-flight

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is latest main |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-0-foundation` | switched |
| 3 | Read this brief in full | (open the file) | every section |
| 4 | Read the strategic plan | `cat docs/plans/2026-06-04-partner-success-command-center/plan.md` | full file |
| 5 | Read the SME spec | `cat docs/research/2026-06-04-partner-success-dashboard-requirements/spec.md` | full file |
| 6 | Read the EXISTING fixture | `cat plugins/edtech-partner-success/bi-report/data.json \| head -200` | confirm top-level keys + 11 partners + band enum is `"green"/"yellow"/"red"` |

**Read also (priors that constrain design):**

- `plugins/edtech-partner-success/CLAUDE.md` — house rules 1, 4, 8, 12.
- `plugins/edtech-partner-success/knowledge/partner-health-score-drift.md`.
- `plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md`.
- `plugins/edtech-partner-success/knowledge/partner-health-decline-which-play.md`.
- `plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md`.

---

## 2. The existing fixture — preserve as superset, but RENAME real-collision partners

Existing `bi-report/data.json` top-level keys: `report{}`, `_README`, `bands{}`, `components[]`, `kpis[]`, `cohort{}`, `trend_weeks[]`, `portfolio_trend[]`, `partners[]`.

Existing `partners[]` shape (preserved verbatim except for names — see below):

```
{name, segment, psm, score, delta, band,
 components{adoption, touchpoint, outcome, sentiment, champion, usage},
 spark[], flags[], play, last_touch, next_qbr, renewal}
```

**band enum is `"green" | "yellow" | "red"` — full words, never abbreviated.**

### Existing 11 names — RENAME these 5 (real-collision risks):

| Existing name | Real-world collision | v3 replacement |
|---|---|---|
| `Riverside Unified` | Riverside USD CA (41k students) | `Quokka Valley Schools` |
| `Mesa Community College` | Mesa Community College AZ | `Marmotview Unified` |
| `Granite State University` | Granite State College NH | `Glassmere ISD` |
| `Cedar Valley Schools` | Cedar Valley Community SD IA | `Stonebridge Unified` |
| `Northshore Academy` | Northshore SD WA | `Norrwhisper Schools` |

Keep these 6 (acceptably generic / no real-collision): `Brightpath Charter`, `Harbor District`, `Summit Learning Co-op`, `Lakeside Public Schools`, `Pinecrest ISD`, `Willowbrook Schools`.

**Discipline:** when you rename, ALSO update the `kpis[]` block + any other inline references to the old names so the fixture stays internally consistent. Run `grep -E 'Riverside Unified|Mesa Community College|Granite State University|Cedar Valley Schools|Northshore Academy' plugins/edtech-partner-success/` after the rename — exit 1 (no match) is success.

### All 14 NEW partners use the v3 fictional name list:

`Wendelhart Public Schools`, `Pellington County Schools`, `Brindleford School District`, `Tussocksprings ISD`, `Kelpforest Public Schools`, `Beigewood Unified`, `Cobblefern School District`, `Murmuring Pines ISD`, `Thistlebrook Unified`, `Quillgarden Schools`, `Saltmarsh Unified`, `Ferncast ISD`, `Heronwood Public Schools`, `Briarholm Unified`.

(v2's list dropped 5 names; v3 replaces them so the curated list stays 14 + the 5 renames = 19 deliberately-fictional names alongside the 6 acceptably-generic ones from the existing fixture.)

---

## 3. The deliverable — exactly these files

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `plugins/edtech-partner-success/bi-report/data.schema.json` | CREATE | Authoritative JSON Schema. |
| 2 | `plugins/edtech-partner-success/bi-report/data.export.schema.json` | CREATE | Tier 0.5 production-required profile (subset). |
| 3 | `plugins/edtech-partner-success/bi-report/field-classifications.json` | CREATE | Per-field tagging: `synthetic_only` / `production_required` / `derived_at_render` / `internal_only`. Read by Tier 1 renderer. |
| 4 | `plugins/edtech-partner-success/bi-report/data.json` | EDIT (superset + rename collisions) | Extend with new blocks. Rename 5 partners (§2). Preserve every existing key on the other 6. |
| 5 | `plugins/edtech-partner-success/bi-report/synthesize.py` | CREATE | Seeded generator. PII self-check wrapped in scrubbed try/except. |
| 6 | `scripts/check-psm-data-integrity.py` | CREATE | 12 checks (incl. contract-cardinality + role-coverage; LOUD-skip jsonschema outside CI). |
| 7 | `plugins/edtech-partner-success/knowledge/dashboard-identity-spine.md` | CREATE | bridge_account_xref shape + match_method aligned with the SKILL. |
| 8 | `plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md` | CREATE | 9 signal formulas (with caps), default weights, contribution-percent derivation. |
| 9 | `plugins/edtech-partner-success/knowledge/dashboard-schema-evolution.md` | CREATE | `schema_version` policy. |
| 10 | `plugins/edtech-partner-success/knowledge/dashboard-dead-zones.md` | CREATE | State-keyed dead-zone table (concretizes `k12-psm-operating-cadence.md` deferrals). |
| 11 | `.prettierignore` | EDIT (append) | Add `plugins/edtech-partner-success/bi-report/data.json`. |
| 12 | `scripts/audit-gates.sh` | EDIT (append) | Wire Gate 52 with VALID-UUIDv4 orphan must-fail. |
| 13 | `.repo-layout.json` | VERIFY ONLY | Already covered. |

**Nothing else.**

---

## 4. Step-by-step build order

### Step 1 — `data.schema.json`

JSON Schema draft 2020-12.

**Top-level required:** `schema_version`, `$id`, `org_uid`, `as_of`, `report`, `_README`, `bands`, `components`, `kpis`, `cohort`, `trend_weeks`, `portfolio_trend`, `priority_weights`, `partners`, `contacts`, `timeline_events`, `usage_daily`, `usage_daily_school`, `success_plans`, `contracts`, `tickets`, `calendar_events`, `bridge_account_xref`.

**`additionalProperties: false` on the top-level AND on every nested object schema** — the brief mandates this; the integrity script asserts recursive closed-object structure (check #3).

**LEGACY-BLOCK SUBSCHEMAS — enumerate them from the existing fixture:**

You MUST inspect the existing `data.json` and ship subschemas for these blocks (closed objects + correct types):

- `report` → `{title: string, subtitle: string, refreshed: date, synthetic: bool, owner: string}`.
- `_README` → string (top-level, type: `["string"]`).
- `bands` → `{green: [integer, integer], yellow: [integer, integer], red: [integer, integer]}` (each is a 2-element tuple).
- `components` (array) → element schema: `{key: string, name: string, weight: integer, half_life_days: integer, plain: string}`. The 6 keys are: `adoption | touchpoint | outcome | sentiment | champion | usage`.
- `kpis` (array) → element schema: inspect existing fixture; capture every key.
- `cohort` → inspect.
- `trend_weeks` (array) → element schema: string (week labels) — inspect.
- `portfolio_trend` (array) → element schema: number — inspect.

(If the existing fixture has additional properties you didn't enumerate, the integrity script's recursive closed-object check fires and you fix in the same PR.)

**`$id`:** `"urn:ravenclaude:psm-dashboard-data"`.

**`schema_version`:** integer, `const: 1`.

**`org_uid`:** strict UUIDv4 regex `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`.

**`as_of`:** date-time (UTC).

**Per-entity required fields:**

#### `partners[]` (superset of existing 13 keys + new v3 keys)

Existing 13 keys PRESERVED EXACTLY: `name`, `segment`, `psm`, `score`, `delta`, `band` (enum `["green","yellow","red"]`), `components` (6-key object), `spark` (array of numbers), `flags` (array of strings), `play`, `last_touch`, `next_qbr`, `renewal`.

New v3 keys ADDED:

- `account_uid` (strict UUIDv4)
- `org_uid` (UUIDv4 — every entity record)
- `state` (US-state 2-char enum: 50 states + DC)
- `arr` (number ≥ 0)
- `contract_start`, `contract_end`, `renewal_date` (dates)
- `funding_source` (enum — see corrected list below)
- `owner_psm`, `sfdc_owner` (string)
- `top15` (`{is_member: bool, reason: enum, owner: string, designated_at: date}` OR `null` — `oneOf` in schema)
- `lifecycle_phase` (enum: `deployment | boi | moi | renewal`)
- `lifecycle_substage` (enum, paired per allowed table below)
- `stage_entered_at` (date-time)
- `last_touchpoint_at` (date-time | null)
- `cadence_tier` (enum: `weekly | bi_weekly | monthly | bi_monthly | quarterly | bi_annual` — extended per PSM P1-4)
- `next_touchpoints` (array of `{type, due_at, derived_from}` — see Step 3 for cardinality)
- `sentiment_score` (number 0–100)
- `engagement_score` (number 0–100 — labeled `synthetic_only` in field-classifications, percentile-rank derivation)
- `usage_trend_30d_pct` (number — SIGNED percent; positive = growth, negative = decline)
- `priority_score` (number 0–100)
- `priority_breakdown` (object with 9 required keys, values 0–100, `additionalProperties: false`)
- `open_escalations` (integer ≥ 0)
- `open_tickets` (integer ≥ 0)

**v3 NOTE:** `enrollment` is REMOVED from v2's spec — it's scope creep beyond what the spec asked for and a quasi-identifier at Tier 0.5.

**v3 CORRECTED `funding_source` enum:**

```
general_fund | esser_legacy | title_i | title_iii | title_iv | idea_b |
state_grant | state_replacement_grant | foundation_grant | mixed | other
```

(v2's `iii_eia` was a typo; ARP-ESSER liquidation deadline was Jan 2025 with some Mar 2026 extensions, so `esser` is renamed `esser_legacy`; `state_replacement_grant` reflects NY Smart Schools / CA LCFF supplemental.)

**Allowed `lifecycle_phase × lifecycle_substage` pairs** (per spec, integrity-script enforced):

| phase | allowed substages |
|---|---|
| `deployment` | `needs_assessment`, `data_mapping`, `data_upload`, `validation`, `configuration` |
| `boi` | `training`, `go_live`, `adoption` |
| `moi` | `data_review`, `insights_and_analysis` |
| `renewal` | `strategic_planning`, `success_and_growth` |

#### `contacts[]`

`contact_uid` · `account_uid` · `org_uid` · `name` (MUST start `Demo:` — integrity check enforces) · `title` · `role` (enum: `champion | exec_sponsor | superintendent | tech_lead | family_engagement | stakeholder`) · `influence_level` (enum: `high | medium | low`) · `sentiment` (enum: `green | yellow | red`) · `last_interaction_at` (date-time | null).

#### `timeline_events[]`

`event_uid` · `account_uid` · `org_uid` · `type` (enum: 13 values per v2 + `success_plan_milestone`) · `ts` (date-time) · `source` (enum: `salesforce | planhat | support | snowflake | calendar | manual`) · `summary` (string ≤ 1000 chars) · `source_ref` (string matching **v3 TIGHTENED regex** below) · `payload` (object — `oneOf` per type; for `sentiment_change`: `{prior_score, new_score, reason, notes, action_plan}`; closed-object per variant).

**v3 TIGHTENED `source_ref` regex** (closes security NEW P0-2 URL smuggling):

```
^(salesforce|planhat|support|calendar)://[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$
```

(No `:` in path body. No `//` past the scheme separator. No `.` in path body — pathological dotted-names are blocked.)

#### `usage_daily[]` (district-level)

`{account_uid, org_uid, date, active_users, active_teachers, active_admins, messages_sent, messages_received, family_invited, family_activated, family_engagement_rate}`.

#### `usage_daily_school[]`

`{account_uid, org_uid, school_uid, school_name (MUST start "Demo School:"), date, active_users, usage_level}`.

#### `success_plans[]`

`{plan_uid, account_uid, org_uid, name, owner, status (enum), goals: [{goal_uid, description, owner, due_date, progress_pct, status}]}`.

#### `contracts[]` (1-to-many)

`{contract_uid, account_uid, org_uid, kind (enum: current | previous | amendment | renewal_quote | order_form), doc_ref (TIGHTENED regex above), start, end, arr, multi_year, schools_included, licensed_users, products_purchased, pd_purchased_sessions, pd_completed_sessions, pd_expiration_date}`.

Integrity check #11: exactly one `kind: "current"` per `account_uid`.

#### `tickets[]`

`{ticket_uid, account_uid, org_uid, opened_at, status (enum), severity (enum), theme (enum: adoption | data_quality | permissions | rostering | outage | feature_request | integration | training | pricing | contract_question), age_days, is_escalation}`.

#### `calendar_events[]`

`{event_uid, account_uid, org_uid, type (enum 8 values), scheduled_at, duration_min, status (enum: scheduled | completed | missed | cancelled | rescheduled | pending_confirmation)}`.

#### `bridge_account_xref[]`

`{account_uid, salesforce_id, planhat_id, support_tool_id, snowflake_partner_key, match_method (SKILL enum: external_id | email_domain | name_fuzzy | manual | unresolved), confidence (number 0–1), manual_override_reason (string ≤ 200 chars | null), overridden_by (string | null), last_verified_at}`.

**v3 SYNTHETIC ID DISCIPLINE:** in the committed fixture, `salesforce_id`, `planhat_id`, `support_tool_id`, `snowflake_partner_key` MUST start with `synthetic-`. Integrity check #13 enforces this for `Tier 0` mode. Tier 0.5 runtime exports use a `--allow-real-ids` flag the integrity check honors.

#### `priority_weights{}`

```json
{
  "renewal_timing": 18,
  "health_decline": 18,
  "sentiment_decline": 10,
  "days_overdue_vs_cadence": 10,
  "open_escalations": 20,
  "ticket_volume": 5,
  "arr_percentile": 5,
  "top15_bonus": 5,
  "usage_decline": 9
}
```

(v3 PSM-tuned: escalations bumped to 20 per PSM NEW P1-1 — open escalations outrank a 60-day renewal. Sum: 18+18+10+10+20+5+5+5+9 = **100**.)

### Step 2 — `data.export.schema.json`

A separate schema that defines what Tier 0.5 export MUST produce vs. MAY omit.

- All fields marked `synthetic_only` in `field-classifications.json` are OPTIONAL here.
- All fields marked `production_required` are REQUIRED.
- All fields marked `derived_at_render` are OPTIONAL (renderer computes).
- `org_uid` strict UUIDv4 still required.
- Cross-entity referential integrity still required (integrity script `--export-mode`).

### Step 3 — `field-classifications.json` (v3 NEW — the synth/prod boundary as machine-readable artifact)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "comment": "Per-field tagging for the Tier 0 → Tier 0.5 → Tier 1 hand-off.",
  "classifications": {
    "synthetic_only": [
      "partners[].priority_breakdown",
      "partners[].priority_score",
      "partners[].engagement_score",
      "partners[].usage_trend_30d_pct",
      "partners[].cadence_tier",
      "contacts[].name"
    ],
    "production_required": [
      "org_uid", "as_of",
      "partners[].account_uid", "partners[].name", "partners[].arr",
      "partners[].contract_end", "partners[].renewal_date",
      "partners[].lifecycle_phase", "partners[].lifecycle_substage",
      "partners[].open_escalations", "partners[].open_tickets",
      "bridge_account_xref[].account_uid", "bridge_account_xref[].salesforce_id"
    ],
    "derived_at_render": [
      "partners[].priority_breakdown",
      "partners[].priority_score",
      "partners[].engagement_score",
      "next_touchpoints[].derived_from == 'cadence_projection'"
    ],
    "internal_only": [
      "partners[].cadence_tier"
    ]
  }
}
```

(A field can appear in multiple categories — `priority_breakdown` is `synthetic_only` in the Tier 0 fixture AND `derived_at_render` for Tier 1 production data.)

Tier 1 renderer reads this at load time and knows which fields to compute vs. trust. Integrity script check #14 asserts every field listed exists in `data.schema.json`.

### Step 4 — `data.json` (extend + rename)

Read current `data.json`. Existing top-level blocks STAY. Existing 11 partners — rename 5 per §2; preserve all 13 keys on each. ADD new v3 keys to each existing partner. ADD 14 new partners using the v3 name list.

**Synthetic content distribution targets** (PSM-realistic per PSM P1-3):

- 14 green / 7 yellow / 4 red (totals: 14+7+4 = 25 partners) — exact, not approximate.
- 7 partners inside a renewal bucket, distributed: 1 at ≤30d (rare-fire-drill), 1 at 60d, 2 at 90d, 1 at 120d, 2 at 180d.
- ≥ 1 partner with `last_touchpoint_at = today` (no-false-alarm test).
- 8 partners flagged `top15.is_member = true`; the other 17 have `top15: null`.
- Demo: prefix on every `contacts[].name`.
- 8 of 25 partners are multi-school (3–7 schools each) → `usage_daily_school` populated.

**`next_touchpoints[]` cardinality (closes PSM NEW P0-2):**

For EVERY partner, synthesize.py MUST produce AT LEAST ONE entry per `type` ∈ {`checkin`, `qbr`, `renewal_meeting`}, with `derived_from = 'cadence_projection'` if no `calendar_event` covers it. Integrity check #15 enforces this. (Other types: `pd_session`, `success_plan_review`, `sentiment_update`, `health_check` are optional.)

**`bridge_account_xref[]`:** 25 rows (1 per partner) with `match_method: "external_id"`, `confidence: 1.0`. ALL synthetic IDs prefixed `synthetic-` per §Step 1 discipline.

### Step 5 — `synthesize.py`

```python
#!/usr/bin/env python3
"""synthesize.py — reproducible synthetic-data generator for the PSM dashboard.

Tested on Python 3.12.x. Stdlib only.

USAGE
  python3 plugins/edtech-partner-success/bi-report/synthesize.py \
      [--seed 42] [--as-of 2026-06-04] \
      [--out plugins/edtech-partner-success/bi-report/data.json]

CANONICAL INVOCATION:
  PYTHONHASHSEED=0 python3 ... --seed=42 \
      --out plugins/edtech-partner-success/bi-report/data.json

DETERMINISM DISCIPLINE:
  - All randomness via `rng = random.Random(seed)`, NEVER module-level random.
  - No `set()` over user-visible values; iterate sorted lists.
  - No `dict()` over hash-randomized iteration sources. Use dict literals
    or `dict(sorted(...))` explicitly.
  - All datetimes derived from `--as-of`. Never `datetime.now()`.
  - UUIDs via `uuid.UUID(int=rng.getrandbits(128))`, NEVER uuid.uuid4().
  - `json.dumps(..., indent=2, sort_keys=False, ensure_ascii=False)`.
  - Floats rounded to 2 decimals AT CONSTRUCTION (not at output time).

FERPA SELF-CHECK (scrubbed traceback discipline — v3):
  - sys.tracebacklimit = 0 BEFORE running assert_no_pii().
  - assert_no_pii wrapped in try/except. On hit:
      - Print to stderr: "FERPA leak in field <field_path>: pattern <pattern_name>"
      - NEVER print the value.
      - sys.exit(1).
  - This prevents the value from re-leaking into CI logs as an
    AssertionError traceback.

OUTPUT DISCIPLINE:
  - No per-entity prints. Summary counts only.
  - No `print(json.dumps(failed_row))` debug paths — that's a leak vector.
"""
```

**Cross-entity assertions (synthesize.py runs before writing):**

- Every non-`partners` `account_uid` exists in `partners[].account_uid`.
- Every `account_uid` is strict UUIDv4.
- Every contract: exactly one `kind: "current"` per partner.
- Every partner: exactly one champion + one exec_sponsor in `contacts[]`.
- `priority_weights` keys are the 9 names; values sum to 100.
- `lifecycle_substage ∈ allowed[lifecycle_phase]`.
- `priority_score == round(sum(weights[k] * breakdown[k]) / 100, 2)`.
- Every partner has ≥1 `cadence_projection` `next_touchpoints` entry per of {`checkin`, `qbr`, `renewal_meeting`}.
- Every `bridge_account_xref[]` ID field starts `synthetic-`.

Exit 1 on any failure (via scrubbed try/except).

### Step 6 — `scripts/check-psm-data-integrity.py` (12 checks total, v3)

Standalone CI validator. Runs against committed `data.json`.

1. **JSON Schema validation.** `python3 -m jsonschema -i data.json data.schema.json`. **v3 CI-marker discipline:** if `os.environ.get('CI')` is set → hard-fail if jsonschema not installed. Otherwise → LOUD-skip: print `"SKIPPED (jsonschema not installed) — THIS IS NOT A PASS. Install jsonschema before declaring victory."` and exit with `2` (not 0), so callers can distinguish skip from pass.
2. Cross-entity refs: every non-partners `account_uid` ∈ partners.
3. Closed-object recursive: walk schema; fail any object subschema with implicit `additionalProperties: true` (and emit a warning for the constrained-additionalProperties `{type:...}` form).
4. Sum-to-100 on `priority_weights`.
5. Phase × substage allowed-pair table.
6. Priority math: `priority_score == round(sum(weights[k] * breakdown[k]) / 100, 2)` for every partner. Use the SAME float rounding as synthesize.py: round each breakdown[k] to 2 decimals first, then weight-sum, then round to 2 again.
7. **FERPA grep (hardened, v3-tightened):** `(?i)(\bssn\b|social\.security|student[_ ]?name|student[_ ]?id|pupil|learner[_ ]?id|child[_ ]?name|parent[_ ]?name|parent[_ ]?email|guardian|iep[_ ]?details|504[_ ]?plan|race[_ ]?code|ethnicity[_ ]?code|\bdob\b|birth[_ ]?date|\bfrpl\b|free[_ ]?and[_ ]?reduced)` + email regex `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|org|edu|net|gov|us|k12\.[a-z]{2}\.us)\b` + phone regex `(\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}`. Word boundaries on `frpl`, `dob`, `ssn` (prevents false positive on `frplease`/`dobermann`).
8. **URL discipline:** every `doc_ref` and `source_ref` matches the v3-tightened regex (`^(salesforce|planhat|support|calendar)://[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$`). Explicit additional sweep: any value matching `://` past the 12th character → fail (catches smuggle attempt).
9. **Real-district guard:** v3 uses **whole-token matching** (not substring). Token = name-words joined with single space, both sides lowercased. Embedded denylist: top-100 US districts by enrollment (LAUSD, NYCDOE, Chicago PS, Houston ISD, Dade County PS, Clark County SD, Broward County PS, Hillsborough County PS, Cobb County SD, Fairfax County PS, Gwinnett County PS, Wake County PS, Montgomery County PS MD, Prince George's County PS, Orange County PS FL, Palm Beach County PS, Duval County PS, Philadelphia SD, San Diego USD, San Francisco USD, Long Beach USD, Fresno USD, Albuquerque PS, DC PS, Atlanta PS, Jefferson County PS CO, Jefferson County PS KY, Mesa PS AZ, Tucson USD, Riverside USD, Anchorage SD, Boston PS, Detroit PS Community District, Charlotte-Mecklenburg SD, Cleveland Metro SD, Cincinnati PS, Granite SD UT, Davis SD UT, Salt Lake City SD, Cherry Creek SD, Denver PS, Baltimore County PS, Baltimore City SD, Anne Arundel County PS, Howard County PS, Loudoun County PS, Henrico County PS, Chesterfield County PS, Virginia Beach City PS, Norfolk PS, Newport News PS) + the top 10 community colleges (Mesa CC, Miami Dade College, Houston CC, etc.) + the top 5 state university systems (USNH including Granite State College, CSU system, SUNY, etc.). Run NCES top-100 list during PR review.
10. `org_uid` strict UUIDv4 on every entity record AND all values identical to top-level `org_uid` (per security NEW P2-5).
11. **Contract cardinality (v3):** exactly one `kind: "current"` per partner.
12. **Role coverage (v3):** exactly one champion + one exec_sponsor in `contacts[]` per partner.
13. **bridge_account_xref synthetic ID (v3):** every ID field starts `synthetic-` in Tier 0 mode.
14. **field-classifications validity (v3):** every field in `field-classifications.json` exists in `data.schema.json`.
15. **`next_touchpoints` coverage (v3):** every partner has ≥1 cadence_projection entry per `{checkin, qbr, renewal_meeting}`.
16. **Demo: prefix:** every `contacts[].name` starts `Demo:`; every `usage_daily_school[].school_name` starts `Demo School:` (skip in `--export-mode`).

Each check supports `--check N` for per-check debug.

### Step 7 — `dashboard-identity-spine.md`

Documents `bridge_account_xref` shape, references `cross-system-identity-resolution/SKILL.md`. Uses the SKILL's match_method enum VERBATIM. Documents the synthetic-ID-prefix rule for the Tier 0 fixture.

### Step 8 — `dashboard-priority-score-rubric.md`

**v3 signal formulas — every signal capped at 100:**

| Signal | Formula | Cap |
|---|---|---|
| `renewal_timing` | `100 if d ≤ 30 else 85 if d ≤ 60 else 65 if d ≤ 90 else 40 if d ≤ 120 else 20 if d ≤ 180 else 10 if d ≤ 270 else 0` | natural |
| `health_decline` | `max(0, 100 - health_score)` | natural |
| `sentiment_decline` | `max(0, 100 - sentiment_score)` | natural |
| `days_overdue_vs_cadence` | **v3 BUCKET MODEL** (closes data-eng NEW P0-1): let `o = max(0, days_since_touchpoint - expected_cadence_days[cadence_tier])`. Then signal = `100 if o ≥ 60 else 80 if o ≥ 30 else 60 if o ≥ 14 else 30 if o ≥ 7 else 0`. Suppressed (→ 0) during dead zones from `dashboard-dead-zones.md` (state-keyed). | 100 by construction |
| `open_escalations` | `min(100, open_escalations * 25)` | explicit min |
| `ticket_volume` | `min(100, open_tickets * 10)` | explicit min |
| `arr_percentile` | `100 * percentile_rank(arr, all_partner_arrs)` | natural |
| `top15_bonus` | `100 if top15.is_member else 0` | natural |
| `usage_decline` | **v3 CORRECTED** (closes data-eng NEW P0-2): `0 if usage_trend_30d_pct ≥ 0 else min(100, abs(usage_trend_30d_pct) * 2)`. (Growth → 0 contribution; -50% decline → 100 capped.) | explicit min |

**Composition:** `priority_score = round(sum(weights[k] * breakdown[k]) / 100, 2)`. Always 0–100 by construction now.

**Default weights:** copy §Step 1 `priority_weights`.

**Per-signal contribution percent (rendered at render time, never stored):**

```
contribution[k]% = (weights[k] * breakdown[k]) / (priority_score * 100) * 100
```

### Step 9 — `dashboard-schema-evolution.md`

`schema_version` evolution policy (unchanged from v2).

### Step 10 — `dashboard-dead-zones.md` (v3 NEW — closes PSM NEW P0-1)

**State-keyed dead-zone table.** During these date ranges (computed against `as_of` year), `days_overdue_vs_cadence` signal returns 0 regardless of actual days.

Universal (all states):
- **Late August onboarding period:** Aug 15 – Sep 7 (first-week-of-school is sacred).
- **Thanksgiving week:** Wed before Thanksgiving – Mon after.
- **Winter break:** Dec 22 – Jan 5.
- **Spring break — universal core week:** Mar 28 – Apr 4 (the most-common single overlap week).
- **End-of-year wrap:** Jun 15 – Jun 30.

State testing windows (per-state, populated from publicly documented assessment calendars — Codex synthesizes a reasonable table):
- TX (STAAR): Dec 5–18 (EOC fall), Apr 7–May 23 (spring).
- CA (CAASPP): Mar 1 – Jun 7.
- NY (Regents + State Tests): Jan 22–28, Apr 21 – May 3, Jun 12–25, Aug 11–14.
- FL (FAST): Sep 9–27, Jan 13–31, May 5–23.
- IL (IAR): Mar 17 – Apr 25.
- IL/MI/OH/PA/IN (default Spring window if state-specific unknown): Mar 15 – Apr 30.
- Default (state not enumerated): Mar 15 – Apr 30 (covers most spring state-testing windows).

(Codex MUST cite the NCES state-assessment-calendar reference URL where each window is sourced.)

### Step 11 — `.prettierignore` append

Append:

```
plugins/edtech-partner-success/bi-report/data.json
```

### Step 12 — `scripts/audit-gates.sh` (Gate 52, v3 — must-fail uses VALID UUIDv4)

```bash
echo "── Gate 52: PSM dashboard data integrity ─────────────────────────────"
rc=0; python3 scripts/check-psm-data-integrity.py >/dev/null 2>&1 || rc=$?
gate "psm-data-integrity (real tree)" must_pass "$rc"

# v3 must-fail: append a contact with a STRICTLY-VALID UUIDv4 that's NOT in
# partners[] — so check #1 (schema) passes, then check #2 (orphan refs) fires.
# v2's must-fail used "00000000-0000-0000-0000-deadbeefcafe" which fails check #1
# (4th group needs to start with 4 per UUIDv4) — audit theater. v3 picks a real
# UUIDv4 that isn't in the synthetic fixture.
DI_BAD="$TMP/data-orphan.json"
python3 - <<'PY' > "$DI_BAD"
import json
d = json.load(open("plugins/edtech-partner-success/bi-report/data.json"))
c = dict(d["contacts"][0])
c["contact_uid"] = "11111111-2222-4333-8444-555555555555"  # valid UUIDv4
c["account_uid"] = "deadbeef-cafe-4dad-8bad-baadc0debaad"  # valid UUIDv4, ORPHAN
d["contacts"].append(c)
print(json.dumps(d, indent=2))
PY
rc=0; python3 scripts/check-psm-data-integrity.py --data "$DI_BAD" >/dev/null 2>&1 || rc=$?
gate "psm-data-integrity (orphan account_uid detected via check #2)" must_fail "$rc"
```

### Step 13 — `.repo-layout.json` (verify only)

Run §6 below. Expected: "Layout OK".

---

## 5. Verification

| # | Command | Expected |
|---|---|---|
| 1 | `npx prettier --write . && npx prettier --check .` | exit 0 |
| 2 | `python3 -m json.tool` on each new JSON file | exit 0 |
| 3 | `python3 -m jsonschema -i data.json data.schema.json` | exit 0 |
| 4 | `python3 -m jsonschema -i data.json data.export.schema.json` | exit 0 (data.json validates against BOTH schemas) |
| 5 | `PYTHONHASHSEED=0 python3 synthesize.py --seed=42 > /tmp/gen.json && diff /tmp/gen.json data.json` | exit 0 |
| 6 | `python3 scripts/check-psm-data-integrity.py` | exit 0 (all 16 checks pass) |
| 7 | `python3 scripts/check-frontmatter.py plugins/edtech-partner-success/knowledge/` | exit 0 |
| 8 | `grep -E 'Riverside Unified\|Mesa Community College\|Granite State University\|Cedar Valley Schools\|Northshore Academy' plugins/edtech-partner-success/` | exit 1 (no match — renames complete) |
| 9 | `bash scripts/audit-gates.sh` | clean |
| 10 | Layout snippet from §6 | "Layout OK" |

---

## 6. Layout snippet

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

---

## 7. PR shape

```sh
git add plugins/edtech-partner-success/bi-report/data.schema.json \
        plugins/edtech-partner-success/bi-report/data.export.schema.json \
        plugins/edtech-partner-success/bi-report/field-classifications.json \
        plugins/edtech-partner-success/bi-report/data.json \
        plugins/edtech-partner-success/bi-report/synthesize.py \
        plugins/edtech-partner-success/knowledge/dashboard-identity-spine.md \
        plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md \
        plugins/edtech-partner-success/knowledge/dashboard-schema-evolution.md \
        plugins/edtech-partner-success/knowledge/dashboard-dead-zones.md \
        scripts/check-psm-data-integrity.py \
        scripts/audit-gates.sh \
        .prettierignore

git commit -m "feat(edtech-partner-success): PSM dashboard Tier 0 — schema + synthetic fixture + 16-check integrity gate"
git push -u origin feat/psm-dashboard-tier-0-foundation
```

Open as draft PR with `draft: true`.

---

## 8. Wall-handling

1. Re-read priors in §1.
2. If silent, take the documented default per `plan.md` Alternatives with inline comment.
3. If silent AND no default, `AskUserQuestion`. Tier 0 should NOT hit Q1–Q6.

---

## 9. What Codex MUST NOT do

- Add Tier 1+ work to this PR.
- Version-bump `plugin.json` / `marketplace.json`.
- Add CLAUDE.md milestone.
- Edit `report.html`.
- Re-author the four "do not re-author" priors from §1.
- Introduce a per-student field, ever.
- Use any real US district name from the integrity script's denylist (v3 whole-token matching enforced).
- Force-push, amend, or rewrite history.
- Mark PR ready-for-review without Matt's say-so.
- Change existing `data.json` top-level blocks (additive only).
- Drop any existing partner per-row key.
- Introduce a new health-component key beyond the existing 6.
- Use module-level `random`.
- Move `synthesize.py` to `data-platform/`.
- Introduce third-party Python deps.
- Use `https://`/`http://` or `:` or `//` past scheme in `doc_ref`/`source_ref`.
- Use v1/v2 example names (Cedar Falls Public Schools is REAL).
- Add `print(json.dumps(failing_row))` debug paths anywhere.
- Add per-entity prints to stderr/stdout in synthesize.py.
- **(v3 new)** Use `"g"/"y"/"r"` band shorthand — band stays `"green"/"yellow"/"red"` everywhere.
- **(v3 new)** Use `iii_eia` in funding_source (v2 typo); use `title_iii` + `idea_b`.
- **(v3 new)** Use v2's literal `enrollment` field; it's removed.
- **(v3 new)** Use substring matching in the real-district guard — use whole-token matching.
- **(v3 new)** Output raw values in PII-check assertion tracebacks; scrub to field path.
- **(v3 new)** Ship `bridge_account_xref` IDs without `synthetic-` prefix.
- **(v3 new)** Synthesize state-testing dead zones without citing the source.

End of v3 brief.
