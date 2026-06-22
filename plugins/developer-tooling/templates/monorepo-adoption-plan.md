# Monorepo Adoption / Migration Plan — <repo or org name>

> Staged plan to adopt (or migrate to) a monorepo build tool. Fill every box. Owned by the [`build-systems-architect`](../agents/build-systems-architect.md), implemented by the [`monorepo-engineer`](../agents/monorepo-engineer.md). Decision logic: [`../knowledge/monorepo-tooling-decision-tree.md`](../knowledge/monorepo-tooling-decision-tree.md).
>
> **Date:** <YYYY-MM-DD> · **Author:** <name> · **Status:** draft / approved / in-progress / done

---

## 1. Why (the measured pain)

> Measure before you migrate. State the pain in numbers, not vibes.

- **Current pain signal:** <slow CI / broken caching / cross-package coordination / version chaos>
- **Baseline metrics (today):**
  - Build/CI wall-clock: <X min cold / Y min warm>
  - Cache-hit rate: <local %, remote % — or "none">
  - Affected-graph size for a typical PR: <should-rebuild vs does-rebuild>
  - Number of packages / repos / teams: <…>
- **What "done" looks like (success criteria, measurable):** <e.g. PR CI < 8 min warm; cache-hit > 80%; affected-only on>

## 2. Tool decision

- **Language mix:** <JS-TS only / polyglot — which>
- **Hermeticity need:** <task-level caching enough / need cross-language byte-reproducibility>
- **Chosen tool:** <Turborepo / Nx / Bazel / Buck2 / Moon / workspaces-only> — via the decision tree
- **Package manager:** <pnpm / yarn / npm> + why
- **What we are explicitly NOT adopting yet:** <e.g. Bazel — no hermeticity need at this scale>
- **Tradeoffs accepted:** <config tax / lock-in / learning curve> vs the pain in §1

## 3. Target layout & policy

- **Workspace layout:** <apps/, packages/, libs/ — the structure>
- **Version policy:** single-version / independent (see [`../skills/manage-dependencies/SKILL.md`](../skills/manage-dependencies/SKILL.md))
- **Module boundaries:** <how enforced — Nx tags / dependency-cruiser / eslint>
- **Task graph:** <the build/test/lint targets and their edges>
- **Caching:** local → remote? <which, and who hosts the backend → devops-cicd>

## 4. Phased rollout

> Incremental and reversible. Never a big-bang cutover.

| Phase | Scope | Exit criteria | Rollback |
|---|---|---|---|
| 0. Baseline | Capture all §1 metrics | Numbers recorded | n/a |
| 1. Foundation | Workspace + package manager + lockfile freeze in CI | `--frozen-lockfile` green; all packages install | Revert config commit |
| 2. Task graph | Wire targets + validate graph edges | Graph matches reality (no missing/spurious edges) | Disable graph, keep workspace |
| 3. Local caching | Correct cache keys + hermeticity audit | Cache-correctness checklist passes | Disable cache |
| 4. Affected-only | `affected`/`since` builds in CI | Only affected packages rebuild on a test PR | Fall back to build-all |
| 5. Remote caching | Backend + auth (with devops-cicd) | Warm cache-hit target met; economics confirmed | Disable remote, keep local |
| 6. Generators/boundaries | Scaffolds + boundary lint | New package via generator; boundary lint blocks a violation | Optional, non-blocking |

## 5. Correctness & safety gates

- [ ] Lockfile committed; CI installs frozen.
- [ ] Cache-correctness checklist passed before remote caching ([`../knowledge/build-caching-and-performance.md`](../knowledge/build-caching-and-performance.md)).
- [ ] Task graph validated (no missing/spurious edges).
- [ ] A cache hit spot-checked equal to a fresh build.
- [ ] Rollback rehearsed for each phase.

## 6. Seams / handoffs

- **`devops-cicd`** — wires the pipeline that runs `affected`/`turbo run`; hosts the remote-cache backend.
- **`backend-engineering` / `frontend-engineering`** — the service code being built.
- **Cloud plugins** — infra for the cache backend / artifacts.
- **`ravenclaude-core/security-reviewer`** — supply-chain review of the cache backend / new deps.
- **`ravenclaude-core/project-manager`** — RAID / status for the migration.

## 7. Re-measure & report

- **Post-migration metrics** (vs §1 baseline): <build time, cache-hit, affected-graph>
- **Delta achieved:** <…>
- **Outstanding / phase-2 work:** <…>

---

*Plus the cross-plugin Structured Output Protocol block — see [`../../ravenclaude-core/skills/structured-output/SKILL.md`](../../ravenclaude-core/skills/structured-output/SKILL.md).*
