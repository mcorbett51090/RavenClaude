---
description: "Design or repair a CI pipeline: order gates cheapest-first, cache on the lockfile, shard slow suites, and define the required-check contract for branch protection."
argument-hint: "[repo description, e.g. 'Node monorepo, 25-min PR build, flaky e2e']"
---

You are running `/devops-cicd:design-ci-pipeline`. Use the `pipeline-engineer` discipline and the `ci-pipeline-design` skill.

## Steps
1. Inventory the current stages and their runtimes; find the ordering and caching faults.
2. Re-order cheapest-first; add lockfile-keyed dependency caching and build caching.
3. Matrix/shard the slow suites; define one aggregating required check.
4. Pin third-party actions to SHAs; move secrets to OIDC.
5. Quarantine any flaky required check with an owner + tracking.
6. Emit the pipeline-as-code (from `templates/ci-pipeline-skeleton.yaml`) + the branch-protection required-check list, then the Structured Output block.
