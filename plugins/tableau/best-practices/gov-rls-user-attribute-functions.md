# Use user attribute functions for RLS — not hardcoded username lists

**Status:** Absolute rule
**Domain:** Governance / row-level security
**Applies to:** `tableau`

---

## Why this exists

Row-level security via a hardcoded `[Username] = "alice" OR [Username] = "bob"`
user filter is a maintenance anti-pattern: every employee change requires a
workbook edit and republish. For any RLS that maps users to data domains
(regions, accounts, tenants, cost centres), the mapping belongs in the data —
not in the calculation. Tableau's `USERNAME()` function combined with a lookup
table (user → permitted domain) lets you change access by updating the data
source without touching the workbook. It also makes the access model auditable
and scalable.

## How to apply

**Step 1 — create the user-domain mapping table:**
```
| username           | region      |
|--------------------|-------------|
| alice@example.com  | Northeast   |
| bob@example.com    | Southwest   |
```

**Step 2 — relate the mapping table to the fact data:**
Use a relationship (logical layer) between the fact table and the mapping table
on `[username] = USERNAME()`.

**Step 3 — write the row-level filter calculation:**
```
// Data source filter on the fact table — add this as a fixed filter
[Region] = [User Region Mapping].[Region]
```

Or use `ISMEMBEROF()` for group-based RLS (where the group represents the
permitted domain) `[verify-at-build — ISMEMBEROF availability varies by
Tableau version and auth configuration]`.

**For Tableau Server/Cloud with data policy RLS (row-level security policies
in the data source):**
Use the data-policy framework where available — it is server-enforced and not
bypassable by a workbook edit.

**Do:**
- Put the user-domain mapping in the data source; change access by updating
  the data, not the workbook.
- Escalate the RLS design to `ravenclaude-core/security-reviewer` for the
  security verdict.
- Test with a `[username] = "known_restricted_user"` parameter to verify
  the filter excludes the correct rows.

**Don't:**
- Hardcode usernames or user lists in a calculated field.
- Rely on Tableau's user filter dialog alone — it does not scale and is
  bypassed by workbook downloads if the data source connection is embedded.
- Treat `USERNAME()` as a sufficient access control without verifying that the
  data source connection is not bypassed by data download permissions.

## Edge cases / when the rule does NOT apply

- A single-user demo workbook or a personal workbook with no multi-user
  audience: no RLS needed.

## See also

- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns RLS design
- [`./gov-rls-as-a-data-policy-not-a-hidden-filter.md`](./gov-rls-as-a-data-policy-not-a-hidden-filter.md) — the upstream rule on RLS as an access control
- [`./embed-scope-the-jwt-and-rls-together.md`](./embed-scope-the-jwt-and-rls-together.md) — embedded contexts need RLS and JWT scoped together

## Provenance

Codifies the user-attribute function RLS pattern from Tableau's row-level
security documentation `[verify-at-build]`. The maintenance-anti-pattern of
hardcoded user lists is a well-documented Tableau governance failure mode.
House opinion #6 from `CLAUDE.md` §3 ("RLS is a security control, not a
convenience filter").

---

_Last reviewed: 2026-06-05 by `claude`_
