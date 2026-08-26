# Runbook: CI didn't run on a pushed commit (remote web session) — detect & re-trigger

> **TL;DR** — In a Claude-Code-on-the-web session, a `git push` can update the PR head on GitHub **without** GitHub Actions creating any workflow runs for that commit. The PR then sits with **no checks** forever, so "merge when green" never fires. **Detect it** by comparing the latest workflow-run `head_sha` to the PR head; **fix it** by manually dispatching each workflow with `workflow_dispatch`. First observed 2026-06-22 on PR #452.

> **Before diagnosing ANY abnormal CI behavior (this runbook's "0 checks" case, or the "stuck queued forever" case below), run `scripts/check-github-status.sh` first.** It checks GitHub's own incident status (githubstatus.com) for Actions/Pages/API/Git outages in ~1 second, for free. On 2026-08-26 a session spent ~150 turns and a full research pass diagnosing what turned out to be a live, GitHub-acknowledged critical Actions outage (see "Stuck queued with zero jobs provisioned" below) — a single status check would have confirmed the cause and correct response (wait) in seconds instead. This does **not** replace the detection steps below when the status page is clean — an "Operational" reading is not proof of health (see [`plugins/ravenclaude-core/knowledge/concepts/github-status-page-cannot-see-this.md`](../plugins/ravenclaude-core/knowledge/concepts/github-status-page-cannot-see-this.md): a runner-image rollout once broke every PR while the status page stayed green). But a **live incident shown** on the affected component (Actions) is strong, immediate evidence — treat it as the working hypothesis before spending tokens on deeper diagnosis.

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

---

## A different failure mode: stuck queued with zero jobs provisioned

This is **not** the "no runs created" case above — here, runs **are** created (webhook delivery is working), but they sit in `status: "queued"` forever with `startedAt: null` and an **empty `jobs[]` array** (`GET .../actions/runs/{id}/jobs` → `total_count: 0`). First observed 2026-08-26 on PR #1031 (`fix/base-ref-unshallow-fetch`), persisting ~50 minutes.

**Symptoms:**
- `gh run list --status in_progress` returns `[]` account-wide, repeatedly, over many minutes.
- The stuck run's `jobs[]` array is empty — no job was ever provisioned to a runner.
- `gh run cancel <id>` / `POST .../cancel` → **HTTP 409 "Cannot cancel a workflow run that has not been queued yet"** — contradicting the run's own `status: "queued"` field.
- `DELETE .../runs/{id}` → **HTTP 403 "Could not delete the workflow run"**.
- A `git commit --allow-empty` push DOES create a fresh `pull_request`-triggered run (unlike the "0 checks" case above) — but the fresh run gets stuck the same way.
- `gh run rerun <id>` on a run that GitHub eventually gave up on and marked `completed`/`conclusion: failure` (after a long enough queue timeout) resets it to `queued` — but it can get stuck again if the underlying cause hasn't cleared.

**Root cause: a known, recurring GitHub Actions backend bug class, usually triggered by a live GitHub-side incident.** GitHub creates the run record before provisioning jobs; when a backend incident (auth failures, database/Vitess issues, capacity saturation) interrupts that window, the run is orphaned — record exists, jobs never provisioned. The 409/403 errors are consistent with this: cancel/delete require a job or a fully-queued state that never materialized. This exact symptom (409 "not been queued yet") has been reported on GitHub's community forums going back to Aug 2024, was called "fixed," and recurred — so it is not durably fixed, and self-resolves only when GitHub's incident/capacity issue clears.

**Fix: check `scripts/check-github-status.sh` FIRST (see the callout at the top of this doc).** If it shows a live incident affecting Actions:
1. **Don't keep retrying** cancel/delete/rerun/re-dispatch — none of it helps while the incident is active; community reports confirm force-cancel fails too.
2. **Don't disable/re-enable Actions, rotate tokens, or otherwise change local config** — this is GitHub-side, not a repo/account/token problem (confirmed by checking: Actions permissions enabled, no self-hosted-runner requirement, no account-wide concurrency saturation from other repos, not an Actions-minutes/billing issue).
3. **Wait, checking `scripts/check-github-status.sh` periodically** (every several minutes, not continuously — it won't resolve faster for being polled more) until the incident moves to `resolved` or drops out of the unresolved list.
4. Once resolved, the next `pull_request` push or `workflow_dispatch` should provision jobs normally. If a specific run is still stuck after resolution, `gh run rerun <id>` on it (or a fresh empty-commit push) is usually enough — no further diagnosis needed.

If `check-github-status.sh` shows nothing relevant, this failure mode is unexplained by that route — fall back to checking account-wide concurrency (`gh run list --status in_progress` across the account's other repos), Actions permissions (`gh api repos/<owner>/<repo>/actions/permissions`), and org/enterprise-level policy before assuming it's transient.
