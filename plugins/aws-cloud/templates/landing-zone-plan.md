# AWS landing zone plan

| Account | Purpose | Key guardrails (SCP) |
|---|---|---|
| management | Org root, billing | restrict member-account root |
| security | GuardDuty, log archive | deny log deletion |
| shared-services | network, CI | — |
| prod | production workloads | deny non-approved regions |
| non-prod | dev/test | budget caps |

**Region(s):** <primary> (+ <DR> if multi-region)  **AZs:** >=2
**RTO/RPO:** <stated>  **Build:** terraform-iac
