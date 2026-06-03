# Unified Customer-Success Analytics Platform — Build Plan

> **How this plan was produced.** Two independent expert panels (six seats each) designed
> this platform from the same brief on **two different models** — Panel A on Opus, Panel B
> on Sonnet — with no knowledge of each other. A gap analysis diffed the two; a separate
> independent senior architect (a third pass, on a fresh model) broke the four genuine ties
> and flagged what both panels missed. This document is the merged, gap-filled result.
>
> **Audience:** a technical-ish solo builder using OpenAI Codex as her coding agent, in a
> greenfield repo, at a small company. It is written to be dropped into that repo and handed
> to Codex phase by phase.
>
> **Status:** plan / proposal. Five open questions at the end gate Phase 0 — answer those first.

---

## 0. The goal in one paragraph

Pull data from six systems — **Salesforce** (CRM), **Planhat** (Customer Success), **Slack**,
**Intercom** (support), **Snowflake** (the warehouse, already owned), and **Sigma** (the BI
tool, already owned, runs on Snowflake) — and bring it together so a Customer Success leader
can answer **"which accounts are at risk and who do I call today?"** in under two minutes. The
first delivered view is **CS health** (account health, churn risk, renewals). Exec KPIs and
support-ops views come later, reusing the same data model.

---

## 1. The decisions, and how confident we are in each

| # | Decision | Verdict | Confidence | Source |
|---|----------|---------|-----------|--------|
| **B** | **Data architecture** | **Snowflake-as-hub.** Land all six sources in Snowflake; model with dbt (RAW → STAGING → MARTS); serve everything from Snowflake. No live per-source API calls at query time. | **Settled** | Both panels unanimous |
| **A** | **Output / BI surface** | **Sigma is the primary BI surface. Tableau rejected** as a redundant second BI stack (they already own Sigma-on-Snowflake; a second tool = a second semantic layer + metric drift). | **Settled** | Both panels agreed |
| **A′** | **Custom React app** | **Conditional, not scheduled.** Stay Sigma-only until explicit triggers fire (see §3, Conflict 2). | Tie-broken → A | Tie-breaker |
| **C** | **Ingestion (Salesforce, Intercom)** | **Buy** managed connectors (Fivetran or Airbyte Cloud). Best-in-class, incremental, schema-drift-aware. | **Settled** | Both panels agreed |
| **C** | **Ingestion (Planhat)** | **Build** a small Codex-authored Python loader — Planhat is niche, no production connector exists. The one connector worth building. | **Settled** | Both panels agreed |
| **C′** | **Ingestion (Slack)** | **Build** a derived-signal extractor that lands **only computed signals, never raw message bodies.** | Tie-broken → B | Tie-breaker |
| — | **Health score** | **Surface Planhat's native score as the anchor in Phase 1**; show Intercom/Slack signals as separate visible sub-indicators. Defer a custom composite. | Tie-broken → B (+A as additive) | Tie-breaker |
| — | **Orchestration** | **Lightweight** — GitHub Actions cron + Snowflake tasks/Snowpipe + dbt. **No Airflow/Prefect** in Phase 0/1. | Tie-broken → A | Tie-breaker |
| — | **Master key** | **Salesforce Account ID** is the master key; everything resolves to it. | **Settled** | Both panels agreed |
| — | **Health scoring method** | **Rule-based, transparent tier (Green/Yellow/Red) in Phase 1. No ML.** Every Red shows *why*. | **Settled** | Both panels agreed |

**Snowflake/Sigma need no ingestion** — Snowflake is the destination, Sigma reads it live.

---

## 2. The four tie-breaks, with reasoning (the contested calls)

These were the genuine conflicts between the two panels. An independent third architect ruled
on each.

