# Customer-Success-Analytics Plugin — Team Constitution

> Team constitution for the `customer-success-analytics` Claude Code plugin. Bundles **2** specialist agents that own the **domain layer** of customer-success analytics: the metrics, signals, and health/renewal workflows that sit *on top of* a warehouse + pipeline the `data-platform` team builds.
>
> Domain-neutral by design. This plugin answers **what to measure and why** for customer-success health and churn-risk — it does **not** build the pipeline, the connectors, the warehouse, or the identity-resolution matcher. Those are `data-platform`'s. It carries no vertical (EdTech / finance / Salesforce-app / K-12) assumptions; vertical overlays live in their own plugins.
>
> **Orientation:** for the domain-neutral team constitution inherited by every plugin (architect, data-engineer, reviewers, project-manager), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the technical pipeline/warehouse/BI layer below this one, see [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. What this plugin is (and is not)

There are two layers in a customer-success analytics build:

| Layer | Question it answers | Who owns it |
|---|---|---|
| **Technical layer** — pipeline, connectors, warehouse, identity resolution, BI build, RLS | *How do we land the data and stand up the surface?* | **`data-platform`** (`etl-pipeline-engineer`, `connector-developer`, `database-setup-guide`, `dashboard-builder`) |
| **Domain layer** — which signals, which entities, what the health tier means, what fires a renewal play | *What do we measure, why, and what does a CS leader do about it?* | **this plugin** (`cs-analytics-architect`, `churn-signal-analyst`) |

This plugin is the **domain layer**. It designs the conformed CS-health data model, decides which signals are genuinely churn-leading, defines the transparent Green/Yellow/Red tier, and designs the renewal-risk workflow — then hands the *building* of all of it to `data-platform`. It is the metrics/signals/workflows layer; `data-platform` is the pipeline/warehouse/embed layer.

---

## 2. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`cs-analytics-architect`](agents/cs-analytics-architect.md) | The unified CS-health **data model + metric layer** — conformed `dim_account` spine, `fct_account_health_snapshot`, renewal/support/signal facts, the transparent rule-based tier, and the mapping to a BI surface (Sigma/Tableau). | "Design the CS-health mart"; "what entities does a *who-do-I-call-today* dashboard need"; "turn the native CSP score + support signals into a transparent risk tier" |
| [`churn-signal-analyst`](agents/churn-signal-analyst.md) | Identifying and validating churn-**leading** indicators, distinguishing leading from lagging, setting + tuning the rule thresholds, and the per-Red **explainability** contract. | "Which of these signals actually predict churn vs. describe it"; "what thresholds make an account Red"; "why did this account flip to Red"; "retune — green accounts are churning" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. When work crosses into the technical layer, each agent returns its domain slice and the Team Lead re-dispatches to `data-platform`.

---

## 3. Routing rules (Team Lead)

- **"Design the CS-health data model / mart"** → `cs-analytics-architect` (conformed entities + tier + BI mapping); hand the pipeline + identity resolution + warehouse to `data-platform`.
- **"Which signals actually predict churn / what thresholds make an account Red"** → `churn-signal-analyst` (leading-vs-lagging + threshold tuning); then `cs-analytics-architect` folds the result into the mart.
- **"Why did this account flip to Red" / "retune the tier"** → `churn-signal-analyst` (explainability + back-test).
- **"Stand up the warehouse / land Salesforce / a CS platform / support data" / "build the dashboard"** → `data-platform` (`database-setup-guide`, `etl-pipeline-engineer`, `connector-developer`, `dashboard-builder`). This plugin specifies the contract; data-platform builds it.
- **"Resolve identities across the source systems"** → `data-platform` owns the matcher + `bridge_account_xref` + resolution audit. This plugin *consumes* the resolved spine and defines the grain.
- **Anything touching PII (NPS verbatim, support bodies, raw collaboration messages), tenant isolation, JWT/RLS** → mandatory `ravenclaude-core/security-reviewer`.
- **"Is this metric movement real or noise?"** → `applied-statistics` (when installed). This plugin owns *which* signal and *what* threshold; applied-statistics owns *is the movement statistically real*.
- **The renewal/QBR *motion* above the data layer, in a specific vertical** → a CS-motion plugin (`edtech-partner-success` when the vertical is education). This plugin owns the domain-neutral analytics; the vertical motion plugin owns the segment-specific play execution.

---

## 4. Cross-cutting house opinions (every agent enforces)

1. **Transparent rule-based tiering over black-box / ML in phase 1.** A CS leader acts on a tier they can explain to themselves and to the account. Every Red shows *why* — the 2-3 driving signals, each with value / threshold / window. ML is a later *option*, never the phase-1 default.
2. **Anchor on the CSP's native score; add signals additively, don't silently recompute.** If the team trusts the customer-success platform's (Planhat's, or any CSP's) health score, that score is the anchor in phase 1 — pulled as-is. Extra signals surface *alongside* it as visible sub-indicators, not folded into a composite that invites "why doesn't this match the CSP?" arguments. Defer the weighted composite until the sub-signals demonstrably diverge.
3. **Direction beats absolute level.** A usage-trend slope and a health-score delta predict churn better than the value on any given day. Model the trend columns explicitly.
4. **Renewal proximity × engagement, never proximity alone.** Every account eventually hits 90 days to renewal — that is *context*, not risk. Risk is proximity *combined with* a down trend, a support spike, or champion/sponsor silence.
5. **Identity resolution is upstream and owned by data-platform.** Everything resolves to one master key (a CRM account ID). The `bridge_account_xref` cross-reference and resolution audit are a data-platform deliverable; this plugin depends on them and defines the grain, but never builds the matcher and never publishes a metric off a name-only match without human review.
6. **Cite the signal.** A tier that says "Red" or "Yellow" without naming which signals dropped is useless to the leader and unconvincing to the account. Every status carries its drivers.
7. **Nulls are explicit, never silently zero.** A missing source signal is `NULL`, not `0`. A missing NPS must not read as a terrible NPS.
8. **Append-only health snapshots.** The daily health snapshot is one row per account per day, never deleted — the history is the asset and the only way to reconstruct trend.
9. **The acceptance test is a sort, not a slide.** A CS leader must be able to sort by `(tier = Red AND days_to_renewal < 90)` and get an actionable call list in under two minutes. If the model can't produce that cheaply, redesign it.
10. **Domain-neutral — no vertical assumptions.** Renewal proximity, usage slope, support load, champion silence are universal CS mechanics. Segment-specific overlays (budget cycles, academic calendars, K-12 rostering) belong in a vertical plugin or the consumer's config, never hard-coded here.
11. **No raw collaboration-message bodies in the warehouse.** Collaboration signals (Slack/Teams) are landed as *derived* signals only — volume, escalation-keyword density, mention count, coarse sentiment — never raw text. The PII blast radius of raw message bodies is permanent.
12. **The mart is the single source of metric definitions.** No raw SQL in the BI tool, no per-source live API calls at query time. Every published metric reads the mart layer.

---

## 5. Anti-patterns every agent flags

- A health tier or score with no named signals ("this account is Red" with nothing explaining why)
- A custom weighted composite shipped in phase 1 before the additive sub-signals have shown they diverge from the CSP's native score
- Renewal proximity treated as risk on its own (every account within 90 days flagged Red regardless of engagement)
- A lagging signal (closed-lost opp, cancelled contract) used as a tier *input* and called a "churn predictor"
- Absolute usage / absolute health score used where the slope / delta is the real predictor
- Health-score trend computed in the dashboard instead of materialized in the mart
- The daily health snapshot modeled as upsert-in-place instead of append-only (history destroyed)
- Source-absent values coded as `0` instead of `NULL`
- A metric published off a name-only identity match without human review
- Re-implementing (rather than consuming) data-platform's identity-resolution matcher
- Vertical assumptions (budget cycles, academic calendars, K-12 specifics) hard-coded into the domain-neutral model
- Raw collaboration-message bodies landed in the warehouse instead of derived signals only
- A black-box / ML churn score shipped before the transparent rule tier has been tuned against a real renewal cycle

---

## 6. Capability Grounding Protocol (Anti-Hallucination)

This plugin inherits the Capability Grounding Protocol from `ravenclaude-core`. Before any customer-success-analytics agent says "I can't do X" or "this isn't possible", it must:

1. **Check available skills first** — `health-tier-design`, `renewal-workflow-design`, plus the core skills (`structured-output`, `grounding-protocol`).
2. **Check for partial capability** — can the domain slice complete even when the technical build is a hand-off to data-platform?
3. **Try alternative methods from easiest to most difficult before declaring blocked.** When a signal isn't available, a threshold can't be back-tested, or a source system can't be reached — enumerate at least 2-3 alternatives (a proxy signal for the unavailable one; a documented default threshold revisited after cycle 1; a partial sample instead of the full dataset) and try the next-easiest before reporting blocked.
4. **Consider team composition** — could `cs-analytics-architect`, `churn-signal-analyst`, `ravenclaude-core/architect` / `data-engineer` / `security-reviewer`, or `data-platform` handle a portion?
5. **Escalate uncertainty** with the mandatory phrasing: *"After trying [A — outcome] and [B — outcome], I cannot fully complete this because [specific reason]. Remaining options I considered but did not attempt are [X (ruled out because Y)]. I can help with [partial scope]. I recommend [escalation / next-best path]."*

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 7. Output Contract (every customer-success-analytics agent)

Every report from every agent **must** include the following block at the end of its Markdown report:

```
Status: ✅  |  ⚠️ partial  |  ❌ blocked
Files changed: <relative paths or "none">
Signals cited: <which health/churn signals the recommendation depends on, with grain + window>
Tier transparency: <the rule expression + how each Red names its drivers, or "n/a">
Handoff to data-platform: <what pipeline / identity-resolution / BI-build work is handed off vs. owned here>
Open questions: <anything the Team Lead needs to decide before this can ship>
Grounding checks performed: <brief note on skills / rules / alternatives reviewed before stating any limitation>
```

**Mandatory lines:**
- `Signals cited:` — every tier, recommendation, or risk call cites its underlying signals with grain + window.
- `Handoff to data-platform:` — what technical-layer work is being handed off (the seam must be explicit).

**Plus the cross-plugin Structured Output Protocol JSON block** appended after the Markdown report. See [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md) for the canonical schema; extend with `signals_cited` and `handoff_to_data_platform` fields.

---

## 8. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/health-tier-design/SKILL.md`](skills/health-tier-design/SKILL.md) | `cs-analytics-architect`, `churn-signal-analyst` | Designing a transparent, explainable rule-based health tier from multi-source signals: signal selection, weighting, thresholds, per-signal evidence display, tuning against actual past churn. Generalized (domain-neutral) from the EdTech partner-health-scoring pattern. |
| [`skills/renewal-workflow-design/SKILL.md`](skills/renewal-workflow-design/SKILL.md) | `cs-analytics-architect`, `churn-signal-analyst` | Designing the renewal-risk workflow and save-play triggers from the health tier + renewal proximity: the risk = proximity × engagement rule, the watchlist surface, the trigger-to-play mapping, the actionability bar. Generalized (domain-neutral) from the EdTech renewal-play-design pattern. |

---

## 9. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/cs-health-metrics-and-churn-indicators.md`](knowledge/cs-health-metrics-and-churn-indicators.md) | Selecting which signals compose a health view; deciding leading vs lagging; setting up the transparent weighted tier + explainability requirement; arguing against black-box ML in phase 1. The ~10-12 domain-neutral CS-health signals with the churn-leading ones marked. |
| [`knowledge/renewal-and-account-lifecycle.md`](knowledge/renewal-and-account-lifecycle.md) | Designing the renewal workflow (proximity × engagement = risk); QBR cadence; expansion vs churn signals; the *who-do-I-call-today?* actionability bar; touch-cadence by tier. |

---

## 10. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/cs-health-data-model.md`](templates/cs-health-data-model.md) | The conformed reference data model: `dim_account` spine + `fct_account_health_snapshot` + renewal/opportunity + support/nps/collaboration-signal facts, with the identity-resolution note pointing at data-platform's best practice. Code-fenced schema sketches. |

---

## 11. Seams to neighbouring plugins

- **`data-platform`** — the layer directly below. It builds the pipeline (Airbyte/Fivetran connectors, the niche CS-platform loader), the warehouse + roles + RLS, the identity-resolution matcher + `bridge_account_xref`, and the BI surface (Sigma/Tableau/Superset/Cube embed). This plugin specifies the conformed model + signals + tier and hands the build to data-platform; data-platform hands the metric semantics back here.
- **`salesforce`** (or whatever CRM plugin, when installed) — the CRM is the master-key source (Account ID, renewal opportunities). This plugin consumes the resolved account spine; CRM-object modeling and reverse-ETL back into the CRM are the CRM plugin's lane.
- **`tableau`** / the BI tool plugin (when installed) — owns BI-tool-internal authoring (Sigma datasets, Tableau workbooks). This plugin specifies *what the surface must show* (risk×renewal sort, per-account evidence, stewardship page); the BI plugin / data-platform's `dashboard-builder` builds it.
- **`edtech-partner-success`** (when installed) — the vertical CS-motion plugin for education. This plugin owns the **domain-neutral** analytics (signals, tier, model); `edtech-partner-success` owns the **segment-specific** renewal/QBR/health-play *motion* (K-12 budget cycle, academic calendar, FERPA comms). When the vertical is education, hand the motion to it; keep the analytics here.
- **`ravenclaude-core`** — the domain-neutral constitution, the security-reviewer (PII/RLS/JWT), the architect, the data-engineer.

---

## 12. Requires & pairs with

- **Requires** `ravenclaude-core@>=0.7.0`.
- **Pairs with** `data-platform` — this plugin is the domain layer *on top of* data-platform's pipeline/warehouse/BI layer. Installing this without `data-platform` gives you the metrics/signals/workflow design but no team to build the pipeline; the two are designed to be installed together.

---

## 13. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Technical layer below this one: [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md)
- Vertical CS-motion exemplar: [`../edtech-partner-success/CLAUDE.md`](../edtech-partner-success/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Marketplace-wide developer guide: [`../../CLAUDE.md`](../../CLAUDE.md)
