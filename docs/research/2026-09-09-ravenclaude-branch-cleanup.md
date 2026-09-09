# RavenClaude remote-branch cleanup — 2026-09-09

Inventory of every non-`main` remote head on `mcorbett51090/RavenClaude`, classified against `origin/main` and associated PRs. Executed under FORGE slug `branch-cleanup` (quick). **Execution continued through the same day** — this doc is the live matrix (initial inventory + outcomes).

## Final state (end of cleanup pass)

| Bucket | Count | Outcome |
|---|---|---|
| Archive + delete remote | 14 | Done (13 from initial clear-cut inventory + `test/g0-control-scratch`) |
| Squash-merged into `main` | 4 | #1138, #1120, #1122, #1126 |
| Closed without merge | 1 | #1123 (Sep 7 findings folded into #1126) |
| Dependabot remaining | 0 | **#1121** squash-merged (`95a6e95a`) |
| Active conflicting feature work | 2 | **#1145**, **#1146** — keep; do not auto-close |
| New dependency-sweep baseline | 1 | **#1147** draft — keep / merge separately (fingerprint only) |
| This analysis PR | 1 | **#1142** (docs-only) |

Remote heads after cleanup (target): `main` + #1145 + #1146 + #1147 + this docs branch (until #1142 lands).

## Summary (initial inventory)

| Bucket | Count | Action taken / recommended |
|---|---|---|
| Merged leftovers / already-landed tips | 5 | Archive tag + delete remote |
| Closed PRs (explicitly superseded / empty) | 8 | Archive tag + delete remote |
| Open drafts (Claude) | 3 | Keep — triage; **#1138 is the CI unblock** |
| Open Dependabot | 3 | Keep — blocked until `validate-marketplace` is green on main |
| Analysis worktree | 1 local (`forge/branch-cleanup`) | Keep until this cleanup finishes |

**Observation (resolved):** `validate-marketplace` was red on `main` (post plan-archive link/`prettierignore`/ratchet drift). Draft **#1138** was the fix-forward; it was rebased and squash-merged (`d7f35eb5`), unblocking Dependabot.

## Detailed classification

### Archive + delete remote (clear-cut) — DONE

| Branch | Evidence | Notes |
|---|---|---|
| `claude/source-control-github-merge-s0b4ve` | PR **#1140** merged | Fresh leftover after merge |
| `feat/ravenclaude-core-launch-guard-dir-recommend` | PR **#1141** merged | Fresh leftover after merge |
| `forge/rebase-886` | Squash commit `074bfaf0` (#886) on main; tip `=` cherry-mark | Tip not ancestor (squash) — archive, don't bare-delete |
| `feat/assumption-claiming-layer` | Landed as **#983** (`1c617b7d`, v0.281.0); `ask-on-ambiguity.sh` + Gate 223 tests on main | Branch tip is older v0.273.0 formulation |
| `forge/tribunal-selfdisable-bash-readfp` | Landed as **#1137**; `concerns-catalog.md` diff vs main = **0 lines** | Tip patch-equivalent |
| `claude/charming-tesla-gfkm6m` | PR **#987** closed — superseded by #1041 | Would rewind core 0.306.1→0.283.0 |
| `claude/charming-tesla-qwt8wz` | PR **#839** closed — superseded by #868 | Opus 5 map from weaker sources |
| `claude/charming-tesla-vpct9c` | PR **#850** closed — superseded by #856 | Agent 365 GA correction duplicate |
| `claude/onedrive-access-ravenpower-daenmv` | PR **#822** closed — empty/no-op | Parsed settings deep-equal |
| `forge/analog-repos-gap-fill` | PR **#926** closed — superseded | Survey/F1/F2 already on main |
| `forge/ci-gate-health-spend` | PR **#965** closed — Gate 223 slot taken | Stale pre-commitment |
| `forge/session-context-handoff` | PR **#927** closed — superseded | Implementation on another branch |
| `forge/task-ledger` | PR **#988** closed — shipped #992/#993/#1001 | Plan-only draft |
| `test/g0-control-scratch` | PR **#1143** closed without merge | Disposable G0-control positive-control scratch; archived `archive/test-g0-control-scratch-2026-09-09-152454` |
| `claude/awesome-wright-lm1y5x` | PR **#1123** closed | Sep 7 findings folded into #1126; archived after close |

### Merged this pass — DONE

| PR | Branch | Result |
|---|---|---|
| **#1138** | `claude/awesome-wright-4jz4tu` | Rebased (kept main `index.html`; restamped Gate 242). Squash → `d7f35eb5`. Unblocked `validate-marketplace` on main. |
| **#1120** | Dependabot actions pin set | Rebased + ratchet restamp; squash → `bf86e951` |
| **#1122** | Dependabot trufflehog 3.97.4 | Rebased after #1120; squash → `ebea696f` |
| **#1126** | `claude/awesome-wright-grq7l7` | Rebased; folded #1123 Sep 7 findings; core `0.320.1→0.320.2`; squash → `493d5b5a` |

### Keep (remaining open work)

| Branch | PR | Recommendation |
|---|---|---|
| `feat/skills-deny-plugins` | **#1145** CONFLICTING | Real feature (`skills.deny_plugins`). Keep — rebase/triage separately; not a cleanup leftover. |
| `claude/source-control-github-merge-s0b4ve` | **#1146** draft, CONFLICTING | Source-control-coordinator agent (+1348). Keep — active opt-in work; not a cleanup leftover. |
| `cursor/dependency-sweep-baseline-bef8` | **#1147** draft | Host-version fingerprint baseline from first dependency sweep. Keep / merge separately. |
| `cursor/branch-cleanup-analysis-d2f1` | **#1142** draft | This docs matrix — merge as docs-only once updated. |

### Also merged this pass (late)

| PR | Result |
|---|---|
| **#1121** | zizmor-action 0.6.2→0.6.3; squash → `95a6e95a` |


## What we did not do

- Did not auto-close or archive **#1145** / **#1146** (live feature work with meaningful diffs).
- Did not force-push or `git branch -D` outside sanctioned `scripts/archive-branch.sh` / authorized Dependabot rebases.
- Did not re-enable repo auto-merge (deliberately off).

## Recovery

Archived tips are recoverable forever:

```shell
git fetch --tags
git checkout archive/<branch-with-slashes-as-dashes>-<UTC-stamp>
git branch <newname>   # if you need a working branch again
```

Audit logs (gitignored): `.ravenclaude/runs/branch-archive/`.
