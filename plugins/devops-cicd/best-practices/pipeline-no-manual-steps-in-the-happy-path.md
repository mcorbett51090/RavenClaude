# The happy path has no manual steps — automate or document the escape hatch

**Status:** Pattern
**Domain:** CI/CD pipeline design
**Applies to:** `devops-cicd`

---

## Why this exists

A pipeline with a manual "click here to promote" step in the normal path is a pipeline that only works when a specific person is awake, available, and remembers the context. Manual steps are the leading cause of deployment bottlenecks, on-call fatigue, and "the engineer who does releases" becoming a single point of failure. The happy path — the routine deployment of a tested artifact — should require zero human intervention. Manual approvals belong only at meaningful governance gates (promote to prod, release to customers), not scattered through the pipeline.

## How to apply

Audit every manual step in the current pipeline and classify it as: (a) a genuine governance gate that should remain manual with a named approver, (b) a safety check that should be automated as a health gate, or (c) a toil step that should be scripted and removed.

```yaml
# GitHub Actions: automated promotion to staging, human gate before prod
jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy.sh dev ${{ github.sha }}

  deploy-staging:
    needs: deploy-dev
    # Automated — health check passes, auto-promote
    steps:
      - run: ./scripts/wait-for-health.sh dev
      - run: ./scripts/deploy.sh staging ${{ github.sha }}

  prod-approval:
    needs: deploy-staging
    environment: production    # GitHub environment with required reviewers
    steps:
      - run: echo "Approval gate"  # waits for named reviewer to approve

  deploy-prod:
    needs: prod-approval
    steps:
      - run: ./scripts/deploy.sh prod ${{ github.sha }}
```

**Do:**
- Automate health checks (SLO burn-rate, smoke tests) as the promotion gate between environments — this is `observability-sre`'s signal.
- Use a formal approval gate (GitHub environment, Argo CD sync window, PagerDuty change request) for the prod gate — not a Slack message.
- Document the emergency manual path for break-glass — but put it in a runbook, not in the happy path.

**Don't:**
- Add a manual step "because it feels safer" without specifying what the human is actually checking.
- Make the prod gate a Slack message in a shared channel — it's invisible, untracked, and often skipped.
- Require a deploy to be initiated by a single person's SSH session or local machine.

## Edge cases / when the rule does NOT apply

Regulated industries (financial services, FDA-regulated medical devices) may require a human change-approval record that cannot be automated away. In those cases, implement the gate as a formal workflow system (ServiceNow, Jira Service Management) with an audit trail, not an ad-hoc manual step.

## See also

- [`../agents/pipeline-engineer.md`](../agents/pipeline-engineer.md) — owns pipeline stage design and automation decisions.
- [`./deploy-rollback-before-you-ship.md`](./deploy-rollback-before-you-ship.md) — automated rollback is the safe replacement for a manual "watch it and revert" step.

## Provenance

Codifies the DORA continuous delivery principle (Humble & Farley, "Continuous Delivery") that the delivery pipeline's happy path must be fully automated. The manual gate vs. toil classification comes from Google SRE's toil reduction framework.

---

_Last reviewed: 2026-06-05 by `claude`_
