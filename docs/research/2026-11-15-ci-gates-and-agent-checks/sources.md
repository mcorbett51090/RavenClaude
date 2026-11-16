# Sources (checked 2026-11-16)

## GitHub docs — gates

- Troubleshooting required status checks: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- Status checks reference: https://docs.github.com/en/pull-requests/reference/status-checks
- Available rules for rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- Troubleshooting rules: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/troubleshooting-rules
- REST API endpoints for rules: https://docs.github.com/en/rest/orgs/rules
- Managing a merge queue: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- About code owners: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- Deployments and environments: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- REST deployment environments: https://docs.github.com/en/rest/deployments/environments
- Custom deployment protection rules: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/configure-custom-protection-rules

## GitHub docs — writers, tokens, supply chain

- Using the REST API to interact with checks: https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks
- Building CI checks with a GitHub App: https://docs.github.com/en/apps/creating-github-apps/writing-code-for-a-github-app/building-ci-checks-with-a-github-app
- REST commit statuses: https://docs.github.com/en/rest/commits/statuses
- Secure use reference: https://docs.github.com/en/actions/reference/security/secure-use
- Locking action dependencies: https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies
- Workflow dependency lockfiles (concept): https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles
- Lockfile public preview changelog (2026-10-14): https://github.blog/changelog/2026-10-14-github-actions-workflow-lockfiles-in-public-preview/
- Enforcing lockfiles: https://docs.github.com/en/actions/how-tos/administer/enforce-workflow-lockfiles
- Dependabot version updates: https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates

## GitHub docs — speed

- Dependency caching reference: https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching
- Dependency caching concept: https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching
- Workflow concurrency: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- Running job variations (`fail-fast`): https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations
- Re-running workflows and jobs: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
- Effective CI (GitHub Learn): https://learn.github.com/well-architected/productivity/recommendations/effective-ci
- Docker BuildKit gha cache backend: https://docs.docker.com/build/cache/backends/gha/
- Read-only cache for untrusted triggers (2026-06-26): https://github.blog/changelog/2026-06-26-read-only-actions-cache-for-untrusted-triggers/

## Attestations

- actions/attest-build-provenance (plan limits): https://github.com/actions/attest-build-provenance
- actions/attest: https://github.com/actions/attest/blob/main/README.md
- SLSA build provenance predicate: https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md
- `gh attestation verify`: https://cli.github.com/manual/gh_attestation_verify
- Reusable workflows and SLSA: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/increase-security-rating

## Agents and injection

- Copilot cloud agent firewall: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-firewall
- Copilot internet-access changelog (2025-07-15): https://github.blog/changelog/2025-07-15-configure-internet-access-for-copilot-coding-agent/
- Claude Code GitHub Actions with cloud providers: https://code.claude.com/docs/en/github-actions-cloud-providers
- Cursor cloud agents: https://cursor.com/docs/cloud-agent
- OWASP Secure Coding with AI: https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html
- GitInject (arXiv:2606.09935): https://arxiv.org/html/2606.09935
- CSA research note on README instruction injection: https://labs.cloudsecurityalliance.org/research/csa-research-note-readme-instruction-injection-ai-coding-age/

## Linters

- zizmor audits, including `unpinned-uses`: https://github.com/zizmorcore/zizmor/blob/main/docs/audits.md
- actionlint: https://github.com/rhysd/actionlint

## This session, not a web page

- `GET /apps/github-actions` → `{"id":15368,"slug":"github-actions","name":"GitHub Actions"}`.
