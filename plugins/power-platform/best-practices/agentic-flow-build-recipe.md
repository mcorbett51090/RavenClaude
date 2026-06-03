# When building a cloud flow with an agent, follow the discover → construct → deploy → validate recipe

**Status:** Pattern — a disciplined four-phase sequence for agent-assisted cloud flow construction. Skipping phases produces flows that work in dev and fail in prod on the first real-data run.

**Domain:** Power Automate

**Applies to:** `flow-engineer`, `power-platform-tester`, `solution-alm-engineer`, any agent session that authors or modifies a cloud flow

> **Recipe credit:** the four-phase structure (discover → construct → deploy → validate) is the organizing logic of the **`power-automate-build`** skill shipped by the **Flow Studio MCP** project (https://mcp.flowstudio.app/ · https://github.com/ninihen1/power-automate-mcp-skills, retrieved 2026-06-03). The recipe content here is our own words, wired to this plugin's house rules (§3, §4), the `flow-engineer` agent's standing opinions, and the `power-automate` skill reference. It does not reproduce Flow Studio's skill content.

---

## Why this exists

A cloud flow looks simple until it isn't. An agent that jumps straight to authoring without reading the environment ends up with a flow that uses connections instead of connection references, duplicates an existing trigger, hard-codes environment-specific values, and has no error handling. The four-phase recipe imposes a minimum amount of pre-authoring discovery that closes the most common gaps — and a post-deploy validation step that catches the remainder before a consumer runs it.

The phases are not ceremonies. Each one has a concrete output that the next phase consumes.

---

## Phase 1 — Discover

**Goal:** understand what already exists before writing a single action.

Before authoring anything, read the environment:

1. **Existing solutions** — identify which solution the new flow belongs to. Does it already exist in a solution? Is there a named solution for this workstream? (House rule §3 #1: no flow lives outside a solution.)

2. **Existing connections and connection references** — enumerate the connection references already registered in the target solution. The new flow must bind to an existing connection reference for any connector it uses, not create a new connection. (House rule §3 #3: connection references, not connections.)

3. **The target trigger** — confirm the trigger type and its configuration. For Dataverse triggers: check the table name, the scope, and whether recursion control is needed (see [`flow-dataverse-trigger-recursion-control.md`](./flow-dataverse-trigger-recursion-control.md)). For HTTP triggers: confirm the schema expected.

4. **Environment variables** — identify which values vary across environments (SharePoint URLs, table names, configuration IDs, feature flags). These become environment variable references in the flow, not hard-coded strings. (House rule §3 #2.)

5. **Existing child flows** — check whether a reusable child flow already exists for any repeated logic (approval pattern, notification pattern, data-enrichment step). Duplicating logic that already exists as a child flow is a maintainability debt from day one (see [`flow-child-flows-and-reuse.md`](./flow-child-flows-and-reuse.md)).

**Output of Discover:** a short list — which solution, which connection references, which environment variables, which trigger — that the authoring phase builds on.

---

## Phase 2 — Construct

**Goal:** author the flow body following house rules, not just the happy path.

Build inside a solution from the start. Do not create a flow in My Flows and move it later — that breaks connection references and requires a manual re-wire.

### Structure every production flow with a top-level Try-Catch-Finally

Every production flow gets the three-scope error wrapper before any business logic is added. This is not optional and is not added "later." (House rule §3 #10; see [`flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) for the full pattern.)

### Use connection references, not connections

Every connector action must reference a connection reference (named in the solution), not a direct user or service account connection. This is what makes the flow promotable across environments without credential re-wiring on import.

### Name every action descriptively

Power Automate auto-names actions by type: `Compose`, `Compose_2`, `Apply_to_each`, `Apply_to_each_3`, `Condition`, `Condition_2`, `Scope`, `HTTP`. These names are unreadable in run history, hard to reference in expressions, and break diffability in source-controlled flow JSON. Rename every action to a plain-language description before moving on. (See [`name-flow-actions-descriptively.md`](./name-flow-actions-descriptively.md) — this is the rule the `validate-flow-action-names.sh` hook checks.)

### Apply trigger conditions, not runtime filters

Where the trigger supports conditions, filter at the trigger (before the flow runs) rather than adding a `Condition` as the first action. Runtime filters burn a flow run (and count against your Power Platform request limits) for every item that fails the filter. Trigger conditions are evaluated by the platform before the run starts. (See [`flow-trigger-conditions-not-runtime-filters.md`](./flow-trigger-conditions-not-runtime-filters.md).)

### Set retry policy deliberately on every action

Non-idempotent writes (`POST` that creates a record, a "send" that fires a notification) get retry policy set to **None** explicitly. Reads and idempotent updates can keep Default (4 exponential retries). The decision is made at authoring time, not discovered in prod when a retry creates four duplicate records. (House rule §3 #10; see [`flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md).)

**Output of Construct:** a complete flow JSON in a solution, with error scope, connection references, environment variable bindings, descriptive action names, and a deliberate retry-policy decision on every action.

---

## Phase 3 — Deploy

**Goal:** move the flow to the target environment using managed solution promotion, not manual export-import.

### Deploy to a solution, not as a standalone flow

The flow exists in a solution. Deployment is: export the solution as managed from dev, import managed into test, import managed into prod. (House rules §3 #4: managed in test and prod; §3 #12: source-control the unpacked solution.)

### Bind environment variables and connection references on import

Every import into a non-dev environment requires the consumer to provide:
- **Environment variable values** for the target environment (the solution's environment variable definitions carry no default values in managed imports — they must be set at import time or via a deployment settings file).
- **Connection reference bindings** — the target environment's connection references must be mapped to valid connections before the flow can be turned on.

Document both requirements before handing the solution to `solution-alm-engineer` for packaging. A flow that can't be turned on after import is not done. (See [`alm-connection-references-not-hardcoded-connections.md`](./alm-connection-references-not-hardcoded-connections.md) and [`alm-environment-variables-not-hardcoded-config.md`](./alm-environment-variables-not-hardcoded-config.md).)

### Turn on the flow in the target environment and confirm it is enabled

After import, confirm the flow is in **On** state. A managed flow that was disabled in the source solution imports as disabled in the target — it will not run until explicitly enabled.

**Output of Deploy:** the flow running in the target environment, with correct env-var values and connection-reference bindings, and confirmed in **On** state.

---

## Phase 4 — Validate

**Goal:** prove correctness against real (or realistic) data before declaring done.

### Run-history assertions

Trigger the flow with a known input and inspect the run history for:
- **All actions succeeded** — no skipped actions on the happy path.
- **Catch scope did not execute** — the happy path did not route through error handling.
- **Output values are correct** — the right record was created/updated, the right notification was sent, the right variable carries the expected value.

Use the flow's **Run History** view and the **Monitor** tool in the Power Apps / Power Automate portal to step through action inputs and outputs. (See [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) for the full test discipline.)

### Test the error path

Deliberately trigger a failure (pass invalid input, revoke a connection, point the flow at a non-existent record) and confirm:
- **Catch scope fires.**
- **Run is marked Failed**, not Succeeded.
- **Error details are captured** in the Terminate action's message.

A flow whose Catch scope has never been tested is not validated.

### Fresh-import smoke test

Before any handoff, do a fresh import into a clean environment (or a freshly-reset dev environment) and run the full trigger → run-history assertion cycle again. This catches any dependency on env-specific state that wasn't captured in env vars or connection refs. (House rule §3 #13; see [`alm-fresh-import-smoke-test-before-release.md`](./alm-fresh-import-smoke-test-before-release.md).)

### pac solution check (optional but recommended)

Run `pac solution check` against the solution containing the flow if the engagement has an ALM pipeline or if the solution is going to a production environment with a managed solution policy. It will surface connector policy violations, hard-coded values, and other issues the manual review may have missed. `[unverified — verify current `pac solution check` coverage of flow JSON against your PAC CLI version]`.

**Output of Validate:** a run-history screenshot or log entry confirming happy path + error path + post-import, and a sign-off from `power-platform-tester` if available.

---

## Do

- Run the Discover phase even on a "small" flow — the most common single cause of post-deploy failures is a missing env-var binding discovered at import time.
- Name every action before the Construct phase ends — renaming after the flow is built is mechanically the same work but harder because expressions referencing the old name must also be updated.
- Test the Catch scope deliberately — a Catch scope that has never fired is not validated.
- Hand the validated solution to `solution-alm-engineer` with an explicit list of env variables and connection references the import will need — this prevents import-time surprises.
- Keep the `validate-flow-action-names.sh` hook enabled — it provides immediate feedback during Construct when an auto-generated name sneaks past the review.

## Don't

- Don't start with My Flows and plan to move to a solution later. The re-wire cost is always higher than predicted, and connection references break.
- Don't treat the four phases as strictly sequential when an engagement has a tight loop — Discover and Construct can overlap on large flows. What must not be skipped is the Validate phase and the Catch-scope test.
- Don't declare the flow "done" after a single happy-path run in dev. Done means: happy path confirmed, error path confirmed, fresh-import smoke test passed.
- Don't deploy to prod before test. Managed-in-test-first is a house rule (§3 #4), not a suggestion.
- Don't skip the retry-policy decision with "I'll come back to it." You won't, and the next person won't know what you intended.

---

## Connection to the hook

`validate-flow-action-names.sh` fires on `PostToolUse` for flow JSON edits and flags action keys that end in `_<number>` or match bare default type names (`Compose`, `Compose_2`, `Apply_to_each`, etc.). It is a structural file check that enforces the "Name every action descriptively" step from Phase 2 of this recipe. See [`name-flow-actions-descriptively.md`](./name-flow-actions-descriptively.md) for the full naming rule.

---

## See also

- [`name-flow-actions-descriptively.md`](./name-flow-actions-descriptively.md) — the naming rule this recipe depends on
- [`flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — the Try-Catch-Finally pattern with run-after configuration
- [`flow-connection-references-and-environment-variables.md`](./flow-connection-references-and-environment-variables.md) — how connection references and env vars are wired
- [`flow-trigger-conditions-not-runtime-filters.md`](./flow-trigger-conditions-not-runtime-filters.md) — filter at the trigger, not inside the flow
- [`flow-child-flows-and-reuse.md`](./flow-child-flows-and-reuse.md) — when to extract reusable logic into a child flow
- [`alm-fresh-import-smoke-test-before-release.md`](./alm-fresh-import-smoke-test-before-release.md) — the import smoke test step
- [`alm-connection-references-not-hardcoded-connections.md`](./alm-connection-references-not-hardcoded-connections.md) — connection reference discipline
- [`../knowledge/power-platform-agentic-toolchain-2026.md`](../knowledge/power-platform-agentic-toolchain-2026.md) — where this recipe fits in the broader agentic toolchain
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — the agent that runs this recipe
- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — the agent that owns Phase 4

---

## Provenance

Adapts the four-phase recipe structure from the **Flow Studio MCP `power-automate-build` skill** (https://mcp.flowstudio.app/, retrieved 2026-06-03) in our own words, wired to this plugin's house rules (§3 #1–4, #10, #12–13), the `flow-engineer` agent's standing opinions, and the `power-automate` skill reference. The recipe phases (discover/construct/deploy/validate) are Flow Studio's framing; the specific content of each phase — connection-reference discipline, Try-Catch-Finally structure, retry-policy decision, descriptive action naming, run-history assertions, Catch-scope testing, fresh-import smoke test — is derived from Power Automate and Power Platform ALM primary sources and this plugin's accumulated house rules.

---

_Last reviewed: 2026-06-03 by `claude`_
