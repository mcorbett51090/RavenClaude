---
name: manage-dependencies
description: "Set and enforce dependency & package management across a monorepo: version policy (single-version vs independent), lockfile hygiene (commit + freeze in CI), automated batched upgrades (renovate/dependabot), supply-chain hygiene (SBOM, provenance/SLSA, digest pinning), and staged cross-repo upgrades. Reach for this when the user asks 'how do we manage versions/lockfiles?' or 'upgrade X safely across the monorepo'. Used by `monorepo-engineer` (primary)."
---

# Skill: manage-dependencies

> **Invoked by:** `monorepo-engineer` (primary). The `build-systems-architect` consults it when a selection/perf call hinges on version policy.
>
> **When to invoke:** "how do we manage versions & lockfiles?"; "set up renovate/dependabot"; "upgrade <dependency/toolchain> across the monorepo safely"; "how do we handle supply-chain risk?".
>
> **Output:** a documented version policy + lockfile-hygiene rules + an upgrade-automation config + supply-chain checks, and for an active upgrade a staged plan keyed to the dependency-upgrade-runbook template.

## Procedure

1. **Choose ONE version policy, on purpose.**
   - **Single-version policy** — one version of each external dep across the whole repo (Google-style). Simplest reasoning, easiest cache/dedup, but forces lockstep upgrades.
   - **Independent versioning** — packages pin their own versions. More flexible, but invites version skew and duplicate installs.
   - Decide, **document it**, and enforce it with tooling (e.g. pnpm `overrides`/`catalog`, Nx, `syncpack`, or a lint rule). Don't drift into both.
2. **Pin ranges per policy.** Decide the range discipline (exact pins for apps/leaf packages; caret/tilde where you want patch flow) and apply it consistently. Exact pins + a lockfile give reproducibility; ranges + a lockfile give controlled flow.
3. **Lockfile hygiene.**
   - Commit the lockfile (`pnpm-lock.yaml` / `package-lock.json` / `yarn.lock`).
   - CI installs **frozen**: `pnpm install --frozen-lockfile` / `npm ci` / `yarn install --immutable`. A fresh resolve every run is a reproducibility bug.
   - Treat a lockfile diff in a PR as a reviewable change, not noise — it's the record of what actually changed transitively.
4. **Automate upgrades — batched and gated.** Configure renovate (or dependabot):
   - **group** related deps into batched PRs (e.g. all `@types/*`, all eslint, the React family) to cut PR noise,
   - **gate** every upgrade PR on a passing **affected build** (the task graph tells you the real blast radius),
   - **auto-merge** only safe classes (patch / lockfile-only) with green CI; minor/major get a human,
   - schedule to avoid a constant interrupt (e.g. a weekly batch).
5. **Supply-chain hygiene.**
   - Generate an **SBOM** (CycloneDX / SPDX) for releasable artifacts,
   - prefer **provenance / SLSA-attested** packages; verify where the registry supports it,
   - **pin CI actions and base images by digest**, not floating tags,
   - treat a **new transitive dependency** as a decision — surface notable additions to `ravenclaude-core/security-reviewer` for a verdict.
6. **For an active cross-repo upgrade, stage it** with the [`dependency-upgrade-runbook`](../../templates/dependency-upgrade-runbook.md): measure blast radius (affected graph) → batch → canary one package → verify → roll the rest → rollback plan ready.

## Worked example

> User: "Upgrade React 18 → 19 across our 30-package pnpm monorepo without breaking everything."

- **Blast radius first:** `pnpm why react` + the affected graph to see which packages actually consume React (and which only transitively).
- **Policy check:** single-version policy → upgrade React + react-dom + the `@types` together via a pnpm `catalog`/`overrides` so the whole repo moves in lockstep; no skew.
- **Stage:** canary one low-risk app package → run its affected build/tests → expand to the rest in batches → keep the previous lockfile tagged for instant rollback.
- **Gate:** the upgrade PR(s) must pass the affected build; codemods (React's official ones) applied before the green check.

```text
Version policy: single-version (React family in one pnpm catalog entry)
Lockfile: committed; CI = pnpm install --frozen-lockfile
Upgrade: renovate group "react" → batched PR → gated on affected build → canary → roll
Supply-chain: SBOM regenerated; new transitive deps flagged to security-reviewer
Rollback: previous pnpm-lock.yaml tagged; revert is one commit
```

## Guardrails
- One version policy, applied fully — never half-single-version, half-independent (house opinion #6).
- Lockfile committed and CI-frozen, always — a fresh resolve per run breaks reproducibility (house opinion #7).
- Upgrades are batched, gated on the affected build, and reversible — no manual big-bang sweeps (house opinion #8).
- A new transitive dependency is a decision (SBOM/provenance), not a default (house opinion #9).
- Volatile registry/tool claims carry a retrieval date; re-verify before a client deliverable.
