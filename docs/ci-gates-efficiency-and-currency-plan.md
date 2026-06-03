# CI Gates & Workflows — Efficiency + Currency Plan

> **How this was produced.** Two independent expert panels (five seats each) on **two different models** — Panel A on Opus, Panel B on Sonnet — each researched current (2026) GitHub Actions practice *and* read this repo's actual CI (`validate-marketplace.yml`, `validate-layout.yml`, `validate-schemas.yml`, `researcher-reminder.yml`, `scripts/audit-gates.sh`, `docs/best-practices/ci-gate-audit.md`). Panel B also gap-analyzed Panel A and enumerated the genuine either/or conflicts. **Eight conflicts (T1–T8) were each ruled by a separate independent expert.** This document is the merged, ruled result.
>
> **Scope:** RavenClaude's gate system — the ~48–50-gate `audit-gates.sh` meta-test, the freshness `--check` gates, prettier-on-the-whole-tree, layout + schema validation. Goal: keep them **efficient** (fast/cheap/low-friction) and **current** (un-stale, self-auditing, deduplicated, up-to-date).
>
> **Status:** plan. Volatile facts carry a 2026-06-03 retrieval date; items needing a live repo/branch-protection read are flagged.

---

## 0. The headline

The gate *correctness* here is best-in-class — the bidirectional fixture discipline in `audit-gates.sh` (every gate proven to fail-on-bad **and** pass-on-good) is exactly the anti-staleness pattern most repos lack. The gaps are **shape, currency, and economics**, not correctness:

- **Shape/efficiency:** one monolithic `validate` job, no `concurrency`, no dependency caching, no `timeout-minutes`.
- **Currency/supply-chain:** actions on floating major tags (not SHA-pinned), no Dependabot, `node-version: "20"` (runner removal **Sept 16 2026**), no least-privilege `permissions:`, `jsonschema` unpinned.
- **Economics:** ~50 gates with a correctness invariant but no ROI/sprawl invariant.

The single biggest *trap* to avoid: path-filtering a **required** check so a job is skipped-out-of-existence leaves PRs stuck at "Expected — waiting" forever. The fix (an always-running aggregator job) is only needed *if/when* the job is split — see T5.

---

## 1. Settled (both panels agree — do these)

