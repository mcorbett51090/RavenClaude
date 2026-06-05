---
name: vpc-network-design
description: "Step-by-step playbook for designing an AWS VPC — CIDR allocation, subnet layout, routing, security groups vs NACLs, egress control, and PrivateLink/VPC endpoint placement. Covers single-VPC through multi-account Transit Gateway topologies."
---

# AWS VPC Network Design

## 1. CIDR Allocation

Pick a non-overlapping RFC 1918 range before you create anything — overlapping CIDRs block VPC peering and Transit Gateway routes permanently.

| Scope | Recommended range | Why |
|---|---|---|
| VPC | /16 per environment | 65 k addresses; room to add AZs |
| Public subnet | /24 per AZ | ~250 public IPs; load balancers, NAT GWs |
| Private (app) subnet | /22 per AZ | ~1 000 IPs; ECS tasks, EC2, Lambda ENIs |
| Private (data) subnet | /24 per AZ | ~250 IPs; RDS, ElastiCache |

Reserve at least one /24 per AZ for future use — subnets cannot be resized.

## 2. Subnet Tiers and Routing

```
Internet Gateway
    └── Public subnet (route: 0.0.0.0/0 → IGW)
            └── NAT Gateway (one per AZ for HA)
App (private) subnet (route: 0.0.0.0/0 → NAT GW in same AZ)
Data (private) subnet  (no default route — data layer stays dark)
```

**Rules:**
1. Only load balancers, bastion hosts, and NAT GWs belong in public subnets.
2. Cross-AZ NAT GW traffic incurs data-transfer cost — always route to the NAT GW in the same AZ.
3. Data subnets have no internet route; app code reaches them through the private tier only.

## 3. Security Groups vs NACLs

| Control | When to use | Key behaviour |
|---|---|---|
| Security group | Default — almost always | Stateful; only `allow` rules; attach to ENI |
| NACL | Subnet-wide deny (e.g., block a known bad CIDR) | Stateless; explicit allow + deny; evaluated in rule-number order |

**Avoid redundant NACL rules.** NACLs are stateless — a `DENY` is not matched by the return traffic; denying an ephemeral-port range silently breaks connections.

## 4. Egress Control Decision

| Traffic type | Control | Rationale |
|---|---|---|
| Internet-bound (app → external API) | NAT Gateway + security group | No per-byte NAT cost for AWS-to-AWS; use VPC endpoints instead |
| AWS service APIs (S3, DynamoDB, SQS, STS…) | VPC Gateway or Interface endpoint | Keeps traffic on the AWS backbone; removes NAT GW dependency and cost |
| Cross-account internal traffic | Transit Gateway or VPC Peering | TGW for hub-and-spoke; peering for point-to-point (no transitive routing in peering) |
| On-premises | Direct Connect + VGW or TGW attachment | Site-to-Site VPN for non-critical; DX for production |

## 5. VPC Endpoint Checklist

At minimum, create endpoints for:
- `com.amazonaws.<region>.s3` (Gateway — free)
- `com.amazonaws.<region>.dynamodb` (Gateway — free)
- `com.amazonaws.<region>.ecr.api` + `ecr.dkr` (Interface — costs apply, saves NAT GW per-byte)
- `com.amazonaws.<region>.sqs`, `ssm`, `secretsmanager` (Interface — eliminates NAT GW for these APIs)

## 6. Multi-Account Transit Gateway

```
Central networking account owns the TGW.
Each spoke account creates a TGW attachment (VPC attachment).
Route tables:
  - Shared-services attachment: can reach all spokes
  - Prod spokes:  can reach shared-services + inspection; not each other
  - Non-prod spokes: same isolation from prod
  - Inspection attachment: default route 0.0.0.0/0 for egress firewall (optional)
```

Enable **resource sharing via RAM** so spoke accounts can attach without cross-account peering invitations.

## Pitfalls

- Allocating /24 VPCs — you'll run out of IPs when ECS and Lambda ENIs proliferate.
- A single NAT GW across AZs — AZ failure kills all outbound traffic.
- Forgetting the ephemeral port range (1024–65535) in NACL return rules.
- Overlapping CIDRs discovered after peering — no fix except re-IP or abandon.
- Security groups that reference `0.0.0.0/0` on port 22/3389 — always a finding; use SSM Session Manager instead.
- Skipping VPC endpoints for S3/DynamoDB — 100% of that traffic transits the NAT GW and incurs per-byte charges.
