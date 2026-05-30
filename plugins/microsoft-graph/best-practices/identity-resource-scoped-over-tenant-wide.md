# Resource-scoped permissions over tenant-wide `.All` — when a scoped grant exists, the `.All` is over-privilege

**Status:** Pattern — strong default; deviate only with a written reason and a routed verdict.

**Domain:** Identity

**Applies to:** `microsoft-graph`

---

## Why this exists

A `Sites.ReadWrite.All` application permission grants write to **every** site collection in a tenant — thousands of sites — when the app may need exactly one. Microsoft Graph now ships **resource-scoped** alternatives precisely so you don't have to grant the whole tenant: `Sites.Selected` (the app is consented broadly but can touch *only* the specific site collections an admin later grants it, per-site, via a Graph `POST .../permissions` call), and Teams **resource-specific consent (RSC)** permissions like `ChannelMessage.Read.Group`, which a team or chat owner consents to *at install time* for that one team/chat — the app can't reach a team it wasn't added to. When such a scoped permission exists, the tenant-wide `.All` is over-privilege by definition: you're granting orders of magnitude more reach than the workload uses, and an enterprise admin will (rightly) balk at it.

## How to apply

Before requesting a `.All` permission, check whether a resource-scoped equivalent exists for that workload. If it does, use it.

```text
SharePoint / OneDrive:  Sites.Selected  (app-only) instead of Sites.ReadWrite.All
  → admin grants the app per-site, e.g.:
     POST https://graph.microsoft.com/v1.0/sites/{siteId}/permissions
     { "roles": ["write"],
       "grantedToIdentities": [{ "application": { "id": "{clientId}",
                                                  "displayName": "{app-name}" } }] }

Teams:  RSC permission (e.g. ChannelMessage.Read.Group, Channel.Create.Group)
  → declared in the Teams app manifest (webApplicationInfo), NOT in Entra app
    registration; a team/chat owner consents when adding the app to THAT team.
```

**Do:**

- Reach for `Sites.Selected` + per-site grants when an app needs a handful of known sites.
- Use Teams RSC (`*.Group` / `*.Chat` scoped permissions, declared in the app manifest) for app access scoped to a single team/chat.
- Note that resource-scoped grants are managed (granted/revoked) at the resource, not just at the app registration.

**Don't:**

- Default to `Sites.ReadWrite.All` / `ChannelMessage.Read.All` when the app touches specific resources.
- Forget the **second step** for `Sites.Selected` — the permission alone grants *nothing* until an admin (or an app with `Sites.FullControl.All`) grants per-site access.
- Assume RSC lives in the Entra portal — RSC permissions are declared in the Teams **app manifest**.

## Edge cases / when the rule does NOT apply

Resource-scoped permissions only exist for a subset of workloads — primarily SharePoint/OneDrive (`Sites.Selected`) and Teams/chats/meetings (RSC) `[verify-at-build]`. For workloads with no scoped variant, a `.All` may be the only option — document it and route to review. An app that genuinely operates across *all* sites/teams (a tenant-wide compliance scanner) is the legitimate `.All` case — but that breadth is what you justify, not what you default to. RSC's consent model differs (resource owner consents at install), so it shifts *who* consents, not just *how much*.

## See also

- [`./identity-least-privilege-permission-selection.md`](./identity-least-privilege-permission-selection.md) — the general least-privilege ladder
- [`./identity-admin-consent-and-the-consent-framework.md`](./identity-admin-consent-and-the-consent-framework.md) — RSC and group-owner consent settings
- [`../knowledge/identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) — consent-required tree
- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — owns scoping; escalates the verdict
- [Understanding Resource Specific Consent for Microsoft Graph and SharePoint Online](https://learn.microsoft.com/sharepoint/dev/sp-add-ins-modernize/understanding-rsc-for-msgraph-and-sharepoint-online) — `Sites.Selected` per-site grants
- [Resource-specific consent for Teams apps](https://learn.microsoft.com/microsoftteams/platform/graph-api/rsc/resource-specific-consent) — Teams RSC

## Provenance

From the Microsoft Learn pages on Resource Specific Consent for SharePoint Online (the `Sites.Selected` + `POST /sites/{id}/permissions` per-site grant flow) and Teams RSC (manifest-declared, owner-consented), plus the permissions-overview RSC section (all retrieved 2026-05-30 via Microsoft Learn MCP). Supports team house opinion #1 (least-privilege). Which workloads expose scoped permissions is volatile — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