| ID | Change | Notes |
|----|--------|-------|
| **S1** | `concurrency: { group: ${{github.workflow}}-${{github.ref}}, cancel-in-progress: <PR-only> }` on the three `validate-*` workflows | **Not** on `researcher-reminder.yml` (scheduled + issue-creating; a cancelled run loses an issue). Scope cancel to `pull_request`, never `push: main` (Pages serves main). |
| **S2** | Per-job `timeout-minutes` | `validate` ≈ 20, `layout`/`schemas` ≈ 5. Caps a hung `npx`/`pip`. |
| **S3** | Add Dependabot `github-actions` ecosystem | `.github/dependabot.yml`, weekly. Companion to S5 (pins don't rot). |
| **S4** | Bump runner Node `20` → `24` | **Hard deadline: Node 20 removed from runners 2026-09-16** ([GitHub Changelog, 2026-06-03](https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/)). Validate the `.mjs` render gates + prettier under Node 24 first. |
| **S5** | SHA-pin actions | (scope ruled in **T1** below) |
| **S6** | Least-privilege `permissions: { contents: read }` on the three `validate-*` workflows | They write nothing; only `researcher-reminder.yml` needs `issues: write`. |
| **S7** | Quarterly gate-review cron | Clone `researcher-reminder.yml` → opens a tracking issue: which gates never caught a defect? pinned-binary versions current? Node timeline? |
| **S8** | Dependency caching (pip + npm/npx) | **Prerequisite (B-A1):** the repo has no `package.json`/lockfile, so `npx --yes prettier` can't be cache-keyed. Add `package.json` + lockfile with prettier as a pinned devDependency first; cache ruff via `requirements.txt`/`pyproject` or a manual key on `ruff==0.15.8`. Also cache the actionlint binary download (B-A9). |
| **S9** | ROI / sprawl criteria | A gate earns its keep only if it: (1) catches a real defect class (cite the incident), (2) has a bidirectional fixture, (3) marginal-runtime < value, (4) isn't redundant. New gates default to an **advisory probation** tier; deprecation = delete the gate **and** its fixture in one PR; assign each gate an **owner area** (security / render / tribunal / layout / freshness). |

---

## 2. The eight tiebreak rulings (the contested calls)

### T1 — SHA-pin scope → **pin ALL actions** (incl. `actions/*`)
The threat is the *mutable tag*, not the author; `actions/checkout@v4` is a movable pointer just like any third-party tag, and the repo already SHA-pins its actionlint binary on exactly this "trust the hash, not the name" principle. Inconsistent pinning trains reviewers to stop noticing exceptions. Maintenance cost is ~zero **because** Dependabot (S3) auto-advances the pins.
**Do:** replace all `actions/*` refs with full commit SHAs + a `# vX.Y.Z` comment; Dependabot keeps them current.

### T2 — Split the monolith now vs measure → **MEASURE FIRST; split only if median wall-clock > 8 min**
The split's benefit (faster lint feedback, throughput) is contingent on a number nobody has measured; the cost (a branch-protection required-check rename — high blast radius) is certain. A ~50-fixture pure-Python/bash job often stays under 5 min. So: capture a baseline first.
- **< 5 min:** don't split (parallelization saves seconds, adds orchestration surface).
- **5–8 min (grey):** take the cheap half-step — reorder so lint/format runs **first and fails fast**; no job split.
- **> 8 min:** split into `lint` / `gates` / `freshness` (then T5 applies).
**Do:** add a step recording `gh run` durations across the last ~10 runs before touching any structure or check name.

### T3 — Shard `audit-gates.sh` → **DEFER until each shard runs in an isolated checkout**
The script mutates shared working-tree files (`marketplace.json`, `plugin.json`, …) via a single `$TMP`/`BACKUPS` mechanism. Naive matrix shards sharing a working tree would race, and a race yielding a false "gate passed" defeats the exact guarantee the meta-test exists for. A nightly unsharded backstop is **too late** for a merge gate (it catches the race after a bad PR already merged). The work *is* parallelizable — the blocker is shared mutable state, not the workload.
**Do:** before any sharding, give each matrix shard its own isolated tree (`git worktree add` or a fresh clone with a shard-local `$TMP`); prove isolation by running two shards against a known-bad fixture and confirming each independently fails (no false pass). `make -j` with per-gate temp dirs is **not** sufficient — the races are over tracked files, not scratch space. Can land as early as Phase 2 *if* isolation is done first.

### T4 — Dependabot vs Renovate → **Dependabot now**
Migrating to Renovate later is additive (add `renovate.json`, remove `dependabot.yml`) — a ~15-min task, not a re-architecture. Renovate's unified npm + actions benefit only materializes if a `package.json` is actually added (hypothetical today). For a solo maintainer, GitHub-native, zero-config, no external app wins.
**Do:** `.github/dependabot.yml` with one `github-actions` entry, weekly; re-evaluate Renovate only when/if a `package.json` lands (S8).

### T5 — Aggregator + job-level path-filter timing → **couple it to the split (gated on T2)**
A *workflow-level* `paths:` that simply doesn't trigger the workflow is handled asymmetrically from a *job-level* skip of a required check — the stuck-"Expected"-forever trap is the **job-skip** case. So the current workflow-level `paths:` on `validate-marketplace.yml` is **low-risk** (its globs were audited to cover all generator inputs, and `workflow_dispatch` is an escape hatch). The aggregator solves a problem the **split creates**, not one that exists today. If T2 defers the split, defer the aggregator; if the split proceeds, the aggregator ships in the *same* change as a hard prerequisite.
**Do:** when the split lands, do it atomically — add the aggregator job (`if: always()`, rolling up `result == success || skipped`) **and** flip branch protection from per-job names to the single aggregator name in one merge, so no PR is ever judged against a check that can be skipped out of existence.

### T6 — Fix `researcher-reminder.yml` prettier debt → **yes, in Phase 1 (last item, standalone commit)**
`.prettierignore` excludes it for a malformed JS template literal in a YAML `script: |` block; the documented fix (`[...].join('\n')`) is already applied to most of the file — the `daily-quick-check` branch still has unrefactored literals (copy-paste debt). Low effort, real consistency gain, and it removes a future foot-gun (a contributor removing the exclusion without fixing the literals breaks CI on every PR). But it touches a *production* workflow whose parser fragility is *why* it was excluded.
**Do:** finish the `.join('\n')` refactor, confirm `prettier --check` on that file exits 0, remove the `.prettierignore` line, run full `prettier --check .` + `bash -n` — **in its own commit**, not commingled.

### T7 — CODEOWNERS for `.github/` + `scripts/` → **add now, advisory only**
Enforced CODEOWNERS for a solo maintainer risks a self-review/self-merge trap. Advisory still pays: it documents that these paths are gate-critical, records on the PR timeline that review wasn't skipped, and becomes load-bearing the instant a second collaborator or an agentic tool opens a PR touching them.
**Do:** `.github/CODEOWNERS` → `/.github/workflows/ @mcorbett51090` and `/scripts/ @mcorbett51090`; leave branch-protection "Require review from Code Owners" **off**; comment that it flips on when a 2nd collaborator joins.

### T8 — Pin `jsonschema` in `validate-schemas.yml` → **pin with `~=4.23`**
Matches the repo's determinism discipline (ruff, actionlint already pinned). `jsonschema` 4.x→5.x can change default draft / `$schema` resolution / accepted keywords — silent validation drift. A compatible-release pin (`~=4.23`) blocks the disruptive 5.x jump while still taking 4.x bug/CVE fixes (and less Dependabot noise than exact `==`).
**Do:** `pip install --quiet 'jsonschema~=4.23'` (confirm current 4.x minor with `pip index versions jsonschema` before merge — *[unverified — exact minor]*).

---

## 3. Phased rollout (revised by the rulings)

### Phase 1 — Quick wins (no branch-protection change)
S1 concurrency · S2 timeouts · **T1** SHA-pin all actions · S3/**T4** Dependabot · S4 Node 24 · S6 permissions · **T8** pin jsonschema · the **T2 baseline step** (`gh run` timing) · **T7** CODEOWNERS (advisory) · **T6** researcher-reminder prettier fix (last, standalone) · S8 caching *after* its lockfile prerequisite.
**Exit:** all workflows green on a no-op PR; a wall-clock baseline recorded; Dependabot opens + passes its first actions-bump PR.

### Phase 2 — Measure-driven restructure
Read the T2 baseline → **<5 min:** stop (no split). **5–8 min:** reorder lint-first only. **>8 min:** split into `lint`/`gates`/`freshness` + the **T5** aggregator + job-level `dorny/paths-filter`, landed atomically with the branch-protection check-name swap.
**Exit:** if split — a markdown-only PR skips render/dashboard gates yet the aggregator reports green and merges; a generator-input PR still triggers `freshness`; required check = the aggregator.

### Phase 3 — Scale + self-audit
**T3** shard `audit-gates.sh` *only after* per-shard isolated checkouts (+ nightly full unsharded backstop) · pre-commit fast tier (`ruff --fix`, `prettier --write`, `bash -n`) with **CI still authoritative** (dedup latency, never coverage) · per-gate `last_reviewed` advisory meta-check **scoped to externally-referenced gates only** (actionlint/Node/platform-fact; behavioral gates don't go stale) · S7 quarterly review cron · S9 ROI criteria written into `ci-gate-audit.md`.
**Exit:** sharded audit < ~⅓ serial wall-clock with proven isolation; first quarterly review issue auto-opens and at least one gate is confirmed-kept or retired with rationale.

---

## 4. Top risks + mitigations

| # | Risk | Mitigation |
|---|------|-----------|
| R1 | Path-filtering a **required** check → PR stuck "Expected — waiting" forever | Aggregator job as the single required status (T5); never job-skip a required check without it |
| R2 | Renaming the job (split) silently breaks branch protection | Add new jobs alongside old → update required-check list → remove old; atomic, in a maintenance window (T2/T5) |
| R3 | SHA-pin **without** auto-update → actions rot / miss security fixes | T1 ships *with* Dependabot (S3/T4); never pin without an updater |
| R4 | Node 20 runner removal (2026-09-16) breaks CI | S4 now; Dependabot also surfaces actions still on the node20 runtime |
| R5 | Cache poisoning / stale cache masks a real failure | Key caches on lockfile hashes; never cache the *artifacts* the freshness gates verify — only package caches |
| R6 | Shard race → **false "gate passed"** | Don't shard until per-shard isolated checkouts (T3); nightly full run as backstop |
| R7 | Path-filter globs miss a generator input → stale generated output ships green | Filter globs must enumerate every input each generator reads (the documented `check-marketplace-claims.py` reads-`README.md` hazard); add a meta-check that globs cover declared inputs |
| R8 | `cancel-in-progress` aborts a half-done `push: main` freshness publish | Scope cancel to `pull_request` only (S1) |

---

## 5. Open questions (would most change the plan)

1. **Current branch-protection / required-check config** — gates the whole T2/T5 sequencing; not readable from the workspace. If no check is *required*, path-filtering is far lower-risk.
2. **Lockfiles?** — S8 npm caching needs a `package.json` + lockfile (none today). This is a discrete prerequisite task.
3. **Real per-run wall-clock baseline** — the T2 split decision is arithmetic once measured; until then it's reasoned.
4. **Which `audit-gates.sh` gates are the true hotspots** — draw T3 shard boundaries from real per-gate timing (the tribunal/`claude -p` gates are the suspected sink), not inference.
5. **Team appetite for advisory-tier gates** — the primary sprawl valve (S9 probation) only works if advisory output is treated as actionable signal, not ignorable noise.

---

## Appendix — provenance

- **Panel A** (Opus) and **Panel B** (Sonnet) ran independently from the same brief; **T1–T8** were each ruled by a separate independent expert (3 on Opus for the high-blast architectural/branch-protection calls, 5 on Sonnet for the bounded ones).
- Verified 2026-06-03: Node 20 runner removal date, SHA-pinning consensus, `concurrency` savings, required-check-skip trap. Items needing a live repo read (branch-protection config, per-run timings, current `jsonschema` minor) are flagged `[unverified]`.
- This is a plan, not an implementation — no workflow has been changed by this document.
