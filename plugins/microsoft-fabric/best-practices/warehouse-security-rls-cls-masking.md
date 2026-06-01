# Warehouse SQL-native security — RLS, CLS, and dynamic data masking inside the warehouse

**Status:** Pattern — strong default for a Fabric Warehouse holding sensitive columns/rows; deviate only with a written reason and a routed security verdict.

**Domain:** Warehouse / security

**Applies to:** `microsoft-fabric`

---

## Why this exists

`workspace-domain-governance-boundary.md` owns the **two-plane model** (workspace roles are not data access; OneLake/control-plane vs data-plane) and the house-opinion-#6 RLS/CLS-preview caveat. This rule is the **SQL-native, inside-the-warehouse** layer it defers to: when sensitive data lives in a Fabric Warehouse, you enforce row/column security *in the warehouse engine* with T-SQL security predicates — and that choice has a load-bearing consequence for Direct Lake. The gap this fills is the warehouse engineer's "how do I actually restrict who sees which rows/columns in the warehouse" — distinct from the plane model, which says where security lives, not how the warehouse implements it.

## How to apply

**Row-level security (RLS)** — a `SECURITY POLICY` with an inline table-valued predicate function filters rows by the querying principal:

```sql
CREATE FUNCTION sec.fn_territory(@territory AS sysname) RETURNS TABLE WITH SCHEMABINDING
AS RETURN SELECT 1 AS ok WHERE @territory = USER_NAME() OR IS_ROLEMEMBER('SalesAdmin') = 1;
CREATE SECURITY POLICY sec.TerritoryFilter
  ADD FILTER PREDICATE sec.fn_territory(Territory) ON dbo.Sales WITH (STATE = ON);
```

**Column-level security (CLS)** — `GRANT`/`DENY` at the column grain so a principal can query a table but not the salary/SSN column.

**Dynamic data masking (DDM)** — mask a column's *display* (email, partial SSN) for non-privileged readers; **it is obfuscation, not access control** — a determined querier can infer masked values, so don't rely on DDM where CLS/RLS is the real requirement.

**The Direct Lake consequence (load-bearing):** warehouse RLS/CLS is enforced by the **SQL engine**. A Power BI **Direct Lake** model reading the same data can **fall back to DirectQuery** (or must, to honor the security) — know that enabling warehouse RLS can change the Direct Lake performance/fallback story for downstream models. Decide where the canonical security lives: warehouse RLS *or* semantic-model RLS, not silently both.

**Do:** RLS via security policy + predicate function; CLS via column GRANT/DENY; DDM only for display-masking; pick one canonical RLS layer (warehouse vs semantic model); **route the security verdict to `ravenclaude-core/security-reviewer`** (house rule).

**Don't:** treat DDM as access control; enforce RLS in both the warehouse and the semantic model without deciding which is canonical; assume Direct Lake performance is unaffected by warehouse RLS.

## Edge cases / when the rule does NOT apply

If the canonical security boundary is the **semantic model** (Power BI RLS roles) and the warehouse is never queried directly by end users, warehouse-native RLS may be redundant — decide deliberately. The two-plane model and the RLS/CLS-still-preview-on-some-surfaces caveat live in `workspace-domain-governance-boundary.md` — this rule does not restate them. RLS/CLS/DDM GA-vs-preview status across Fabric Warehouse vs SQL endpoint is version-sensitive — `[verify-at-build]`.

## See also

- [`./workspace-domain-governance-boundary.md`](./workspace-domain-governance-boundary.md) — the two-plane model this rule operates *within* (the authority on plane + preview caveat)
- [`./warehouse-scd-and-merge-patterns.md`](./warehouse-scd-and-merge-patterns.md) — modeling the warehouse this rule secures
- [`../agents/warehouse-engineer.md`](../agents/warehouse-engineer.md) — owns warehouse security implementation
- Security verdict escalates to [`ravenclaude-core/security-reviewer`](../../ravenclaude-core/agents/security-reviewer.md)
- [Fabric Warehouse — row-level / column-level security, DDM](https://learn.microsoft.com/fabric/data-warehouse/security) — authoritative

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01). Panel 2 scope caveat (honored): this BP is **SQL-native warehouse security** and explicitly defers the two-plane model + preview caveat to the existing `workspace-domain-governance-boundary.md` rather than duplicating it. Grounded in Fabric Warehouse security docs. GA-vs-preview status is `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
