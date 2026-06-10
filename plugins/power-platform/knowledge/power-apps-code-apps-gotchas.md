# Power Apps Code Apps — Production Gotchas

> **Last reviewed:** 2026-06-10
> **Source:** Alexander Siedler (zyborc — github.com/zyborc/power-apps-code-apps-skill; blog 2026-03) — hard-won production lessons credited here in full.
> **Subsumption check:** 2026-06-10 against `microsoft/power-platform-skills` code-apps plugin (verified via rc-deep-research harness run `wf_e0543b9a-dde`, 104 agents). Gotchas 1 and 2 confirmed **absent** from Microsoft's official skill at that date.
>
> **Refresh triggers:**
>
> - Re-check `microsoft/power-platform-skills` before relying on "MS doesn't cover this" — Microsoft iterates weekly.
> - Re-check SDK version and CLI state after any `@microsoft/power-apps` release ≥ 1.0.4 (npm CLI is now the primary path — see §SDK note below).
> - Re-check Gotcha 2 (header mangling) after any PAC CLI upgrade or after migrating to the npm CLI.

---

## SDK / CLI state [verify-at-use]

Code Apps are **PREVIEW** as of 2026-06-10 [verified: Microsoft Learn, `power-apps/developer/code-apps/overview`].

Starting with `@microsoft/power-apps` ≥ **1.0.4**, the SDK ships a new **npm-based CLI** that **replaces** `pac code` commands:

| Old (deprecated) | New npm CLI |
| --- | --- |
| `pac code init` | `power-apps init` |
| `pac code run` | `power-apps run` (or `npm run dev`) |
| `pac code push` | `power-apps push` |
| `pac code add-data-source` | connector commands pending GA (Wave 1 2026) |

`pac code` still works today but will be removed in a future PAC CLI release [verified: Microsoft Learn `pac code` reference page]. The existing `power-apps-code-apps` skill still documents `pac code` patterns — treat them as valid but note this transition.

---

## Gotcha 1 — People-Picker: UPN ≠ Email; Claims string required

**Read when:** building or debugging a SharePoint Person/Group column write from a Code App, or any feature that must assign a SharePoint item to a specific user.

### The problem

`getContext()` returns `context.user.userPrincipalName` (a UPN such as `alice@contoso.com`). A SharePoint **Person or Group** column does **not** accept a raw UPN or email string — it requires the **claims identity string** in the form:

```
i:0#.f|membership|<upn>
```

Passing the raw UPN silently produces a 201/200 response but leaves the person field blank or incorrectly resolved. No error is thrown.

### The fix

```typescript
import { getContext } from "@microsoft/power-apps/app";
import { Office365UsersService } from "./generated/services/Office365UsersService";

// Step 1 — resolve UPN via the Office365Users connector
// (more reliable than context.user.userPrincipalName for guest/alias tenants)
const ctx = await getContext();
const profile = await Office365UsersService.MyProfile_V2();
const upn = profile.data?.userPrincipalName ?? ctx.user.userPrincipalName;

// Step 2 — build the claims string SharePoint expects
const claimsString = `i:0#.f|membership|${upn}`;

