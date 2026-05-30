# Create cloud flows programmatically through the Dataverse Web API, not the PA Management API

**Status:** Primary diagnostic — when an SPN gets HTTP 401 from `api.flow.microsoft.com`, switch surfaces; don't retry auth.

**Domain:** Power Automate / ALM

**Applies to:** `power-platform`

---

## Why this exists

The natural path for bulk cloud-flow creation — the [Power Automate Management API](https://learn.microsoft.com/en-us/connectors/flowmanagement/) at `https://api.flow.microsoft.com` — is **almost always blocked for service principals in real customer tenants.** It enforces Azure AD *application* permissions (`Flows.Read.All` / `Flows.Manage.All`) that require Global Admin consent, and the common misstep of adding the *delegated* versions does nothing for the `client_credentials` flow. The trap is the confident next inference: "so cloud flows can't be created programmatically." That is **false** — modern cloud flows are Dataverse `workflow` records, and the same SPN you already use for solution import can create them without any new grant. There is no `pac flow` command (verified `pac` v2.6.4 / v2.7.4), so the Dataverse Web API is the escape hatch, not the CLI.

## How to apply

Cloud flows are `workflow` entity records with `category = 5`, `type = 1`, `primaryentity = "none"`. Three Dataverse Web API calls do the whole job:

```http
POST   /api/data/v9.2/workflows               # create the flow (clientdata = JSON string)
POST   /api/data/v9.2/AddSolutionComponent    # bind to a named solution, ComponentType = 29
DELETE /api/data/v9.2/workflows({fid})        # clean up on rerun
```

```json
{ "name": "Flow Display Name", "category": 5, "type": 1,
  "primaryentity": "none", "clientdata": "<JSON string — pulled from a WORKING flow record>" }
```

**Do:**
- Pull the `clientdata` template by GET-ing a working flow record — `connectionReferenceLogicalName` lives under a `connection` sub-object, **not** at the top level (the PA-export shape imports clean but fails at runtime).
- `AddSolutionComponent` (ComponentType 29) immediately after each create, or the flow lands in the default solution and won't promote.
- Assert no `<PLACEHOLDER>` / `{{...}}` / `TODO` residue remains in the serialized `clientdata` before POST — a leftover placeholder creates a flow that runs silently broken.
- For dependent flows, create the parent first, capture its GUID, inject it into the child's `clientdata`, then create the child.

**Don't:**
- Retry auth against `service.flow.microsoft.com` when the token's `roles` claim is `null` — that's a permission wall, not a transient failure.
- Treat a PA Management API export JSON as a drop-in `clientdata` source.

## Edge cases / when the rule does NOT apply

- **Run-history inspection, ownership transfer, sharing with named users/groups, and some trigger-state changes** still need the PA Management API or portal — the Dataverse path covers create/read/update/delete/list of the workflow record itself.
- If the customer's Global Admin **has** granted the application permissions for a specific scenario, the PA Management API is fine for that scenario.

## See also

- [`../knowledge/programmatic-flow-creation.md`](../knowledge/programmatic-flow-creation.md) — the full trap, `clientdata` shape, GUID-injection rule, and bulk-create checklist
- [`../knowledge/dataverse-token-acquisition.md`](../knowledge/dataverse-token-acquisition.md) — how to acquire the Dataverse bearer token before any of this
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) · [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — owners of the flow + ALM surfaces

## Provenance

Extracted from [`../knowledge/programmatic-flow-creation.md`](../knowledge/programmatic-flow-creation.md) (production lesson: ~136 cloud flows created in a customer DEV environment, May 2026). The 401-is-a-wall-not-a-retry framing is the canonical Capability Grounding Protocol case in [`../CLAUDE.md`](../CLAUDE.md) §5.

---

_Last reviewed: 2026-05-30 by `claude`_
