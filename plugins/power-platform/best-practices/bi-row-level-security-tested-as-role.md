# Define RLS on dimensions, and test it "View as role" with a real account

**Status:** Absolute rule — shipping an RLS model you only tested as the author is a security defect.

**Domain:** Power BI / security

**Applies to:** `power-platform`

---

## Why this exists

Row-level security (RLS) filters rows by the viewer's identity. Two failures recur. First, makers write the filter on the **fact table** (`Sales[Region] = ...`) where it evaluates per fact row and performs badly; the filter belongs on the **dimension** so the single-direction relationship propagates it to the fact for free. Second — and worse — makers test RLS as themselves (a workspace admin or model author, who **bypasses RLS entirely**) and ship a role that leaks every row. RLS is only real when verified with **View as role** *and* a non-author test account actually assigned to the role. Microsoft's [Row-level security guidance](https://learn.microsoft.com/power-bi/guidance/rls-guidance) and the `power-platform-tester` agent both treat "tested only as admin" as no test at all.

## How to apply

Put the security filter on the dimension table, keyed off the logged-in user via `USERPRINCIPALNAME()`:

```dax
-- Role: "Region Manager" — filter applied to the Region DIMENSION, not the Sales fact.
-- Table: Region    Filter DAX:
[RegionEmail] = USERPRINCIPALNAME()

-- A mapping-table pattern when one user maps to many regions:
-- Table: Region
VAR _user = USERPRINCIPALNAME()
RETURN
    Region[RegionKey]
        IN SELECTCOLUMNS (
            FILTER ( UserRegionMap, UserRegionMap[Email] = _user ),
            "rk", UserRegionMap[RegionKey]
        )
```

**Do:**
- Apply the filter on the **dimension**; let the single-direction relationship flow it to the fact.
- Use `USERPRINCIPALNAME()` (not `USERNAME()`, which returns DOMAIN\user on-prem and the UPN in the service — inconsistent).
- Test with **Modeling → View as → Other user / Role**, then a second time with a **real account assigned to the role** in the workspace.
- Keep a user→scope **mapping table** for many-to-many; don't hard-code emails in the role filter.

**Don't:**
- Write the RLS filter on the fact table when a dimension filter would propagate.
- Use **bidirectional** relationships with RLS unless you've reasoned through the leak path — they can expose rows the filter meant to hide.
- Declare RLS "tested" because it worked for you — the author and admins bypass RLS.

## Edge cases / when the rule does NOT apply

- **Dynamic RLS via a mapping table** is the pattern when a user maps to many scopes; static per-role filters are fine only for a small fixed set of roles.
- **Object-level security (OLS)** hides whole tables/columns, not rows — a different mechanism for "this role can't see the Salary column."
- **Direct Lake / DirectQuery** push RLS predicates to the source; confirm the source honors them and that you're not double-filtering.
- RLS does **not** secure the underlying dataset from XMLA/Analyze-in-Excel users with Build permission unless the workspace role is also constrained — RLS is not a substitute for workspace access control.

## See also

- [`bi-star-schema-not-flat-table.md`](./bi-star-schema-not-flat-table.md) — single-direction dimension→fact relationships are what make dimension-side RLS propagate
- [`pages-table-permissions-before-publish.md`](./pages-table-permissions-before-publish.md) — the Power Pages analogue of "test as the real user, not the admin"
- [`test-as-real-security-context-not-admin.md`](./test-as-real-security-context-not-admin.md) — the cross-surface testing rule
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md)
- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — owns the "RLS / OLS with View as role *and* a real test account" check

## Provenance

Grounded in [Row-level security (RLS) with Power BI](https://learn.microsoft.com/power-bi/enterprise/service-admin-rls) and [RLS guidance](https://learn.microsoft.com/power-bi/guidance/rls-guidance) (retrieved 2026-05-30). Encodes `power-platform-tester`'s RLS/OLS test discipline (agent §"Power BI / DAX").

---

_Last reviewed: 2026-05-30 by `claude`_
