---
name: power-automate
description: Veteran-level reference for Power Automate work — expressions, error handling + scopes, child flows, solution-aware flows + connection references, Dataverse triggers, throttling, approvals, performance patterns. Used by `flow-engineer` (primary) and any agent touching flows.
---

# Power Automate Skill

**Purpose:** Provide veteran-level depth for `flow-engineer` (and any agent touching flows) on design patterns, troubleshooting, solution-aware best practices, expressions, error handling, performance, and integration with the broader Power Platform ALM story.

## When to Use

- Designing or reviewing complex cloud flows (especially solution-aware ones).
- Troubleshooting intermittent failures, throttling, approvals, child flows, or Dataverse trigger issues.
- Needing reference on expressions, run-after configuration, or performance patterns.
- Ensuring flows follow ALM hygiene (connection references, env vars, solution packaging).

## How to Use This Skill

1. Read this `SKILL.md` for the overall playbook and decision framework.
2. Consult specific `resources/*.md` files on-demand for deep reference (expressions, error handling, etc.).
3. Combine with `solution-alm-engineer` guidance for packaging, env vars, and pipelines.

## Core Playbook

### 1. Flow Architecture Principles
- **Top-level Try-Catch-Finally** on every production flow.
- **Child flows** for any reusable logic used 2+ times.
- **Scopes** liberally for readability and targeted error handling.
- Prefer **solution-aware flows** with connection references and environment variables.
- Keep flows lean — refactor large ones into child flows + parent orchestrator.

### 2. Expression & Dynamic Content Mastery
- Use `outputs()`, `body()`, `triggerOutputs()` correctly.
- Compose early and often for intermediate values (makes debugging easier).
- Master `coalesce()`, `if()`, `equals()`, `formatDateTime()`, `split()`, `join()`.
- Avoid hard-coded GUIDs, site URLs, list IDs — move to env vars or parameters.

### 3. Error Handling & Resilience
- Always configure **run after** on failure paths.
- Use parallel branches for independent actions + join.
- Implement retry policies thoughtfully (exponential backoff for transient errors).
- For Dataverse triggers: use proper filter expressions and depth control to avoid infinite loops.

### 4. Performance & Scale
- Increase **Apply to each** parallelism explicitly (often to 50).
- Use batching / Dataverse Web API for bulk operations instead of sequential loops.
- Watch connector throttling limits (consult resources).
- Consider Logic Apps or Azure Functions for very high-volume or complex orchestration.

### 5. ALM & Solution Hygiene (Critical for git/ADO)
- Never hard-code connections — always use **connection references**.
- Use **environment variables** for everything that changes per environment.
- Test import on a fresh environment.
- Keep flow JSON changes reviewable (small, focused changes preferred).

## Recommended Resources (read on demand)
- `resources/expressions-and-dynamic-content.md`
- `resources/error-handling-scopes-child-flows.md`
- `resources/solution-aware-flows-connection-refs.md`
- `resources/dataverse-triggers-best-practices.md`
- `resources/throttling-and-performance.md`

This skill expands the knowledge base for the `flow-engineer` agent and supports the enhanced ALM guidance in `solution-alm-engineer`.