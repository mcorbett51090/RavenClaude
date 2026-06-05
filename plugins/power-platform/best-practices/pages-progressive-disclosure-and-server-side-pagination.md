# Paginate Power Pages list results server-side; never load all rows into the browser

**Status:** Absolute rule
**Domain:** Power Pages performance and security
**Applies to:** `power-platform`

---

## Why this exists

A Power Pages list (entity list / Dataverse grid) with no pagination enabled fetches all matching rows on every page load. On a public-facing site with a fast-growing Dataverse table, this becomes: a slow first-paint for the visitor, a high-volume query against the Dataverse API on every request, and a potential data-over-exposure surface (the grid may render rows a scoped filter should have excluded but the table permission still allows). Power Pages renders lists in the browser — once the JSON payload is in the network response, the visitor can read it. Loading only the page of rows the user is viewing is both a performance control and a blast-radius reduction.

## How to apply

On every Dataverse list component in Power Pages:

```liquid
{%- entitylist id: '...' page_size: 10 -%}
```

Or via the Portal Management app → Entity Lists → Page Size: set to ≤ 25 rows for any list on a public page.

Checklist:
- [ ] **Page size set** — default is 10; confirm it matches the visual design and the expected row count per table.
- [ ] **Sort is server-side** — do not `JS`-sort the full payload client-side; use the `sort_column` and `sort_direction` FetchXML attributes.
- [ ] **Search is FetchXML** — use the Portal's built-in search filter (FetchXML `like` clauses), not JavaScript `.filter()` on the loaded array.
- [ ] **Table permissions still apply** — pagination is not a substitute for scoped table permissions. Both must be set correctly.
- [ ] **Count query** — confirm the "total records" count query is bounded by the same table-permission filter as the list query, or omit it on public pages to avoid revealing total row counts to unauthenticated visitors.

**Do:**
- Use `offset` and `page` parameters in the liquid tag to preserve page state on URL reload.
- Test the list with a real authenticated user in the target web role, verifying that page 2+ honors the same table-permission scope as page 1.

**Don't:**
- Disable pagination for "simplicity" on a public anonymous-access list — every row the anonymous user can query is returned without pagination.
- Use a JavaScript-based infinite-scroll that fetches all rows and hides them in the DOM — the data is in the response regardless of CSS visibility.

## Edge cases / when the rule does NOT apply

An admin-only back-office page with a fixed-size table (e.g., a system settings list with < 50 rows total) may reasonably load all rows. Document the upper bound and add a guard condition to the page.

## See also

- [`../agents/power-pages-engineer.md`](../agents/power-pages-engineer.md) — owns Power Pages design and security
- [`./pages-table-permissions-before-publish.md`](./pages-table-permissions-before-publish.md) — the security layer that this rule complements

## Provenance

Codifies `power-pages-engineer`'s opinion from CLAUDE.md §3 and the `power-pages-permissions` skill; standard Power Pages performance guidance from Microsoft Learn.

---

_Last reviewed: 2026-06-05 by `claude`_
