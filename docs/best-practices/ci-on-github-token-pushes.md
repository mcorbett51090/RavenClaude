# CI doesn't run on a session's own pushes — trigger it with `workflow_dispatch`

**Status:** Primary diagnostic — when a PR's head commit shows **zero checks** and you pushed it from a Claude Code remote/web session, this is the first thing to check.

**Domain:** CI / Remote-environment mechanics.

**Applies to:** any Claude Code session running in the remote/web execution environment (Claude Code on the web, GitHub Actions trigger, mobile/desktop hand-off) that pushes to a branch with `pull_request`-triggered workflows — i.e. this whole marketplace, and any consumer repo a session operates on.

---

## Why this exists

In the remote execution environment, `git push` is authenticated by the session's **`GITHUB_TOKEN`**. GitHub deliberately **does not spawn new workflow runs for events produced by `GITHUB_TOKEN`** — it is the platform's anti-recursion guard (so an Action pushing a commit can't infinitely re-trigger itself). The practical consequence for an agent: **you push commit after commit to a PR branch and no CI ever starts.** The PR's combined status sits at `pending` with `total_count: 0`, `get_check_runs` returns an empty list, and "merge when green" never reaches green because nothing is running. This was rediscovered the hard way on PR #275 (2026-06-04): four pushes from the session produced **zero** workflow runs, while the original PR-`opened` event (fired from a *different*, non-`GITHUB_TOKEN` context at branch creation) had run CI green once. A session that doesn't know this will either wait forever or wrongly conclude CI is broken.

Two related traps in the same family:

- **Marking a draft PR "ready for review" does NOT trigger CI** unless the workflow's `on.pull_request.types` explicitly lists `ready_for_review` (most here list only the defaults: `opened`, `synchronize`, `reopened`). Flipping draft→ready is not a substitute for a trigger.
- **An empty "trigger" commit also won't help** — it's still a `GITHUB_TOKEN` push, so it produces no run either.

## How to apply

When a PR head has no checks and you need CI to run, trigger each workflow explicitly with `workflow_dispatch` against the branch ref. Every gate workflow in this repo already has `workflow_dispatch:` in its `on:` block, so this Just Works:

```
# Load the tool first (deferred): ToolSearch "select:mcp__github__actions_run_trigger"
mcp__github__actions_run_trigger(
  method      = "run_workflow",
  owner       = "<owner>",
  repo        = "<repo>",
  workflow_id = "validate-marketplace.yml",   # the workflow FILENAME, not its display name
  ref         = "<your-branch>",               # dispatch runs against the branch head
)
# repeat for each required workflow (validate-schemas.yml, validate-layout.yml, …)
```

Then poll for completion (webhook events are **not** delivered for `workflow_dispatch` runs, nor for CI *success* on any run — so you must poll, not wait):

```
mcp__github__pull_request_read(method="get_check_runs", owner=…, repo=…, pullNumber=…)
# each run reports status: queued → in_progress → completed, with conclusion: success|failure
```

A `workflow_dispatch` run attaches its check to the branch **head SHA**, so a branch-protection rule that requires a named check (e.g. "Validate manifests and hooks") is satisfied by the dispatched run on that SHA — you can then merge.

**Do:**
- Run the **full local gate suite first** (`prettier --check .`, the `--check` freshness gates, `scripts/audit-gates.sh`) so you catch failures in-session instead of round-tripping through remote CI you had to hand-trigger anyway.
- Back off between polls with a **background** `sleep` (`run_in_background: true`) — foreground sleep is blocked, and rapid-fire polling is noise.
- Use the workflow **filename** as `workflow_id` (`validate-marketplace.yml`), not its display title.

**Don't:**
- Don't push an empty commit "to kick CI" — same `GITHUB_TOKEN`, same no-op.
- Don't rely on draft→ready to start CI.
- Don't wait on webhook events for a dispatched run or for CI success — poll.
- Don't conclude "CI is broken" or "I can't get it green" from an empty check list — that's evidence about the *trigger*, not the pipeline (the accuracy-discipline "can't" trap).

## Edge cases / when the rule does NOT apply

- **A human (or a non-`GITHUB_TOKEN` actor) pushes the branch** → normal `synchronize` CI fires; no dispatch needed.
- **The workflow lacks `workflow_dispatch:`** in its `on:` block → you cannot dispatch it; either add the trigger in a separate change, or rely on a human push. (All current marketplace gate workflows already have it.)
- **`push`-to-`main` workflows** still run on the actual merge to `main` through the normal path — this trap is specific to **PR-branch** `pull_request` runs during a session.
- **Branch protection requires a check that only ever runs on `pull_request` (not `workflow_dispatch`)** → the dispatched run's context name must match the required check name; if it doesn't, escalate to a human push rather than assuming blocked.

## See also

- [`ci-gate-audit.md`](./ci-gate-audit.md) — the gates themselves (every gate must fail-on-bad and pass-on-good).
- [`github-api-and-rate-limits.md`](./github-api-and-rate-limits.md) — the GitHub MCP surface this uses.
- [`pr-vs-direct-push.md`](./pr-vs-direct-push.md) — when a change needs a PR (and therefore CI) at all.
- The mirror-image "I can't" trap and its falsifiability bar: `AGENTS.md` § "Accuracy discipline" + [`../../plugins/ravenclaude-core/CLAUDE.md`](../../plugins/ravenclaude-core/CLAUDE.md) (Capability Grounding Protocol).

## Provenance

Discovered on **PR #275 (2026-06-04)** while driving a "merge when green" task: four `GITHUB_TOKEN`-authenticated pushes produced zero workflow runs (`get_check_runs` empty, combined status `pending`/`total_count: 0`), while the branch-creation `opened` event had run all three gates green once. Confirmed the workflows' `paths:` covered the changes and that they carried `workflow_dispatch:`, then triggered them via `mcp__github__actions_run_trigger` against the branch ref — all three produced checks on the head SHA and went green, unblocking the squash merge. The repo's own `guard-destructive.sh` blocks `curl`-to-API polling, which independently confirms MCP (`get_check_runs` / `actions_list`) as the sanctioned status-polling route.

---

_Last reviewed: 2026-06-04 by `mcorbett51090`_
