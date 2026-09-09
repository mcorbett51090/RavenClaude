# RavenClaude remote-branch cleanup — 2026-09-09

Inventory of every non-`main` remote head on `mcorbett51090/RavenClaude`, classified against `origin/main` (`44a1a22e`) and associated PRs. Executed under FORGE slug `branch-cleanup` (quick).

## Summary

| Bucket | Count | Action taken / recommended |
|---|---|---|
| Merged leftovers / already-landed tips | 5 | Archive tag + delete remote |
| Closed PRs (explicitly superseded / empty) | 8 | Archive tag + delete remote |
| Open drafts (Claude) | 3 | Keep — triage; **#1138 is the CI unblock** |
| Open Dependabot | 3 | Keep — blocked until `validate-marketplace` is green on main |
| Analysis worktree | 1 local (`forge/branch-cleanup`) | Keep until this cleanup finishes |

**Observation:** `validate-marketplace` is red on `main` (post plan-archive link/`prettierignore`/ratchet drift). Draft **#1138** is the fix-forward; it is `CONFLICTING` and needs rebase before merge. Dependabot PRs #1120–#1122 fail the same required check because of that shared failure, not because the bumps themselves are broken.

## Detailed classification

### Archive + delete remote (clear-cut)

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

### Keep (open work)

| Branch | PR | Recommendation |
|---|---|---|
| `claude/awesome-wright-4jz4tu` | **#1138** draft, CONFLICTING, checks green on the tip | **Rebase onto main → mark ready → merge.** Highest priority — restores required check. |
| `claude/awesome-wright-grq7l7` | **#1126** draft, CONFLICTING | Rebase or cherry-pick the review findings onto main (`docs/` may go straight to main). Do not close until findings are landed or rejected. |
| `claude/awesome-wright-lm1y5x` | **#1123** draft, CONFLICTING | Same as #1126 — Sep 7 review write-up not yet on `docs/reviews/`. |
| `dependabot/github_actions/actions-4684ddd577` | **#1120** | Merge after #1138 (or once main core suite is green). Bump itself is trivial. |
| `dependabot/github_actions/trufflesecurity/trufflehog-3.97.4` | **#1122** | Same |
| `dependabot/github_actions/zizmorcore/zizmor-action-0.6.3` | **#1121** | Same |

## What we did not do

- Did not merge or close any open PR (preference / CI-gated).
- Did not force-push or `git branch -D` (guard + house rule 5).
- Did not archive heads that still back an open PR.

## Recovery

Archived tips are recoverable forever:

```shell
git fetch --tags
git checkout archive/<branch-with-slashes-as-dashes>-<UTC-stamp>
git branch <newname>   # if you need a working branch again
```

Audit logs (gitignored): `.ravenclaude/runs/branch-archive/`.
