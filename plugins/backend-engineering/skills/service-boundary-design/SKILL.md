---
name: service-boundary-design
description: "Decide backend structure: default to a modular monolith, split into services only for a concrete need (scaling, team autonomy, deploy/runtime isolation), draw boundaries by bounded context (each owning its data), and choose sync vs async per seam."
---

# Service Boundary Design

## Default: modular monolith
One deployable, clear internal module boundaries. Split only for: independent **scaling**, **team autonomy**, **deploy isolation**, or a real **tech/runtime** boundary.

## Boundaries follow the domain
Bounded contexts; a service owns a coherent capability **and its data**. A service-per-table is distribution with no benefit; a shared DB across services is a distributed monolith.

## Sync vs async
Sync = couples availability + latency. Prefer **async/events** for work that can be eventual (decouples failure, smooths load). Own the failure model of every boundary (timeout, idempotency, fallback).
