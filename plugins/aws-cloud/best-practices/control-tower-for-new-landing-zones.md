# Use Control Tower for new multi-account landing zones

**Status:** Pattern
**Domain:** AWS Organizations / landing zone
**Applies to:** `aws-cloud`

---

## Why this exists

Standing up a multi-account landing zone by hand — Organizations + custom SCPs + log archive + security tooling + account factory — is a weeks-long project with bespoke, hard-to-audit results. AWS Control Tower codifies the same structure (root OU, Security OU with log-archive and audit accounts, standard guardrails, Account Factory for vending) into a managed service. Starting from scratch with hand-rolled SCPs is justified only when Control Tower's opinionated structure genuinely conflicts with the estate's requirements — which is uncommon.

## How to apply

For a greenfield multi-account estate:

1. **Enable Control Tower** in the Organizations management account. It creates:
   - Log Archive account (aggregated CloudTrail + Config)
   - Audit account (read-only security tooling access)
   - Root OU → Security OU → Custom OUs
2. **Configure Account Factory** — use the built-in Service Catalog product or Account Factory for Terraform (AFT) for IaC-driven vending.
3. **Enroll existing accounts** using the Control Tower console or `aws controltower register-organizational-unit`.
4. **Apply additional SCPs** via the Organizations console or IaC on top of Control Tower's guardrails.

```hcl
# Terraform — Account Factory for Terraform (AFT) bootstrap
module "aft" {
  source  = "aws-ia/control_tower_account_factory/aws"
  version = "~> 1.12"

  ct_management_account_id    = var.management_account_id
  log_archive_account_id      = var.log_archive_account_id
  audit_account_id            = var.audit_account_id
  aft_management_account_id   = var.aft_management_account_id
  ct_home_region              = var.home_region
  tf_backend_secondary_region = var.secondary_region
}
```

**Do:**
- Use AFT when you need GitOps-driven account vending with custom account-level IaC.
- Enable AWS Security Hub and GuardDuty in the Audit account to aggregate findings across all enrolled accounts.
- Tag accounts at the OU level with `environment`, `owner`, and `cost-center` mandatory tags via a Tag Policy.
- Review and accept Control Tower's managed guardrails before enabling — understand what they block.

**Don't:**
- Launch workloads in the Management (root) account — it is for Organizations/Control Tower admin only.
- Enroll the Management account itself into a Control Tower OU.
- Disable Control Tower guardrails without documenting the business justification.
- Hand-roll an account-vending pipeline before evaluating AFT.

## Edge cases / when the rule does NOT apply

- **Single-account, single-team, MVP workload**: Control Tower overhead is unjustified. Start simple and migrate to multi-account when the blast-radius argument becomes real.
- **Existing complex OU structures**: Control Tower requires a clean OU hierarchy; heavily customized existing structures may require remediation before enrollment.
- **GovCloud / China regions**: Control Tower is available in GovCloud (US) and expanding, but verify current region coverage before designing the landing zone.

## See also

- [`../agents/aws-architect.md`](../agents/aws-architect.md) — owns multi-account landing zone design.
- [`./multi-account-by-blast-radius.md`](./multi-account-by-blast-radius.md) — the rationale for multi-account structure.
- [`./scp-guardrails-set-the-ceiling.md`](./scp-guardrails-set-the-ceiling.md) — SCPs layer on top of Control Tower guardrails.

## Provenance

Codifies the `aws-architect` house opinion on landing zones from `CLAUDE.md` §2 (#3 "Multi-account by blast radius") and the AWS Landing Zone Accelerator / Control Tower documentation. Standard enterprise AWS architecture pattern.

---

_Last reviewed: 2026-06-05 by `claude`_
