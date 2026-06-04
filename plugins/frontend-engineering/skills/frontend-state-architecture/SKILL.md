---
name: frontend-state-architecture
description: "Architect frontend state: treat server data as a cache (TanStack Query/SWR/RSC), place client state at the narrowest workable scope (local -> context -> store), invalidate deliberately, use optimistic updates with rollback, and derive rather than duplicate."
---

# Frontend State Architecture

## Server state != client state
API data is a **cache** -> TanStack Query / SWR / RSC (revalidation, loading/error free). **Never** put server data in a global store — that's the classic staleness bug.

## Client state scope
Local -> context (small shared tree) -> store (Zustand/Redux) **only** for genuinely global cross-cutting state. Don't globalize by default.

## Mutations
Define what each mutation invalidates; optimistic update + **rollback** on failure.

## Derive, don't duplicate
Compute derived values in render; stored derived state desyncs.
