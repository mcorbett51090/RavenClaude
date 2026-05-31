---
description: "Set up Tableau row-level security as an enforced data policy and the governance skeleton around it — entitlements keyed to USERNAME() on the published source, certified data sources, locked projects, and (for embedding) the JWT subject bound to the RLS key."
argument-hint: "[the requirement, e.g. 'each regional manager sees only their region']"
---

# Set up RLS and governance

You are running `/tableau:set-up-rls-and-governance`. Implement the access requirement the user described (`$ARGUMENTS`) as an *enforced data policy*, not a hidden workbook filter, and build the governance skeleton that makes it durable — the work the `tableau-admin` agent owns. RLS is an access control, so the verdict escalates to `ravenclaude-core/security-reviewer`.

## When to use this

Two viewers of the same content must see different rows, or you are designing the project/site/permission structure. NOT for performance (that is `/tableau:tune-workbook-performance`).

## Steps

1. **Implement RLS as an enforced data policy, not a user filter** (`gov-rls-as-a-data-policy-not-a-hidden-filter.md`): key the policy off the logged-in identity via `USERNAME()` / `ISMEMBEROF()` against an **entitlements table** (one row per user→scope grant), applied on the published data source (ideally a Virtual Connection data policy). A calculated user filter leaks the moment someone web-edits, downloads, or builds a new workbook on the same extract.
2. **Put RLS on a certified, separated source** (`gov-certified-data-sources-and-governance.md`, `server-publish-with-separated-data-sources.md`): RLS lives once on the certified published source and is inherited everywhere — you can't centralize RLS on an extract copied into every workbook.
3. **Build the governance skeleton** (`gov-sites-and-projects-as-the-governance-skeleton.md`): use a **site** only for hard tenancy isolation (different companies, regulatory separation, separate admin); use a **locked project per team** in one shared site for content governance — most "keep these teams apart" needs are a locked project, not a new site.
4. **Grant permissions via locked projects, not per workbook** (`gov-permissions-via-locked-projects-not-per-workbook.md`): lock the project, grant groups on it, and let content inherit — per-workbook permission grants drift and don't scale.
5. **For embedded analytics, bind the JWT subject to the RLS key as one contract** (`embed-scope-the-jwt-and-rls-together.md`, `embed-connected-apps-jwt-not-trusted-tickets.md`): the JWT `sub` must resolve to the exact identity the entitlements table is keyed on — a correctly-authenticated session against the wrong entitlement key still leaks another tenant's rows. Prove it with a cross-population test.
6. Escalate the RLS/embedding design to `ravenclaude-core/security-reviewer` for the verdict — this plugin supplies the domain rubric, core owns the sign-off.

## Guardrails

- A user filter is a convenience, not a control — a single leaked row has real cost, so RLS gets the same scrutiny as any access control.
- Reaching for a new site when a locked project would do over-isolates: users/groups/data sources don't cross the site boundary, so you re-create everything.
- Auth succeeding does not mean isolation held — always cross-population test the JWT-sub-to-entitlement-key binding.
