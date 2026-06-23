# Monorepo Tooling — Decision Tree

> **Last reviewed:** 2026-06-21. Confidence: **high** on the decision *structure* (language-mix → scale → hermeticity is stable); **medium** on specific tool feature claims and **lower** on version/positioning specifics (this space moves fast — re-verify any version-pinned claim before a client deliverable).
>
> Used by [`choose-monorepo-tooling`](../skills/choose-monorepo-tooling/SKILL.md) and the [`build-systems-architect`](../agents/build-systems-architect.md). Pairs with [`build-caching-and-performance.md`](build-caching-and-performance.md).

## How to use this

Recommend from the **measured shape of the repo**, not the tool named in the request. The three axes that actually decide the tool:

1. **Language mix** — JS/TS-only, or polyglot (Go/Python/Java/Rust/…)?
2. **Scale** — number of packages, repo size, build wall-clock, team size.
3. **Hermeticity need** — do you need byte-reproducible, cross-language, content-addressable builds, or is *task-level* caching enough?

## The tree

```mermaid
flowchart TD
    Start([Need to organize/build multiple packages]) --> Q0{Is a monorepo even the right call?\ncoupling + shared release cadence?}
    Q0 -->|"Loosely coupled, independent\nrelease cadence, separate teams"| Poly[Polyrepo + a package registry\n— don't force a monorepo]
    Q0 -->|"Shared code, atomic cross-package\nchanges, coordinated releases"| Q1{Language mix?}

    Q1 -->|JS / TS only| Q2{Scale & needs?}
    Q1 -->|Polyglot| Q3{Need hermetic, byte-reproducible,\ncross-language caching?}

    Q2 -->|"Small–mid, want low-ceremony\ntask caching + affected-only"| Turbo[Turborepo + pnpm workspaces\n— fastest to adopt]
    Q2 -->|"Mid–large, also want generators,\nmodule-boundary lint, richer graph"| Nx[Nx + pnpm workspaces]
    Q2 -->|"Just need workspaces + linking,\nno task-graph caching yet"| WS[pnpm / yarn / npm workspaces only\n— add a task runner later if pain appears]

    Q3 -->|"Yes — large org, many languages,\nreproducibility is a hard requirement"| Bazel[Bazel or Buck2\n— content-addressable, hermetic\n(pay the BUILD-file config tax)]
    Q3 -->|"No — want a lighter polyglot\ntask runner with caching"| Moon[Moon\n— polyglot task runner, simpler than Bazel]

    Turbo --> Cache[[Then: configure the task graph\n+ caching — see build-caching doc]]
    Nx --> Cache
    Moon --> Cache
    Bazel --> Cache
    WS --> Cache
```

## Tool comparison (retrieved 2026-06-21 — re-verify specifics)

| Tool | Best for | Caching | Strengths | Costs / cautions |
|---|---|---|---|---|
| **pnpm / yarn / npm workspaces** | The package-manager spine under everything; small repos | Package store (pnpm content-addressable store); no *task* cache by itself | Simple, fast install, strict (pnpm); foundation for the runners above | No task graph / affected-only on its own |
| **Turborepo** | JS/TS, low-ceremony task caching + affected-only | Local + remote task cache (content-hashed task outputs) | Minimal config, fast to adopt, good DX | Thinner graph model than Nx; JS/TS-centric |
| **Nx** | JS/TS (+ some polyglot via plugins), richer needs | Local + remote ("Nx Replay"-style) task cache | Task graph, generators, module-boundary lint, affected, plugin ecosystem | More concepts to learn; can feel heavy for a tiny repo |
| **Lerna** | Legacy JS monorepos | Delegates to Nx now | Still used in older repos | **Not a greenfield default** — now Nx-powered; choose Nx/Turborepo directly |
| **Moon** | Polyglot, want caching without Bazel's tax | Local + remote task cache | Lighter polyglot task runner; toolchain management | Smaller ecosystem than Bazel/Nx |
| **Bazel** | Large polyglot orgs needing hermetic reproducibility | Content-addressable + remote cache + remote execution | Hermetic, byte-reproducible, scales to huge; cross-language | Steep `BUILD` file config tax; learning curve; overkill for small single-language repos |
| **Buck2** | Same niche as Bazel; perf-focused alternative | Content-addressable + remote cache/execution | Fast, Starlark-based, hermetic | Smaller community than Bazel; same config investment |

## Package-manager pick (JS/TS)

- **pnpm** — default. Strict (no phantom deps), fast, content-addressable global store, first-class workspaces + `catalog`/`overrides` for version policy. *(retrieved 2026-06-21)*
- **yarn (Berry)** — choose with a reason (PnP, existing investment, specific plugin needs).
- **npm** — workspaces are fine for simple repos; reach for pnpm when strictness/dedup/perf matter.

## Decision heuristics (the house line)

- **Measure before you migrate.** A `pnpm` workspace + `turbo` clears most JS build pain before Bazel is ever justified — don't pay a heavy tool's config tax against a *guessed* bottleneck.
- **Match the tool to the language mix.** JS/TS → Turborepo/Nx + pnpm. Polyglot + hermetic + huge → Bazel/Buck2. Polyglot but lighter → Moon.
- **"Don't adopt yet" is a valid recommendation.** Defer the heavy tool until a measured reason appears.
- **A monorepo isn't always right.** If packages are loosely coupled with independent release cadences and separate teams, a polyrepo + registry may beat forcing them together.

## See also

- Build performance + caching mechanics: [`build-caching-and-performance.md`](build-caching-and-performance.md)
- The adoption plan template: [`../templates/monorepo-adoption-plan.md`](../templates/monorepo-adoption-plan.md)
