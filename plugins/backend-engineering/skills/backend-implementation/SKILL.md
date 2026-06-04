---
name: backend-implementation
description: "Implement business logic cleanly: keep the framework at the edges with logic in testable use-cases, model errors explicitly (expected vs bug), validate inputs into domain types at the boundary, add idempotency keys for retried operations, and use the outbox for write-then-publish."
---

# Backend Implementation

## Framework at the edges
Logic in plain testable use-cases; HTTP/ORM/framework in thin adapters. A controller full of rules is untestable.

## Errors
Distinguish expected failures (validation/not-found/conflict) from bugs; typed results mapped to status at the edge. No bare catch-all.

## Validate at the boundary
Parse-and-validate inputs into domain types; the core works with valid data.

## Idempotency + outbox
Dedup key for retried work (webhooks/payments/async). **Outbox**: write the event in the same transaction as the state change so you never publish for a rolled-back write.
