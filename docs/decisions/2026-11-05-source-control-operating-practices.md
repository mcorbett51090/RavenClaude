# Decision — source-control operating practices

**Date:** 2026-11-05. **Reading taken:** the fleet's behind-first merge order is already standing GO. This record does not reopen it. It writes the classification, the remount, and the checks that make that order executable, and it names what Website and Master Overseer ops adopt.

Production deploy and go-live are out of scope. No required check was removed. `FAIL_AT` in `scripts/check-repo-file-budget.py` stays 9,990.

## What the tree already did

| Area | Where it lived before this change |
|---|---|
| Branch names, conventional commits, four-gate branch hygiene | `ravenclaude-core` `rules/git-workflow.md` |
| Trunk versus long-lived branches | `devops-cicd` decision tree, plus a one-paragraph best-practice |
| Required checks, `paths:` trap, merge queue, CODEOWNERS | `knowledge/github-actions-hardening.md`, `AGENTS.md` |
| Pre-merge SHA re-read | `agents/source-control-coordinator.md` |
| Admin bypass on this marketplace | `AGENTS.md` — scoped so docs can land on `main` |
| Auto-merge off on this repo | `CLAUDE.md` dated correction 2026-09-03 |
| Preview per PR, build-once, no plaintext secrets | one-paragraph `devops-cicd` best-practices |
| Placement ship gate name | `web-design` — `check-content-placement.mjs`, Website #953 |
| Fleet SCM ownership | `grok-bot-delegation` `fleet-standing-rules` — Sage merges; update-branch commits skip re-review; no bot deploy; vault only |

## Gaps that were high-impact

| Gap | Why it mattered |
|---|---|
| No classification of behind-clean versus dirty, and no remount | A conflict edited inside a lagging worktree mixes uncommitted files into the pull request. Merging the conflicting PR first makes every sibling conflict again. |
| Trunk-based guidance had no numbers | DORA's bar is daily merge, three or fewer active branches, and branch lifetimes of hours. The rule file still says a week. |
| Hand-merge order was a slogan ("plan the merge order") | Stacks merge from the bottom (Graphite). A queue tests the group against the latest base (GitHub) and does not understand stacks. |
| `neutral` and `skipped` satisfy a required check | An advisory bot on the required list passes when it did not review. GitHub's troubleshooting page says so. |
| Secret dual-write had only the git half | `gitops-no-plaintext-secrets` stops a committed value. It does not say what to do when the vault write succeeds and the runtime write does not. |
| Preview was not tied to production | A second build from a branch is not the artifact the preview ran. |
| Placement was a prose pass in the design plugin | Website ops need it named as a fail-closed check with no `paths:` filter. |

## What closed

- Checklist: `plugins/ravenclaude-core/knowledge/source-control-operating-practices.md` (core 0.360.3, remounted onto main's 0.360.2).
- Specialist rules: `devops-cicd` 0.3.6 — trunk citations, `merge-behind-clean-tips-before-dirty-ones`, `secrets-sync-from-one-store-do-not-hand-dual-write`, preview-then-production, required-check notes.
- Fleet adoption: `grok-bot-delegation` 0.3.1, `skills/fleet-standing-rules` section "Source control — Website and Master Overseer".
- `source-control-coordinator` points at the checklist before a merge.

## Residual

- `rules/git-workflow.md` still contains "don't let it drift more than a week." Command review refused a rewrite of that file, because the file documents the force-push prohibition and the review treats the rewrite as that prohibition. The knowledge file says it supersedes that sentence.
- `ravenclaude-core/CHANGELOG.md` on main already records 0.360.1 and 0.360.2 for other work. This change ships as 0.360.3 in `plugin.json`. A changelog heading for 0.360.3 was not added in the same edit when the premise gate refused a rewrite of that file. `plugin.json` remains the version source of truth (`AGENTS.md`).
- This marketplace's admin bypass and the auto-merge-off setting are unchanged.
- No product repository was edited. Website still has to keep `check-content-placement.mjs` as a required check that exits non-zero, with no `paths:` filter, and to keep preview and production secrets under different names. Those are follow-ups for Website ops, not for this PR.

## Sources (retrieved 2026-11-05)

- <https://dora.dev/capabilities/trunk-based-development/>
- <https://dora.dev/capabilities/continuous-integration/>
- <https://martinfowler.com/articles/branching-patterns.html>
- <https://abseil.io/resources/swe-book/html/ch16.html>
- <https://cacm.acm.org/research/why-google-stores-billions-of-lines-of-code-in-a-single-repository/>
- <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue>
- <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>
- <https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks>
- <https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews>
- <https://github.blog/changelog/2023-06-06-security-enhancements-to-required-approvals-on-pull-requests/>
- <https://graphite.com/docs/merge-stack-prs-github>
- <https://graphite.com/docs/github-configuration-guidelines>
- <https://external-secrets.io/latest/introduction/overview/>
- <https://owasp.github.io/DevSecOpsGuideline/2-Process/2-6-Deploy/2-6-2-Secrets-in-Kubernetes-and-GitOps/>
