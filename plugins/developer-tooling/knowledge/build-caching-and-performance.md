# Build Caching & Performance

> **Last reviewed:** 2026-06-21. Confidence: **high** on the concepts (task graph, affected/since, content-addressable + remote caching, hermeticity — these are stable across tools); **medium** on tool-specific config names and **lower** on version/pricing specifics (re-verify before pinning).
>
> Used by [`optimize-build-and-cache`](../skills/optimize-build-and-cache/SKILL.md) and the [`build-systems-architect`](../agents/build-systems-architect.md). Pairs with [`monorepo-tooling-decision-tree.md`](monorepo-tooling-decision-tree.md).

## The one rule above all: correctness before speed

A cache that can return a **stale or wrong artifact** is worse than no cache — it silently ships incorrect output and destroys trust in the whole system. **Audit cache correctness (hermeticity + input-hash completeness) before tuning hit rate.** Everything below assumes this gate has passed.

## Core concepts

### Task graph

The directed dependency graph of tasks (build → test → lint, package A → package B). It is the **source of truth** for everything else:

- **Affected/since builds** derive from it (which tasks a change touches).
- **Parallelism** derives from it (independent branches run concurrently).
- **Cache invalidation** derives from it (a changed input invalidates its task and everything downstream).

A **wrong graph** is the root cause of most "why didn't this rebuild?" (missing edge) and "why did everything rebuild?" (spurious edge) failures. **Fix the graph first.**

### Affected / `since` builds

Build/test only what a change actually affects, not the whole repo:

- `nx affected --target=build` (Nx), `turbo run build --filter=...[origin/main]` (Turborepo), `bazel query` (Bazel), `moon run :build --affected` (Moon). *(commands retrieved 2026-06-21 — re-verify flags)*
- Driven by a base ref (e.g. `origin/main`) + the task graph. Usually the **single biggest early win** on a monorepo with no affected-only yet.

### Caching layers (cheapest → most powerful)

1. **Local cache** — task outputs hashed by their inputs, reused on the same machine. Free; first thing to turn on (after correct keys).
2. **Remote cache** — share cached task outputs across CI runs and across developers. Turns a teammate's/CI's already-done work into a cache hit for you. Needs a backend (hosted by the tool's vendor or self-hosted — a `devops-cicd` concern).
3. **Content-addressable caching (CAS)** — artifacts keyed by a hash of their *content/inputs* (Bazel/Buck2 model). Enables fine-grained reuse and, with **remote execution**, distributing the build itself.

### Cache key = hash of all inputs

The cache key must include **every input that affects the output**: source files, dependency versions, the tool/compiler version, task config, and any environment that matters. **A missing input → stale-cache-returns-wrong-artifact.** Example: declare global/env inputs in `turbo.json` `globalDependencies` / a task's `inputs`, or Bazel's explicit declared inputs.

### Hermeticity

A hermetic build produces the **same output from the same inputs**, independent of the machine, clock, or network. Non-hermetic leaks that poison cache keys and reproducibility:

- timestamps baked into artifacts,
- absolute / machine-specific paths,
- network fetches *during* the build (unpinned, mutable),
- unpinned tool/compiler versions,
- locale / env differences,
- nondeterministic ordering (e.g. unsorted globs).

Bazel/Buck2 enforce hermeticity by construction (sandboxed, declared inputs); Turborepo/Nx rely on you declaring inputs correctly.

## Cache-correctness checklist (run BEFORE speed tuning)

- [ ] Does the cache key include **all** inputs that affect output (source, deps, tool version, config, relevant env)?
- [ ] Are there any **non-hermetic leaks** (timestamps, absolute paths, network-in-build, unpinned tools, locale)?
- [ ] Does the **task graph** have all real edges (no missing dependents) and no spurious ones?
- [ ] Does a deliberate input change correctly **invalidate** the cache (and only the right scope)?
- [ ] Is a **cache miss safe** (rebuilds correctly) and a **cache hit verified** to equal a fresh build (spot-check byte-equality where possible)?

If any box fails: **fix it or disable the cache** before chasing speed.

## The measurement playbook

Never prescribe a fix from intuition — the long pole is rarely where you'd guess.

1. **Baseline the wall-clock**: total build/CI time, cold vs warm.
2. **Per-task timing**: find the **long pole** (one task often dominates).
3. **Cache-hit rate**: local and remote, cold vs warm. A low warm-hit rate points at bad keys or non-hermeticity, not "the build is just slow."
4. **Affected-graph size**: for a typical PR, how much *should* rebuild vs how much *does*. A gap points at a graph problem.
5. **Re-measure after each change** and report the delta against the baseline.

## Highest-leverage fixes (cheapest first)

| Fix | When it wins | Caution |
|---|---|---|
| **Affected/since-only** | No affected-only yet → everything rebuilds | Requires an accurate graph |
| **Local caching** | Repeated identical tasks | Correct keys + hermeticity first |
| **Parallelism** | Many independent graph branches, idle cores | Bounded by the critical path + resources |
| **Remote caching** | CI redoes work devs/other runs already did | Backend cost + ops surface; correctness gate first |
| **Split / re-architect the long pole** | One un-cacheable or monolithic task dominates | Architectural effort; last resort |
| **Remote execution (Bazel/Buck2)** | Build itself is the bottleneck at scale | Significant infra investment |

## Remote-caching economics

Remote caching is a **conditional** win, not a default: weigh **CI-minutes (and developer-minutes) saved** against **backend cost + operational surface** (hosting, auth, cache eviction policy, security of the artifacts). Do the arithmetic. **Hosting the backend and the runner config belong to `devops-cicd`;** this layer owns the build-tool cache configuration (keys, inputs, what's cacheable).

## See also

- Tool selection: [`monorepo-tooling-decision-tree.md`](monorepo-tooling-decision-tree.md)
- The optimize skill: [`../skills/optimize-build-and-cache/SKILL.md`](../skills/optimize-build-and-cache/SKILL.md)
