---
scenario_id: 2026-06-05-nat-gateway-cost-spike
contributed_at: 2026-06-05
plugin: aws-cloud
product: finops
product_version: "n/a"
scope: likely-general
tags: [finops, nat-gateway, vpc-endpoints, data-transfer, cost-spike]
confidence: high
reviewed: false
---

## Problem

A monthly AWS bill jumped sharply with no corresponding launch or traffic increase, and Cost Explorer attributed most of the delta to "EC2 - Other." The team assumed they'd been over-provisioned on instances and started planning a rightsizing exercise. The actual driver was **NAT Gateway data-processing charges**: a batch job in private subnets had started pulling large objects from S3 and DynamoDB *through the NAT Gateway to the public AWS endpoints*, and every gigabyte was billed twice — NAT data processing plus cross-AZ/egress transfer.

## Context

- Estate: one prod VPC, three AZs, a single NAT Gateway per AZ, all private-subnet egress routed through them. No VPC endpoints (gateway or interface) configured.
- Constraint: the workload genuinely needs S3/DynamoDB access from private subnets — the answer is *not* "make it public," it's "stop routing AWS-service traffic through the NAT." The team had conflated "instance cost" (the rightsizing story) with "data-transfer cost" (the real one) — the classic single-cause misread the cost trees warn against.
- "EC2 - Other" in Cost Explorer is a grab-bag line item — NAT Gateway data processing and inter-AZ transfer both land there, which is why the spike looked like compute.

## Attempts

- Tried: rightsizing the batch instances down. Outcome: trivial savings — the instances weren't the cost. Treating the wrong line item.
- Tried (the diagnosis that worked): decomposed the "EC2 - Other" line in Cost Explorer by **usage type** (filtered to `*NatGateway-Bytes*` and `*DataTransfer*`) instead of by service. Outcome: the spike was ~90% NAT Gateway data processing on traffic to S3 and DynamoDB — AWS-service traffic that never needed to leave the AWS network at all.
- Tried (the fix): added a **gateway VPC endpoint** for S3 and for DynamoDB (gateway endpoints are free and route that traffic off the NAT entirely), and an **interface endpoint** for the one other AWS API the job called frequently. Re-pointed the route tables. Outcome: NAT data-processing volume dropped to near zero for AWS-service traffic; the bill returned to baseline. Added a **budget + anomaly-detection alarm** on the data-transfer usage type so the next spike pages instead of surprising the next bill.

## Resolution

The spike was **NAT Gateway data-processing on AWS-service traffic**, not compute. The fix was **VPC endpoints over NAT egress** (CLAUDE.md house opinion — private by default, but route AWS-service traffic through endpoints, not the NAT): free gateway endpoints for S3/DynamoDB, an interface endpoint for the high-volume API, and a cost anomaly alarm on the data-transfer usage type so the pattern is caught at the metric, not the invoice.

**Action for the next engineer hitting this pattern:** when a bill spikes in "EC2 - Other," **decompose by usage type before rightsizing** — split NAT data processing, inter-AZ transfer, and egress before accepting an "instances are too big" story. If private workloads talk to S3/DynamoDB through a NAT, add **gateway VPC endpoints first** (they're free) and interface endpoints for high-volume APIs. Set a **cost anomaly alarm** on the data-transfer usage type. Tag and watch the bill from day one (CLAUDE.md §2). Dollar figures are account-specific and the per-GB rates change by region — treat any specific number as `[ESTIMATE]` and validate against the account's actual Cost and Usage Report.

**Sources (retrieved 2026-06-05):**
- AWS — VPC endpoints (gateway endpoints for S3/DynamoDB are free): https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html
- AWS — NAT Gateway pricing (data-processing charge per GB): https://aws.amazon.com/vpc/pricing/
- AWS Cost Explorer — analyzing costs by usage type: https://docs.aws.amazon.com/cost-management/latest/userguide/ce-exploring-data.html

Pricing pages are volatile — `[verify-at-use]` the current per-GB NAT data-processing and data-transfer rates for the relevant region before quoting savings.
