# Showback / Chargeback Model — `<org / team name>`

> Showback = read-only cost visibility per team. Chargeback = showback + GL financial transfer.
> Start with showback. Earn chargeback after 2-3 months of behavior change.

- **Model type:** `<showback | chargeback>`
- **Owner:** `<FinOps team / Finance>`
- **Billing period:** `<monthly | weekly>`
- **Version:** `<semver, e.g. 1.0.0>`
- **Effective date:** `<YYYY-MM-DD>`
- **Last reviewed:** `<date>`

---

## Scope

| Cloud(s) | Included services | Excluded services |
|---|---|---|
| `<AWS / Azure / GCP>` | `<EC2, RDS, S3, ...>` | `<Support, Marketplace, ...>` |

---

## Allocation dimensions

The primary tag dimensions used to attribute cost to a team. These must match the mandatory tags
in `templates/tagging-policy.md`.

| Dimension | Tag key | Notes |
|---|---|---|
| Team | `team` | Primary allocation dimension |
| Application | `application` | Secondary — enables per-app view within a team |
| Environment | `environment` | Enables prod vs non-prod split |
| Project / cost-centre | `project` | Maps to the GL cost-centre code |

---

## Shared cost allocation

Shared resources (Kubernetes clusters, networking, shared tooling) that cannot be tagged to a
single team are allocated using the method below.

| Shared resource | Allocation method | Denominator | Version | Effective date |
|---|---|---|---|---|
| `<Kubernetes cluster>` | Proportional by CPU+memory request-seconds per namespace | Monthly namespace consumption from Kubecost/OpenCost | v1.0 | `<date>` |
| `<NAT Gateway / Shared VPC>` | Proportional by egress bytes per team | VPC Flow Logs egress bytes per team CIDR | v1.0 | `<date>` |
| `<Security tooling>` | Even split | Number of active teams in billing period | v1.0 | `<date>` |
| `<Support contract>` | Even split | Number of active teams | v1.0 | `<date>` |

> **Version discipline:** when the allocation method or denominator changes, increment the version
> and record the effective date. Historical periods must be re-stated using the method in effect
> at the time, or the change must be documented as a restatement.

---

## Untagged cost handling

| Rule | Details |
|---|---|
| Untagged spend destination | `<"shared/unattributed" cost centre OR proportional split>` |
| Untagged spend target | `<5% of total monthly cloud spend within 90 days>` |
| Alert threshold | Team receives alert if >5% of their compute cost is untagged |
| Escalation | Engineering lead + FinOps team notified weekly until resolved |

---

## Delivery mechanism

| Channel | Audience | Cadence | Content |
|---|---|---|---|
| `<Dashboard (Grafana / Cost Explorer / Power BI)>` | Engineering leads | Live / weekly | Team spend, trend, budget vs actual |
| `<Slack digest (#finops-weekly)>` | All engineers | Weekly | Team's week-over-week delta, top cost drivers |
| `<Email report>` | Finance / VP Engineering | Monthly | Full allocation report, unit economics |

---

## Unit economics (if applicable)

| Metric | Numerator | Denominator | Definition agreed by | Target range |
|---|---|---|---|---|
| Cost per active customer | Attributed cloud cost (tagged + allocated shared) | Monthly active customers (MAU, agreed definition: `<…>`) | Finance, Engineering, Product | `$<low>` – `$<high>` |
| Cost per API request | Attributed compute + egress | Total API requests | Engineering | `$<low>` – `$<high>` |
| AI cost per feature user | Attributed LLM inference cost | Feature MAU | Engineering, Product | `$<low>` – `$<high>` |

> **Denominator agreement is required before publishing.** A unit-economics metric without a
> documented and agreed denominator definition will be contested.

---

## Chargeback (if applicable)

*Skip this section if model type is showback only.*

| Item | Details |
|---|---|
| GL cost-centre mapping | `<BU → GL code mapping table, or link to Finance GL chart of accounts>` |
| Allocation key for shared services | `<see shared cost section above>` |
| Reconciliation process | Finance reconciles monthly; discrepancies >$500 escalated to FinOps |
| Journal entry owner | `<controller / finance partner>` |
| Handoff to Finance plugin | `finance/cost-centre-chargeback` — provide the monthly attribution CSV |
| Effective date | `<YYYY-MM-DD>` |

---

## Governance

- **Policy owner:** `<FinOps team>`
- **Review cadence:** quarterly review of allocation methods, annually re-confirm denominator
  definitions with Finance/Engineering/Product.
- **Method change process:** 30 days' notice to affected teams before changing an allocation method.
  New method takes effect the first day of the following billing period.

---

## See also

- `templates/tagging-policy.md`
- `skills/cost-allocation-and-tagging/SKILL.md`
- `knowledge/finops-cloud-cost-decision-trees.md` — the allocation model tree
- `finance` plugin — for GL chargeback booking
