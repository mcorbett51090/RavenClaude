# Cross-references — Partner Success Command Center Dashboard

_Compiled 2026-06-04 by background `/wrap`. Maps the new spec (`./spec.md`) onto pre-existing planning artifacts, plugin substrate, and memory entries. No artifact below was modified — this file is a navigation index only._

---

## A. Planning artifacts already on disk

### A.1 In-flight `data-viz-designer` agent — `docs/research/2026-06-02-data-viz-agent/`

| File | Size | Relationship to the new spec |
|---|---|---|
| `strategic-plan.md` | 47 KB | **Adjacent / methodology gap-filler.** Owns the chart-from-intent + page-composition + WCAG floor + IBCS opt-in canon that this dashboard's visualization layer would consume. The spec is a *deliverable* the agent could be invoked to design; the agent itself is *not* the dashboard. |
| `build-plan.md` | 90 KB | Same as above — the build plan delivers the design discipline (skills + linter + knowledge files). It does **not** deliver a Partner-Success dashboard. |
| `pre-build-gate-results.md` | 5 KB | Process artifact; not directly load-bearing here. |
| `webfetch-injection-memo.md` | 6 KB | Security-floor finding now generalized at marketplace level (PR #227, `webfetch-hardening` skill). Indirect. |

**Status of the agent itself:** awaiting Ultraplan execution (per `project_data_viz_designer_in_flight` memory, 2026-06-02). When it lands, it becomes the natural consultee for the design layer of the dashboard in this spec.

### A.2 Today's `unified-dashboard-shell` plan — `docs/plans/2026-06-04-unified-dashboard-shell/plan.md`

**Relationship: parallel infrastructure, NOT competing.** That plan is about *RavenClaude's own* dashboard UI shell (collapse `index.html` + `dashboard.html` + `repo-guide.html` into one front door via iframe lazy-loading). It does NOT speak to a Partner-Success operational dashboard for a PSM. The two could share zero code and both ship. If a future Partner-Success dashboard were itself a RavenClaude artifact, the shell pattern (iframe + route table + smart-fallback banner) would be the template — but the spec captured here reads as a customer-deliverable, not a marketplace artifact.

### A.3 Other 2026-06 plans (skimmed — not topical)

- `2026-06-03-adaptive-run-classifier/` — agent dispatch tuning; unrelated.
- `2026-06-03-agent-dispatch-evaluator/` — agent dispatch tuning; unrelated.
- `2026-06-03-mimir-session-tab/` — RavenClaude internal dashboard tab; unrelated.

### A.4 Sibling research from 2026-06 (skimmed — not topical)

- `docs/research/2026-06-03-copilot-adapter-diagnostic/` — Copilot CLI bridge diagnostics; unrelated.

---

## B. Plugin substrate — what already exists that the build would draw from

### B.1 `plugins/edtech-partner-success/` — the home plugin for this work

**This is the plugin that owns the PSM lane.** The dashboard described in the spec is the **operational surface** that the agents in this plugin would inform / score / fill.

**Agents (6) directly relevant to dashboard content:**

| Agent | What it contributes to the dashboard |
|---|---|
| `partner-success-manager.md` | Onboarding / adoption / ongoing pulse — the "which partners need attention today?" question routes here. |
| `learning-analytics-analyst.md` | The health-score signal-selection + weighting + decay design — feeds the "at risk" + portfolio-health widgets. |
| `partner-profile-curator.md` | The durable partner record — feeds the partner-detail drill-downs and pre-meeting context. |
| `success-playbook-designer.md` | Which play applies — the "what action should I take?" question routes here once the dashboard surfaces the signal. |
| `qbr-composer.md` | The QBR motion — feeds the "next required touchpoint" widget when a QBR is due. |
| `ferpa-comms-translator.md` | Comms-layer for any partner-facing notification the dashboard might draft. |

**Knowledge files directly relevant (17 total in the plugin; the 5 most load-bearing for this spec):**

| File | Relationship |
|---|---|
| `knowledge/partner-health-score-drift.md` | Health-score signal decay — directly feeds the "at risk" lens. |
| `knowledge/partner-health-decline-which-play.md` | Decline-to-play mapping — the "what action" rubric. |
| `knowledge/k12-psm-operating-cadence.md` | Touchpoint cadence by segment + calendar — feeds the "next required touchpoint" widget. |
| `knowledge/k12-adoption-arc-fall-spring-summer.md` | Calendar seasonality — informs which alerts fire when (don't escalate in late August). |
| `knowledge/psm-metrics-glossary.md` | Names the numbers the dashboard would surface (DAU/WAU, MAU, adoption depth, health composite). |
| `knowledge/psm-tools-landscape-2026.md` | Already covers Gainsight / Planhat / ChurnZero / Salesforce-as-system-of-record + the EdTech reality that no vertical CSP exists. |

**House rules from `plugins/edtech-partner-success/CLAUDE.md` that constrain this dashboard's design:**

- Rule 1: *"The partner profile is the source of truth, not the CRM."* — the dashboard must not implicitly elevate Salesforce above the durable partner record.
- Rule 4: *"Cite the signal."* — every "yellow" or "red" badge in the dashboard needs the 2–3 signals that drove it visible inline or one click away.
- Rule 8: *"Rostering is the silent killer."* — for a K-12 partner, rostering health is a first-class dashboard signal.
- Rule 12: *"Provenance on every claim."* — every dashboard number needs source query / date range / comparison baseline accessible.

### B.2 `plugins/data-platform/` — the connector + warehouse layer

**This plugin owns the data layer beneath the dashboard.** Five of the seven sources named in the spec already have first-class knowledge files:

| Spec source | Existing coverage | File |
|---|---|---|
| **Salesforce** | ✅ Yes — Bulk API 2.0 ceilings, SOQL relationship-query nuances, explicit field enumeration | `knowledge/salesforce-integration.md` |
| **Planhat** | ✅ Yes — **BUILD** verdict (no managed connector), custom watermark+MERGE loader, `externalId` as the Salesforce-Account-ID cross-reference anchor, raw-JSON-land-then-parse-in-dbt | `knowledge/planhat-integration.md` |
| **Snowflake** | ✅ Implicit — `cloud-database-landscape-2026.md` + the "don't reinvent the warehouse — data sharing not new ELT pipeline" rule in CLAUDE.md house rule 10 | `knowledge/cloud-database-landscape-2026.md` |
| **Support data** | ✅ Partial — Intercom (BUY managed connector) covered explicitly. **Gap if the support tool is Zendesk / Freshdesk / Jira Service Management / Salesforce Service Cloud** — not covered. | `knowledge/intercom-integration.md` (only) |
| **Contracts** | ⚠️ Gap — no contract-system-of-record connector knowledge file. Often lives inside Salesforce (CPQ) or Ironclad / DocuSign CLM. Would need a research pass. | none |
| **Success Plans** | ⚠️ Gap — Planhat carries success-plan objects natively; if the SoR is elsewhere (Gainsight, Notion, Airtable, custom Salesforce object), needs a per-system pass. Adjacent to `success-playbook-designer.md` in `edtech-partner-success`. | none |
| **Calendar** | ⚠️ Gap — no Google-Calendar / Outlook-Calendar connector knowledge file. Common ELT-vendor coverage exists (Fivetran, Airbyte) but no first-class plugin note. | none |

**Skills directly relevant:**

| Skill | Relationship |
|---|---|
| `skills/cross-system-identity-resolution/SKILL.md` | **Load-bearing.** Stitching Salesforce + Planhat + Snowflake + Support into one conformed `account` spine is exactly the problem this skill solves (candidate-key inventory → deterministic → domain → name precedence ladder → `bridge_account_xref` with `match_method` + `confidence`). |
| `skills/connector-configuration/SKILL.md` | Per-source connector patterns for the data-layer build. |
| `skills/dashboard-performance-tuning/SKILL.md` | The widget-budget loop — directly applies to a "answer 8 questions per day" surface where slow widgets defeat the use case. |
| `skills/build-embedded-dashboard/SKILL.md` | The secure-by-construction embed pattern — metric defined once in the semantic layer, tenant scope at the data layer, short-lived JWTs, CSP+iframe boundary. Applicable if the dashboard is exposed to a non-Matt-owned tenant. |

**Agents:**

- `etl-pipeline-engineer.md` — owns the actual connector configuration / land-and-shape work.
- `dashboard-builder.md` — owns the front-end build (Evidence / Superset / Metabase / Cube + React + Tremor + Recharts).

### B.3 `plugins/ravenclaude-core/` — domain-neutral support

- The pending `data-viz-designer` agent (per A.1) is the natural design-layer consultee.
- The existing `architect`, `security-reviewer`, `code-reviewer`, `pm` agents are the standard review pass.

---

## C. Memory entries that scope this work

| Memory file | Relationship to the spec |
|---|---|
| `project_psm_means_partner_success.md` | Confirms the end-user is Matt's wife, a real Partner Success Manager — this is a real operational dashboard, not a demo. |
| `project_data_viz_designer_in_flight.md` | The in-flight design-agent work; once it lands, it's the natural consultee for the dashboard's chart layer. |
| `feedback_dashboards_over_slash_commands.md` | Matt's primary design constraint: every tool / setting / metric visible in a dashboard. Reinforces the spec's "single source of truth, no swivel-chairing between systems" premise. |
| `project_business_direction.md` | Consulting-first business model — this dashboard could be the *exemplar* deliverable for a $25–50K Partner-Success-operations engagement. |
| `feedback_persist_deep_research.md` | The reason this file lives in `docs/research/` (gitignored, Codespace-restart-safe). |
| `project_dashboards_plugin_2026-05.md` | The earlier "dashboards plugin" idea — captures intent to ship per-engagement dashboards as a productized layer. |

---

## D. Suggested home plugin for the build

**If Matt decides to formalize this:** the build artifact belongs in `plugins/edtech-partner-success/` (it's PSM-shaped) with `plugins/data-platform/` carrying the connector + warehouse + semantic-layer work below it. The `data-viz-designer` (when shipped) is consulted for the chart layer. The unified-dashboard-shell pattern from `docs/plans/2026-06-04-unified-dashboard-shell/` is the iframe-routing template if the dashboard ever needs to be embedded inside RavenClaude itself.
