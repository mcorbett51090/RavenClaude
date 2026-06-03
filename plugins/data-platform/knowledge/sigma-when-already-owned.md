# Sigma — when the client already owns it

> **Last reviewed:** 2026-06-03. Sources: Sigma Computing documentation (help.sigmacomputing.com, sigmacomputing.com/docs) `[unverified — training knowledge; confirm current Sigma feature set, write-back capabilities, and pricing tiers at build time]`. Refresh when: (a) Sigma materially changes its write-back / input-tables feature set, (b) Sigma's pricing model changes (per-viewer pricing is the key variable), or (c) a client's Sigma contract terms change.

## The standing plugin opinion — and why this file exists

The `data-platform` plugin is **opinionated against per-viewer-priced BI tools** for greenfield SMB consulting engagements (§3, house opinion #2). Looker, Tableau Embedded, Sigma, and Metabase Pro all have pricing models that punish viewers at scale: 5–50 viewers × 4–6 clients × $400+/viewer/year makes the math untenable for fixed-fee consulting. The plugin flags this explicitly and steers toward flat-rate or usage-priced alternatives.

**This opinion governs SELECTION. It does not govern LEVERAGING a sunk investment.**

The per-viewer-pricing caution is a greenfield decision rule — it prevents a client from unknowingly committing to a pricing model that punishes growth. When a client already owns Sigma-on-Snowflake and has absorbed the per-viewer cost into their budget, the calculation is different: **not using Sigma means discarding a working, well-integrated tool and introducing a second semantic layer, a second metric definition surface, and the metric drift that comes with them.**

When the client already runs Sigma on Snowflake, **Sigma is the correct primary BI surface for this build.**

## When Sigma is the right answer

All three conditions hold for the CS-health analytics build described in `docs/analytics-dashboard-plan.md`:

1. **Already owned** — the client's Sigma license exists and is paid for. The marginal cost of building dashboards in Sigma is near-zero.
2. **Snowflake-native** — Sigma reads Snowflake directly; it is not a separate semantic layer on top of a separate BI database. The warehouse is already the hub; Sigma sits natively on top of it.
3. **Feature set matches the need** — governed metrics / semantic layer, pushes compute down to Snowflake, spreadsheet-like UI for CS leader exploration, RLS via Snowflake roles, embedding capability.

### Sigma's strengths in this context

| Capability | Why it matters for CS health |
|---|---|
| **Pushes compute to Snowflake** | Queries run in Snowflake, not Sigma's cloud. No data duplication; uses the same XS warehouse. |
| **Governed datasets / semantic layer** | Metric definitions live once in Sigma datasets; all dashboards read from them. No metric drift between views. |
| **Spreadsheet-like exploration** | CS leaders can pivot, filter, and build ad-hoc views without writing SQL. |
| **RLS via Snowflake roles** | Per-CSM access is enforced at the Snowflake role level (see [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md)); Sigma passes through the role. |
| **Embedding** | Sigma visuals can be embedded in a conditional React app (if the four Phase 2 triggers fire) without duplicating metric logic. |

### The rejected alternative — Tableau alongside Sigma

The build plan explicitly rejects adding Tableau as a second BI surface (§1, Decision A). Adding Tableau alongside Sigma means:

- A **second semantic layer** — metric definitions in both tools diverge within one quarter
- **Metric drift** — "Revenue" in Sigma and "Revenue" in Tableau will not agree by month 6
- **Doubled maintenance burden** — two tools to version, govern, and train users on
- **License cost stacked on top of an already-paid Sigma subscription**

**Decision: reject Tableau and any other second BI tool when Sigma is already owned and the Snowflake-native requirement is met.** The build plan's tie-breaker settled this (§1, Decision A, confidence: Settled, both panels agreed).

## When a custom React app is warranted instead (or alongside Sigma)

Sigma is the right primary surface, but there are specific capabilities Sigma cannot provide that may justify a custom React app. Build the React app **only when two or more of these triggers have fired** (they must be observed, not speculated):

| Trigger | Example |
|---|---|
| **Write-back action Sigma can't serve** | Creating a Planhat task or updating a Salesforce field directly from the dashboard view |
| **Repeated context-switch cost** | Users demonstrably leaving Sigma to take action in Planhat/Salesforce, and this round-trip is measurably costing adoption |
| **Multi-step conditional logic** | An action requiring branching logic, system calls, or transactional writes across systems |
| **Auditable human-in-the-loop workflow** | Health-flag overrides that need an approval chain, version history, and a compliance record |

**Sigma's input-tables / write-back feature** may already serve some write-back cases `[unverified — confirm Sigma's current write-back and input-tables feature set; feature availability and limitations vary by Sigma tier and have evolved; the build plan §2 Conflict 2 explicitly marks this unverified]`. Check before building a React layer for a write-back need — if Sigma can serve it natively, the custom app cost is avoidable.

Until two or more triggers have fired: maintain a one-line backlog entry, not a dated phase. Instrument Sigma usage (session logs, user interviews) so the triggers are observable.

**If the React app is built:** embed Sigma visuals within it rather than duplicating metric visualizations. This keeps metric definitions single-sourced in Sigma, and the React app adds only the workflow/write-back surfaces Sigma can't provide.

## The pricing distinction — sunk cost vs. greenfield selection

To be explicit about the rule boundary:

| Situation | Plugin verdict |
|---|---|
| **Client is evaluating BI tools for a new build; no existing contract** | Apply the per-viewer-pricing caution. Flag Sigma's pricing model. Recommend flat-rate alternatives (Evidence.dev, Superset, Metabase OSS, Cube + React). |
| **Client already owns Sigma-on-Snowflake; it is in active use** | Sigma is the correct primary BI surface. Use it. Do not layer a second tool. |
| **Client owns Sigma but Snowflake is not the warehouse** | Evaluate on a case-by-case basis; Sigma's Snowflake-native advantage disappears. |
| **Client owns Sigma but is not using it; contract is up for renewal** | Apply the selection caution to the renewal decision. Do not assume the existing contract justifies continuing. |

The hook `hooks/flag-data-platform-smells.sh` flags Sigma in `stack-decision-record.md` templates as a per-viewer-priced tool — this is correct behavior for the **greenfield selection** case and should not be overridden. The hook does not fire on dashboard build work; it fires on stack-selection documents. The nuance is context-dependent and requires human judgment on the selection vs. leverage distinction.

## Common gotchas

1. **RLS through Sigma requires the Snowflake role to carry the tenant context** — Sigma passes through the Snowflake role; the RLS policy must be on the Snowflake table, not in Sigma. See [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) for Snowflake row-access policy patterns.
2. **Dataset governance requires discipline** — Sigma's governed-datasets feature is only as good as the discipline around it. If analysts build workbooks pointing directly at raw/staging tables (bypassing the governed dataset), metric drift will occur. Enforce a "Sigma workbooks read the mart layer only" rule from day one.
3. **Write-back feature set is tier-dependent** — Sigma's input-tables and write-back capabilities vary by license tier `[unverified — confirm current tier gating]`. Verify before relying on them to avoid a scope-change surprise mid-build.
4. **Embedding requires a specific Sigma license tier** — confirm the client's contract covers embedding before designing a React-embedded architecture around it `[unverified — confirm current Sigma embedding tier requirements]`.
5. **"Last refreshed" timestamp** — Sigma does not auto-display when the underlying Snowflake data was last updated. Add a `mart_last_refreshed` model to the dbt project and surface it explicitly in every Sigma dashboard. Stale data that looks fresh is worse than an outage for renewal decisions.

## See also

- [`../knowledge/embedded-analytics-landscape-2026.md`](../knowledge/embedded-analytics-landscape-2026.md) — the full landscape doc with per-viewer-pricing analysis
- [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) — Snowflake row-access policies + Sigma RLS passthrough
- [`docs/analytics-dashboard-plan.md`](../../../docs/analytics-dashboard-plan.md) — §1 Decision A (Sigma primary, Tableau rejected) and §2 Conflict 2 (React app triggers)
- [`../best-practices/model-semantic-layer-single-source-of-truth.md`](../best-practices/model-semantic-layer-single-source-of-truth.md) — why a single semantic layer matters; applies directly to the "no second BI tool" principle
