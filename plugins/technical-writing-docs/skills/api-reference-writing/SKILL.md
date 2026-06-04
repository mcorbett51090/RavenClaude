---
name: api-reference-writing
description: "Write trustworthy developer reference: drive it from the spec (OpenAPI/AsyncAPI) so it can't drift, make every example runnable, document the unhappy path (errors/limits/auth/pagination), and optimize the quickstart for time-to-first-success."
---

# API Reference Writing

## Spec-driven
Generate reference from the OpenAPI/AsyncAPI (api-engineering); enrich with prose + examples. It can't drift from the contract that way.

## Examples run
Test every snippet (or extract from tested code). A failing quickstart example is an active trust-destroyer.

## The unhappy path
Document errors (real shapes), rate limits, auth/scopes, pagination, idempotency — needed exactly when the happy path fails.

## Time-to-first-success
The quickstart's job: zero -> a working call in minutes. Optimize it ruthlessly. READMEs answer what/why/how/where.
