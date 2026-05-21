---
scenario_id: 2026-05-21-pa-management-api-roles-null
contributed_at: 2026-05-21
plugin: power-platform
product: power-automate-management-api
product_version: "unknown"
scope: likely-general
tags: [spn, pa-management-api, oauth, client-credentials, 401, roles-null, application-permissions]
confidence: high
reviewed: false
---

## Problem

Service principal authenticating to the **Power Automate Management API** at `https://api.flow.microsoft.com` returned HTTP 401 on every endpoint, even though token acquisition succeeded against `https://service.flow.microsoft.com/.default`. Inspecting the JWT showed the `roles` claim was `null`.

## Permissions context

- Customer DEV environment, bulk-flow-creation engagement (~136 flows in scope)
- Service principal authenticated via `client_credentials` OAuth flow
- Customer's app-registration access available; tenant-side `Global Admin` access **not** available
- Delegated permissions for `Flows.Read.All` / `Flows.Manage.All` had been added to the app registration ("Admin consent required: No" in the Azure AD portal — appeared friendly)

## Attempts

- Tried: Token acquisition against `https://service.flow.microsoft.com/.default` → succeeded; got a bearer token with no `roles` claim
- Tried: Any PA Management API call (e.g., `GET /providers/Microsoft.ProcessSimple/environments/<env>/flows`) → 401 with no useful error detail
- Tried: Re-checking app-registration permissions; confirmed *delegated* `Flows.Read.All` was granted with apparent admin consent → still 401
- Tried: Switching to confidential client + verified `roles: null` in the issued token → confirmed the application permissions were not granted at all
- Tried: Requested Global Admin to grant **application** (not delegated) `Flows.Read.All` and `Flows.Manage.All` → blocked; Global Admin consent process was a multi-week wait in customer's change-management
- Tried (workaround): Pivoted to the **Dataverse Web API** at `https://<env>.api.<region>.dynamics.com/api/data/v9.2/` and the `workflow` entity with `category=5`, `type=1` → worked

## Resolution

The Power Automate Management API enforces **Azure AD application permissions** on the `https://service.flow.microsoft.com/` resource. The two relevant permissions (`Flows.Read.All`, `Flows.Manage.All`) are *application* permissions, and application permissions on this resource **always require Global Admin consent**. The token returns `roles: null` because the consent never landed.

The common misstep: a user with app-registration access can add the *delegated* versions of these permissions (they show "Admin consent required: No" in the portal), thinking they've granted access. They haven't — **delegated permissions do not work with the `client_credentials` OAuth flow**. Only application permissions do, and only after Global Admin consent.

**The escape hatch is the Dataverse Web API.** Modern Power Automate cloud flows are Dataverse `workflow` entity records with `category = 5` and `type = 1`. An SPN with `System Administrator` (or equivalent Dataverse role with create/update on the `workflow` table) can create, read, update, and delete cloud flows **without ever touching the PA Management API**. This is what the customer DEV engagement actually used to ship ~136 flows.

**Action for the next consultant hitting this pattern:**
1. Before debugging the 401, check the JWT's `roles` claim. If `null`, you're missing application permissions, not delegated.
2. If Global Admin consent for application permissions is blocked, **don't fight it** — pivot to the Dataverse Web API immediately. It's almost always available where the PA Management API isn't, because the SPN already has Dataverse access for the same engagement.

Cross-reference: full canonical detail in [`../knowledge/programmatic-flow-creation.md`](../knowledge/programmatic-flow-creation.md). This scenario is the field-note version of the auth-surface trap; the knowledge file goes deeper on the Dataverse Web API workaround mechanics.
