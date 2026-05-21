---
scenario_id: 2026-05-21-spn-flow-create-403
contributed_at: 2026-05-21
plugin: power-platform
product: dataverse
product_version: "2026.04"
scope: likely-general
tags: [spn, dataverse, application-user, 403, permissions]
confidence: medium
reviewed: false
---

## Problem

Service-principal-authenticated POST to `/api/data/v9.2/workflows` returned HTTP 403 on a customer DEV environment even though the SPN had the System Customizer security role applied at the environment level.

## Permissions context

- Service principal added to the target environment with **System Customizer** role
- SPN was **NOT** added as an Application User in the *target* environment (only at tenant level)
- OAuth flow: `client_credentials` against the Dataverse Web API audience (`https://<env>.api.<region>.dynamics.com/.default`)
- Token was acquired successfully; `roles` claim populated as expected; the 403 surfaced only at the Dataverse API call

## Attempts

- Tried: Re-confirmed the System Customizer role was applied via Power Platform Admin Center → environment → roles → outcome: role visible, still 403
- Tried: Added the SPN to a security group with appropriate permissions, then re-granted the role to the security group → still 403
- Tried: Bumped role to **System Administrator** → still 403
- Tried: Created an explicit **Application User** record in the *target* environment via Power Platform Admin Center (Settings → Users + permissions → Application users → "+ New app user" → selected the SPN → Business Unit → assigned System Customizer) → worked on the next API call

## Resolution

In a Dataverse target environment, an SPN needs **both** the security role **and** an Application User record in that environment. The Application User record is what binds the SPN to the environment's security model. Granting the role at the tenant level (or to a security group) without the Application User record results in a token that authenticates but has no environment-scoped authorization → 403.

**Action for the next consultant hitting this pattern:** before debugging role assignments, confirm the Application User record exists in the target environment. It's the single most likely root cause and it's easy to miss because the Admin Center UI shows the role binding without surfacing the missing Application User.

Cross-reference: the full programmatic-flow-creation lesson is at [`../knowledge/programmatic-flow-creation.md`](../knowledge/programmatic-flow-creation.md) (canonical, reviewed). That knowledge file covers the auth surface in depth; this scenario is the field-note version that surfaces the specific 403 pattern.
