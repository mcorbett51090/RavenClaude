# CI gates, efficient checks, and agent-reported results (research, 2026-11-16)

Research into five questions: what a merge gate actually is, how to run CI without wasting runner time, when a coding agent should do the work instead of a runner, how an agent-run check can count as a pass without being spoofable, and how to review the check list on a schedule. Six research passes were run. The last one turned up nothing materially new, so the loop stopped there ([pass log](passes.md)).

Facts are tagged with where they came from and the date they were checked. Treat capability rows as `[verify-at-use]`. GitHub's ruleset and Actions pages move.

The private product repo holds the reading of its live ruleset and the numbered changes that still need a GO. This public note keeps the pattern and leaves out host names, tokens, and the exact pass token the bridge scans for.

## Files

| File | What it covers |
|---|---|
| [01-gates.md](01-gates.md) | Rulesets versus branch protection, skipped jobs, path filters, merge queues, the aggregate gate, source apps, environments, CODEOWNERS, signed commits, deploy gates |
| [02-efficient-ci.md](02-efficient-ci.md) | Change detection, affected tests, sharding, caches, concurrency, fail-fast order, flakes, timeouts, cost |
| [03-agent-or-runner.md](03-agent-or-runner.md) | When a coding agent should run the check, and when a runner should |
| [04-agent-checks-that-count.md](04-agent-checks-that-count.md) | Binding a result to a SHA, pinning the source app, attestations, sampling, and the false-green threat |
| [05-review-and-update.md](05-review-and-update.md) | Inventory, ownership, metrics, pinning, linters, and the byte-pin anti-pattern |
| [06-recommendations-factory.md](06-recommendations-factory.md) | What this factory should change, as a pattern |
| [runbook.md](runbook.md) | The checklist to run on a cadence |
| [sources.md](sources.md) | Every source, grouped |
| [passes.md](passes.md) | The research pass log |

## Top findings

1. **A skipped job is a pass.** GitHub's troubleshooting page, retrieved 2026-11-16, lists `success`, `skipped`, and `neutral` as successful check statuses. A job skipped by `if:` reports Success and does not block a merge, even when that job name is required. A workflow skipped by `paths:`, `branches:`, or a commit message reports nothing, and the required check stays Pending. The safe shape is one aggregate job that always runs, and that job is the only required name. ([01](01-gates.md))
2. **Anyone with write access can set a commit status.** Rulesets let you name the GitHub App that must report each required context (`integration_id`). "Any source" accepts a status from any person or app that can write statuses, including a workflow token that opted into `statuses: write`. Check runs are a different object: the Checks REST guide says only a GitHub App can create them. A personal access token posts commit statuses, not check runs. ([04](04-agent-checks-that-count.md))
3. **The agent's sentence is not the test result.** A cloud agent is good at running commands and explaining a red log. It is a bad source of truth for green, because the repository it reads can contain instructions, and the model can report a pass it did not earn. The status writer must be a program that does not trust the model's last message, and the ruleset must accept that status only from one App. ([03](03-agent-or-runner.md), [04](04-agent-checks-that-count.md))
4. **A green status is per SHA, and a loose ruleset does not refresh it.** Required checks are evaluated on the latest head SHA. A new push has no status until something posts one. With strict off, a head that was green against an older base can still merge. Strict, or a merge queue, is what re-tests the code that will land. A merge queue does not run unless the workflow also triggers on `merge_group`. ([01](01-gates.md))
5. **Cheap checks first, and cancel only the superseded pull request.** Order lint and the change probe before the long suite. A concurrency group per pull request with `cancel-in-progress` only on `pull_request` drops the stale run. Do not cancel the default-branch run or a merge-group run. Cache on the lockfile hash. Give each image its own BuildKit `scope` or the `gha` backend keeps only the last image. ([02](02-efficient-ci.md))
6. **Pin the action code, then review the bumps.** GitHub's secure-use page now says a workflow dependency lockfile (`.github/workflows/actions.lock`, public preview, changelog 2026-10-14) is stronger than a SHA pin in the workflow file, because it covers transitive actions and checks the source repository id at run time. Where the lockfile is not available, pin `uses:` to a full SHA. Dependabot's `github-actions` ecosystem opens the bumps. `zizmor` and `actionlint` lint the workflows. ([05](05-review-and-update.md))
7. **A test that pins a workflow byte for byte freezes the pipeline.** Pin the contract: the check name, the permissions ceiling, that the guard is the first step, that a required workflow has no trigger-level path filter. Pin bytes only where the bytes are the control, such as a runner-name script copied into every job. ([05](05-review-and-update.md))

## How this extends what we already had

- `plugins/devops-cicd/best-practices/pipeline-required-checks-gate-the-merge.md` already said that `skipped` and `neutral` satisfy a required check, and that a `paths:` filter must not sit on a required workflow. This research adds the source-app pin, the aggregate job, and the agent-reported status.
- `plugins/devops-cicd/knowledge/deployment-strategy-and-runner-cache-decision-trees.md` already had runner placement and lockfile-keyed caches. The capability map now points here for gates and for the lockfile.
- The self-hosted runner research ([2026-11-15](../2026-11-15-self-hosted-runners/README.md)) still owns fleet sizing, labels, and the postponed per-minute fee. This note does not repeat it.
