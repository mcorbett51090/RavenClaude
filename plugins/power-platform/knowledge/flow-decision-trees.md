# Power Automate flow decision trees

> **Last reviewed:** 2026-05-30. Canonical multi-tree reference for `flow-engineer`. Format follows [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md). Each tree is traversed **top-to-bottom before selecting a method** — do NOT pattern-match on keywords in the user's situation description; the first branch whose condition resolves cleanly is the leaf to apply.
>
> The PA-flow-*recovery* tree (a flow that's stuck / off / broken after import) lives separately in [`programmatic-flow-creation.md`](programmatic-flow-creation.md) — this file covers *design-time* decisions (which trigger, which surface, reuse, error pattern, programmatic-create approach). Refresh any tree whose `Last verified` is older than ~90 days.

---

## Decision Tree: Triggers — which trigger type?

**When this applies:** You are starting a new cloud flow and must pick its trigger. The observable inputs are: *what kicks it off* (a data change, a person, a clock, an external system) and *where the data lives* (Dataverse, SharePoint, a mailbox, an external API).

**Last verified:** 2026-05-30 against Power Platform release wave 2026.1 (trigger categories: automated / instant / scheduled; Dataverse *When a row is added, modified or deleted*).

```mermaid
flowchart TD
    START[New cloud flow — pick the trigger] --> Q1{Does a data change start it,<br/>or a person/clock/external call?}
    Q1 -->|Data change| Q2{Is the data in Dataverse?}
    Q2 -->|YES| DV["Dataverse: When a row is added,<br/>modified or deleted<br/>(scope + Filter rows + Select columns)"]
    Q2 -->|NO — SharePoint/mailbox/etc| AUTO["Automated trigger for that source<br/>(When an item is created/modified, etc.)<br/>+ trigger condition"]
    Q1 -->|Person initiates| Q3{From a canvas app / button,<br/>or needs typed inputs?}
    Q3 -->|YES| INSTANT["Instant: Power Apps V2<br/>or Manually trigger a flow<br/>(typed inputs)"]
    Q3 -->|NO — called by another system| HTTP["When an HTTP request is received<br/>(premium; secured endpoint)"]
    Q1 -->|Clock / interval| SCHED["Scheduled: Recurrence<br/>(set timezone + interval)"]
```

**Rationale per leaf:**

- *Dataverse trigger (DV)* — when the source is a Dataverse table, the first-party row trigger gives you server-side **Filter rows** (OData) + **Select columns** + **scope** (User/BU/Org), which filter *before* a run is created. **requires:** the trigger's connection reference bound in the target environment.
- *Automated (AUTO)* — for non-Dataverse sources (SharePoint, Outlook, etc.), use that source's automated trigger and add a **trigger condition** to gate runs at the source (see `flow-trigger-conditions-not-runtime-filters.md`).
- *Instant (INSTANT)* — a human (or a canvas app) starts it and you want **typed inputs**; Power Apps V2 / Manually-trigger carry a typed schema the caller fills.
- *HTTP* — an external system calls in; *When an HTTP request is received* is the inbound webhook surface (premium, secure the URL/SAS, validate payload).
- *Scheduled (SCHED)* — time-driven; Recurrence with an explicit timezone (the #1 scheduled-flow bug is a missing/UTC timezone firing at the wrong local hour).

**Tradeoffs summary:**

| Trigger type | Fires on | Filters before run? | Premium? | Use when |
|---|---|---|---|---|
| Dataverse row add/mod/del | A Dataverse row change | YES — Filter rows + Select columns + scope | Dataverse = premium | Source is a Dataverse table |
| Automated (SharePoint/mail/etc.) | A source-system event | Partial — trigger condition only | Depends on connector | Source is a non-Dataverse first-party connector |
| Instant (Power Apps V2 / Manual) | A person / canvas app | n/a | No (unless premium action inside) | Human- or app-initiated, typed inputs |
| When an HTTP request is received | External inbound call | n/a (validate in-flow) | **Yes** | Another system calls the flow as a webhook |
| Scheduled (Recurrence) | A clock / interval | n/a | No | Time-driven batch work |

---

## Decision Tree: Automation surface — cloud flow vs desktop flow (RPA)

**When this applies:** You must automate an interaction with some system and are deciding *how* the flow touches it. Observable input: does the target system expose a programmatic surface (connector / REST / OData / SOAP), or is its UI the only way in?

**Last verified:** 2026-05-30 against Power Automate (cloud) + Power Automate for desktop. RPA licensing/capacity specifics marked volatile.

```mermaid
flowchart TD
    START[Automate an interaction with system X] --> Q1{First-party connector exists for X?}
    Q1 -->|YES| CLOUD["Cloud flow with that connector"]
    Q1 -->|NO| Q2{X has a documented REST/OData/SOAP API?}
    Q2 -->|YES, worth a connector| CUSTOM["Custom connector (OAuth 2.0)<br/>+ cloud flow"]
    Q2 -->|YES, one-off| HTTPACT["HTTP action (premium)<br/>in a cloud flow"]
    Q2 -->|NO — UI is the only surface| Q3{High volume / Azure-governed?}
    Q3 -->|NO| RPA["Desktop flow (RPA) — last resort<br/>unattended + stable selectors + on-error"]
    Q3 -->|YES, belongs in a subscription| AZURE["Hand off to azure-cloud/<br/>integration-engineer (Logic Apps/Function)"]
```

**Rationale per leaf:**

- *Cloud + connector (CLOUD)* — observable, testable, survives vendor UI changes; always first choice when a connector exists.
- *Custom connector (CUSTOM)* — the system has an API but no first-party connector worth reusing; wrap it once in an OAuth-2.0 custom connector. **requires:** an OAuth app registration / API credentials for X.
- *HTTP action (HTTPACT)* — API exists but a full custom connector isn't justified for a single call; the premium HTTP action does it inline. **requires:** premium licensing.
- *Desktop flow (RPA)* — **only** when there is genuinely no programmatic surface; fragile, needs a machine group + gateway, premium/RPA capacity. Build defensively (see `flow-desktop-rpa-is-last-resort.md`). **requires:** RPA capacity + a registered machine/machine-group + gateway.
- *Azure handoff (AZURE)* — if it's high-volume, Bicep/Terraform-governed, and lives in an Azure subscription, it's not a Power Automate flow at all (CLAUDE.md §11).

**Tradeoffs summary:**

| Surface | Fragility | Testable? | Licensing | Use when |
|---|---|---|---|---|
| Cloud flow + first-party connector | Low | Yes | Standard/premium per connector | A connector exists |
| Custom connector + cloud flow | Low | Yes | Premium | Documented API, reusable |
| HTTP action in cloud flow | Low | Yes | Premium | Documented API, one-off |
| Desktop flow (RPA) | **High** — breaks on UI change | Hard | Premium + RPA capacity | No API; UI is the only surface |
| Azure Logic App / Function | Low | Yes | Azure subscription | High-volume, subscription-governed |

---

## Decision Tree: Reuse — child flow vs inline vs other surface

**When this applies:** You have a sequence of actions and must decide whether to inline it, extract it into a child flow, or push it to another platform tier. Observable input: how many call sites reuse it, how big the parent already is, and whether the logic belongs lower on the mechanism ladder.

**Last verified:** 2026-05-30 against Power Automate solution-aware child-flow model (Run a Child Flow).

```mermaid
flowchart TD
    START[A sequence of actions — how to structure it?] --> Q1{Used in 2+ places<br/>OR parent already large/unreviewable?}
    Q1 -->|NO — single use, parent small| INLINE["Inline it<br/>(optionally wrap in a named Scope)"]
    Q1 -->|YES| Q2{Is it pure data shaping<br/>that Power Fx / a formula column could do?}
    Q2 -->|YES — belongs lower on the ladder| LOWER["Power Fx named formula /<br/>Dataverse formula column / plug-in"]
    Q2 -->|NO — it's flow orchestration| Q3{Called per-row inside<br/>a high-iteration loop?}
    Q3 -->|YES| BATCH["Don't child-flow per row —<br/>batch (Dataverse $batch / one call)"]
    Q3 -->|NO| CHILD["Child flow:<br/>typed input + Respond to PowerApp/flow"]
```

**Rationale per leaf:**

- *Inline (INLINE)* — single use in a small parent; a child flow's synchronous round-trip and extra run record aren't worth it. Wrap in a named `Scope` for readability/error-isolation if useful.
- *Lower on the ladder (LOWER)* — if it's pure data shaping, the platform's "lowest-tier mechanism" rule says do it in Power Fx / a formula column / a plug-in, not a flow round-trip.
- *Batch (BATCH)* — reusable but invoked per-row in a big loop; N child-flow calls is N runs against your budget. Collapse to a batch call instead (see `flow-concurrency-and-pagination.md`).
- *Child flow (CHILD)* — genuine reuse (2+ sites) or a parent that's grown unreviewable; extract with a **typed input schema** + **Respond to a PowerApp or flow** output. **requires:** child and parent in the **same solution** (child must be solution-aware to be callable, and inherits the parent's connection references).

**Tradeoffs summary:**

| Choice | Maintenance | Run/latency cost | Review impact | Use when |
|---|---|---|---|---|
| Inline (+ Scope) | Drift risk if copied | None extra | Larger parent | Single use, small parent |
| Power Fx / formula column / plug-in | Lowest (right tier) | None (no flow round-trip) | Logic leaves the flow | Pure data shaping |
| Batch instead of per-row child | One call to maintain | **Far lower** than N calls | Simpler loop | Reusable but per-row in big loop |
| Child flow | One place to fix/test | One sync round-trip per call | Smaller, reviewable parent | Reused 2+ times / big parent |

---

## Decision Tree: Error handling — which resilience pattern?

**When this applies:** You are adding error handling to a flow and choosing the *shape*. Observable input: is this the whole flow, one risky block, or a transient backend fault — and is the failing operation safe to repeat?

**Last verified:** 2026-05-30 against Power Automate / Logic Apps shared runtime (Scope + Configure run after; retry policies Default/Exponential/Fixed/None).

```mermaid
flowchart TD
    START[Add resilience to the flow] --> Q1{Whole-flow structure,<br/>or one risky operation?}
    Q1 -->|Whole flow| TCF["Try-Catch-Finally:<br/>3 top-level Scopes + run-after"]
    Q1 -->|One block among many| Q2{Independent block whose failure<br/>shouldn't abort the rest?}
    Q2 -->|YES| SCOPE["Wrap that block in a Scope<br/>+ Configure run after on its successor"]
    Q2 -->|NO — a single action| Q3{Failure is a transient backend fault?}
    Q3 -->|YES| Q4{"Is the operation idempotent<br/>(safe to repeat)?"}
    Q4 -->|YES| RETRY["Retry policy: Default/Exponential<br/>on that action's Settings"]
    Q4 -->|NO — non-idempotent write| NONE["Retry = None + handle failure<br/>in Catch yourself"]
    Q3 -->|NO — 401/403/404/permission| RUNAFTER["No retry — Configure run after<br/>to a fix/notify path; it's a wall not a fault"]
```

**Rationale per leaf:**

- *Try-Catch-Finally (TCF)* — the mandatory whole-flow scaffold for any production flow: a `Try`, a `Catch` (run-after **has failed / has timed out / is skipped**), a `Finally` (all four). See `flow-error-handling-and-retry-policy.md`.
- *Scope (SCOPE)* — one block whose failure should be contained without aborting the run; wrap it and route its successor's run-after to handle the failure locally.
- *Retry (RETRY)* — a single action hitting a transient 408/429/5xx, and the op is **idempotent**; Default (4 exponential) or a tuned Exponential policy.
- *Retry = None (NONE)* — transient-looking but the op is **non-idempotent** (a `POST` that creates a record); retrying risks duplicates, so disable retry and recover in `Catch`.
- *No retry / run-after (RUNAFTER)* — 401/403/404 are permission/not-found **walls**, not transient faults; retrying just delays the fix. Route run-after to a notify/fix path.

**Tradeoffs summary:**

| Pattern | Scope of protection | Risk if misused | Use when |
|---|---|---|---|
| Try-Catch-Finally | Whole flow | Boilerplate on tiny flows | Every production flow |
| Scope + run-after | One block | Over-nesting | Contain one risky block |
| Retry (Default/Exponential) | One action | Duplicates if non-idempotent | Transient fault, idempotent op |
| Retry = None + Catch | One action | Lost recovery if Catch absent | Transient-looking, non-idempotent write |
| No retry, run-after to fix | One action | Retrying masks the real wall | 401/403/404 permission/not-found |

---

## Decision Tree: Programmatic flow creation — Approach A vs B

**When this applies:** You must create / update / delete cloud flows *programmatically* (a script, not the designer) — typically bulk. Observable inputs: does a service-principal token come back from the PA Management API with a usable `roles` claim, and does the SPN hold Dataverse `System Administrator` (or create/update on the `workflow` table)?

**Last verified:** 2026-05-30 (consistent with [`programmatic-flow-creation.md`](programmatic-flow-creation.md), production lesson May 2026; `pac flow` still does not exist as of `pac` v2.7.4).

```mermaid
flowchart TD
    START[Create/update/delete cloud flows programmatically] --> Q1{PA Management API token<br/>has non-null roles claim<br/>AND Flows.Manage.All consented?}
    Q1 -->|YES — rare in customer tenants| APPROACH_A["Approach A:<br/>PA Management API<br/>(api.flow.microsoft.com)"]
    Q1 -->|NO — 401, roles: null| Q2{"SPN has Dataverse System Admin<br/>(or create/update on workflow table)?"}
    Q2 -->|YES| APPROACH_B["Approach B:<br/>Dataverse Web API<br/>(workflow entity, category=5, type=1)"]
    Q2 -->|NO| ESCALATE["Blocked on permissions —<br/>escalate: request SPN role<br/>or Global Admin consent"]
```

**Rationale per leaf:**

- *Approach A (PA Management API)* — only viable when a Global Admin has consented `Flows.Manage.All` (application permission) to the SPN, so the token carries a usable `roles` claim. Needed regardless for run-history inspection, ownership transfer, and sharing. **requires:** Global-Admin-consented `Flows.Read.All`/`Flows.Manage.All` on the SPN.
- *Approach B (Dataverse Web API)* — the reliable path in real tenants: cloud flows are `workflow` records (`category=5`, `type=1`, `primaryentity="none"`); three calls (`POST /workflows`, `POST /AddSolutionComponent` ComponentType 29, `DELETE /workflows({id})`) do create/bind/delete. The SPN you already use for solution import usually suffices. **requires:** SPN with `System Administrator` (or create/update/delete on the `workflow` + `solution` tables) in the target environment. Watch the two failure modes: `clientdata` must be templated from a **live** record (not a PA export), and dependent-flow GUIDs must be injected after the parent is created.
- *Escalate (ESCALATE)* — neither permission held; this is the Capability Grounding Protocol's "do I have authority?" moment — request the SPN role or Global Admin consent rather than guessing.

**Tradeoffs summary:**

| Approach | Permission needed | Reliability in customer tenants | Covers | Use when |
|---|---|---|---|---|
| A — PA Management API | Global-Admin-consented app permission | Low (usually 401, roles null) | Create + run history + sharing + ownership | App permission genuinely consented |
| B — Dataverse Web API | SPN System Admin (or workflow CRUD) in env | High (same SPN as solution import) | Create / read / update / delete of the workflow record | Default for bulk create/update/delete |
| Escalate | n/a | n/a | n/a | Neither permission held |

The canonical write-up — auth-surface trap, the `clientdata` live-shape gotcha, the GUID-injection rule, and the full bulk-create checklist — is [`programmatic-flow-creation.md`](programmatic-flow-creation.md); the adjacent best-practice is [`../best-practices/create-cloud-flows-via-dataverse-web-api.md`](../best-practices/create-cloud-flows-via-dataverse-web-api.md).
