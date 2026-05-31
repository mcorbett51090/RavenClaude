---
description: Scaffold a Power Automate cloud flow the right way — pick the trigger with trigger conditions (not runtime filters), use connection references + environment variables (never hardcoded), add error handling/retry + concurrency/pagination, and reach for child flows for reuse. Recommends the Dataverse Web API creation path.
argument-hint: "[what the flow should do, e.g. 'on Account create, notify owner']"
---

# Scaffold a cloud flow

You are running `/power-platform:scaffold-cloud-flow`. Design a Power Automate cloud flow for what the user described (`$ARGUMENTS`), following this plugin's `flow-engineer` discipline. The goal is a flow that's source-controllable, environment-portable, and resilient — not one that only works in the dev environment it was clicked together in.

## When to use this

A new automation is needed. If the logic is same-record Dataverse field work, consider a **business rule or low-code plug-in** first (`dataverse-where-to-enforce-logic`); if it's desktop UI automation, treat **RPA as a last resort** (`flow-desktop-rpa-is-last-resort`).

## Steps

1. **Trigger + trigger conditions** (`flow-trigger-conditions-not-runtime-filters`): filter at the trigger, not with a downstream Condition — an unfiltered trigger that bails at runtime still consumes runs.
2. **Recursion control** for Dataverse triggers (`flow-dataverse-trigger-recursion-control`) so an update-in-the-flow doesn't re-fire the flow.
3. **Connection references + environment variables** (`flow-connection-references-and-environment-variables`, `alm-connection-references-not-hardcoded-connections`, `alm-environment-variables-not-hardcoded-config`): never hardcode a connection or config value — they must travel through ALM.
4. **Error handling + retry policy** (`flow-error-handling-and-retry-policy`): configure run-after fault paths and a sensible retry policy on each external action.
5. **Concurrency + pagination** (`flow-concurrency-and-pagination`): set the right concurrency; enable pagination on list actions that can exceed the default page.
6. **Null-safe expressions** (`flow-compose-and-null-safe-expressions`) and **child flows for reuse** (`flow-child-flows-and-reuse`).
7. If creating the flow programmatically, use the **Dataverse Web API** path (`create-cloud-flows-via-dataverse-web-api`), not the PA Management API.

## Guardrails

- Never hardcode a connection or secret in the flow — connection reference + Key Vault (`alm-secrets-in-key-vault-not-env-var-defaults`).
- Filter at the trigger, not at runtime.
- Tee up the solution-aware export/import; the flow must live in a solution, not the default environment.
