---
name: test-infrastructure
description: "Build trustworthy test infrastructure: factory-based isolated test data, ephemeral per-run environments + service virtualization, automated flaky-test detection/quarantine, parallel sharding, and coverage+mutation reporting in CI."
---

# Test Infrastructure

**Purpose:** keep the suite fast, isolated, trustworthy at scale.

## Test data
**Factories/builders**, per-test, disposable. Shared mutable fixtures are the #1 flake cause.

## Environments
Ephemeral per run (containerized deps, service virtualization for third parties); tear down after. Make **local == CI** by containerizing.

## Flake control
Track pass/fail history; auto-quarantine intermittent failures out of the required gate + assign an owner.

## Speed & quality
Parallelize/shard (isolation is the precondition). Report **coverage (floor) + mutation (truth)** in CI.
