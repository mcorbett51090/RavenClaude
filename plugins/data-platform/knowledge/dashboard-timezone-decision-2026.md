> **Last reviewed:** 2026-09-03. Sources: this plugin's own two app starters (FORGE
> dashboard-top1pct P2-15), Cube's REST API query-format docs (query-level `timezone` field,
> verified via Context7 against `cube-js/cube`'s `docs-mintlify/reference/core-data-apis/rest-api/
> query-format.mdx`, 2026-09-03). Refresh when: (a) either starter's chosen fork changes, (b) a
> real engagement's requirement contradicts the tenant-configured default below.

# The multi-tenant timezone decision fork

A genuine design fork with no universally right answer — three real options, each correct for a
different engagement shape. Pick one explicitly and document the choice; don't let it default
silently to whatever the server happens to run in (that's the warehouse-UTC fork, chosen or not).

## The three forks

### 1. Tenant-configured (this plugin's starters implement this one)

The tenant's timezone (and, separately, locale) is stored as tenant configuration — a column on
the `tenants` table, resolved into the session alongside `tenant_id`. Every viewer belonging to
that tenant sees the same "today," regardless of where they personally sit.

- **Right for:** a B2B SaaS where the tenant is an organization with a canonical operating
  timezone (a US regional retailer, a single-office consultancy) and "our numbers" should mean
  the same thing to every viewer in that org, including the ones traveling.
- **Wrong for:** a tenant whose viewers are meaningfully spread across timezones and each
  genuinely wants "my local today," not "head office's today."
- **This starter's implementation:** `lib/locale.ts`'s `resolveLocaleContext(session)` reads
  `session.locale`/`session.timezone` (optional fields on the `Session` seam) and falls back to
  `en-US`/`UTC` when the session doesn't provide them — the fallback is the warehouse-UTC fork by
  default, not a third option; a real engagement should populate these fields from the tenant's
  own configuration.

### 2. Viewer-browser (`Intl.DateTimeFormat().resolvedOptions().timeZone`)

Each viewer's own browser reports its timezone; the dashboard renders in that, independent of
tenant configuration.

- **Right for:** an internal analytics tool where "when did I look at this" matters more than "one
  canonical org-wide view" — individual contributors checking their own numbers.
- **Wrong for:** any dashboard where two viewers comparing the same widget need to see the same
  computed date-range boundary — two viewers in different zones would each get a *different*
  "last 30 days" window, which defeats "let's look at this together" collaboration and makes a
  screenshot ambiguous the moment it leaves the browser that rendered it.
- **Not implemented in this plugin's starters** — would replace `resolveLocaleContext`'s session
  read with a client-side `Intl.DateTimeFormat().resolvedOptions()` call, which also means the
  timezone can only be known client-side, complicating the server-issued Cube token's query
  (the token itself doesn't carry timezone, but the *query* built from it would need to be
  client-driven rather than server-resolved).

### 3. Warehouse-UTC (the silent default when nobody chooses)

Every query runs in UTC; the rendering layer optionally converts UTC timestamps to *something*
for display, but the query's own date-range boundaries never account for any tenant or viewer
timezone.

- **Right for:** a warehouse-facing internal tool where "UTC" is the organization's own operating
  convention already (common at engineering-heavy companies), or a Case A portfolio piece with no
  real multi-tenant stakes.
- **Wrong for:** any client-facing dashboard where a tenant outside UTC will notice their "today"
  doesn't match their calendar — this is the fork an unset `timezone` field silently falls into,
  which is exactly why `best-practices/dashboard-render-in-the-viewer-locale-and-tenant-timezone.md`
  requires the field be set explicitly rather than left to Cube's own UTC default.
- **This is what happens if `resolveLocaleContext`'s fallback fires** in this plugin's starters —
  named honestly here rather than presented as a deliberate third option nobody chose.

## Why "tenant-configured" is this plugin's default, not a universal recommendation

The default matches this plugin's overall stance (§3 of `CLAUDE.md`): the tenant is the unit of
isolation and configuration throughout the rest of the plugin (RLS, `access_policy`,
`tenant_memberships`), so resolving locale/timezone from the same session that already carries
`tenant_id` is the path of least new surface area, and it produces the collaboration-friendly
property (same widget, same numbers, for every viewer of one tenant) that most consulting
engagements in this plugin's stated scope (SMB, one operating timezone per client org) actually
want. An engagement whose tenant genuinely spans timezones with viewers who need their own local
view should implement fork 2 instead — the `resolveLocaleContext` seam is a documented,
overridable extension point precisely so that swap doesn't require touching every widget.

## Related

- [`best-practices/dashboard-render-in-the-viewer-locale-and-tenant-timezone.md`](../best-practices/dashboard-render-in-the-viewer-locale-and-tenant-timezone.md) —
  the absolute rule this file's fork analysis supports.
- `templates/cube-nextjs-dashboard-starter/lib/locale.ts` and
  `templates/cube-astro-dashboard-starter/src/lib/locale.ts` — the implementation.
