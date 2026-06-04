# Codex priors addendum — 2026-06-04

> Read this **after** `build-plan-for-codex.md` and `plan.md`, **before** opening any file in `plugins/edtech-partner-success/`. This addendum exists because the build plans were finalized 2026-06-04 morning, and several Tier 0.5 reference implementations + 2026 H1 research-derived knowledge files landed later the same day (PR #274). The base plans don't link to them; this doc does.

## What this addendum changes vs the base build plan

**Nothing in the base plan's gating logic changes.** All the v3 issue closures, MUST-NOTs, integrity gates, FERPA boundary rules, and tier-scope statements remain authoritative. This addendum only adds **pre-existing priors Codex can lean on** — reference SQL, reference dbt models, additional knowledge files — so Codex doesn't have to invent what's already there.

If anything in this addendum appears to contradict the base build plan, **the base plan wins**. Surface the conflict in the PR body and escalate.

---

## 1. Tier 0.5 reference implementations (NEW — landed PR #274)

**Location:** `plugins/edtech-partner-success/templates/dashboard-tier-0.5-reference/`

These are **reference-only** (not auto-executed; not part of any plugin install). Codex consumes them as priors when implementing Tier 0.5 of the build plan. Copy + adapt; don't blind-paste.

| File | What it provides | How to use |
|---|---|---|
| `README.md` | Top-level orientation: what this dir is and is NOT | Read first |
| `snowflake-database-ddl.sql` | Two databases (`PSM_RAW` + `PSM_CONFORMED`) + four XS Standard warehouses (auto-suspend 60s) + five roles | Copy DDL, adapt names to consumer account |
| `dbt-project.yml` | dbt config: view → ephemeral → dynamic_table layering, MetricFlow enabled, `target_lag: "15 minutes"` on marts, snapshot strategy `timestamp` | Base dbt project structure |
| `dbt-models-sources.yml` | Sources for `salesforce` (T1), `planhat` (T2), `google_calendar` (T2), `usage_share` (T3) — with FERPA notes inline | Adapt to consumer's actual connector setup |
| `dbt-models-staging.sql` | 7 split-marked staging models — Snowflake-flavored (`IFF`, `QUALIFY ROW_NUMBER()`, `DATEDIFF`) | Stg layer reference |
| `dbt-models-bridge-account-xref.sql` | Dynamic Table UNIONing the 7-tier Splink confidence ladder (T0 LEAID exact → T6 unresolved) | Identity resolution spine |
| `dbt-models-marts-partners.sql` | Conformed `dim_partner` matching Tier 0's `partners[]` shape exactly. **Triple-defended: nulls `priority_score` / `priority_breakdown` / `engagement_score`** per `derived_at_render` | Conformed dim layer |
| `dbt-models-marts-timeline-events.sql` | Cross-source event union (SF cases + Planhat NPS + Calendar) with opaque URI scheme on `source_ref`, FERPA filter on `type='user'` | Timeline mart |
| `dbt-models-marts-usage-daily.sql` | District-level rollups from inbound Snowflake zero-copy share. NULLIF on divisor to avoid DIV/0 | Usage fact |
| `dbt-models-marts-priority-score.sql` | **Audit-only mart** — reads weights from `PRIORITY_WEIGHTS` config (single SoT); export script must null these fields | Reference for weight reconciliation |
| `dbt-tests.yml` | Generic + UUIDv4 regex + opaque-URI regex + relationships + sum-to-100 on `priority_weights` + phase × substage allowed-pair | Test scaffold |
| `export-psm-dashboard.py` | Stdlib + `snowflake-connector-python` + (gated) `jsonschema`. CLI `--out --as-of --org-uid [--allow-real-ids] [--validate]`. Atomic write + per-source degradation + **always nulls 3 `derived_at_render` fields** | Export tool |
| `dynamic-tables-and-tasks.sql` | DT cascade: `bridge_account_xref` + `usage_daily` at 15-min lag (roots); marts at `DOWNSTREAM`; `mart_connector_health` at 5-min; hourly safety-net + observability view | Refresh layer |
| `tier-0.5-acceptance-tests.md` | 8-step end-to-end DoD smoke test with per-step wall-handling | Acceptance criteria |

**Cross-cutting discipline preserved:**
- Snowflake-only SQL — zero Postgres-isms.
- FERPA annotated inline on email (domain-only mask), NPS verbatim (dropped at staging), calendar summary (`--ferpa-strip-user-content` toggle), and `type='user'` filter at the timeline mart.
- `priority_score` / `priority_breakdown` nulled in the export in **three places** — triple-defense against the renderer's `derived_at_render` classification leaking.
- No third-party deps beyond `snowflake-connector-python` and (gated) `jsonschema`. dbt tests use `dbt_utils` only.

---

## 1a. Tier 1 dashboard reference implementations (NEW — landed PR #274)

**Location:** `plugins/edtech-partner-success/templates/dashboard-evidence-reference/`

Reference-only support files for the Tier 1 daily-operating-system render layer. Codex consumes these when implementing Tier 1.

| File | What it provides |
|---|---|
| `README.md` | Top-level orientation for the Tier 1 render layer |
| `dashboard-styles.css` | CSS-variable color tokens (deuteranopia/protanopia-safe), secondary-channel utility classes (`.status-icon--circle/--triangle/--square` per WCAG 1.4.1), `.freshness-chip--live/--stale/--paused`, `.empty-state` surface, `.drawer` panel, `.bandline` sparkline, `prefers-reduced-motion` overrides, dark-scheme block — every selector carries an inline `WCAG:` / `UX:` provenance comment |
| `dashboard-deployment-notes.md` | Three-tier hosting guide: (T1) Evidence.dev → Cloudflare Pages with hourly-cron GHA workflow; (T2) Streamlit-in-Snowflake with stage + warehouse + STREAMLIT SQL + **owner-rights-vs-caller-rights governance warning**; (T5) React + Tremor + Cube on Vercel with JWT-`tenant_id` + Cube `securityContext` + `queryRewrite` pattern. Side-by-side cost/complexity/governance comparison |
| `dashboard-acceptance-tests.md` | Eight binary acceptance tests for the PSM SME: 5-second test, 8-spec-questions ≤2 clicks, three-flavor honest empty states, drill-down URL+back+breadcrumbs, WCAG (deuteranopia + protanopia + axe-core), freshness + manual-refresh, 5-day ≤5% false-positive alarm-fatigue, timezone-clarity |
| `dashboard-feature-flag-tier-1.md` | Per-widget feature-flag pattern. T1: `evidence.config.yaml` `features:` block; T2: matching `feature_flags.toml` for Streamlit (same flag names = one source of truth). Evidence Markdown `{#if features.x}` guards and Streamlit `if flags.get("x", False)` guards both demonstrated. Rollback procedure per tier + four-wave staged rollout mapping the ~20 spec sections to flags |
| `pages/` | Subdirectory for Evidence.dev page-level reference |

**Codex usage rule:** when implementing Tier 1, adapt this CSS + the deployment notes + the acceptance test surface. The owner-rights-vs-caller-rights warning in `dashboard-deployment-notes.md` is load-bearing for partner-facing multi-tenant — do NOT ignore.

---

## 2. 2026 H1 knowledge refresh — FERPA + state privacy law

**Location:** `plugins/edtech-partner-success/knowledge/`

Two new + four edited files. Codex consumes these as the **enforcement-aware** layer over the build plan's FERPA decision tree.

### NEW: `edtech-enforcement-precedents-2025-2026.md`
- Six-theory taxonomy: Illuminate $5.1M multistate AG (Nov 2025) / PowerSchool Dec 2024 breach / PowerSchool Naviance $17.25M wiretapping (Feb 2026 preliminary) / CDE FERPA finding (Jan 28 2026) / Edmodo + IXL amicus / CAADCA NetChoice.
- **Mapping decision tree** — Mermaid diagram from "vendor incident" to "which theory."
- PSM playbook per theory.

### NEW: `coppa-2025-amendment-edtech-implications.md`
- **Apr 22 2026 full compliance deadline has passed.**
- Four new STOP-needs-counsel leaves: biometric collection from <13, government-ID collection from <13, K-5 product without written cybersecurity program, third-party data flow for non-educational purpose without separate VPC.
- 10-point operational checklist for K-5 vendor evaluation.

### EDITED: `ferpa-aggregate-threshold-defaults.md`
- New §7a — 2026 enforcement context note. The threshold *what* hasn't changed; the threshold *who-enforces* has.

### EDITED: `ferpa-dashboard-boundaries.md`
- New §11a — Naviance-pattern silent-monitoring anti-pattern (no-breach wiretapping theory).
- New §11b — 2026 enforcement context table.

### EDITED: `state-privacy-law-matrix.md`
- CT watch-list note (first enforcement under CT student-data law via Illuminate).
- VA / CT / TX / MD / TN refreshed.
- §6a — 2026 enforcement scoreboard.

### EDITED: `ai-training-prohibition-clauses.md`
- §7 — biometric-identifier overlay (post-COPPA amendment).
- §8 — federal AI EO + COPPA Apr 2026 enforcement window.

---

## 3. 2026 H1 knowledge refresh — K-12 PSM

**Location:** `plugins/edtech-partner-success/knowledge/`

Four new + four edited files. Codex consumes these as the **2026-aware** K-12 operational signal layer.

### NEW: `essa-evidence-tier-as-renewal-asset.md`
- ESSA evidence tiering (Strong / Moderate / Promising / Demonstrates a Rationale) has crossed from vendor marketing to **district renewal rubric** in 2025-2026.
- Where to look up: IES What Works Clearinghouse, Evidence for ESSA, vendor pages.
- 90/60/30 positioning + worked example (Lexia Core5).

### NEW: `pe-ownership-effect-on-renewal-posture.md`
- PowerSchool (Bain $5.6B), Instructure (KKR $4.8B), Renaissance (H&F ~$1.1B), Imagine Learning (active roll-up) all PE-owned by 2026.
- PE underwriting model implications (NRR >110%, discount latitude, multi-year preference).
- 6-12 month integration window for acquired products.

### NEW: `cbt-readiness-checkpoint-spring.md`
- **NY mandates CBT for grades 3-8 ELA + Math + Science spring 2026** — first full window.
- March-cadence checkpoint (device + bandwidth + rostering + SSO + vendor-side readiness).
- Incident-response framing if a CBT-window failure happens.

### NEW: `ai-teammate-adoption-psm-self.md`
- ChurnZero AI Marketplace + Gainsight AI agents context.
- What AI teammates DO / NOT do for a PSM.
- How to talk about AI-teammate adoption with an AI-cautious K-12 district.

### EDITED: `k12-signal-taxonomy.md`
- §11a — 2026 refresh adding 7 new signal classes (district AI-guidelines maturity, vendor ESSA tier, vendor PE-ownership, NY CBT readiness, Common Sense badge, AI teammate adoption, internal-vs-external sup hire).

### EDITED: `k12-superintendent-turnover-as-renewal-event.md`
- §6a — Internal-vs-external two-mode trigger (58/42 split per ILO 2024-25): internal = 30-60d grace; external = 90-180d portfolio review.

### EDITED: `k12-spend-utilization-43pct.md`
- §6a — Disambiguating 43% utilization waste vs 27% unused licenses (different denominators).
- 2026 procurement-maturity context (86%/65%/61% vetting cadence).

### EDITED: `k12-renewal-motion-90-60-30.md`
- §5a — Tool-rationalization overlay (71% cost-driven keep/cut), Garland HS displacement pattern, NY CBT-readiness, PE-vendor caveat.

---

## 4. 2026 H1 knowledge refresh — Codex / coding-agent

**Location:** `plugins/ravenclaude-core/skills/` and `docs/best-practices/`

### NEW: `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md`
- Cross-tool onboarding for Copilot CLI ≥1.0.59 + Cursor ≥3.3 + Aider + Devin.
- First-five-minutes checklist (AGENTS.md → .repo-layout.json → plugin CLAUDE.md → relevant skills → tool version floor).
- Before-edit-batch + before-PR-open mechanical mitigations.

### NEW: `docs/best-practices/2026-q1-q2-failure-modes.md`
- Three dominant H1 2026 failure clusters (eval gaps / tool-call chaos / governance theatre).
- Six agent-specific failure modes (tool misuse / context loss / goal drift / retry loops / cascading errors / silent quality degradation).
- Memory wall five sub-failures (context overflow / instruction dilution / error accumulation / state loss / evaluation blindness).
- Tool-version floors that prevent regression-class failures.

### EDITED: `plugins/ravenclaude-core/skills/diff-budget/SKILL.md`
- New section — 2026 Q1-Q2 fill-% gating (40%/60%/80% triggers).
- Mutating-tool-call hygiene (per-call timeout + idempotency key + bounded retries + structured error).

---

## 5. 2026 H1 knowledge refresh — data-platform rendering

**Location:** `plugins/data-platform/knowledge/`

Two new files. Codex consumes these when implementing Tier 1+ rendering layer choices.

### NEW: `dashboard-productization-multi-tenant-2026.md`
- Build-vs-buy decision rule.
- Tenancy patterns cheapest → most isolated (Parquet+DuckDB-WASM → pooled+RLS → schema-per-tenant → DB-per-tenant → Hypertenancy).
- **SiS owner's-rights trap** (CURRENT_ROLE returns app owner — silent FERPA breach risk).
- Cost-stacking awareness (license + warehouse compute).

### NEW: `charting-library-selection-2026.md`
- Decision rule + maintained-status table (Recharts / Tremor v4-beta / ECharts / Visx / Nivo / Plotly / Chart.js).
- SVG-vs-Canvas threshold (5K nodes).
- INP-aware bundle sizing.
- Tremor Vercel acquisition status.

---

## 6. How Codex should consume this addendum

1. **Read this whole addendum first**, before touching any plugin file.
2. **Read the base build plans** (`build-plan-for-codex.md` + `plan.md`).
3. When implementing Tier 0.5: **lean heavily on the reference implementations** in §1. Don't reinvent the dbt model layer or the Snowflake DDL — adapt these.
4. When making FERPA/state-privacy calls: **consult §2 + the existing decision tree**. The enforcement context from 2025-2026 changes the *who-enforces*, not the *what*.
5. When evaluating K-12 vendors or designing renewal motions: **consult §3** for the 2026-aware signal interpretation.
6. When operating as Codex/Copilot CLI: **invoke the codex-onboarding skill** (§4) at session start; honor the diff-budget fill-% gating.
7. When choosing a rendering layer (Tier 1+): **consult §5** before committing to Sigma/Looker/SiS/etc.

---

## 7. What this addendum does NOT do

- Does NOT replace `build-plan-for-codex.md`.
- Does NOT introduce new MUST-NOTs (those stay in the base plan).
- Does NOT change the Tier 0 scope (Tier 0 stays fixture + schema + integrity gate + knowledge files — no rendering, no real connectors).
- Does NOT pre-authorize Codex to skip any verification gate.

## 8. Source ledger

- PR #266 (merged) — base build plan + adversarial gap-fill.
- PR #274 — Tier 0.5 reference implementations + 2026 H1 knowledge refresh.
- `/tmp/research-ferpa-2026-updates.md` — 30+ sources on FERPA enforcement 2025-2026.
- `/tmp/research-k12-2026-updates.md` — 75 sources on K-12 EdTech 2026.
- `/tmp/research-codex-2026-updates.md` — 49 sources on coding-agent H1 2026.
- `/tmp/research-rendering-multi-tenant-2026.md` — 78 sources on rendering / multi-tenant.

`[verify-at-use — 2026-06-04 — all dates and amounts per deep-research scans this date]`
