# Shared VPC design

| Element | Choice |
|---|---|
| Host project | network-host (owns the VPC + subnets) |
| Service projects | app-prod, data-prod (attach) |
| Firewall | default-deny + allow by tag/SA |
| Private access | Private Google Access + Private Service Connect |
| Egress | Cloud NAT |

CIDRs planned to avoid overlap. Exposure verdicts -> security-engineering.
