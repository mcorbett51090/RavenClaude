# Build plan for Codex — Partner Success Command Center, Tier 0

**Audience:** A fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace that already has **RavenClaude installed** (per [`scripts/ravenclaude install`](../../../scripts/ravenclaude)). Codex is the engineer; this file is the engineer's brief.

**Scope:** Tier 0 of [`plan.md`](./plan.md) — the **JSON schema + synthetic fixture + two knowledge files**. Everything else (Tier 0.5 real connectors, Tier 1 daily-operating-system widgets) is a separate brief once this lands. This file is intentionally **narrow and concrete**, not a substitute for the strategic plan.

**Output:** one draft PR against `main`, named `feat/psm-dashboard-tier-0-foundation`, containing exactly the files this brief enumerates. Nothing more, nothing less. If a step has ambiguity Codex can't resolve from the priors below, **stop and ask Matt** (via `AskUserQuestion`) instead of inventing.

---

## 1. Pre-flight (5 min)

Before touching a single file, Codex MUST do all four of these. They take seconds individually and protect against the failure modes that ate hours of overnight session time on 2026-06-04 (file-state drift, draft-PR CI quirks, layout-allow-list misses, regen-on-manifest-change side effects).

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is the latest commit on main |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-0-foundation` | confirmed switched |
| 3 | Read the strategic plan | `cat docs/plans/2026-06-04-partner-success-command-center/plan.md` | full file, not just headers — Tier 0 acceptance and the schema enumeration live there |
| 4 | Read the source spec | `cat docs/research/2026-06-04-partner-success-dashboard-requirements/spec.md` | full file — this is the SME (Matt's wife) ground-truth |

**Read also (priors that constrain design choices — Codex MUST internalize these before writing code):**

- `plugins/edtech-partner-success/CLAUDE.md` — house rules 1, 4, 8, 12 (partner profile = SoT, cite the signal, rostering is silent killer, provenance on every claim).
- `plugins/edtech-partner-success/bi-report/data.json` — current shape; **Tier 0 extends, never replaces**.
- `plugins/edtech-partner-success/knowledge/partner-health-score-drift.md` — health-score decay model (don't re-author).
- `plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md` — cadence rules consumed by the priority score and the calendar countdowns (don't re-author).
- `plugins/edtech-partner-success/knowledge/partner-health-decline-which-play.md` — recommended_action source (don't re-author).
- `plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md` — identity spine pattern (Tier 0 references it; doesn't re-author it).

---

## 2. The deliverable — six files, one diff, zero scope creep

Codex creates / edits exactly these files. Anything else gets stopped at the layout-allow-list gate anyway.

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `plugins/edtech-partner-success/bi-report/data.schema.json` | **CREATE** | The authoritative JSON Schema for the Tier 0 dashboard contract. |
| 2 | `plugins/edtech-partner-success/bi-report/data.json` | **EDIT** (extend, do not replace) | Add the Tier 0 blocks (`partners[]`, `contacts[]`, `timeline_events[]`, `usage_daily[]`, `success_plans[]`, `contracts[]`, `tickets[]`, `calendar_events[]`, `priority_weights{}`, `org_uid`, `as_of`). KEEP the existing `report{}` / `bands{}` / `components[]` blocks. |
| 3 | `plugins/edtech-partner-success/bi-report/synthesize.py` | **CREATE** | Reproducible seeded synthetic-data generator. Produces a `data.json` that validates against `data.schema.json`. |
| 4 | `plugins/edtech-partner-success/knowledge/dashboard-identity-spine.md` | **CREATE** | Documents `bridge_account_xref` shape; references `cross-system-identity-resolution/SKILL.md` (does NOT re-author). |
| 5 | `plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md` | **CREATE** | Documents the 9-signal weighted rubric; references `partner-health-score-drift.md`. Defines `priority_weights{}` defaults. |
| 6 | `.repo-layout.json` | **EDIT** | Add globs for `plugins/edtech-partner-success/bi-report/**` (already covered) — confirm via the verification snippet in §6 — AND `plugins/edtech-partner-success/knowledge/**` (already covered). **If both already match, no edit needed.** |

**No other files.** No render changes, no `report.html` regen (that's Tier 1), no new agent, no version bump (the schema + fixture + knowledge are "knowledge addition" scoped — Tier 1 ships the version bump). No CLAUDE.md milestone yet.

---

## 3. Step-by-step build order

The order matters — each step's output is the next step's input. Codex MUST NOT skip ahead.

### Step 1 — `data.schema.json` (the contract)

JSON Schema draft 2020-12. **Required top-level fields:** `org_uid`, `as_of`, `report`, `bands`, `components`, `priority_weights`, `partners`, `contacts`, `timeline_events`, `usage_daily`, `success_plans`, `contracts`, `tickets`, `calendar_events`.

**Per-entity required fields** (from `plan.md` Tier 0 §"Define the JSON schema"):

- `partners[]`: `account_uid` (string, format=uuid OR salesforce-id-shape) · `name` · `segment` (enum from existing data.json — confirm by reading it first) · `state` (US state, 2-char) · `arr` (number, ≥0) · `contract_start` (date) · `contract_end` (date) · `renewal_date` (date) · `funding_source` (string) · `owner_psm` (string) · `sfdc_owner` (string) · `top15_status` (boolean) · `lifecycle_stage` (enum: `deployment` | `boi` | `moi` | `renewal`) · `stage_entered_at` (date-time) · `last_touchpoint_at` (date-time, nullable) · `next_required_touchpoint_at` (date-time, nullable) · `health_components` (object: `adoption`, `touchpoint`, `outcome`, `sentiment` — each number 0–100) · `health_score` (number 0–100) · `sentiment_score` (number 0–100) · `engagement_score` (number 0–100) · `priority_score` (number 0–100) · `priority_breakdown` (object: per-signal contribution percent) · `open_escalations` (integer ≥ 0) · `open_tickets` (integer ≥ 0) · `ticket_aging_days` (integer ≥ 0, nullable).

- `contacts[]`: `contact_uid` · `account_uid` · `name` · `title` · `role` (enum: `champion` | `exec_sponsor` | `superintendent` | `tech_lead` | `family_engagement` | `stakeholder`) · `influence_level` (enum: `high` | `medium` | `low`) · `sentiment` (enum: `green` | `yellow` | `red`) · `last_interaction_at` (date-time, nullable).

- `timeline_events[]`: `event_uid` · `account_uid` · `type` (enum exactly from `plan.md` — 12 values) · `ts` · `source` (enum: `salesforce` | `planhat` | `support` | `snowflake` | `calendar` | `manual`) · `summary` (string, ≤ 280 chars) · `source_ref_url` (string, format=uri, nullable).

- `usage_daily[]`: `{account_uid, date, active_users, active_teachers, active_admins, messages_sent, messages_received, family_invited, family_activated, family_engagement_rate, schools}` where `schools` is `[{school_id, school_name, active_users, usage_level}]`. All counts integer ≥ 0; rates number 0–1.

- `success_plans[]`: `{plan_uid, account_uid, goal, owner, due_date, progress_pct (0–100), status (enum: on_track | at_risk | complete | overdue)}`.

- `contracts[]`: `{contract_uid, account_uid, doc_url, start, end, arr, multi_year (bool), schools_included (int), licensed_users (int), products_purchased (string[]), pd_purchased_sessions (int), pd_completed_sessions (int)}`.

- `tickets[]`: `{ticket_uid, account_uid, opened_at, status (enum: open | in_progress | resolved | closed), severity (enum: p1 | p2 | p3 | p4), theme (string), age_days (int), is_escalation (bool)}`.

- `calendar_events[]`: `{event_uid, account_uid, type (enum: qbr | checkin | renewal_meeting | strategic | pd_session | success_plan_review | sentiment_update | health_check), scheduled_at, duration_min (int > 0), status (enum: scheduled | completed | missed)}`.

- `priority_weights` (object): all keys present, all values integer ≥ 0, sum to 100. Default values per `plan.md` S3.

**Cross-entity discipline (R3 in the risk matrix):**
- `additionalProperties: false` on every object — drift fails CI loudly.
- Every `account_uid` in non-`partners` arrays MUST reference a `partners[].account_uid` (this is a soft constraint — assert in `synthesize.py`, not enforceable in pure JSON Schema).
- Add a top-level `$id` field: `"$id": "https://ravenpower.net/schemas/psm-dashboard-data.schema.json#"`.

**Acceptance:** `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` exits 0 after Step 2 completes. Run it as the last action of Step 2, not before.

---

### Step 2 — `data.json` (extend the existing fixture)

**Read the current `data.json` first.** Identify the existing `report{}` / `bands{}` / `components[]` blocks — they STAY. Add the new top-level fields next to them.

**Synthetic content shape (Codex generates — see Step 3 for the seeded generator that's the canonical source):**

- `org_uid`: a fixed UUID string (e.g. `"00000000-0000-0000-0000-0000000000a1"`) — represents the wife's org in single-tenant mode (a `org_uid` field is the multi-tenant-readiness slack per A6).
- `as_of`: `"2026-06-04"` (today; matches the existing `report.refreshed`).
- `partners`: **exactly 25** synthetic partners spanning the health bands per `plan.md` Tier 0 Acceptance:
  - ≥ 5 green (`health_score ≥ 70`).
  - ≥ 5 yellow (50–69).
  - ≥ 3 red (< 50).
  - ≥ 2 in each renewal bucket: 180 / 120 / 90 / 60 / 30 days (so ten of the 25 are renewal-active, the rest scattered).
  - Mix of segments (don't hardcode 25× the same segment) — segments must match the existing `data.json` segments (read first to identify the enum).
  - ≥ 5 marked `top15_status: true`.
  - Each partner's `priority_score` is computable from `priority_breakdown` × `priority_weights` (the breakdown sums to 100; the score is the weighted sum).
- `contacts`: 3–6 per partner. Each partner has exactly one `role: "champion"` and one `role: "exec_sponsor"`. Other roles distributed.
- `timeline_events`: 8–20 per partner; mix of all 12 event types; at least 3 sources represented per partner (R3).
- `usage_daily`: last 90 days per partner — synthesize a daily walk with seasonality (lower on weekends, higher mid-week). Each row has `schools` populated for multi-school districts (mark 8 of the 25 as multi-school with 3–7 schools).
- `success_plans`: 1–3 per partner; status distribution: 60% on_track, 20% at_risk, 15% complete, 5% overdue.
- `contracts`: exactly 1 per partner (this is a single-tenant single-org demo; multi-contract per partner is Tier 0.5).
- `tickets`: 0–5 per partner; 70% closed, 20% open, 10% in_progress; severity p2 dominant; theme synthesized from a fixed enum (`adoption`, `data_quality`, `permissions`, `rostering`, `outage`, `feature_request`).
- `calendar_events`: 2–6 per partner; mix of all 8 types; statuses spread across scheduled / completed / missed.
- `priority_weights`: copy the defaults from `plan.md` S3. They MUST sum to 100.

**FERPA discipline (R1):**
- Synthetic partner names: use placeholders like `"Riverbend ISD"`, `"Hollow Creek Schools"`, `"Cedar Falls Public Schools"` — **never** real district names (Codex MUST NOT use Matt's wife's actual customers — the wife's customer list is NOT in the repo, but anti-pattern: any name that matches a real US district).
- Synthetic contact names: use fictional names (`"Riley Carter"`, `"Morgan Singh"`, etc.). **Never** real names.
- Synthetic student data: NONE. Aggregates only — `family_activated: 423` not `students: ["Alice", "Bob"]`. Codex MUST NOT introduce a per-student field.

**Acceptance:** the file validates against the schema (Step 1) AND the FERPA grep returns zero hits:

```sh
grep -rE '(SSN|student_name|child_name|first_name|last_name)' plugins/edtech-partner-success/bi-report/ ; echo "exit=$?"
# exit=1 means no match — good.
```

---

### Step 3 — `synthesize.py` (the reproducible generator)

**Purpose:** make Step 2's `data.json` reproducible. Same `--seed` → byte-identical output. Future contributors regenerate by `python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > plugins/edtech-partner-success/bi-report/data.json`.

**Shape:**

```python
#!/usr/bin/env python3
"""synthesize.py — reproducible synthetic-data generator for the PSM dashboard.

USAGE
  python3 plugins/edtech-partner-success/bi-report/synthesize.py [--seed N] [--partners N] [--out PATH]

By default writes to stdout (so the canonical fixture is regenerated by
`python3 ... > plugins/edtech-partner-success/bi-report/data.json`).
"""
# ... implementation ...
```

**Discipline:**

- `import random; rng = random.Random(args.seed)` — never use the module-level `random` directly.
- **No `time.time()` or `datetime.now()` for synthesizing fields** — pass `--as-of YYYY-MM-DD` (default `2026-06-04`) so the output is reproducible regardless of when the script is run.
- For float-bearing fields, round to a stable precision (e.g. 2 decimals) so byte-equality holds.
- For UUIDs, use `uuid.UUID(int=rng.getrandbits(128))` — seeded UUID generation, NOT `uuid.uuid4()`.
- `json.dumps(...)` with `indent=2, sort_keys=False, ensure_ascii=False` — match the existing `data.json` style. Verify by `head` of current file before deciding.
- Cross-entity integrity: assert at end-of-generation that every non-`partners` `account_uid` is in `partners[].account_uid` (mirror the soft schema constraint).
- Exit 1 if cross-entity check fails. Print which row violated.

**Acceptance:**

```sh
python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/run1.json
python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/run2.json
diff /tmp/run1.json /tmp/run2.json
# exit 0, no diff — reproducible.
```

AND:

```sh
python3 -m jsonschema -i /tmp/run1.json plugins/edtech-partner-success/bi-report/data.schema.json
# exit 0.
```

---

### Step 4 — `dashboard-identity-spine.md` (knowledge file)

Documents `bridge_account_xref` shape. **References `cross-system-identity-resolution/SKILL.md`; does NOT re-author it.**

**Required sections (skim the existing knowledge files for tone — terse, sourceable, decision-tree-aware):**

1. **What this is** — a knowledge file describing how the PSM dashboard joins Salesforce / Planhat / Support / Snowflake / Contract-system / Calendar into one conformed `account_uid` spine. **The implementation pattern lives in [`plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md`](../../data-platform/skills/cross-system-identity-resolution/SKILL.md);** this file is the dashboard-specific application.

2. **The `account_uid` choice** — Salesforce Account ID as the canonical key (per `plan.md` S2). Planhat's `externalId` is wired to this in `planhat-integration.md`.

3. **`bridge_account_xref` shape** — exactly the table from `plan.md` Tier 0:

   ```
   account_uid (PK) | salesforce_id | planhat_id | support_tool_id | snowflake_partner_key | match_method (enum) | confidence (0-1) | last_verified_at (datetime)
   ```

4. **Match methods + confidence tiers** — `match_method` enum: `salesforce_account_id_direct` (confidence 1.0), `planhat_external_id` (1.0), `domain_match` (0.9), `name_normalized` (0.7), `manual_override` (1.0). Anything < 0.9 carries the dashboard banner: "identity-resolution uncertain — verify before acting" (R3).

5. **Anti-patterns** — email domain as primary key (M&A drift), name-similarity (false positives), per-source IDs only (no cross-system joins).

6. **References** — link to the SKILL, link to `planhat-integration.md`'s externalId convention.

**Acceptance:** `python3 scripts/check-frontmatter.py plugins/edtech-partner-success/knowledge/dashboard-identity-spine.md` exits 0 (frontmatter discipline — every knowledge file). Score ≥ 4/6 by `agent-quality-rubric` mental rubric.

---

### Step 5 — `dashboard-priority-score-rubric.md` (knowledge file)

Documents the 9-signal weighted rubric.

**Required sections:**

1. **What this is** — the rubric that turns 9 partner signals into a single 0–100 priority score driving the Daily Action Center sort order. **Inputs:** renewal_timing, health_decline, sentiment_decline, days_since_touchpoint, open_escalations, ticket_volume, arr, top15_bonus, usage_decline.

2. **Each signal's measurement formula** (concrete, computable from `data.json`):

   - `renewal_timing` — `max(0, 100 - days_to_renewal)` where `days_to_renewal = (contract.end - today).days`. Score caps at 100 for ≤ 0-day; floor at 0 for > 180-day.
   - `health_decline` — `max(0, 100 - health_score)`. A green partner contributes 0; a red one 50+.
   - `sentiment_decline` — `max(0, 100 - sentiment_score)`. Same shape.
   - `days_since_touchpoint` — `min(100, (today - last_touchpoint_at).days)`. Caps at 100 days.
   - `open_escalations` — `min(100, open_escalations * 25)`. 4+ escalations → 100.
   - `ticket_volume` — `min(100, open_tickets * 10)`. 10+ open tickets → 100.
   - `arr` — `min(100, arr / 5000)`. $500k ARR → 100. **Inverted intent: high ARR EARNS attention, not loses it.**
   - `top15_bonus` — `100 if top15_status else 0`.
   - `usage_decline` — `max(0, 100 - usage_trend_30d_pct)` where `usage_trend_30d_pct` is the percent change in `active_users` over the trailing 30 days. A flat trend → 100 contribution; growing → lower.

3. **Default weights** (sum to 100) — copy from `plan.md` S3.

4. **The per-signal contribution rendering** (Rule 4 — cite the signal) — every Daily Action Center row carries inline percent contributions: e.g. *"renewal_timing 32% · health_decline 28% · days_since_touchpoint 15%"*. The implementation is in Tier 1; this rubric file documents the CONTRACT.

5. **Tuning protocol** — the wife edits `priority_weights{}` directly in `data.json`. Weights MUST sum to 100; the dashboard refuses to render with bad totals.

6. **References** — `partner-health-score-drift.md` (signal decay), `k12-psm-operating-cadence.md` (cadence rules), `partner-health-decline-which-play.md` (next-action mapping).

**Acceptance:** frontmatter passes the check; readable by a non-technical PSM (the wife is the reviewer).

---

### Step 6 — `.repo-layout.json` (verify only, edit if needed)

Run the verification snippet from `AGENTS.md`:

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

**Expected: "Layout OK"** — both `bi-report/**` and `knowledge/**` are already covered. If violations: extend `allowed_globs` with the missing pattern, NOT each file individually.

---

## 4. Verification — what Codex runs before pushing

In order. ALL must pass before `git push`. **Run them in parallel where independent (steps 1–4 are independent):**

| # | Command | Expected | Why |
|---|---|---|---|
| 1 | `npx --yes prettier --write . --log-level warn && npx --yes prettier --check . --log-level warn` | exit 0 | Whole-tree prettier — even if the diff is markdown-only, a previously-merged unrelated file can fail this. |
| 2 | `python3 -m json.tool plugins/edtech-partner-success/bi-report/data.json > /dev/null` | exit 0 | JSON syntax. |
| 3 | `python3 -m json.tool plugins/edtech-partner-success/bi-report/data.schema.json > /dev/null` | exit 0 | Schema syntax. |
| 4 | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 | The contract holds. |
| 5 | `python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/gen.json && diff /tmp/gen.json plugins/edtech-partner-success/bi-report/data.json` | exit 0 | The committed `data.json` IS the seeded output. |
| 6 | `grep -rEi '(ssn\|social.security\|student[_ ]name\|child[_ ]name\|first.name\|last.name)' plugins/edtech-partner-success/bi-report/ ; echo "exit=$?"` | exit=1 (no match) | FERPA discipline (R1). |
| 7 | `python3 scripts/check-frontmatter.py plugins/edtech-partner-success/knowledge/` | exit 0 | Knowledge files have correct frontmatter. |
| 8 | `bash scripts/audit-gates.sh` | clean | Full CI audit. **Exception:** Gate 47 `validate-schemas` may fail locally if `python3 -m jsonschema` module is missing in the local env — confirm by running it standalone; if it's an env gap, document in the PR body. |
| 9 | The layout-allow-list snippet from §3 Step 6 | "Layout OK" | The Discipline Lesson from AGENTS.md. |

---

## 5. PR shape — exact format

Once verification passes:

```sh
git add plugins/edtech-partner-success/bi-report/data.schema.json
git add plugins/edtech-partner-success/bi-report/data.json
git add plugins/edtech-partner-success/bi-report/synthesize.py
git add plugins/edtech-partner-success/knowledge/dashboard-identity-spine.md
git add plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md
# .repo-layout.json only if Step 6 surfaced a violation

git commit -m "$(cat <<'EOF'
feat(edtech-partner-success): PSM dashboard Tier 0 — schema + synthetic fixture + spine

Tier 0 of docs/plans/2026-06-04-partner-success-command-center/plan.md —
the JSON shape contract every later tier reads against, plus the seeded
synthetic generator that produces the canonical 25-partner fixture, plus
two knowledge files (identity spine + priority-score rubric).

What ships:
- bi-report/data.schema.json — authoritative JSON Schema (draft 2020-12)
  for the 11-block dashboard contract (partners + contacts + timeline +
  usage_daily + success_plans + contracts + tickets + calendar_events +
  priority_weights + org_uid + as_of).
- bi-report/data.json — extended to validate against the schema. The
  existing report{} / bands{} / components[] blocks are preserved.
- bi-report/synthesize.py — seeded reproducible generator. The committed
  data.json IS the output of `synthesize.py --seed=42`.
- knowledge/dashboard-identity-spine.md — documents the bridge_account_xref
  shape + match-method confidence tiers. References (does NOT re-author)
  data-platform/skills/cross-system-identity-resolution/SKILL.md.
- knowledge/dashboard-priority-score-rubric.md — the 9-signal weighted
  rubric driving the Daily Action Center sort. Per-signal formula +
  default weights + the "weights sum to 100 or refuse to render" contract.

What this PR deliberately does NOT do:
- No render changes (report.html unchanged) — Tier 1 ships the widgets.
- No real connectors — Tier 0.5 ships those.
- No version bump or CLAUDE.md milestone — wait until Tier 1 lands so the
  user-visible change is what gets versioned.
- No new agent.

FERPA discipline (R1):
- Synthetic partner names are fictional (Riverbend ISD, Hollow Creek
  Schools, ...) — no real US district name appears.
- No per-student field anywhere; aggregates only.
- grep for SSN / student_name / child_name returns zero hits.

Verification this session:
- python3 -m jsonschema -i data.json data.schema.json → exit 0
- synthesize.py --seed=42 → byte-identical to committed data.json
- npx prettier --check . → exit 0
- bash scripts/audit-gates.sh → clean (modulo local-env jsonschema gap;
  CI has the module)
- Layout allow-list → clean

Plan: docs/plans/2026-06-04-partner-success-command-center/plan.md Tier 0
Build brief: docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md

Migration: none. Tier 0 is foundation — no consumer-visible change.

https://claude.ai/code
EOF
)"

git push -u origin feat/psm-dashboard-tier-0-foundation
```

**Open as a draft PR** via `mcp__github__create_pull_request` with `draft: true`. PR body mirrors the commit message (above) trimmed to the bulleted summary + the test plan checklist:

```markdown
## Test plan
- [ ] CI green (validate-marketplace / validate-layout / validate-schemas).
- [ ] Matt's wife eyeballs the synthetic data.json — fictional names? 25 partners? Bands distributed?
- [ ] Sanity: the per-signal contributions on three highest-priority partners make narrative sense.
```

---

## 6. What to do if Codex hits a wall

The wall pattern Codex MUST follow (NOT "ask Matt immediately"; NOT "guess and move on"):

1. **Re-read the relevant prior** in §1's read-list. The constraint is almost always already documented.
2. **If the prior is silent** but a reasonable default exists per the strategic `plan.md` Alternatives table, take the default and note the choice inline in the file as a code comment: `# Default per plan.md A4: config-driven priority_weights`.
3. **If the prior is silent AND no default exists**, the question is genuinely "needs Matt." Stop, summarize the question + the two best answers + the consequence of each, ask via `AskUserQuestion`.
4. **Wall types where step 3 is mandatory** (per the strategic plan's Settling Steps Q1–Q6):
   - Support tool identity (Q1)
   - Contract system-of-record (Q2)
   - Calendar tool (Q3)
   - Top 15 list source (Q4)
   - PSM-owned scoping (Q5)
   - Sentiment source (Q6)

For Tier 0, none of Q1–Q6 are blocking — Tier 0 is synthetic data + contract + knowledge. Q1–Q3 block **Tier 0.5**, not Tier 0. So Codex should reach step 4 only if a *new* ambiguity surfaces.

---

## 7. After Tier 0 ships

Once the PR is merged (Matt's call, not Codex's), the next two parallel briefs are:

- **Tier 0.5** — real connectors → Snowflake → `data.json` export. Authored separately because it depends on Settling Steps Q1–Q3 (the wife's actual support / contract / calendar tool).
- **Tier 1** — Portfolio Summary + Daily Action Center + Calendar countdowns + Health Snapshot widgets. Authored separately because it's the rendering work.

Both are independent of each other (Tier 1 ships against the synthetic fixture; Tier 0.5 lands separately and the dashboard transparently swaps to real data when the fixture is replaced).

---

## 8. What Codex MUST NOT do

- **Do not** add Tier 1 / 2 / 3 / 4 / 5 work to this PR. The strategic plan is tiered for a reason; mixing tiers in a single PR makes review impossible.
- **Do not** version-bump `plugin.json` / `marketplace.json`. Wait for Tier 1.
- **Do not** add a CLAUDE.md milestone. Wait for Tier 1.
- **Do not** edit `report.html`. Wait for Tier 1.
- **Do not** re-author content that already lives elsewhere (the four "do not re-author" files in §1's read list).
- **Do not** introduce a per-student field, ever, for any reason. FERPA hard rule.
- **Do not** use real US district names. Even if a "synthetic-looking" name happens to be real.
- **Do not** force-push, amend, or otherwise rewrite history on a pushed branch. New commits only.
- **Do not** mark the PR ready-for-review without Matt's say-so. Draft only.

End of brief.
