# Runbook: CI didn't run on a pushed commit (remote web session) — detect & re-trigger

> **TL;DR** — In a Claude-Code-on-the-web session, a `git push` can update the PR head on GitHub **without** GitHub Actions creating any workflow runs for that commit. The PR then sits with **no checks** forever, so "merge when green" never fires. **Detect it** by comparing the latest workflow-run `head_sha` to the PR head; **fix it** by manually dispatching each workflow with `workflow_dispatch`. First observed 2026-06-22 on PR #452.

## What happened (the incident)

On PR #452 the first two pushes (`8510ddf`, `922bb13`) auto-triggered the three PR workflows (Validate Layout / Schemas / Marketplace) normally. The next two pushes — `cf63669` (real changes) and `f84a62d` (empty re-trigger commit) — produced **zero** workflow runs:

- `pull_request_read` `get_status` → `state: "pending", total_count: 0`
- `pull_request_read` `get_check_runs` → `total_count: 0`
- `actions_list` `list_workflow_runs` (branch) → newest run still the *previous* commit; head count frozen.

Yet GitHub clearly had the new commit (`get_status.sha` == the pushed SHA), and all workflows were `state: active`. So the refs arrived but **no runs were created**.

## Root cause (what it was — and what it was NOT)

- **NOT exhausted Actions minutes / spending limit.** That was the first hypothesis (the heavy `Validate Marketplace` gate-audit is minute-hungry), but it was **disproven**: a manual `workflow_dispatch` of the same workflows executed immediately and to completion. If minutes were exhausted, the dispatched runs wouldn't have run either. *(Lesson: don't assert "minutes exhausted" from "no runs"; a successful dispatch falsifies it.)*
- **NOT a `paths:` filter.** Two of the three workflows have `pull_request: paths:` filters, but `validate-layout.yml` has **no** filter and should run on every PR push — and it *also* produced no run. When the unfiltered workflow doesn't spawn either, the path filters aren't the cause. (Note: the empty commit `f84a62d` is separately path-filtered out of two workflows, but that's a side issue, not the root cause.)
- **Operative cause: the remote git proxy push did not reliably emit the `pull_request: synchronize` event that auto-creates runs.** Web/remote sessions push through a local git proxy (`http://127.0.0.1:<port>/git/...`) that forwards to github.com. The ref update reaches GitHub (head SHA updates) but the `synchronize` webhook that GitHub Actions keys off **was not delivered/processed** for those pushes — intermittently (it worked for the first two pushes, not the later ones). The result is a ref with no associated workflow runs. This is environmental and intermittent, not a repo-config bug.

## How to detect it (check this before waiting on "green")

After any push in a remote session, **do not assume CI will run.** Verify a run was actually created for the *current* head:

1. `pull_request_read method:get_status` — if `total_count: 0` **and** `state: "pending"` a minute+ after the push, suspect it.
2. `pull_request_read method:get_check_runs` — `total_count: 0` confirms no checks exist for the head.
3. `actions_list method:list_workflow_runs` (filter the branch) — if the newest run's `head_sha` is **not** the current PR head, the auto-trigger didn't fire for this commit. (This list can be large; parse it for `head_sha | status | conclusion | name`.)

If runs exist and are `in_progress`/`queued`, just wait — this runbook does **not** apply. It applies only when **no runs were created** for the current head.

## How to fix it (re-trigger)

Every PR workflow here also declares `workflow_dispatch`, so trigger each one manually against the branch ref:

```
actions_run_trigger method:run_workflow ref:<branch> workflow_id:validate-marketplace.yml
actions_run_trigger method:run_workflow ref:<branch> workflow_id:validate-layout.yml
actions_run_trigger method:run_workflow ref:<branch> workflow_id:validate-schemas.yml
```

Each returns `204 / "Workflow run has been queued"`. Wait ~2–3 min, then re-check `get_check_runs` — the dispatched runs attach to the head commit and appear as PR checks. Merge once all are `conclusion: success`.

Notes:
- A `workflow_dispatch` run **does** create check runs on the head commit, so it satisfies a "green checks" merge gate the same way an auto-run would. (If the repo ever adds branch protection that requires a *specific auto-triggered* status context, a dispatched run may not satisfy it — re-confirm at that point.)
- An **empty commit does not reliably re-trigger** here: it changes no files, so any `paths:`-filtered workflow correctly skips it, and the auto-trigger may not fire anyway. Prefer `workflow_dispatch` over an empty commit.
- Before relying on a dispatched green, make sure the head is **not behind main** — a stale head can pass its own checks yet still hit merge conflicts (also seen on #452; resolve by merging `origin/main` and re-dispatching).

## One-line procedure for future sessions

> After pushing to a PR in a remote session: confirm a run exists for the current head (`get_check_runs` / `list_workflow_runs` head_sha); if none, `workflow_dispatch` each PR workflow on the branch, wait, then merge when all are `success`. Never conclude "minutes exhausted" — a successful dispatch disproves it.