### Conflict 1 — Slack: buy a connector vs. build a no-raw-messages extractor → **BUILD (Panel B wins)**
The PII blast radius of dumping raw Slack channel messages into Snowflake is enormous and
permanent — every analyst, every Sigma viewer, every future connector inherits that exposure,
and "mask it downstream" means the sensitive text already lives in RAW and must be governed
forever. For CS health, the *valuable* Slack signal is almost entirely derived (volume trend,
escalation-keyword hits, mention counts, coarse sentiment); the literal message text adds little
to a churn tier. The build cost is bounded and squarely in Codex's wheelhouse.
**Implementation:** an idempotent per-channel extractor pages `conversations.history`, computes
metrics in-memory, and writes only `(account_id, channel, date, msg_count, escalation_hits,
mention_count, sentiment_score)` to a RAW Slack table — never the message text.

### Conflict 2 — React app: deferred vs. committed Phase 2 → **CONDITIONAL (Panel A wins)**
Committing weeks of a solo+Codex builder's time to a bespoke app before anyone has proven they
*act* on the dashboard is the classic over-build — it doubles the surface area (auth, hosting,
write-back error handling, a UI to maintain). Sigma may already serve several "inline action"
cases via input tables / write-back [unverified — confirm Sigma's current write-back feature set].
Ship Sigma, watch how CS actually works, let the unmet needs declare themselves.
**Build the React app when ANY TWO of these hold:**
1. A recurring write-back action is demanded that Sigma's native input-tables/actions genuinely cannot serve.
2. Users repeatedly context-switch out of Sigma into Planhat/Salesforce to act, and the round-trip is measurably costing adoption.
3. An action needs logic Sigma can't express (multi-step, conditional, or transactional write across systems).
4. Health-flag overrides need an auditable human-in-the-loop workflow with state.

Until then: a one-line backlog entry, not a dated phase. Instrument Sigma usage so the triggers are observable.

### Conflict 3 — Health score: own composite now vs. Planhat-native as-is → **PLANHAT-NATIVE anchor + additive signals (Panel B wins, A survives as complement)**
Trust and adoption are the whole game in Phase 1. The CS team already anchors on Planhat's
score; replacing it on day one with a hand-rolled composite invites "why doesn't this match
Planhat?" arguments that torpedo credibility before the platform earns any. Pulling Planhat's
score is near-zero effort. Panel A's real concern — Planhat's score can't see Intercom support
load or Slack escalation — is answered by **additive transparency, not silent recomputation**:
show Planhat's native score as the anchor, and surface the extra signals *alongside* it as their
own visible sub-indicators. That captures the blend's value without asking anyone to trust a
black-box-replacing-a-black-box, and it builds the evidence base for whether a custom composite
is ever warranted.
**Implementation:** in MARTS, expose `planhat_health_score` as the primary tier alongside
discrete, individually-visible `intercom_support_load` and `slack_escalation_signal` columns;
defer any weighted composite until those sub-signals demonstrably diverge from Planhat's tier.

### Conflict 4 — Orchestration: lightweight vs. Airflow/Prefect → **LIGHTWEIGHT (Panel A wins)**
Standing up Airflow for a solo operator is textbook over-engineering — you'd spend more time
operating the orchestrator than running the 3–4 pipelines it schedules. The DAG here is trivially
shallow (land raw → run dbt → done), and dbt already owns model-level dependency ordering. You
need a *trigger* and a *log*, not a DAG engine. Reach for Prefect (lighter than Airflow) only
when you have genuine cross-system dependencies, retries-with-backoff, and dynamic fan-out that
cron can't express — a Phase 2+ problem, if ever.
**Implementation:** schedule the Codex loaders (Planhat, Slack-derived) as GitHub Actions cron
workflows that write to Snowflake then trigger `dbt build`; let bought connectors run on their
own managed schedule and reconcile via dbt `source freshness` checks.

---

## 3. Unified CS-health data model

### 3.1 Master entity — `dim_account` (the join spine)
One row per real customer company. **Everything resolves to the Salesforce Account ID.**

```
dim_account
  account_key            surrogate
  sfdc_account_id        MASTER KEY
  account_name
  account_domain         used for fuzzy resolution
  arr                    from Salesforce
  segment                SMB / Mid-Market / Enterprise
  csm_owner_id
  renewal_date
  planhat_company_id     resolved FK
  intercom_company_id    resolved FK
  slack_channel_ids[]    resolved FK (one account → many channels)
  created_at / updated_at
```

### 3.2 Facts (daily/event grain)

```
fct_account_health_snapshot   one row per account per day; APPEND-ONLY, never deleted
  account_key, snapshot_date
  planhat_health_score            -- ANCHOR (pulled as-is, not recomputed)
  health_score_trend_7d / _30d    -- derived (direction beats absolute value)  ★
  nps_score, nps_response_date
  product_dau_7d, feature_adoption_pct   -- Planhat usage  ★
  open_support_tickets, p1_p2_tickets_30d, median_first_response_hrs  -- Intercom  ★
  intercom_support_load           -- additive sub-indicator (see Conflict 3)
  slack_message_volume_7d, slack_escalation_signals_7d, slack_sentiment_7d   ★
  slack_escalation_signal         -- additive sub-indicator (see Conflict 3)
  days_to_renewal, renewal_stage  -- Salesforce (context, gates urgency)
  open_tasks_count, overdue_tasks_count   -- Planhat CSM cadence
  churn_risk_tier                 -- Green/Yellow/Red, RULE-BASED, explainable
  computed_at

fct_opportunities         Salesforce renewals/expansions (type, stage, amount, close_date, arr_impact)
fct_support_conversations Intercom (created/resolved, priority, tags, csat, first_response_at)
fct_nps_responses         Planhat (score 0–10, verbatim, responded_at) — verbatim is PII, mask it
slack_signal              DERIVED ONLY (account_key, channel, date, msg_count, escalation_hits,
                                         mention_count, sentiment) — NO raw message bodies
```

### 3.3 Identity resolution (the #1 technical risk — both panels agreed)
Match in this precedence, highest confidence first:

1. **Deterministic cross-reference fields.** Best case: Planhat stores the Salesforce Account ID
   in its `externalId` field (if the SFDC↔Planhat sync is configured); Intercom Companies store
   the SFDC ID in their `company_id`/external field (if Intercom's Salesforce integration is on).
   **If these exist, resolution is exact — use them and stop.** *(This is Open Question #1 — it
   collapses or explodes Phase 0.)*
2. **Email-domain match.** Derive a primary domain per account; join Intercom companies and Slack
   customer channels by domain. Strong but imperfect (multi-domain customers, shared domains).
3. **Normalized name match** — **last resort, human-reviewed only. Never auto-trusted.**
4. **Slack → account** has no native concept: maintain a seed table
   `slack_channel_account_map(channel_id, account_name, account_key)`, seeded once for top
   accounts and maintained as channels are created. A weekly Codex script lists channels matching
   the naming convention (`#customer-acme`, `#ext-acme-cs`) and proposes matches for human confirmation.

**Guardrails (merge of both panels):**
- A `bridge_account_xref(source, source_id, account_key, match_method, confidence)` table records every match.
- A daily `resolution_audit` dbt model **alerts if >5% of Planhat or Intercom companies are unresolved**, or any Slack channel is unmapped >7 days.
- Unresolved records are **quarantined explicitly (null FK), never silently dropped.**
- A **Sigma stewardship page** surfaces low-confidence matches for human confirmation. **No metric is published off a name-only match without review.**
- Manual review of the **top ~20 accounts by ARR** before Phase 1 launch.

### 3.4 Health signals — the ~12 that make the tier (★ = churn-leading)
1. ★ **Usage trend (30/60/90d slope)** — strongest single predictor; slope, not absolute level.
2. ★ **Health-score trend (7/30d delta)** — direction beats Planhat's absolute value.
3. ★ **Renewal proximity × engagement** — renewal <90d *combined with* low touch/usage = red. Proximity alone is not risk.
4. ★ **Support volume + P1/P2 rate** (Intercom) — a spike 90d pre-renewal is a strong signal; P1/P2 rate matters more than raw volume.
5. ★ **Slack escalation signal** — escalation-keyword density, or a *dead* channel (absence is also a signal).
6. **NPS + recency** — detractors not followed up; stale NPS is noise, recency matters.
7. **CSM touch cadence** — days since last meaningful Planhat task vs. tier expectation; overdue QBR/onboarding.
8. **Median first-response time** (Intercom) — slow support erodes trust at renewal.
9. **Feature adoption / breadth** — narrow adoption → fragile.
10. **Days to renewal** (Salesforce) — context; gates urgency of everything else.
11. **Renewal opportunity stage** (Salesforce) — stuck early or "Closed Lost" 90d out = flag.
12. **Rule-based churn-risk tier** — the output: e.g. `health_trend down AND days_to_renewal < 90 AND (p1_tickets > t OR slack_escalation > t)` → Red. **Transparent and tunable; every Red shows the signals that drove it.**

> **Day-one acceptance test (the CS domain seat was firm on this):** the leader must be able to
> sort by `(tier = Red AND days_to_renewal < 90)` and get an actionable call list in under 10 seconds.

---

## 4. Reference architecture

```
SOURCES            INGESTION                         STORAGE + MODEL (Snowflake)        SEMANTIC          PRESENTATION
─────────          ─────────                         ───────────────────────────       ────────          ────────────
Salesforce ─┐      Fivetran / Airbyte (BUY) ─┐
Intercom  ──┼─BUY─▶ managed connectors        ├─▶  RAW  (landed; raw JSON for niche     Sigma datasets    Sigma CS-Health
            │       (incremental, schema-aware)│         APIs so schema drift can't       (governed         dashboard
Planhat   ──┼─BUILD▶ Codex Python loader ──────┤         break loads)                     metrics:          (Green/Yellow/Red,
            │       (watermark + MERGE upsert) │     │                                    risk tier,        sort by risk×renewal,
Slack     ──┘─BUILD▶ Codex signal extractor ───┘     ▼  STAGING (dbt: typed, 1:1, tests)  health, usage,    drill to evidence,
                     (DERIVED signals only —          │  + dim_account / bridge_xref      renewal)          renewal watchlist,
                      NO raw messages)                 ▼    + resolution_audit                │              stewardship page)
                                                       ▼  MARTS (dbt: fct_* + mart_cs_health,  │            + RLS per CSM
Snowflake ─(already the hub; no ingest)───────────────┘    mart_renewal_pipeline)             │
Sigma ─────(reads Snowflake live; no ingest)──────────────────────────────────────────────────┤
                                                                                               │
                                                                  [CONDITIONAL] React app ◀─────┘  embeds Sigma visuals,
                                                                  gated on the 4 triggers (§3)      adds write-back/workflow

Scheduling: GitHub Actions cron → loaders write to Snowflake → trigger `dbt build`. No Airflow/Prefect.
Governance overlay: secrets in a vault (never in repo/Codex output); Snowflake RBAC + RLS;
                    dynamic masking on PII (NPS verbatim, Intercom bodies); no raw Slack text in warehouse.
FinOps overlay: XS warehouse, AUTO_SUSPEND=60s, resource monitor + monthly credit quota/alert from day one.
```

---

## 5. Phased build plan

### Phase 0 — Foundations (≈2 weeks; 1 builder + Codex)
**Goal:** plumbing, identity resolution, and governance proven *before* any metric is shown.
- Repo structure (`/ingestion`, `/transforms`, `/sigma`, `/infra`); secrets pattern documented so **Codex never hard-codes a credential**.
- Snowflake: `raw` / `transform` / `mart` databases; `loader` / `transformer` / `analyst` roles (+ per-CSM role stubbed). **Resource monitor + AUTO_SUSPEND=60s + XS warehouse on day one.**
- Managed connectors (Fivetran or Airbyte Cloud) live for **Salesforce + Intercom**, initial sync to RAW. **Get the cost quote before turning them on.**
- **Planhat** API access verified (key, `GET /companies` test, rate limits documented [unverified — confirm with Planhat]).
- **Slack** app created (`channels:history`, `channels:read`, `users:read`), bot added to customer channels, `conversations.history` tested.
- `slack_channel_account_map` seeded for top ~10 accounts.
- dbt project initialized; `stg_salesforce_accounts` + `stg_planhat_companies` written **with `unique`/`not_null`/`relationships` tests** as the data-contract layer.
- `bridge_account_xref` + `dim_account` populated; **PII inventory + masking plan documented.**

**Exit criteria:** Salesforce + Planhat landing in RAW on schedule; staging models pass dbt tests; a known ~20 accounts correctly stitched across systems with documented match method/confidence; **zero secrets in git**; resource monitor active.

### Phase 1 — First CS-health view shipped (≈4–6 weeks)
**Goal:** a CS leader opens Sigma and answers "who do I call today?" in under 2 minutes.
- Planhat Codex loader complete (`/companies`, `/npsAnswers`, `/metrics`, `/tasks`) — **watermark + MERGE upsert** (see §6 risk #1), raw JSON landing, daily.
- Intercom managed connector verified (conversations + companies, incremental).
- Slack signal extractor complete — **derived signals only, no raw messages**.
- `dim_account` resolved across all four primary systems; `resolution_audit` alerting on >5% unresolved.
- `fct_account_health_snapshot` (daily grain, all 12 signals; **nulls where source data is absent — explicit, never silently zero**); `mart_cs_health` + `mart_renewal_pipeline`.
- **Sigma CS-Health dashboard:** account list sorted by risk tier × days-to-renewal; account detail (health-score sparkline, NPS, ticket count, Slack signal, renewal stage, open tasks); filter by CSM/segment/renewal window; **stewardship page**; **"last refreshed" timestamp on every dashboard**.
- Masking on PII fields; Sigma on the shared `analyst` role initially (per-CSM RLS in Phase 2).

**Exit criteria:** leader identifies top-10 at-risk accounts in <2 min; the Red list matches their gut on ≥80% of accounts **and every Red shows why**; all 12 signals have >90% coverage for accounts with >90 days history; `resolution_audit` <5% unresolved; mart dbt tests pass; **signed off as used in a real renewal review.**

### Phase 2 — Operational depth + conditional React (≈6–8 weeks, partly trigger-gated)
**Goal:** deepen signals, add per-CSM access, act (not just read) — *if* the triggers fire.
- Per-CSM RLS in Snowflake + Sigma (each CSM sees only their book; **test with two users before launch**).
- Historical backfill (Planhat health history [unverified — confirm API supports it], SFDC opp history, Intercom >90d) — using the documented full-refresh path (§6).
- Rule-based risk tier tuned against Phase 1 data + a real renewal cycle; **optional** lightweight logistic-regression churn score only if volume justifies.
- Alerting: Snowflake task / GitHub Action → Slack webhook when health drops >10pts/7d or a P1 opens.
- **React app — only if ≥2 of the four triggers (§3, Conflict 2) have fired.** If built: account detail with inline Planhat-task creation, Intercom preview, Slack link, auditable health-flag override; embeds Sigma visuals so metric definitions stay single-sourced.

**Exit criteria:** CSMs see their book only; churn score validated against ≥1 renewal cycle; React decision made on evidence, not on spec.

### Phase 3 — Broaden audiences (later)
- Exec KPI board (ARR, NRR, GRR, logo churn, NPS cohort) and support-ops board — **in Sigma, reusing conformed dimensions, zero new pipelines** (the proof the hub paid off).
- Data-quality SLA suite in CI; alert on dbt test failures.
- **Reverse ETL** (Census/Hightouch) to push churn scores back into Salesforce/Planhat for CRM-native workflows.
- Re-evaluate Tableau **only** if specific Sigma visualization gaps were confirmed in Phase 2 — never preemptively licensed.

---

## 6. Risks + mitigations (panels' top risks + the four the tie-breaker added)

| # | Risk | Mitigation |
|---|------|-----------|
| 1 | **★ Watermark / idempotency footgun in Codex loaders** (the single biggest one — a naive "fetch-all + INSERT" duplicates or drops rows on re-run/crash) | Every custom loader must: (a) read a `last_loaded_at` watermark from a control table; (b) pull only `updated_at > watermark`; (c) write via **MERGE/upsert on the source primary key**; (d) advance the watermark **only after a successful commit**. Plus a documented `--full-refresh` path to force a clean re-pull. |
| 2 | **Identity resolution wrong → every metric wrong, silently** | Deterministic keys first; quarantine unresolved (null FK, never drop); `bridge_account_xref` + `resolution_audit` alerting; Sigma stewardship review; manual top-20-by-ARR check before launch. |
| 3 | **★ Codex-generated pipeline code has latent edge-case bugs** (pagination, timezone drift on watermarks, swallowed exceptions) | dbt `unique`/`not_null`/`relationships` tests at the STAGING boundary as a non-negotiable data contract; pytest unit tests on each loader's transform/watermark logic against recorded API fixtures; **human review of every Codex diff touching auth or watermarks.** |
| 4 | **PII / customer data in Slack + Intercom** | No raw Slack messages in the warehouse (the extractor is the mitigation); PII inventory in Phase 0; Snowflake dynamic masking on NPS verbatim + Intercom bodies; RLS; documented retention. |
| 5 | **Planhat connector fragility** (niche API, thin docs, rate limits ~1k/hr [unverified], schema drift) | Incremental cursor + exponential backoff + **dead-letter queue** (failed records logged, not dropped); land **raw JSON, parse in dbt** so API shape changes don't break loads; daily row-count anomaly alert (>20% drop). |
| 6 | **★ Cost / FinOps surprise** (metered Snowflake + connector MAR/row pricing) | XS warehouse, `AUTO_SUSPEND=60s`, **Snowflake resource monitor with a monthly credit quota + alert on day one**; confirm the connector's pricing unit before enabling Salesforce + Intercom. |
| 7 | **★ Freshness SLA undefined → stale data that looks fresh** (worse than an outage for renewal decisions) | One-line freshness target per source (e.g. Salesforce/Planhat ≤24h, Intercom ≤6h), encoded as dbt `source freshness` thresholds; **"last refreshed" on every dashboard**; one cheap failure alert (GitHub Action → email/Slack) so a broken load pages the builder. |
| 8 | **Black-box score CSMs distrust → adoption fails** | Transparent rule-based tier with per-signal explanation; Planhat's native score as the trusted anchor; defer ML. |
| 9 | **Slack channel→account map drifts** (new channels not mapped → silently absent signals) | Weekly Codex diff script proposes unmapped candidates to an ops channel for human confirmation. |
| 10 | **Sigma RLS misconfig exposes one CSM's accounts to another** | Test RLS with two users before Phase 2; document the role mapping; RLS in the exit criteria even if a single shared role initially. |
| 11 | **dbt mart layer grows into untrusted spaghetti** | dbt from Phase 0, not Phase 2; every mart model has a `description` + ≥1 test; **no raw SQL in Sigma — all datasets read the mart layer only.** |

★ = surfaced by the tie-breaker, missed by both panels.

---

## 7. Open questions for the stakeholder (answer these before Phase 0)

Ranked by how much the answer changes the plan.

1. **Does Planhat already store the Salesforce Account ID (in `externalId`/via the SFDC sync), and does Intercom store it on its Companies?** *(Both panels independently ranked this #1.)* If yes, identity resolution is largely **deterministic** and Phase 0 shrinks dramatically. If no, configure the sync now — it's a cheap ops task, far cheaper than building a fuzzy-match pipeline and throwing it away.
2. **Are the Slack channels genuinely shared *customer* channels, what's the naming convention, and is mining them acceptable to customers / legally?** Governs whether Slack is a real health source (signals #5, #11) or dropped to internal-only, and how hard the mapping automation is.
3. **What is Planhat's native health score composed of, and do you want to keep it as the anchor or eventually blend in Intercom/Slack signals?** Phase 1 keeps it as the anchor + additive sub-indicators; if you want a custom composite, that changes the mart design.
4. **What compliance regime governs this data (GDPR/CCPA/SOC 2), and what's the retention requirement?** Sets the scope of Phase 0 governance (masking, retention tasks, deletion workflows). A baseline is built in; a formal obligation expands it.
5. **Is the primary Phase 1 user a CS *leader* reviewing the whole book, or an individual *CSM* on their own ~20 accounts — and is this also a board-presentation artifact?** Doesn't change the architecture, but moves RLS/personalization earlier and raises the visualization/export bar. *(Bonus, from Panel A's dissent: is a goal here also "learn to build with Codex"? If so, the React app moves earlier than the triggers would otherwise dictate.)*

---

## 8. Repo scaffolding & agent-tooling setup (Codex-first, Claude + Copilot wired in)

This build is driven primarily through **OpenAI Codex**, but the repo is set up so **Claude
Code** and **GitHub Copilot** are first-class too — no rework if a second tool joins. The trick
is a **single canonical instruction file** (`AGENTS.md`) that all three read, plus thin per-tool
config that points back at it. Don't maintain three drifting copies of the rules.

### 8.1 One source of truth, three readers

| Tool | What it reads | Setup |
|------|---------------|-------|
| **Codex** (primary) | **`AGENTS.md`** natively (repo root; also nested `AGENTS.md` per directory — closest file wins) | Make `AGENTS.md` the canonical rulebook. Codex picks it up with zero extra config. |
| **Claude Code** | **`CLAUDE.md`**, which does `@AGENTS.md` to import the canonical file, then adds Claude-only notes (plan mode, hooks) | One-line import — no duplication. |
| **GitHub Copilot** | **`.github/copilot-instructions.md`** (repo-wide) + optional **`.github/instructions/*.instructions.md`** with `applyTo:` globs for path-scoped rules | Keep `copilot-instructions.md` short and have it say "the canonical engineering rules live in `/AGENTS.md` — follow them"; use path-scoped instruction files for the loader contract. |

> This is exactly the pattern the marketplace repo this plan lives in uses (`CLAUDE.md` →
> `@AGENTS.md`), so it's a proven setup, not a guess.

### 8.2 Recommended repo layout (tailored for Codex's working style)

Codex works best with **small, well-bounded directories** and a `_lib/` of shared primitives it
can reuse instead of re-deriving (which is where the watermark/idempotency footgun creeps in).

```
cs-analytics/
├── AGENTS.md                         # CANONICAL cross-tool rules (Codex + Copilot read natively)
├── CLAUDE.md                         # @AGENTS.md import + Claude-Code-only notes
├── README.md
├── .env.example                      # secret NAMES only, never values
├── .github/
│   ├── copilot-instructions.md       # short; points at /AGENTS.md
│   ├── instructions/
│   │   ├── ingestion.instructions.md # applyTo: "ingestion/**" — THE loader contract (§8.4)
│   │   └── transforms.instructions.md# applyTo: "transforms/**" — dbt test/style rules
│   └── workflows/
│       ├── dbt-ci.yml                # dbt build + tests on every PR
│       └── pipelines.yml             # cron: run the Codex-built loaders (no Airflow)
├── .claude/
│   └── settings.json                 # Claude-only hooks: PreToolUse secret-scan, etc.
├── ingestion/
│   ├── _lib/                         # SHARED primitives — Codex reuses, never re-derives:
│   │   ├── watermark.py              #   read/advance last_loaded_at control table
│   │   ├── upsert.py                 #   MERGE-on-primary-key helper
│   │   └── backoff.py                #   exponential backoff + dead-letter logging
│   ├── planhat/                      # Codex-built loader (watermark + MERGE, raw-JSON land)
│   └── slack/                        # derived-signal extractor (NO raw messages)
├── transforms/                       # dbt project (staging → marts + tests)
│   ├── models/staging/
│   ├── models/marts/
│   └── tests/
├── sigma/                            # dashboard definitions / export-as-code if used
├── infra/                            # Snowflake DDL: databases, roles, RLS, resource monitor
└── tests/
    └── fixtures/                     # recorded API responses → loader unit tests (§6 risk #3)
```

### 8.3 Driving Codex phase-by-phase
- **Feed it one phase at a time** from §5, not the whole plan. Each Codex task = one bounded deliverable (e.g. "build the Planhat loader per `ingestion.instructions.md`").
- **Point every ingestion task at `_lib/`** — "use `watermark.read()` / `upsert.merge()` from `ingestion/_lib`, do not write your own." This is the single most effective guard against the duplicate-rows footgun, because Codex's default is a naive fetch-all-and-INSERT.
- **Sandbox/network:** Codex runs in a sandbox — give it a setup script that installs deps and document which outbound hosts (Snowflake, the six APIs) the task needs, so a run isn't silently blocked.
- **Never let Codex inline a credential.** Secrets come from env vars named in `.env.example`; review every diff that touches auth.

### 8.4 The cross-tool "loader contract" (put this in `AGENTS.md` + `ingestion.instructions.md`)
Because all three tools read these files, encoding the §6 hard-won rules here means **every
agent inherits them** — you don't re-explain per task or per tool:

1. Every loader reads a `last_loaded_at` watermark, pulls only `updated_at > watermark`, writes via **MERGE on the source primary key**, and advances the watermark **only after a successful commit**.
2. Land **raw JSON** for niche APIs (Planhat); parse in dbt — API shape changes must not break loads.
3. **Slack lands derived signals only — never raw message bodies.**
4. Failed records go to a **dead-letter log**, never silently dropped.
5. Every loader ships with **pytest unit tests against recorded fixtures** in `tests/fixtures/`; every staging model ships with `unique`/`not_null`/`relationships` dbt tests. No loader merges without both.
6. A documented `--full-refresh` path exists to force a clean re-pull (backfill / schema change).

### 8.5 Per-tool division of labor (play to each tool's strengths)
- **Codex** — the workhorse for generating loaders, dbt models, and the (conditional) React app. Bounded, well-specified, fixture-tested tasks.
- **Claude Code** — best for the **cross-cutting / plan-mode work**: identity-resolution design, the dbt mart architecture, multi-file refactors, and reviewing Codex's auth/watermark diffs. Use its hooks (`.claude/settings.json`) for a `PreToolUse` secret-scan so a credential can't be written even by accident.
- **GitHub Copilot** — inline autocomplete during hand-editing, and **Copilot code review on PRs** as a cheap second pass over Codex-generated diffs (it's good at spotting the null-handling / pagination / timezone bugs flagged in §6 risk #3).

> **Net:** one `AGENTS.md` rulebook, three tools pointed at it, and the loader contract encoded
> once so the watermark/idempotency/testing discipline is enforced no matter which agent writes
> the code. Codex drives; Claude architects and guards; Copilot reviews.

---

## Appendix — provenance & verification notes

- **Panel A** (Opus) and **Panel B** (Sonnet) ran independently from an identical brief; **tie-breaker** was a third independent senior architect on a fresh model.
- Items marked **[unverified — training knowledge]** in the source panels (Planhat connector availability + rate limits, cross-system external-ID fields, Intercom API rate limits, Sigma embed/JWT-SSO and write-back feature set, Slack API method names/rate-limit tiers) are **not confirmed against live docs** — they fold into Open Questions #1–#3 and the Phase 0 verification tasks. Confirm before committing engineering effort that depends on them.
- This is a plan, not an implementation. Nothing here has been run against the actual six systems.
