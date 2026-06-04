# VPC design

| Subnet tier | Purpose | Public? |
|---|---|---|
| public | load balancers, NAT | yes |
| private-app | compute | no (NAT egress) |
| private-data | RDS/cache | no |

- Security groups: **referential** (SG-to-SG), no wide CIDRs to admin/db ports
- VPC endpoints: S3, ECR, SSM (private service access)
- CIDR planned to avoid overlap; Transit Gateway for inter-VPC
