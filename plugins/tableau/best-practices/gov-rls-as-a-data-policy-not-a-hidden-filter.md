# Implement RLS as an enforced data policy, not a hidden workbook filter

**Status:** Absolute rule — row-level security is an access control; the *verdict* escalates to `ravenclaude-core/security-reviewer`. A user filter is a convenience, not a control.

**Domain:** Governance / row-level security

**Applies to:** `tableau`

---

## Why this exists

Two viewers of the same dashboard must see different rows — "each regional manager sees only their region," "each customer sees only their tenant." It is tempting to drop a calculated **user filter** on the workbook and call it secured. That filter is unenforced, lives per-workbook, and leaks the moment someone web-edits the viz, downloads the underlying data, builds a new workbook on the same extract, or simply forgets to apply it on the next sheet. RLS that matters is a **data policy enforced once on the data layer** and inherited everywhere — an entitlements table joined to the data, keyed to the viewer's identity, applied at the source (ideally a Virtual Connection with centralized row-level security). The point isn't which function you call; it's that a single leaked row has a real cost, so the mechanism gets the same scrutiny as any access control — which is why the verdict goes to security review, not the dashboard author.

## How to apply

Key the policy off the logged-in user via `USERNAME()` / `ISMEMBEROF()`, against an **entitlements table**, enforced on the published data source (or a Virtual Connection data policy).

```
-- Entitlements table (one row per user→scope grant):
--   user_name           | region
--   amy@corp.com         | West
--   amy@corp.com         | East        (one user, many scopes — rows, not a CASE)
--   ben@corp.com         | South

-- Centralized row-level data policy (Virtual Connection) — policy predicate:
[Entitlements].[user_name] = USERNAME()
--   → every workbook/data source on this Virtual Connection inherits the filter.

-- Fallback when there is no Data Management add-on:
--   join Entitlements into the PUBLISHED data source and add a data-source filter:
USERNAME() = [Entitlements].[user_name]     -- TRUE keeps the row; enforced at the source
```

**Do:**
- Drive the filter from `USERNAME()` (or group membership via `ISMEMBEROF()`), against an **entitlements table** — never hard-code names in a CASE.
- Enforce at the **data layer** (Virtual Connection data policy, or a data-source filter on a *published* data source) so every downstream workbook inherits it.
- Model one-user-maps-to-many-scopes as **rows in the entitlements table**, not a widening calc.
- **Escalate the RLS verdict to `ravenclaude-core/security-reviewer`** with the threat model: populations, entitlement key, and the cost of one leaked row.

**Don't:**
- Treat a per-worksheet calculated filter as a security boundary — it's personalization, and it leaks via web edit / download / new workbook.
- Test RLS only as yourself (an admin/owner can bypass it) — verify as a real member of each population.
- Leave the entitlements table unsecured — whoever can edit it can grant themselves rows.

## Edge cases / when the rule does NOT apply

- **Personalization, not security** — "default each user's dashboard to their own region for convenience, but they *may* see others" is a legitimate user-filter use; say so explicitly and it still gets a security note.
- **Fully disjoint, fixed populations** — separate workbooks/data sources per population removes the row-leak surface entirely; correct when populations never overlap.
- **No Data Management add-on** — Virtual Connections + centralized RLS require it `[verify-at-build]`; without it, fall back to entitlements-join RLS in the published data source (still enforced, just not central).
- **Initial SQL / RAWSQL** — passing `USERNAME()` into initial SQL can enforce at the database, but verify the connection caching/pooling model doesn't serve one user's rows to another.

## See also

- [`./embed-scope-the-jwt-and-rls-together.md`](./embed-scope-the-jwt-and-rls-together.md) — when the RLS key must match the embedded JWT subject
- [`./gov-certified-data-sources-and-governance.md`](./gov-certified-data-sources-and-governance.md) — RLS lives once on the certified/published data source
- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: RLS mechanism`
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule; escalates the verdict to `ravenclaude-core/security-reviewer`
- Tableau Help, "Row-level security options overview" + "Virtual Connections and Data Policies" `[verify-at-build]`

## Provenance

Codifies constitution house opinion #6 ("RLS is a security control, not a convenience filter") and the `tableau-admin` discipline #2. Grounded in Tableau's RLS options (user filters, entitlements-table joins, Virtual Connection data policies). The Data Management add-on requirement and policy syntax move — re-verify before quoting. The security *verdict* is owned by `ravenclaude-core/security-reviewer`, never this plugin.

---

_Last reviewed: 2026-05-30 by `claude`_
