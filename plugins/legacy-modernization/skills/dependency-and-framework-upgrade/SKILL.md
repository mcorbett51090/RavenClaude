---
name: dependency-and-framework-upgrade
description: "Upgrade a stuck dependency, framework, or language version incrementally — one major at a time, on green tests, deprecations resolved between each — instead of a single risky leap. Reach for this when a system is several versions behind."
---

# Skill: Dependency & framework upgrade

A system three majors behind doesn't jump three majors at once.

## Step 1 — Establish the safety net
Ensure characterization/regression tests cover the surface that the upgrade touches (use [`characterization-testing`](../characterization-testing/SKILL.md)). No green baseline → build one first.

## Step 2 — Map the upgrade path
Read each major version's migration guide and breaking-change/deprecation list *between* your current and target versions. The path is a sequence, not a destination.

## Step 3 — Upgrade one major at a time
Bump a single major version, resolve its deprecations and breaks, get tests green, commit. Then the next. Never batch majors — a failure becomes un-bisectable.

## Step 4 — Separate the upgrade from refactors
The version bump is its own change; resist "while I'm in here" refactors in the same commit (§2 #3).

## Step 5 — Verify and pin
Run the full suite and a smoke test of the real app, then pin the new versions. Record the path taken so the next upgrade starts from a known state.

> Re-verify version-specific facts at use — see the dated [`../../knowledge/legacy-modernization-2026-capability-map.md`](../../knowledge/legacy-modernization-2026-capability-map.md). DDL/schema changes inside the upgrade route to `database-engineering`.
