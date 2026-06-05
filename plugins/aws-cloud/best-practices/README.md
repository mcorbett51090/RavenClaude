# aws-cloud — best-practice docs

Named, citable rules for the `aws-cloud` plugin's specialists. Each file is **one rule**, grounded in this plugin's house opinions ([`../CLAUDE.md`](../CLAUDE.md)) and the decision trees in [`../knowledge/aws-cloud-decision-trees.md`](../knowledge/aws-cloud-decision-trees.md). Read a doc whole and cite it; don't paraphrase a fragment.

---

## Index

_26 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`aurora-serverless-for-spiky-relational.md`](./aurora-serverless-for-spiky-relational.md) | Pattern | Choosing a relational engine for a workload with intermittent or burst traffic |
| [`budget-alarms-before-the-bill.md`](./budget-alarms-before-the-bill.md) | Absolute rule | Setting up a new AWS account or subscription — always set cost alerts from day one |
| [`cloudtrail-on-in-every-account.md`](./cloudtrail-on-in-every-account.md) | Absolute rule | Enabling audit logging in a new or existing AWS account |
| [`cloudwatch-alarms-not-just-dashboards.md`](./cloudwatch-alarms-not-just-dashboards.md) | Absolute rule | Wiring up observability — a dashboard without alarms is not observability |
| [`control-tower-for-new-landing-zones.md`](./control-tower-for-new-landing-zones.md) | Pattern | Standing up a new multi-account AWS estate |
| [`ecs-task-definition-secrets-from-secrets-manager.md`](./ecs-task-definition-secrets-from-secrets-manager.md) | Absolute rule | Configuring ECS task definitions that need database passwords or API keys |
| [`encrypt-at-rest-and-in-transit.md`](./encrypt-at-rest-and-in-transit.md) | Absolute rule | Any resource that stores or transmits data |
| [`eventbridge-over-direct-coupling.md`](./eventbridge-over-direct-coupling.md) | Pattern | Designing event-driven integration between AWS services or microservices |
| [`guardduty-on-in-every-account.md`](./guardduty-on-in-every-account.md) | Absolute rule | Enabling baseline threat detection in any AWS account |
| [`idempotency-and-dlqs-for-async.md`](./idempotency-and-dlqs-for-async.md) | Pattern | Designing SQS/SNS/EventBridge consumers and Lambda event handlers |
| [`irsa-not-node-roles.md`](./irsa-not-node-roles.md) | Absolute rule | Granting AWS API access to workloads running on EKS |
| [`lambda-power-tools-structured-logging.md`](./lambda-power-tools-structured-logging.md) | Pattern | Writing Lambda functions that need debuggable, searchable logs |
| [`least-privilege-with-boundaries.md`](./least-privilege-with-boundaries.md) | Absolute rule | Writing any IAM policy or reviewing an existing one |
| [`multi-account-by-blast-radius.md`](./multi-account-by-blast-radius.md) | Pattern | Deciding how many AWS accounts an estate needs |
| [`multi-az-by-default.md`](./multi-az-by-default.md) | Pattern | Provisioning any prod workload or managed service |
| [`private-by-default.md`](./private-by-default.md) | Absolute rule | Provisioning any AWS resource — public exposure requires an explicit justification |
| [`roles-not-keys.md`](./roles-not-keys.md) | Absolute rule | Any workload, CI system, or human needing AWS API credentials |
| [`s3-block-public-access-at-account-level.md`](./s3-block-public-access-at-account-level.md) | Absolute rule | Creating a new AWS account or S3 bucket |
| [`savings-plans-after-rightsizing.md`](./savings-plans-after-rightsizing.md) | Pattern | Optimizing AWS spend — rightsize first, then commit |
| [`scp-guardrails-set-the-ceiling.md`](./scp-guardrails-set-the-ceiling.md) | Absolute rule | Configuring AWS Organizations to enforce guardrails across accounts |
| [`security-groups-least-privilege-ingress.md`](./security-groups-least-privilege-ingress.md) | Absolute rule | Writing or reviewing security group rules — especially ingress |
| [`step-functions-for-multi-step-orchestration.md`](./step-functions-for-multi-step-orchestration.md) | Pattern | Designing workflows with multiple sequential steps, retries, or human gates |
| [`tag-and-watch-cost-from-day-one.md`](./tag-and-watch-cost-from-day-one.md) | Pattern | Launching a new workload or onboarding a new team to AWS |
| [`test-the-restore-not-just-the-backup.md`](./test-the-restore-not-just-the-backup.md) | Absolute rule | Setting up backup for any stateful AWS resource |
| [`vpc-endpoints-over-nat-egress.md`](./vpc-endpoints-over-nat-egress.md) | Pattern | Connecting resources in private subnets to AWS services |
| [`waf-on-every-public-alb-and-cloudfront.md`](./waf-on-every-public-alb-and-cloudfront.md) | Pattern | Exposing any HTTP/HTTPS workload to the public internet |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution + the house opinions these docs codify.
- [`../knowledge/aws-cloud-decision-trees.md`](../knowledge/aws-cloud-decision-trees.md) — decision trees for compute, account layout, database, networking, and IAM.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
