# 06: Security and cost

## Threat model (from GitHub's [secure use reference](https://docs.github.com/en/actions/reference/security/secure-use))

- Self-hosted runners "can be persistently compromised by untrusted code in a workflow". **Never attach them to public repos.** On private repos, anyone who can open a PR (read access plus fork) can run code on them.
- Jobs on the same runner can see each other: env vars, files left in shared dirs, the Docker socket, and **secrets passed on the command line are visible via `ps`**. Per-job destruction helps, but "there is no way to guarantee that a self-hosted runner only runs one job" unless it's ephemeral or JIT.
- Keep sensitive material off runner hosts: SSH keys, cloud credentials, metadata-service reachability, personal browser sessions. A personal laptop is a high-value host. Run CI as a dedicated OS user inside a VM or sandbox.

## Controls, in order of value

1. **Trust lanes.** Secrets and deploy jobs run only on dedicated runners, ideally **ephemeral or JIT** with a fresh work dir, with labels no PR job can request, and hard-coded `runs-on` (no `vars.*` override). Use environments plus required reviewers for production secrets.
2. **JIT or 1-hour registration tokens** minted by a control host. No long-lived registration secret on runner disks. The minting credential (repo Administration: write) never sits on a PR runner.
3. **Least-privilege `GITHUB_TOKEN`** (`permissions:` per job), pinned actions (SHA or a workflow lockfile), and `persist-credentials: false` on checkout.
4. **Cache hygiene.** Untrusted triggers get read-only cache by default (2026-06). Don't design jobs that write cache from untrusted triggers ([see the devops-cicd tree](../../../plugins/devops-cicd/knowledge/deployment-strategy-and-runner-cache-decision-trees.md)).
5. **Workspace and process cleanup hooks** (`ACTIONS_RUNNER_HOOK_JOB_STARTED` / `_COMPLETED`) on persistent runners: kill stray processes from the runner's own `_work`, and empty the workspace.
6. **Egress limits** on runner hosts (GitHub domains plus what builds need). The domain list is in the [self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners).

## Cost (checked 2026-11-15)

- **Self-hosted execution is free.** GitHub announced a $0.002/min "cloud platform charge" for self-hosted minutes in private repos starting 2026-03-01 (2025-12-16), then **postponed it** with no new date ([changelog](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/), [RunsOn status](https://runs-on.com/blog/github-self-hosted-runner-fee-2026/)). Plan as if it could come back. At $0.002/min, 40k min/month would be $80.
- Hosted rates dropped by up to 39% on 2026-01-01 (Linux 2-core about $0.006/min; macOS about $0.062/min).
- **Cache:** 10 GB per repo included, with usage above that billed, so on an account where billing is blocked keep caches under 10 GB ([changelog](https://github.blog/changelog/2025-11-20-github-actions-cache-size-can-now-exceed-10-gb-per-repository/)).
- The real self-hosted costs are electricity, wear, and **operator time**: supervising sleep, ghosts, upgrades, and label drift. Ephemeral or scale-set designs trade a bit of setup for much less babysitting.
