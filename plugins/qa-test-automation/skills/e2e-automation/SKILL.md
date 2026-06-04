---
name: e2e-automation
description: "Write deterministic E2E/integration tests: target resilient role/test-id selectors, wait on conditions never fixed sleeps, isolate and clean up test data, and structure with page objects so a UI change updates one locator."
---

# E2E Automation

**Purpose:** automate the few critical journeys, reliably.

## Selectors
Roles + `data-testid` > brittle CSS/XPath. Request testability from `frontend-engineering`.

## Waiting
**Condition-based** (await element/state/network-idle), never a fixed `sleep` (flaky if short, slow if long).

## Isolation
Each test sets up + tears down its own data; no order-dependence, no shared mutable state.

## Structure
Page objects / fixtures so a UI change touches one locator, not fifty tests.

## Flake
A flaky test is broken: fix determinism or quarantine — never normalize 're-run until green'.
