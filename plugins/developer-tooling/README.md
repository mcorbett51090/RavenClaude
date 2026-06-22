# developer-tooling

> The **build-tooling layer** for Claude Code — monorepo & build-systems engineering. Answers the questions your CI/CD and app tools punt on: **"which monorepo tool?", "why is the build slow?", "is the cache even safe to trust?", and "how do I upgrade dependencies without breaking everything?"**

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

This is the **build-tooling** layer, deliberately distinct from `devops-cicd` (which owns the CI/CD *pipeline*) and from the application plugins (`backend-engineering` / `frontend-engineering`, which own the *service code*). We pick and tune the build tool, the task graph, the cache, and the dependency policy; the pipeline that *runs* them belongs to `devops-cicd`.

## What it does

| You ask | It returns |
|---|---|
| "Should we adopt Nx / Turborepo / Bazel — or just pnpm workspaces?" | A decision-tree-driven recommendation tied to your language mix, scale, and team appetite — plus what to *not* adopt yet |
| "Our build takes 40 minutes — why?" | A measured task-graph + cache-hit-rate diagnosis, then the highest-leverage fix (affected-only, remote cache, parallelism, splitting) |
| "Is our remote cache actually correct?" | A cache-correctness audit (input hashing completeness, non-hermetic leaks) before any speed tuning |
| "How do we manage versions & lockfiles across the monorepo?" | A version policy (single-version vs independent), lockfile-hygiene rules, and a renovate/dependabot batching strategy |
| "Upgrade React / the toolchain across 30 packages safely" | A staged upgrade runbook: affected blast radius, batching, canary, rollback |

**Two rules it never breaks:** *measure before you migrate*, and *cache correctness before cache speed* — a fast cache that returns wrong artifacts is worse than no cache.

## What's inside

- **2 agents** — `build-systems-architect` (tool selection, build performance, cache architecture, the "do we even need this?" call) and `monorepo-engineer` (hands-on monorepo wiring, task-graph config, workspace protocol, dependency policy, codegen/scaffolding).
- **3 skills** — `choose-monorepo-tooling`, `optimize-build-and-cache`, `manage-dependencies`.
- **2 knowledge files** — a Mermaid monorepo-tooling decision tree, and a build-caching & performance reference (task graph, affected/since, content-addressable + remote caching, hermeticity).
- **2 templates** — a monorepo-adoption plan, and a dependency-upgrade runbook.

## How it seams with the neighbors

```
developer-tooling  →  picks & tunes the build tool, task graph, cache, dep policy
devops-cicd        →  runs them in a pipeline (the CI that calls `nx affected`, the cache backend infra)
backend / frontend →  the service code the build tool builds
cloud plugins      →  the container image / IaC the artifacts deploy into
```

We hand the *pipeline* to `devops-cicd` (it owns the runner config and the remote-cache backend hosting); we own the *build-tool configuration* the pipeline invokes. We hand the *service code* to the app plugins; we own how it's wired into the workspace and built.

## Tooling stance (retrieved 2026-06-21 — re-verify before pinning)

- **JS/TS monorepos:** `pnpm` workspaces as the package-manager spine; `Turborepo` for low-ceremony task caching, `Nx` when you want the richer task graph + generators + module-boundary lint. `Lerna` is largely legacy (now Nx-powered) — not a greenfield default.
- **Polyglot / large-scale / hermetic needs:** `Bazel` (or `Buck2`) when reproducibility and a true content-addressable cache across languages justify the steep config cost; `Moon` as a lighter polyglot task runner.
- **Dependency hygiene:** lockfile committed + verified, ranges pinned per policy, `renovate`/`dependabot` for batched automated upgrades, SBOM + provenance (SLSA) for supply-chain assurance.

Versions and tool-positioning move fast — treat any version-specific claim as carrying its retrieval date and re-verify before it goes in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install developer-tooling@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
