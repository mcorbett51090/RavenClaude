---
scenario_id: 2026-06-05-slow-build-cache-strategy
contributed_at: 2026-06-05
plugin: devops-cicd
product: github-actions
product_version: "unknown"
scope: likely-general
tags: [build-cache, cache-key, docker-layer, monorepo, ci-speed]
confidence: high
reviewed: false
---

## Problem

A monorepo's CI ran ~22 minutes per PR even for a one-line README change, because every pipeline rebuilt every service's container image and re-installed every dependency from scratch. The team had "added caching" — an `actions/cache` step keyed on a static string — but the cache hit rate was near zero and nobody knew why. The ask was "make CI fast"; the instinct was to throw a bigger runner at it.

## Context

- GitHub Actions, a monorepo with ~8 services, each a multi-stage Dockerfile, plus a shared dependency-install step.
- Constraint: the existing cache key was a **constant** (`key: deps-cache`), so the cache was written once and then never invalidated — every install after a dependency change silently served a **stale** cache, and CI papered over it by reinstalling anyway. A cache that never invalidates is worse than no cache: it's a correctness risk that also doesn't save time.
- The Dockerfiles installed dependencies **after** copying the full source, so every source change busted the dependency layer — Docker layer cache was structurally defeated.

## Attempts

- Tried: a bigger runner (4-core → 16-core). Cut ~22 min to ~16 min but cost 4x per minute and didn't address the cause — the work was redundant, not under-resourced. Rejected as the primary fix.
- Tried: fixing the cache key to **encode every input**, per the **"cache keys must encode every input"** best-practice and the build-cache reasoning in [`../knowledge/devops-cicd-decision-trees.md`](../knowledge/devops-cicd-decision-trees.md). Keyed the dependency cache on a hash of the lockfile (`hashFiles('**/package-lock.json')`) with a restore-key fallback prefix, so a lockfile change invalidates cleanly and an unchanged lockfile hits.
- Tried: reordering the Dockerfiles to **copy the lockfile and install deps before copying source** (the classic layer-cache ordering), so a source-only change reuses the cached dependency layer.
- Tried (the move that worked together): added **change-detection** so a README-only PR builds/tests **only the affected service graph**, not all 8 services. Combined with the fixed cache key and the Dockerfile layer reorder, a docs PR dropped to ~3 minutes and a single-service change to ~6.

## Resolution

**Caching only helps when the key encodes every input and the cache is structurally reachable; otherwise it's a stale-data risk that also wastes time.** The three compounding fixes — a content-addressed cache key (lockfile hash, not a constant), Dockerfile layer ordering that puts the slow-changing dependency install before the fast-changing source copy, and affected-only execution so unrelated services don't rebuild — turned a flat 22-minute pipeline into one that scales with the size of the change. The bigger runner addressed none of these.

**Action for the next engineer:** before resizing the runner, audit the cache key (does it change when the cached content's inputs change? does it hit when they don't?) and the Dockerfile layer order (are slow-changing layers above fast-changing ones?). A constant cache key is a latent stale-cache bug. In a monorepo, affected-only execution is the price of admission — a pipeline that rebuilds everything on every commit is the worst of both worlds. Cross-reference [`../best-practices/build-cache-keys-must-encode-every-input.md`](../best-practices/build-cache-keys-must-encode-every-input.md), [`../best-practices/build-monorepo-pipelines-must-be-change-scoped.md`](../best-practices/build-monorepo-pipelines-must-be-change-scoped.md), and [`../best-practices/artifact-image-layer-hygiene.md`](../best-practices/artifact-image-layer-hygiene.md).

**Sources:** `actions/cache` keying + `hashFiles()` and `restore-keys` fallback semantics per the [GitHub Actions caching docs](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows) `[verify-at-use]`; Docker layer-cache ordering per the [Dockerfile best-practices](https://docs.docker.com/build/building/best-practices/) `[verify-at-use]`. Timings (22/16/6/3 min) are illustrative; validate against the team's actual pipeline.
