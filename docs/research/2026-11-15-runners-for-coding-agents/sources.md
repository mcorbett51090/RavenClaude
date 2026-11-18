# Sources

Retrieved 2026-11-16 unless the row says otherwise. Secondary write-ups are marked. They were used to find the primary page, and the claim in the topic files cites the primary page.

## Copilot

| Source | Used for |
|---|---|
| https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment | Setup file keys, 59-minute setup timeout, Ubuntu x64 / Windows 64-bit, self-hosted firewall-off requirement, host list, larger-runner example |
| https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github | Cloud vs Actions comparison, 59-minute session cap, one repo / one branch / one PR |
| https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/ | Sandbox is the default, no one-hour sandbox cap, billing begins November 2026 with no day, shared compute entitlement, `--environment-host` |
| https://docs.github.com/en/billing/concepts/product-billing/cloud-and-local-sandboxes | Sandbox rates. No machine size |
| https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall | Firewall limits, org and repo toggles |
| https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/risks-and-mitigations | Approve-workflows default, write-access trigger, hidden-character filter, extra review |
| https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/configure-runner-for-coding-agent | Org runner lock. Does not apply to a user account |
| https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-runners | Code review runners: ARC only, Ubuntu x64, different API host |
| https://github.blog/changelog/2026-02-13-network-configuration-changes-for-copilot-coding-agent/ | Plan-specific API hosts from 2026-02-27 |
| https://github.blog/changelog/2025-10-28-copilot-coding-agent-now-supports-self-hosted-runners/ | Earlier ARC announcement. Superseded in detail by the environment doc above |
| https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/github-copilot-premium-requests | Legacy "one premium request per session." Plan-limited |

## Claude Code action

| Source | Used for |
|---|---|
| https://code.claude.com/docs/en/github-actions | Permissions, cost, `--max-turns`, concurrency advice, default-token pushes do not start workflows |
| https://github.com/anthropics/claude-code-action/blob/main/docs/security.md | `pull_request_target`, `restrict_untrusted_prs`, `allowed_bots`, cancelled-run git config on a persistent runner |

## Cursor and Codex

| Source | Used for |
|---|---|
| https://cursor.com/docs/cloud-agent | Cloud agents run in Cursor VMs |
| https://cursor.com/docs/cloud-agent/automations | CI completed vs workflow-run-completed |
| https://cursor.com/docs/cloud-agent/self-hosted | Outbound worker, not an Actions runner |
| https://cursor.com/docs/cloud-agent/self-hosted-pool | Pool labels, one session per worker |
| https://cursor.com/docs/cli/github-actions | CLI inside a workflow, API key |
| https://learn.chatgpt.com/docs/environments/cloud-environment | Codex cloud: internet off by default in the agent phase, secrets removed before that phase, 12-hour cache. Page is marked legacy |
| https://learn.chatgpt.com/docs/github-action | `openai/codex-action` safety strategies and the two-job split |

## Actions platform

| Source | Used for |
|---|---|
| https://docs.github.com/en/actions/reference/limits | 6-hour hosted job, 5-day self-hosted job, 24-hour queue, 35-day workflow, concurrency queue of 100, event rates, matrix 256, re-runs 50 |
| https://docs.github.com/en/actions/concepts/security/github_token | Token lifetime 6 hours hosted, 24 hours self-hosted |
| https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency | `cancel-in-progress`, `queue: max` cannot be combined |
| https://docs.github.com/en/actions/reference/security/secure-use | Self-hosted runners and public repositories |
| https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target | Secrets, read-only cache, ephemeral compute |
| https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue | `merge_group`, build concurrency 1–100 |
| https://docs.github.com/en/billing/concepts/product-billing/github-actions | `$0.006`/min Linux 2-core, shared entitlement |
| https://docs.github.com/en/billing/reference/actions-runner-pricing | Larger-runner per-minute rates |
| https://docs.github.com/en/actions/concepts/runners/larger-runners | Larger runners are org/enterprise, Team or Enterprise Cloud |
| https://docs.github.com/en/actions/how-tos/manage-runners/larger-runners/use-custom-images | What `snapshot` actually does |
| https://github.com/actions/actions-runner-controller/releases/tag/gha-runner-scale-set-0.15.1 | ARC 0.15.1, 2026-10-23. Same version the 2026-11-15 research recorded |
| https://github.com/actions/scaleset/releases/tag/v0.5.0 | `actions/scaleset` v0.5.0, 2026-10-23, still public preview. A pseudo-version dated 2026-11-07 exists on a module index and is not a release tag |

## This factory, this session

| Source | Used for |
|---|---|
| GitHub API `GET /repos/mcorbett51090/RavenClaude` and `GET /repos/mcorbett51090/RavenPower-Website` | Public vs private, owner type User |
| Website `.github/workflows/claude.yml` on the default branch | 90-minute timeout, fallback `runs-on`, amd64 `gh` install, job-level concurrency |
| Code search `concurrency` in `commerce-ci.yml` | No matches on the default branch |
| Code search `copilot-setup-steps` and `codex-action` | No matches in the Website repo |

## Secondary, not cited for a number

| Source | Why it is listed |
|---|---|
| https://dev.to/kalemi/copilot-setup-stepsyml-the-rules-runners-and-limits-gfd | 2026-11-15 walkthrough. Confirmed against the environment doc; no number was taken from it |
| https://www.datastudios.org/post/github-copilot-cloud-sandboxes-generally-available-billing-november-shared-compute-pool | Agrees the November billing start has no day and the sandbox size is unpublished. Arithmetic in that post was not used |
| https://runs-on.com/github-actions/concurrency/ | Notes `queue` landed May 2026 and is absent on GitHub Enterprise Server. The key behavior was checked on the official concurrency page |

## Not re-checked this session

The postponed `$0.002`/min self-hosted platform fee, ARC's multi-label behavior, and the 14-day offline deletion. Those were checked 2026-11-15 and are linked from the earlier research. `actions/scaleset` v0.5.0 and ARC 0.15.1 were re-confirmed above because the dates sit on the release pages.
