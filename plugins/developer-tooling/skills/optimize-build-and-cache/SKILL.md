---
name: optimize-build-and-cache
description: "Diagnose and fix a slow build by measuring the task graph and cache-hit rate, auditing cache CORRECTNESS (input-hash completeness, hermeticity leaks) before any speed tuning, then applying the highest-leverage fix (affected-only, remote cache, parallelism, splitting the long pole). Reach for this when the user says 'the build is slow' or 'is remote caching worth it / even correct?'. Used by `build-systems-architect` (primary)."
---

# Skill: optimize-build-and-cache

> **Invoked by:** `build-systems-architect` (primary). Also consulted by `monorepo-engineer` when validating a graph/cache it just wired.
>
> **When to invoke:** "our build/CI is slow"; "is remote caching worth it?"; "is our cache correct?"; "why didn't this rebuild / why did everything rebuild?".
>
> **Output:** a measured diagnosis (task graph + cache-hit rate + the long pole), a cache-correctness verdict *before* any speed work, then the single highest-leverage fix with its expected payoff.

## Procedure

1. **Measure, don't guess.** Capture the baseline before touching anything (see the measurement playbook in [`../../knowledge/build-caching-and-performance.md`](../../knowledge/build-caching-and-performance.md)):
   - total build/CI wall-clock and the **per-task timing** (find the long pole — it's rarely "the whole build"),
   - **cache-hit rate** (local and remote, cold vs warm),
   - **affected-graph size** for a typical PR (how much *should* rebuild vs how much does).
2. **Validate the task graph.** Confirm the graph's edges match reality. A missing edge → a dependent silently doesn't rebuild (correctness bug); a spurious edge → over-rebuilding (perf bug). Fix the graph before anything downstream — caching and affected-only both derive from it.
3. **Audit cache CORRECTNESS before cache SPEED.** This gate is non-negotiable. Check:
   - **input-hash completeness** — does the cache key include every input that affects output (source, deps, tool version, config, env that matters)? Missing inputs → stale-cache-returns-wrong-artifact.
   - **hermeticity leaks** — timestamps, absolute/machine paths, network fetches mid-build, unpinned tool versions, locale. Each is a non-determinism that poisons cache trust.
   - A cache that can return a wrong artifact is **worse than no cache** — fix correctness first or disable the cache.
4. **Pick the single highest-leverage fix** against the measured long pole, cheapest-first:
   - **affected/since-only** builds (stop rebuilding untouched packages) — usually the biggest early win,
   - **local caching** of cacheable tasks (correct keys first),
   - **parallelism** across independent graph branches,
   - **remote caching** (share artifacts across CI runs + devs) — only after correctness passes; weigh CI-minutes saved vs backend cost/operational surface,
   - **split / re-architect the long pole** task if it's un-cacheable by nature.
5. **Re-measure and report the delta** — payoff vs the baseline from step 1. Name the seam: `devops-cicd` owns hosting the remote-cache backend and the runner config; this skill owns the build-tool configuration.

## Worked example

> User: "We turned on Turborepo remote caching but builds are still slow and sometimes ship stale output."

- **Stale output is a red flag — stop and audit correctness (step 3) before any speed work.** Likely an incomplete cache key: e.g. an env var or a generated file that affects output isn't in the hashed inputs, so a changed input reuses a stale artifact.
- Fix: bring the missing input into the hash (e.g. declare the env/global dep in `turbo.json` `globalDependencies` / task `inputs`), or eliminate the non-determinism.
- Only then chase speed: measure per-task timing, confirm affected-only is on, check remote cache-hit rate cold vs warm.

```text
Step 1 baseline: CI 25m; cache-hit 30% warm; long pole = `build` of pkg-core (8m, on every run)
Step 2 graph: pkg-core has no inbound edge from its config file → cache never invalidates correctly
Step 3 correctness: FAIL — `inputs` omits codegen output; stale artifact reused → fix keys first
Step 4 fix (post-correctness): affected-only + correct keys → only pkg-core's dependents rebuild
Re-measure: CI 25m → 9m warm; cache-hit 30% → 85%
Seam: devops-cicd hosts the remote cache backend; we own turbo.json inputs/pipeline
```

## Guardrails
- **Never tune speed before correctness.** A stale/wrong cached artifact is the worst failure mode here (house opinion #2).
- Don't prescribe a fix without the baseline measurement — the long pole is rarely where intuition points (house opinion #1).
- Fix the task graph before trusting affected-only or cache invalidation (house opinion #4).
- Remote caching is an economics + operational decision, not a default — do the CI-minutes-vs-cost arithmetic. See [`../../knowledge/build-caching-and-performance.md`](../../knowledge/build-caching-and-performance.md).
