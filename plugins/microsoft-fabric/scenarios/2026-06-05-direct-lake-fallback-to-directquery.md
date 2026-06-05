---
scenario_id: 2026-06-05-direct-lake-fallback-to-directquery
contributed_at: 2026-06-05
plugin: microsoft-fabric
product: direct-lake
product_version: "2026.05"
scope: likely-general
tags: [direct-lake, directquery-fallback, rls, sql-endpoint, on-onelake]
confidence: high
reviewed: false
---

## Problem

A finance team's flagship Power BI report, built on a "Direct Lake" semantic model over a Fabric Warehouse, had degraded from sub-second visuals to 8–15-second loads, and a few cards intermittently showed stale numbers. Nobody had changed the report. The team described it as "Direct Lake got slow" and wanted to know whether to rebuild as Import.

## Constraints context

- Semantic model over a Warehouse SQL analytics endpoint — i.e. **Direct Lake on SQL**, though no one had written the mode down (CLAUDE.md §3 #8 / the "name your mode" rule).
- A **row-level security** requirement had recently been added at the **Warehouse** layer (SQL-native RLS security policy + predicate) to restrict cost-center visibility.
- F64 capacity; model well under volume guardrails; gold tables framed and V-Ordered.
- Slowness correlated with the RLS rollout date, not with any data-volume growth.

## Attempts

- Tried: naming the mode first (the non-optional step). This was **Direct Lake on SQL** (reads via the SQL endpoint). That immediately reframed the question — on-SQL *falls back to DirectQuery*, and **SQL-endpoint OLS/RLS forces that fallback**. Outcome: hypothesis = the new Warehouse RLS is forcing every query through DirectQuery, which is why it got slow (and why freshness looked off — DQ federates live but pays per query).
- Tried (confirmation): checked the semantic model's fallback behavior / query trace — queries were resolving as DirectQuery against the SQL endpoint, not reading Delta directly. Outcome: confirmed the RLS-forces-fallback root cause; the model was technically working, just no longer in the fast Direct Lake path.
- Tried (rejected): "rebuild as Import." Would have restored speed but reintroduced heavy refresh and stale-between-refreshes data, and **silently dropped the RLS** unless re-implemented in the model — trading one problem for two. Outcome: ruled out.
- Tried (the move that worked): picked **one canonical RLS layer** instead of two. Removed the Warehouse-layer RLS and re-expressed the cost-center restriction as **semantic-model RLS** (Power BI roles) so the Direct Lake path was preserved, with `security-reviewer` signing off on the equivalence of the new policy. Visuals returned to Direct Lake speed; the security boundary held. (For an *on-OneLake* model the equivalent fix is OneLake security data-access roles — but on-OneLake there is **no** DirectQuery fallback, so a bad role yields *empty*, not slow.)

## Resolution

This was not "Direct Lake got slow" — it was **Direct Lake on SQL falling back to DirectQuery because RLS was enforced at the SQL endpoint.** The load-bearing trap is enforcing RLS in *two* planes (Warehouse SQL **and** the consuming model): warehouse RLS can force the Direct Lake model to DirectQuery (on-SQL) or error (on-OneLake). The fix is to choose **one** canonical RLS layer for the data a Direct Lake model reads — never silently both (house opinions #6 + #8).

**Action for the next consultant hitting this pattern:** when a Direct Lake report "slows down" right after a security change, **name the mode first**, then suspect a forced DirectQuery fallback (on-SQL) or empty results (on-OneLake) before you suspect data volume or "Direct Lake being slow." Decide one canonical RLS plane for the model's source via [`../knowledge/fabric-decision-trees.md`](../knowledge/fabric-decision-trees.md) "Data security — which plane (and engine)?" and apply [`../best-practices/name-your-direct-lake-mode.md`](../best-practices/name-your-direct-lake-mode.md). Every data-security verdict escalates to `ravenclaude-core/security-reviewer` (CLAUDE.md §10). The field-note complement to the canonical Direct Lake + security rules.

**Sources (Microsoft Learn, retrieved 2026-06-05 — `[verify-at-use]`, ships monthly):** [Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview) · [How Direct Lake works (fallback)](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works) · [Row-level security in Fabric Warehouse](https://learn.microsoft.com/fabric/data-warehouse/row-level-security). The mode-specific fallback/empty behavior is the load-bearing fact; re-confirm GA/preview of Direct Lake variants before quoting (house opinion #9).
