---
description: Build a performant canvas app — delegation-first data access (no non-delegable warnings at scale), an OnStart/OnVisible performance budget, named formulas + With() over repeated work, Patch with defaults + IfError, and a clear canvas-vs-model-driven-vs-code-app call.
argument-hint: "[the app and its main data, e.g. 'field-service app over Work Orders']"
---

# Build a canvas app

You are running `/power-platform:build-canvas-app`. Design or review a canvas app for what the user described (`$ARGUMENTS`), following this plugin's `power-fx-engineer` performance discipline. Canvas apps are easy to build slow; this command builds them fast.

## When to use this

A pixel-controlled or task-focused app is needed. **First, pick the surface** (`apps-model-driven-form-vs-canvas`, `apps-code-app-vs-canvas-tradeoffs`): record-centric CRUD over Dataverse → model-driven (cheaper, governed); highly custom UX → canvas; complex SPA needs → code app. Don't default to canvas reflexively.

## Steps

1. **Delegation first** (`apps-delegation-first-data-access`): every data query must delegate to the source — no client-side filtering of large sets, no non-delegable functions on big tables. Flag each non-delegable warning.
2. **Performance budget** (`apps-canvas-performance-budget`, `apps-form-onload-performance-budget`): minimize OnStart work; defer non-critical loads to OnVisible; cap concurrent calls; measure against the budget.
3. **Named formulas + `With()`** (`apps-power-fx-named-formulas-and-with`): compute once, reuse — don't recompute the same expression across controls.
4. **Write safely** (`apps-patch-with-defaults-and-iferror`): `Patch` with `Defaults()` for create, wrap in `IfError` for resilient writes.
5. **Business rules before JavaScript/PCF** (`apps-business-rules-before-javascript`); reach for **PCF only when justified** (`apps-pcf-when-to-build`, `apps-react-virtual-controls-default`, `apps-pcf-lifecycle-and-cleanup`).

## Guardrails

- A non-delegable query over a large table is a defect, not a warning to dismiss.
- Don't put heavy work in OnStart — it's the app's load-time tax.
- Keep the app solution-aware with connection references; never hardcode connections.
