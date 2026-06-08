# Cloud Tagging Policy — `<org / team name>`

> Tag at birth or you cannot allocate. This policy is enforced via IaC and cloud-native tag
> enforcement mechanisms — not a quarterly cleanup spreadsheet.

- **Version:** `<semver, e.g. 1.0.0>`
- **Owner:** `<FinOps team / platform team>`
- **Last reviewed:** `<date>`
- **Clouds in scope:** `<AWS | Azure | GCP | multi-cloud>`
- **Enforcement status:** `<enforced | advisory | in-rollout>`

---

## Mandatory tags

Every resource **must** have these tags on creation. Resources missing a mandatory tag will be
flagged (advisory) or denied at creation (enforced).

| Tag key | Allowed values / format | Description | Example |
|---|---|---|---|
| `environment` | `prod` \| `staging` \| `dev` \| `sandbox` | The lifecycle stage | `prod` |
| `team` | `<slug from team registry>` | The owning engineering team | `platform-eng` |
| `project` | `<project-id or GL cost-centre code>` | The GL cost centre or project | `proj-payments` |
| `application` | `<service slug>` | The application or microservice | `order-api` |
| `managed-by` | `terraform` \| `pulumi` \| `cdk` \| `console` \| `cli` | How the resource was provisioned | `terraform` |

> **Allowed-values enforcement:** define these values in AWS Tag Policies, Azure Policy allowed-
> values parameters, or a GCP org policy label constraint. Free-form tags are unqueryable.

---

## Recommended tags

Not mandatory, but strongly encouraged for improved cost attribution and operations.

| Tag key | Allowed values / format | Description |
|---|---|---|
| `data-classification` | `public` \| `internal` \| `confidential` \| `restricted` | Data sensitivity |
| `backup-policy` | `daily-7d` \| `daily-30d` \| `weekly-90d` \| `none` | Backup retention |
| `cost-centre` | `<GL code>` | Override for cross-team billing |
| `expiry-date` | `YYYY-MM-DD` | For sandbox/temporary resources |

---

## Enforcement mechanisms

### AWS

```hcl
# SCP: deny resource creation if required tags are missing (customize per service)
# aws_organizations_policy — apply to the target OU
# Example: deny EC2 RunInstances without required tags
```

- **AWS Tag Policies** — enforce allowed values per tag key at the OU level.
- **SCP deny** — deny `ec2:RunInstances`, `s3:CreateBucket`, `rds:CreateDBInstance` when required
  tags are missing. [verify-at-use: SCP syntax and supported resources evolve]

### Azure

```hcl
# Azure Policy: deny resource creation missing required tags
# policy_definition_id: "audit or deny on missing tag"
```

- **Azure Policy** with `deny` effect — applied at the subscription or management-group level.
  [verify-at-use: built-in policy IDs and parameter names change]

### GCP

```hcl
# GCP org policy: require labels on resource creation
# constraints/gcp.resourceLocations / constraints/compute.requireLabels (custom)
```

- **Resource Manager label constraints** via organization policy.
  [verify-at-use: GCP org policy constraint names evolve]

---

## Untagged cost fallback

Resources provisioned before this policy was enforced, or resources that bypass enforcement
(some managed services do not support all tags), produce untagged spend. Fallback rule:

- **Primary:** allocate proportionally — untagged spend is split among teams in the same ratio as
  their tagged spend in the same billing period.
- **Escalation:** any team with >5% of their compute cost untagged receives a weekly alert until
  resolved. Target: untagged cost <5% of total within 90 days of policy rollout.

---

## Shared resource allocation

| Shared resource | Allocation method | Denominator | Review cadence |
|---|---|---|---|
| `<Kubernetes cluster name>` | Proportional by CPU/memory request-seconds | Namespace CPU+mem consumption | Quarterly |
| `<NAT Gateway / shared networking>` | Proportional by egress bytes | Per-team egress from flow logs | Monthly |
| `<Security tooling>` | Even split | Number of active teams | Quarterly |

> Document the denominator version — if the method changes, note the version and date so historical
> trends remain comparable.

---

## Governance & exceptions

- **Policy owner:** `<FinOps team>`
- **Exception process:** tag-exception requests go to `<FinOps Slack channel>`. Exceptions are
  time-limited (max 30 days) and require a JIRA ticket to resolve.
- **Audit:** monthly audit of untagged spend. Results shared with engineering leads in the FinOps
  weekly digest.

---

## See also

- `skills/cost-allocation-and-tagging/SKILL.md`
- `templates/showback-chargeback-model.md`
- `knowledge/finops-cloud-cost-decision-trees.md` — the allocation model tree