// Step 3 — write to the Person/Group field
const payload = {
  Title: "My Item",
  AssignedTo: { Claims: claimsString },
};
await MyListService.create(payload as Omit<MyList, "ID">);
```

**Why `MyProfile_V2()` instead of `getContext()` directly?**
In some tenants the Entra UPN and the SharePoint claims UPN diverge (guest accounts, domain aliases, federated identity). `Office365UsersService.MyProfile_V2()` resolves the UPN as the SharePoint connector sees it — safer for claims string construction.

**Prerequisites:**

- `Office365Users` connector must be added as a data source (`pac code add-data-source --dataset Office365Users`).
- The Office365Users connector is **premium** — end users need a Power Apps Premium license. Flag this at design time.

**Source:** Alexander Siedler (zyborc), `power-apps-code-apps-skill`. Verified absent from `microsoft/power-platform-skills` `add-sharepoint` skill 2026-06-10. [verify-at-use]

---

## Gotcha 2 — Copilot Studio connector: `x-ms-conversation-id` mangled to underscores

**Read when:** integrating a Code App with a Copilot Studio bot via `pac code add-data-source` and multi-turn conversation tracking is broken (the bot forgets context on every message).

### The problem

`pac code add-data-source` generates `MicrosoftCopilotStudioService.ts` from the connector schema. The PAC CLI code generator **converts hyphens to underscores** in property names. The critical header becomes:

```typescript
// GENERATED — BROKEN
x_ms_conversation_id: conversationId, // underscore → wrong
```

The Copilot Studio backend requires `x-ms-conversation-id` (hyphen). With underscores the header is silently dropped. Every call is treated as a new conversation — stateful multi-turn bots fail without any runtime error.

### The fix

After `pac code add-data-source`, open `generated/services/MicrosoftCopilotStudioService.ts` and rename the field in both the method signature and the underlying request:

```typescript
// FIXED — rename after generation
"x-ms-conversation-id": conversationId, // hyphen → correct
```

> **Re-generation hazard.** If you re-run `pac code add-data-source` for this connector the mangling reappears. Add a code comment at the fix site and a step to your project's setup runbook.

**Status:** Code-generator bug in `pac code`. [verify-at-use] — A future PAC CLI release or the new npm CLI may preserve hyphens; test after any CLI upgrade before assuming the fix is still needed.

**npm CLI note:** The new `power-apps` npm CLI (≥1.0.4) takes over connector management as the `add-data-source` equivalent lands. Whether it replicates the same mangling is **[unverified — verify-at-use]** until the connector commands reach GA.

**Source:** Alexander Siedler (zyborc), `power-apps-code-apps-skill` / `copilot-studio.md`. Verified absent from `microsoft/power-platform-skills` `add-mcscopilot` skill 2026-06-10. [verify-at-use]

---

## Gotcha 3 — SharePoint Choice-field payload format [unverified — contested]

> **⚠️ This item is CONTESTED — do not treat either form as fact without testing.**
>
> zyborc documents a `{Value: "string"}` wrapper. Microsoft Learn's official Code Apps SharePoint page (fetched 2026-06-10, `how-to/sharepoint-operations`) shows passing the **full expanded object** from `getReferencedEntity()` (contains both `Id` and `Value`). A third form — plain string — is referenced in other contexts. The failure mode across all wrong forms is **silent** (the SharePoint connector returns a success code but the field is not written). Verify in your specific environment and PAC CLI / SDK version before shipping.

### Form A — zyborc's approach (not independently confirmed against MS Learn)

```typescript
const payload = {
  Title: "My Item",
  ChoiceColumn: { Value: "Option1" },
};
```

### Form B — Microsoft Learn's documented approach [verified 2026-06-10]

Retrieve choices via `getReferencedEntity()`, then pass the full returned object:

```typescript
// Retrieve available choices
const res = await MyListService.getReferencedEntity("", "ChoiceColumn");
const dataArray = (res.data as { value?: unknown[] })?.value ?? res.data;
const options = Array.isArray(dataArray) ? dataArray : [];
// Each option has shape { Id: number, Value: string, ... }

// Pass the full object in create/update
const choiceObj = (options as { Id: number; Value: string }[]).find(
  (o) => o.Value === "Option1"
);
const payload = {
  Title: "My Item",
  ChoiceColumn: choiceObj, // full object: { Id: N, Value: "Option1", ... }
};
await MyListService.create(payload as Omit<MyList, "ID">);
```

**Why contested:** Whether Form A (`{Value: "..."}`) or Form B (full expanded object) is required may depend on the SharePoint connector version, the PAC CLI version, and whether the column is single-select or multi-select Choice. When in doubt, use Form B (Microsoft Learn's documented pattern) and check the `getReferencedEntity` response shape in your environment.

**Source:** Original gotcha documented by Alexander Siedler (zyborc), `sharepoint.md`. Form B from Microsoft Learn `how-to/sharepoint-operations` fetched 2026-06-10. Contested discrepancy flagged in RavenClaude research brief `docs/research/2026-06-10-power-platform-cluster1-deepening/report.md` Find 4.
