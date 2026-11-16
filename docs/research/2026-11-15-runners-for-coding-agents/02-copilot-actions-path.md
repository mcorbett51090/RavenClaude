# 02: Copilot cloud agent on GitHub Actions

Retrieved 2026-11-16 from GitHub's docs and the 2026-10-28 and 2026-02-13 changelogs. GitHub now calls the coding agent "Copilot cloud agent." A session starts in one environment and cannot switch: Cloud (default), Actions, or a custom environment (`--environment-host`).

Website has no `copilot-setup-steps.yml` (code search on the default branch, 2026-11-16). Nothing here is live until someone adds that file and chooses Actions at session start.

## When Actions is the right environment

Choose Actions only when the task needs something the sandbox does not have: `copilot-setup-steps.yml`, a Windows toolchain, or a runner on the private network. Otherwise leave the session on Cloud.

Cloud sandbox, from the [2026-10-28 changelog](https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/):

- Default, on GitHub-managed infrastructure.
- No one-hour limit on total running time. A stopped sandbox keeps a snapshot and can resume.
- Billing "begins in November 2026." No day is stated. Usage draws from the shared Actions compute entitlement.
- Rates on the [sandbox billing page](https://docs.github.com/en/billing/concepts/product-billing/cloud-and-local-sandboxes): compute `$0.000024` per second, memory `$0.000003` per GiB-second of **allocated** memory, snapshot storage `$0.005` per GiB-month. The page does not publish the sandbox's vCPU or memory size, so an hourly total cannot be computed from the docs.

Actions sessions, from [Copilot on GitHub.com](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github):

- One repository, one branch, one pull request per task.
- **Maximum execution time 59 minutes.** "This limit cannot be extended or bypassed."
- Setup steps, larger runners, self-hosted runners, and Windows exist only on this path.

## The setup file

Path: `.github/workflows/copilot-setup-steps.yml`. It must be on the default branch. The job must be named `copilot-setup-steps`. GitHub honors only these job keys; anything else is ignored:

| Key | Constraint |
|---|---|
| `steps` | Run before the agent. A non-zero exit skips the remaining steps and the agent starts anyway, in whatever state the environment reached |
| `permissions` | Keep them at `contents: read` if a step checks the repo out. Copilot uses its own token afterwards |
| `runs-on` | The runner. See below |
| `services` | Service containers |
| `snapshot` | The Actions custom-image keyword. It generates a larger-runner image and needs an org or enterprise image-generation runner. It does nothing useful on this user account |
| `timeout-minutes` | Maximum `59` |

`actions/checkout`'s `fetch-depth` is overridden so the agent can roll commits back. `concurrency`, `container`, and `environment` on this job are ignored.

## Runners

Default is `ubuntu-latest`. To move it:

1. **Larger hosted runners** (`runs-on: ubuntu-4-core` and similar). Not available on a user account. On Team or Enterprise Cloud they bill at the [published per-minute rates](https://docs.github.com/en/billing/reference/actions-runner-pricing) (Linux 4-core `$0.012`, 8-core `$0.022`, 16-core `$0.042`, retrieved 2026-11-16). Idle larger runners are not billed.
2. **Self-hosted.** GitHub's recommendation is ephemeral, single-use runners, usually ARC or the Runner Scale Set Client. Set `runs-on` to the scale set's name. Persistent runners that also run tests are the shape they tell you to avoid.

Architecture: Ubuntu x64 or Windows 64-bit. macOS and anything else, including Linux arm64, are unsupported. The Mac lanes cannot take this job.

Windows: the integrated firewall is not compatible. GitHub says to use self-hosted runners or larger runners with your own network controls. This fleet has no Windows runner.

## Firewall

The integrated firewall is on by default and applies to processes the agent starts through its Bash tool. It does not cover every MCP server, and it does not cover processes started by setup steps. GitHub says it is not a complete security boundary.

**Self-hosted runners: the firewall must be disabled in the repository's Internet access settings, or Copilot cloud agent is blocked.** Disabling it lets the agent reach any host. The replacement is a firewall on the runner host.

Hosts the runner must be allowed to reach, plus the usual Actions runner hosts:

- `uploads.github.com`
- `user-images.githubusercontent.com`
- `api.individual.githubcopilot.com` for Copilot Pro, Pro+, and Max
- `api.business.githubcopilot.com` for Copilot Business
- `api.enterprise.githubcopilot.com` for Copilot Enterprise

The plan-specific hosts took effect 2026-02-27 ([changelog](https://github.blog/changelog/2026-02-13-network-configuration-changes-for-copilot-coding-agent/)). The current environment doc adds Copilot Max on the individual host. `[verify-at-use]` if a new plan name appears.

If a third-party coding agent (the docs name OpenAI Codex in this slot) shares that Actions network path, also allow `npmjs.org`, `npmjs.com`, `registry.npmjs.com`, `registry.npmjs.org`, and `skimdb.npmjs.com`.

Proxy variables (`https_proxy`, `http_proxy`, `no_proxy`, `ssl_cert_file`, `node_extra_ca_certs`) can be set as Agents variables or on the runner image.

Copilot **code review** is a different runner story: ARC only, Ubuntu x64, and `api.githubcopilot.com` rather than the plan-specific hosts. Do not reuse a cloud-agent scale set for it without checking that host list ([code review runners](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-runners)).

## What a Copilot pull request does to the fleet

By default, workflows do not run when Copilot pushes. A person with write access clicks Approve and run workflows. Turning that off is a repository setting, and GitHub's warning is that unreviewed agent code can then reach Actions secrets ([risks and mitigations](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/risks-and-mitigations)).

Leave the approval on. A burst of Copilot pull requests then does not multiply Commerce CI until someone has looked at them.

Other controls on the same page: only users with write access can start the agent; it pushes to one branch; it cannot merge or mark a pull request ready; the person who asked for the pull request cannot be the approving review; an extra review is required when the pull request is the agent's own identity. Hidden characters and HTML comments in issues are stripped before they reach the model. That filter is not a reason to disable the host firewall.

## Premium requests

The [legacy request-based billing page](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/github-copilot-premium-requests) says each cloud agent session is one premium request plus Actions compute, and that the page applies only to Copilot Pro and Pro+ subscribers who stayed on legacy billing after 2026-06-01. Do not quote "one premium request" as the rule for every plan. `[verify-at-use]`
