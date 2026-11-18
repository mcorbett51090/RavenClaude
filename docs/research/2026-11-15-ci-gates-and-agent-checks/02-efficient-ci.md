# 02 — Running CI efficiently

Checked 2026-11-16. Efficiency here means fewer minutes and a shorter wait, without a required check that never reports. Runner fleet sizing, labels, and the postponed self-hosted per-minute fee stay in the [self-hosted runner research](../2026-11-15-self-hosted-runners/README.md).

## Decide inside the workflow

A trigger-level `paths:` or `paths-ignore:` on a workflow that posts a required check leaves that check Pending when the filter skips the run. GitHub's own effective-CI guidance says the same thing as the troubleshooting page: keep the required workflow unfiltered, and skip jobs inside it.

The change-detection job should be the cheapest job in the file (a shallow diff, no third-party action required). Its outputs gate the expensive jobs. An empty diff is not "nothing changed" unless a second fact agrees (the pull request's `changed_files` is 0, and the merge tree equals the base tree). A broken probe that reports an empty list fails closed.

Affected-only tests (`nx affected`, `turbo --filter`, a path-to-package map) belong in that same job. Schedule a full run on the default branch so a bad filter cannot hide a break forever. A dependency manifest change is a code change: the lockfile feeds the install the tests run against.

## Order and cancel

Run the 10-second check before the 20-minute one. A lint or typecheck failure should skip the browser matrix via `needs`, not run beside it.

Concurrency, from the workflow concurrency page, retrieved 2026-11-16:

- Group by workflow and pull request (the pull request number, not the branch name, so a reused branch does not collide).
- `cancel-in-progress: true` only for `pull_request`. A cancelled run is attached to a SHA that is no longer the head, so it cannot gate the new head. The new push starts a new run.
- Do not cancel a push to the default branch. That run is the record that the default branch built.
- Do not cancel `merge_group` runs. The queue is the record for that group.
- `queue: single` (the default) keeps one pending run and drops the older pending one. `queue: max` keeps up to 100 pending runs. `queue: max` together with `cancel-in-progress: true` is a workflow validation error.
- Concurrency group names are global in the repository. Include `github.workflow` or two workflows will cancel each other.

## Cache

Key dependency caches on the lockfile hash plus the OS and tool version (`hashFiles('**/package-lock.json')`). A constant key serves a stale tree. `restore-keys` may fall back to a prefix; the job must still be correct on a miss.

The Actions cache is 10 GB per repository before it is billed, and entries age out. A cache is shared by branch, not by workflow. Treat restored files as untrusted input. Do not put secrets in a cache. Since the 2026-06 change, untrusted triggers get a read-only cache token for the default-branch cache. Do not design a job that needs to write the cache from a fork pull request.

For BuildKit's `type=gha` backend, the default scope is `buildkit`. Two images in one repository overwrite each other's cache; the last writer wins. Set `scope` to the image name on both `cache-from` and `cache-to`. `mode=max` keeps intermediate stages and uses more of the 10 GB. Docker's gha backend page, retrieved 2026-11-16, is the source. Cache writes from some events are read-only in the default-branch context; a miss is a normal case.

A self-hosted runner that keeps a workspace between jobs is not a cache. It is leftover state. Clean the workspace at the start of the job, and still key a real cache so a fresh machine is not a full download.

## Shards, flakes, timeouts

Split a suite by measured duration, not by file count. Rebalance when one shard is the long pole. `strategy.fail-fast` defaults to true: one failed matrix leg cancels the others. Set it false when you need every leg's log. A leg with `continue-on-error: true` does not cancel its siblings.

GitHub Actions has no step-retry key. Retry at the layer that failed:

| What failed | Retry | Do not |
|---|---|---|
| A network install | The install step, a small number of times, with the attempt count in the log | Retry the test suite |
| The runner lost the network or ran out of memory | Re-run the failed jobs (`gh run rerun --failed`). Same SHA, new machine, at most 50 times within 30 days | Hide the count |
| One test flips | The test runner's own retry, and record the flake | Mark the job green with `continue-on-error` |

Quarantine a test that fails for a reason you have not fixed: take it out of the required job, keep it in a non-required report, and give it an owner and a removal date. A retry that turns a real assertion green is a hole in the gate.

Set `timeout-minutes` on every job. The platform default is 6 hours. A hung checkout should die in minutes. Scale timeouts up for a slow lane with one knob. Do not scale them down.

## Cost

Hosted minutes are the bill. The largest saving on a pull-request-heavy repo is cancelling the superseded run, then not starting the long job when the diff cannot affect it. A post-merge run of the long job on a docs-only commit to the default branch is spend with no gating value; a push filter on the default branch is safe because that run is not a required check. The pull-request trigger of a required workflow stays unfiltered.

Self-hosted minutes were still free as of the November 2026 runner research (the $0.002/min fee was postponed). They are not free in wall-clock or in the machine's RAM. A weak runner that carries a strong runner's labels takes the heavy job. That research's finding stands.

Larger hosted runners cost more per minute and help only when the job is CPU-bound or memory-bound after the cache and the shard split are right. Buy the cache first.
