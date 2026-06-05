# Security groups grant minimum ingress from known sources, never 0.0.0.0/0 to admin ports

**Status:** Absolute rule
**Domain:** AWS networking / security
**Applies to:** `aws-cloud`

---

## Why this exists

`0.0.0.0/0` ingress to SSH (22), RDP (3389), or database ports (3306, 5432, 1433) is the single most common finding in AWS security assessments. These ports exposed to the internet invite brute-force and exploitation. The blast radius of an open security group is the entire resource it protects. Security groups are stateful and free; there is no cost reason to accept `0.0.0.0/0` on admin or data ports.

## How to apply

**Minimum-ingress checklist:**

| Port | Correct source | Never |
|---|---|---|
| 22 (SSH) | Named security group of a bastion or Systems Manager endpoint; or SSM Session Manager (no port 22 at all) | `0.0.0.0/0` |
| 3389 (RDP) | Same as SSH | `0.0.0.0/0` |
| 3306/5432/1433 (DB) | Security group ID of the app tier | `0.0.0.0/0` or VPC CIDR block |
| 443/80 (app) | ALB security group ID; public-facing ALBs may accept `0.0.0.0/0` on 443 | Never 80 without redirect; never 443 to internal services directly |
| Management APIs | VPC endpoint security group or PrivateLink | `0.0.0.0/0` |

```hcl
# Terraform — app SG allows only from ALB SG; no 0.0.0.0/0
resource "aws_security_group_rule" "app_from_alb" {
  type                     = "ingress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
  security_group_id        = aws_security_group.app.id
}

# DB SG allows only from app SG
resource "aws_security_group_rule" "db_from_app" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.app.id
  security_group_id        = aws_security_group.db.id
}
```

Prefer SSM Session Manager over SSH wherever possible:
```json
// SCP that prevents 0.0.0.0/0 ingress to port 22
{
  "Sid": "DenySSHOpen",
  "Effect": "Deny",
  "Action": "ec2:AuthorizeSecurityGroupIngress",
  "Resource": "*",
  "Condition": {
    "StringEquals": { "ec2:FromPort": "22" },
    "IpAddress": { "ec2:IpRange": "0.0.0.0/0" }
  }
}
```

**Do:**
- Reference security group IDs as sources, not CIDR blocks, for intra-VPC traffic.
- Use SSM Session Manager for interactive shell access — eliminates SSH/22 entirely.
- Enforce via SCP: deny `ec2:AuthorizeSecurityGroupIngress` with `0.0.0.0/0` on admin ports.
- Audit with AWS Config rule `restricted-ssh` and `restricted-common-ports`.

**Don't:**
- Add a CIDR range for "just my IP" as a persistent rule — it becomes stale and nobody removes it.
- Allow ingress from an entire VPC CIDR to a database port — scope it to the app tier's SG ID.
- Conflate NACLs and security groups — NACLs are stateless and coarse; security groups are the primary per-resource control.

## Edge cases / when the rule does NOT apply

- **Public-facing HTTP/HTTPS** on a load balancer (`0.0.0.0/0` on 443/80) — this is intended; the load balancer in a public subnet is the designed entry point. The back-end compute stays private.
- **Specific admin CIDR ranges for on-premises access** via Direct Connect — a well-managed CIDR range is acceptable; document and review quarterly.

## See also

- [`../agents/aws-network-engineer.md`](../agents/aws-network-engineer.md) — owns security group design and VPC security posture.
- [`./private-by-default.md`](./private-by-default.md) — the parent principle; security groups are the enforcement mechanism.
- [`./scp-guardrails-set-the-ceiling.md`](./scp-guardrails-set-the-ceiling.md) — SCPs can enforce the no-open-SSH rule preventively.

## Provenance

Codifies `aws-network-engineer`'s house opinion #4 in `CLAUDE.md`: "private by default; no `0.0.0.0/0` to admin ports." Standard AWS security assessment finding from the AWS Foundational Security Best Practices standard in Security Hub.

---

_Last reviewed: 2026-06-05 by `claude`_
