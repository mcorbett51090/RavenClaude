# Dataverse — the "Active-layer dependency" managed-export trap (don't delete-and-recreate)

> **Last reviewed:** 2026-06-11. Source: a production managed-ALM session (Contoso-style DEV-unmanaged → TEST/PROD-managed pipeline; org/repo identifiers removed). A managed export failed on a hard dependency on the **Active** solution; the fix attempt **deleted and recreated 19 entities — twice** before the real, no-delete fix was found. This file captures the verified root cause so the next agent skips the rabbit hole. Refresh when the Dataverse Web API metadata surface or the `AddSolutionComponent` message shape changes.
>
> **Claim-grounding note.** The four load-bearing facts below are verified against Microsoft Learn (retrieved 2026-06-11): the `RootComponentBehavior` enum values, the `DoNotIncludeSubcomponents` semantics, that unmanaged components are *always* added to the default solution, and the `MSCRM.SolutionUniqueName` create-context mechanism. Each is cited inline. The one claim that is **observed, not documented** — that `POST /EntityDefinitions?solutionUniqueName=` yields `behavior="1"` specifically — is marked `[unverified — observed in the source session, not in the docs]`.
>
> **When to read this file.** A **managed solution import fails with a `MissingDependency` on `solution="Active"`** (`canResolveMissingDependency="False"`), OR you're about to **delete and recreate a Dataverse table/column "to move it out of the Active layer."** Stop before the delete — that is almost always the wrong move, and this file is why.

---

## 1. The symptom

A solution exported as **managed** from DEV imports into a managed-only environment (TEST/PROD) and the import **aborts**. The `solution.xml` inside the ZIP contains:

```xml
<MissingDependency canResolveMissingDependency="False">
  <Required type="1" schemaName="new_thing" solution="Active" />
  <Dependent type="1" schemaName="new_thing" />
</MissingDependency>
```

