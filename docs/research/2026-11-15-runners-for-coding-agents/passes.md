# Research passes

Loop rule: stop when a pass adds no new primary fact. Minimum three passes. Dates are 2026-11-16.

## Pass 1 — map the products

Searches: Copilot self-hosted runners and `copilot-setup-steps.yml`; Claude Code GitHub Action runner requirements; Cursor cloud agents and CI; Codex in GitHub Actions; hosted versus self-hosted job ceilings; concurrency and merge queues.

New primary facts:

- Copilot setup job honors six keys. `timeout-minutes` max 59. Self-hosted requires the integrated firewall off. Ubuntu x64 and Windows 64-bit only. ARC or the scale-set client is the recommended shape.
- Claude action cost section assumes hosted minutes. `--max-turns`, timeouts, and concurrency are the documented caps. Default token pushes do not start workflows.
- Cursor cloud agents run on Cursor VMs. A separate docs page puts the CLI inside Actions. A self-hosted worker is outbound-only.
- Codex action: Linux or macOS, `drop-sudo` by default, Windows only with `unsafe`.
- Hosted jobs 6 hours, self-hosted jobs 5 days, queue 24 hours.
- `queue: max` holds up to 100 pending runs and cannot be combined with `cancel-in-progress: true`.

## Pass 2 — read the pages, fill the holes

Fetched the Copilot environment doc, the firewall doc, the organization runner doc, the Claude docs page (saved in full), the limits page, and the concurrency page. Searched billing, isolation (gVisor / Firecracker), larger-runner prices, and current ARC / scaleset releases.

New primary facts:

- Three Copilot environments. Cloud is the default and is chosen at session start.
- Session cap of 59 minutes is on the Actions path, separate from the setup job's own 59-minute timeout.
- Firewall does not cover setup-step processes or every MCP server.
- Organization runner lock exists and is irrelevant to a user account.
- Legacy premium-request page is plan-limited.
- Sandbox meters: `$0.000024` per compute-second, `$0.000003` per GiB-second, `$0.005` per GiB-month.
- Larger-runner price table (4-core `$0.012`, 8-core `$0.022`, 16-core `$0.042`).
- Token lifetime 24 hours on self-hosted even though the job ceiling is 5 days.
- Claude security doc: `pull_request_target` checkout rule, `restrict_untrusted_prs`, `allowed_bots` on public repos, leftover git config after cancel on a persistent runner.
- ARC `gha-runner-scale-set-0.15.1` and `actions/scaleset` v0.5.0, both 2026-10-23. No newer release tag.
- gVisor / Firecracker are real options and need a cluster or a microVM controller this fleet decided not to run.

## Pass 3 — contradictions and the factory

Fetched Copilot risks and mitigations, the Claude security doc in full, the Codex action page, the Codex cloud page, and the custom-image page (to see what `snapshot` means). Searched for a later change to the 59-minute cap. Read Website `claude.yml` and searched the default branch for concurrency and for Copilot/Codex workflow files. Confirmed account type and repository visibility via the GitHub API.

New primary facts:

- 2026-10-28 changelog: sandbox has no one-hour cap; Actions path still required for setup steps and self-hosted; `--environment-host` is a third place to run; sandbox billing begins November 2026 with no day; shared dollar entitlement; larger runners only on Team and Enterprise Cloud.
- 2026-02-13 changelog: plan-specific Copilot API hosts from 2026-02-27. Current docs also list Copilot Max on the individual host.
- `snapshot` generates a larger-runner custom image. It is not a cache for a self-hosted box.
- Copilot workflows do not run until approved, by default. That is the opposite of the Claude app, whose pushes are supposed to start CI.
- Codex cloud: internet off in the agent phase by default, secrets stripped before that phase, 12-hour container cache. The page is labeled legacy.
- Website Claude job: 90 minutes, fallback `["self-hosted"]`, no name guard, amd64 `gh` tarball, per-issue concurrency with cancel off.
- `commerce-ci.yml` has no `concurrency` key. No `copilot-setup-steps.yml` and no `codex-action` in the repo.
- Owner is a user. RavenClaude is public. Website is private.

## Pass 4 — stop check

Searched for a published November billing start day and a published sandbox machine size, and re-read the 2026-10-28 changelog.

No new primary fact. The changelog still says "begins in November 2026" with no day. The billing page still does not state vCPU or GiB. Secondary posts agree those two numbers are unpublished; none of their arithmetic was copied. ARC and scaleset had no release newer than pass 2.

Stopped.
