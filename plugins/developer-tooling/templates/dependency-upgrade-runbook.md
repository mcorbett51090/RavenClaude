# Dependency / Toolchain Upgrade Runbook — <dependency> <from> → <to>

> Safe, staged upgrade of a dependency or toolchain across a monorepo. Owned by the [`monorepo-engineer`](../agents/monorepo-engineer.md); drives [`../skills/manage-dependencies/SKILL.md`](../skills/manage-dependencies/SKILL.md). Use for anything with cross-package blast radius (framework majors, the compiler/toolchain, a widely-shared internal lib).
>
> **Date:** <YYYY-MM-DD> · **Driver:** <name> · **Risk:** low / medium / high · **Status:** planned / in-progress / done / rolled-back

---

## 1. What & why

- **Upgrade:** <dependency> <from-version> → <to-version>
- **Class:** patch / minor / **major** / toolchain
- **Reason:** <security fix / EOL / feature needed / debt>
- **Breaking changes (from release notes, retrieved <date>):** <bullet the ones that hit us>
- **Codemods available?** <official codemod / none — link>

## 2. Blast radius (measure first)

> Don't upgrade blind. The task graph tells you what actually breaks.

- **Direct consumers:** `pnpm why <dep>` / dependency-graph query → <packages>
- **Transitive consumers:** <packages affected only indirectly>
- **Affected build scope:** `nx affected` / `turbo run --filter` against the change → <N of M packages>
- **Version-policy implication:** single-version → must move repo-wide in lockstep; independent → can stage per-package.

## 3. Batching plan

- **Group:** <which deps move together — e.g. react + react-dom + @types/react>
- **Order:** <canary package first → then batches → leaf apps last (or as the graph dictates)>
- **PR strategy:** <one gated PR / a renovate-grouped batch>

## 4. Staged execution

| Step | Action | Verify | Rollback point |
|---|---|---|---|
| 1. Tag rollback anchor | Record/commit current lockfile state | Lockfile tagged | — |
| 2. Apply codemods | Run official codemods on affected packages | Diff reviewed | Revert commit |
| 3. Bump + resolve | Update versions per policy (catalog/overrides); regenerate lockfile | `--frozen-lockfile` resolves clean | Restore tagged lockfile |
| 4. Canary | Upgrade one low-risk package | Its affected build + tests green | Revert canary only |
| 5. Roll the rest | Expand in batches | Affected build green each batch | Revert the batch |
| 6. Full verify | Whole affected graph builds/tests | All green | Restore tagged lockfile |

## 5. Verification gates

- [ ] CI installs with `--frozen-lockfile` / `npm ci` and resolves clean.
- [ ] **Affected build + tests green** for every touched package (the real blast radius, not the whole repo).
- [ ] Lockfile diff reviewed (transitive changes understood).
- [ ] **SBOM regenerated;** new transitive deps reviewed (flag notable ones to `ravenclaude-core/security-reviewer`).
- [ ] Provenance/SLSA verified where the registry supports it; actions/images pinned by digest unaffected.
- [ ] No new non-hermetic input introduced (cache keys still complete).

## 6. Rollback plan

- **Trigger:** <what failure forces a rollback>
- **Action:** restore the tagged lockfile from step 1 + `git revert` the bump commit(s) → one-commit recovery.
- **Verify rollback:** affected build green on the restored state.

## 7. Automation follow-up

- **Renovate/dependabot:** add/adjust a group so future <dep> upgrades batch automatically and gate on the affected build.
- **Auto-merge policy:** patch/lockfile-only with green CI → auto; minor/major → human.

## 8. Seams / handoffs

- **`devops-cicd`** — the pipeline running the affected build/gate.
- **`backend-engineering` / `frontend-engineering`** — app-code changes the upgrade forces.
- **`ravenclaude-core/security-reviewer`** — supply-chain verdict on new deps.

---

*Plus the cross-plugin Structured Output Protocol block — see [`../../ravenclaude-core/skills/structured-output/SKILL.md`](../../ravenclaude-core/skills/structured-output/SKILL.md).*
