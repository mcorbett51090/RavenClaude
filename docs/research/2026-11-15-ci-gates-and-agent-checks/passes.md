# Research pass log (2026-11-16, UTC)

The folder date matches the 2026-11-15 research batch. The fetches in this log were made 2026-11-16.

## Pass 1 — gates (01:30 UTC)

- Troubleshooting required status checks: `success`, `skipped`, and `neutral` satisfy a required check. A workflow skipped by path, branch, or commit message stays Pending. A job skipped by `if:` reports Success. Events that count on a pull request. `merge_group` is separate. A check and a commit status of the same name must both pass. https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- Status checks reference: skipped job reports Success and does not block the merge. Conclusion table. https://docs.github.com/en/pull-requests/reference/status-checks
- Available rules for rulesets: any writer with write access can set a status; select an app as the expected source; the app needs `statuses: write`, a recent check run, and a pre-existing required check. Strict versus loose. Signed commits, including the unsigned-head squash block. Code-owner review. Copilot extra approval has no effect at zero required approvals. Merge queue settings (build concurrency, group size, status check timeout, all-entries versus head). https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- Managing a merge queue: `merge_group` or the queue never sees the check. https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- CODEOWNERS: first file in `.github/`, root, or `docs/`; last matching pattern wins; owners need write. https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- Environments and deployment protection, including the private-repo plan split for required reviewers. https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments and https://docs.github.com/en/rest/deployments/environments
- This session: `GET /apps/github-actions` returned id 15368, slug `github-actions`.

Pass 1 verdict: large.

## Pass 2 — efficient CI, writers, attestations (01:40 UTC)

- Dependency caching reference: `hashFiles`, restore keys, hit versus miss. https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching
- Concurrency: `cancel-in-progress`, and `queue: single` versus `queue: max`. The max-plus-cancel pair is a validation error. https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- Checks guide: creating check runs is Apps-only. https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks
- Commit statuses: fine-grained tokens with Commit statuses: write, 1000 per SHA and context. https://docs.github.com/en/rest/commits/statuses
- Secure use: default token contents: read; workflow lockfile supersedes in-file SHA pins. https://docs.github.com/en/actions/reference/security/secure-use
- Lockfile how-to and changelog 2026-10-14 (public preview; Enterprise Cloud, Team, and Free named). https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies and https://github.blog/changelog/2026-10-14-github-actions-workflow-lockfiles-in-public-preview/
- Artifact attestations: private repositories need Enterprise Cloud. https://github.com/actions/attest-build-provenance
- `zizmor` `unpinned-uses`. https://github.com/zizmorcore/zizmor/blob/main/docs/audits.md
- Re-run failed jobs, same SHA, 30 days. https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs

Pass 2 verdict: large. The lockfile preview was new relative to the SHA-pin advice already in this repo.

## Pass 3 — agents and injection (01:48 UTC)

- Copilot firewall limits (shell tool, not MCP or setup steps, appliance only, bypass called out by GitHub) and the self-hosted requirement to disable it. https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-firewall and https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/customize-the-agent-environment
- Claude Code GitHub Action cloud providers: OIDC, the job is still an Actions job. https://code.claude.com/docs/en/github-actions-cloud-providers
- Cursor cloud agents: VM, secrets, outbound policy, API start. https://cursor.com/docs/cloud-agent
- OWASP Secure Coding with AI cheat sheet: repository files as indirect prompt injection, CI agent token scope. https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html
- GitInject, config-file injection via instruction files on the pull request branch. https://arxiv.org/html/2606.09935

Pass 3 verdict: large.

## Pass 4 — ruleset schema (01:55 UTC)

- REST rules schema: `do_not_enforce_on_create`, `integration_id`, merge-queue `check_response_timeout_minutes` 1–360, `grouping_strategy` `ALLGREEN` / `HEADGREEN`, bypass actor types. https://docs.github.com/en/rest/orgs/rules
- Troubleshooting rules: check names are not indexed above the repository; evaluate mode does not block. https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/troubleshooting-rules
- The status-checks overview says users with push access can create checks. The Checks guide says creation is Apps-only. Recorded as a conflict, resolved in favor of the guide in [04](04-agent-checks-that-count.md).

Pass 4 verdict: small. Schema fields and the checks-versus-statuses wording conflict.

## Pass 5 — effective CI round-up (02:00 UTC)

- GitHub Learn, effective CI: path filters on required workflows, concurrency, lockfile cache keys. Restates passes 1 and 2. https://learn.github.com/well-architected/productivity/recommendations/effective-ci
- Secondary posts (Avrea, a monorepo note) restate the aggregate job and add one footnote: BuildKit's `gha` backend keeps one scope, so the last image wins. That footnote is the only new item.

Pass 5 verdict: one footnote.

## Pass 6 — the cache footnote's primary page (02:05 UTC)

- Docker's gha backend: default scope `buildkit`, set `scope` per image, `mode` min versus max, cache writes follow Actions cache restrictions. https://docs.docker.com/build/cache/backends/gha/
- The write-restriction half was already in the 2026-06 cache row. The scope parameter is the fix for the pass 5 footnote, not a new topic.

Pass 6 verdict: **nothing materially new. Stop.**
