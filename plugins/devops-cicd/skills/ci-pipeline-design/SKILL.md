---
name: ci-pipeline-design
description: "Design a fast, deterministic CI pipeline: stage ordering by cost, dependency/build caching keyed on the lockfile, build matrices and test sharding, required-check contracts for branch protection, and SHA-pinned third-party actions."
---

# CI Pipeline Design

**Purpose:** turn a repo into a fast, trustworthy CI pipeline.

## The ordering rule
Gate cheapest-first: `format -> lint -> typecheck -> unit -> build -> integration -> e2e`. A red cheap gate must never wait on an expensive one.

## Caching
- Dependency cache keyed on the **lockfile hash** (restore, install, save).
- Build cache keyed on its **inputs**.
- A cache that is never invalidated is a correctness bug — key it on what actually changes the output.

## Parallelism & required checks
- Matrix across versions/OS; **shard** slow suites.
- A single aggregating required check fans-in the matrix so branch protection stays simple.
- Never make a **flaky** job required — quarantine it.

## Supply chain inside the pipeline
Pin third-party actions to a **SHA**, not a moving tag. Use OIDC to the cloud, never a long-lived key in a CI variable.