Read literally: *"`new_thing` must already exist in the **Active** (unmanaged) solution of the target environment before this import can proceed."* TEST has no Active layer (it's managed-only), so the dependency can't resolve and the import fails.

## 2. The rabbit hole — "delete and recreate to move it out of Active"

The intuitive (and wrong) reading is: *"the entity's canonical home is the Active layer; I must physically relocate it into the named solution — so delete it and recreate it inside `MySolution`."* This drove two rounds of delete+recreate in the source session, costing hours of rebuilding picklist options, lookups (`RelationshipDefinitions`), and option-set conflicts — and it **did not fix the export.**

**Why it's wrong — verified.** In a DEV (unmanaged) environment, **every unmanaged component is *always* in the default/Active solution.** That's the definition of "unmanaged," not a defect to escape:

> "All tables are **automatically added to the default solution**. However, when you use this optional property, you **also** add the table as a solution component to the specified unmanaged solution." — [`CreateEntityRequest.SolutionUniqueName`](https://learn.microsoft.com/dotnet/api/microsoft.xrm.sdk.messages.createentityrequest.solutionuniquename)

So "relocate the component *out of* Active" is a **non-goal that cannot be achieved** while the component is unmanaged. The `?solutionUniqueName=` / `MSCRM.SolutionUniqueName` create-context adds **named-solution membership on top of** default membership ([Web API create-context](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/create-update-entity-definitions-using-web-api)) — it never suppresses the default membership. Deleting to escape Active chases a goal that doesn't exist.

## 3. The real lever — `RootComponentBehavior` (and why the *old* entities worked)

The actual determinant of a self-contained managed export is **not** which layer the component lives in — it's the **`RootComponentBehavior`** on the *solution-component record* in the manifest. Verified enum ([SolutionComponent reference](https://learn.microsoft.com/power-apps/developer/data-platform/reference/entities/solutioncomponent#read-only-columns-attributes)):

| Value | Label | Meaning for a managed export |
|---|---|---|
| **0** | **Include Subcomponents** | Entity **and all its subcomponents** (attributes, forms, views, relationships) are packaged into the ZIP — **self-contained.** This is what a *new* component needs. |
| 1 | Do not include subcomponents | Entity shell only; subcomponents must already exist in the target. |
| 2 | Include As Shell Only | Even less than 1 — the bare shell. |

> **Correction to a common mental model:** `behavior="2"` is **"Include As Shell Only," not "fully owned."** Old, working entities in the source session showed `behavior="2"` — but they didn't work *because* `2` means ownership. They worked because **they already exist as managed components in TEST from a prior import**, so a shell reference resolves against TEST's managed layer. The *new* entities at `behavior="1"` broke because their subcomponents existed **only in DEV's Active layer and nowhere in TEST** — there was nothing for the shell to resolve against. The `Required solution="Active"` dependency is the symptom of a shell (`1`/`2`) reference to subcomponents that have no managed home in the target.

## 4. The fix — `AddSolutionComponent` with `DoNotIncludeSubcomponents=false` (no delete)

Set the component's behavior to **0 (Include Subcomponents)** on the **existing** component — in place, no deletion:

```http
POST /api/data/v9.2/AddSolutionComponent
{
  "ComponentId": "<entity MetadataId>",
  "ComponentType": 1,
  "SolutionUniqueName": "MySolution",
  "AddRequiredComponents": false,
  "DoNotIncludeSubcomponents": false   // ← false => behavior=0 (subcomponents INCLUDED)
}
```

This rewrites the RootComponent to `behavior="0"` and removes the `Required solution="Active"` self-dependency, making the managed export self-contained. **No entity was deleted.** The same call would have fixed the *original* entities directly — the deletes were never necessary.

> **Documentation footgun (read this).** [`AddSolutionComponentRequest.DoNotIncludeSubcomponents`](https://learn.microsoft.com/dotnet/api/microsoft.crm.sdk.messages.addsolutioncomponentrequest.donotincludesubcomponents) has a **confusingly-worded Learn page** whose "Property Value" text reads backwards ("`true` if you want subcomponents to be included"). Trust the **property name + the empirical result**: `DoNotIncludeSubcomponents=false` ⇒ *do not [not include]* ⇒ **subcomponents included** ⇒ `behavior=0`. That is the verified-by-export behavior from the source session.

## 5. Correct procedure going forward

When creating Dataverse tables/columns via the Web API that you intend to ship in a named solution:

1. **Create *with* solution context** — the `MSCRM.SolutionUniqueName` request header (or the `?solutionUniqueName=` query parameter) on `POST /EntityDefinitions`. This adds named-solution membership at create time. ([SDK: without it, the component is "only added to the default solution and you must add it to a solution manually."](https://learn.microsoft.com/power-platform/alm/solution-api))
2. **Then register with subcomponents included** — `AddSolutionComponent` with `DoNotIncludeSubcomponents=false` (⇒ `behavior=0`), so the managed export packages the whole component.

`?solutionUniqueName=` **alone is not sufficient** for a self-contained export — `[unverified — observed in the source session, not in the docs]` it lands the component at `behavior="1"` (shell), so the `behavior=0` follow-up is what tells Dataverse "this solution **owns** this component" vs "it must come from Active."

**Better default — the maker portal.** Create the component **in the portal with the target solution selected**; the portal's **Add Required Components** dialog does the `behavior=0` inclusion for you ([Create a solution and add components](https://learn.microsoft.com/dynamics365/customerengagement/on-premises/customize/create-solution#add-solution-components)). Reserve the Web API recipe for headless/scripted creation.

## 6. The general lesson (and where it lives)

The deletes were an irreversible, high-cost activity launched on an **unverified premise** ("layer membership must be physically relocated") that one doc-read would have falsified. That is the canonical case study for the core discipline **[Verify the load-bearing assumption before a high-impact activity](../../ravenclaude-core/CLAUDE.md)** — name the assumption, verify it (here: the `RootComponentBehavior` enum + the "always in default solution" fact), and prefer the smaller-blast-radius path (an in-place `AddSolutionComponent`) before the irreversible one (delete + recreate). The Dataverse mechanics are this file; the general discipline is the constitution.

## See also

- [`dataverse-http-error-attribution.md`](dataverse-http-error-attribution.md) — a 401/403/404 is access/auth/routing, not "the field is missing" (the verify-the-axis sibling discipline).
- [`model-driven-app-update-paths.md`](model-driven-app-update-paths.md) — the "**unmanaged solution import is irreversible**" gotcha (the same managed-ALM blast-radius family).
- [`dataverse-token-acquisition.md`](dataverse-token-acquisition.md) — the bearer-token decision tree these Web API calls assume you already hold.
