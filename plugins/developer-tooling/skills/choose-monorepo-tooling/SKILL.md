---
name: choose-monorepo-tooling
description: "Pick the right monorepo/build tool and package manager for a described repo by traversing the monorepo-tooling decision tree (language mix → scale → hermeticity need → tool), then return the recommended tool, the package-manager pick, the tradeoffs, and an explicit list of what NOT to adopt yet. Reach for this when the user asks 'which monorepo tool?' or 'should we adopt Nx/Turborepo/Bazel?'. Used by `build-systems-architect` (primary)."
---

# Skill: choose-monorepo-tooling

> **Invoked by:** `build-systems-architect` (primary). Also consulted by `monorepo-engineer` when the tool isn't chosen yet before wiring.
>
> **When to invoke:** "which monorepo/build tool should we use?"; "should we adopt Nx / Turborepo / Bazel / Moon?"; "is a monorepo even right for us?".
>
> **Output:** the recommended tool + the package-manager pick + the tradeoffs (config tax, lock-in, learning curve) + an explicit list of what to NOT adopt yet, all tied to the *measured* shape of the repo.

## Procedure

1. **Gather the measured context first** — do not recommend from the tool name in the request. Establish:
   - **language mix** (JS/TS-only? polyglot? which others — Go, Python, Java, Rust?),
   - **scale** (number of packages/projects, repo size, build wall-clock today, team size),
   - **pain signal** (slow CI? broken caching? cross-package coordination? release versioning chaos?),
   - **hermeticity need** (do you need byte-reproducible, cross-language, content-addressable builds — or is task-level caching enough?).
2. **Traverse the decision tree** in [`../../knowledge/monorepo-tooling-decision-tree.md`](../../knowledge/monorepo-tooling-decision-tree.md) against that context: language mix → scale → hermeticity need → tool leaf.
3. **Name the tool, then the package manager.** For JS/TS the package-manager spine (`pnpm` default; yarn/npm with a reason) is a separate, lower-ceremony decision than the task runner (Turborepo vs Nx).
4. **State the tradeoff, not just the pick** — config tax, lock-in, learning curve, who maintains it — against the measured pain. A tool that solves a pain you don't have is a net negative.
5. **List what to NOT adopt yet.** The most valuable output is often "don't reach for Bazel; a `pnpm` workspace + `turbo` clears your measured pain at a fraction of the cost." Defer heavy tools until a measured reason appears.
6. **Hand off:** if the tool is chosen, route implementation to `monorepo-engineer`; if the pain is actually pipeline-shaped (runner config, cache-backend hosting), name the `devops-cicd` seam.

## Worked example

> User: "We have 18 TypeScript packages, CI takes 25 min because everything rebuilds on every PR. Should we adopt Bazel?"

- Context: **JS/TS-only**, **mid-scale (18 pkgs)**, pain = **no affected-only + no caching**, hermeticity need = **low** (single language, task-level caching suffices).
- Tree leaf: JS/TS-only + needs task caching + affected-only → **Turborepo** (low ceremony) **or Nx** (if you also want generators + module-boundary lint + a richer graph). Package manager: **pnpm** workspaces.
- **Not Bazel:** Bazel's value is cross-language hermetic reproducibility; you'd pay a steep `BUILD` file config tax for capabilities your single-language repo doesn't need. Revisit only if you go polyglot at much larger scale.
- Tradeoff: Turborepo = fastest to adopt, thinner graph; Nx = more power, more concepts to learn. Either gives you affected-only + caching that should cut the 25 min sharply.

```text
Recommend: pnpm workspaces + Turborepo (or Nx if you want generators + boundary lint)
Package manager: pnpm  (strict, fast, content-addressable store)   [retrieved 2026-06-21 — re-verify]
Do NOT adopt yet: Bazel/Buck2 (no cross-language/hermeticity need at this scale)
Next: monorepo-engineer wires turbo.json + affected; devops-cicd runs `turbo run` + hosts remote cache
```

## Guardrails
- Never recommend a tool without the measured context (language mix / scale / pain / hermeticity) — guessing the bottleneck is the cardinal sin (house opinion #1).
- Don't pay Bazel/Buck2's config tax for a small single-language repo (house opinion #5).
- Always include "what to NOT adopt yet" — deferral is a valid, often optimal, recommendation.
- Volatile tool-positioning/version claims carry a retrieval date; re-verify before a client deliverable. See [`../../knowledge/monorepo-tooling-decision-tree.md`](../../knowledge/monorepo-tooling-decision-tree.md).
