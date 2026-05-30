---
name: oversharing-remediation-playbook
description: "Remediate Microsoft 365 oversharing BEFORE enabling Copilot — assess the blast radius, then run the sequence (RCD/RSS reach-reduction → Purview sensitivity labels + DLP-for-Copilot → site/permission cleanup → enable), framing RSS/RCD as reach-reduction and NOT a security boundary, with owners, verification, comms, and rollback. Use when planning a Copilot rollout over a tenant with uncertain permissions."
---

# Oversharing remediation playbook

Playbook for `copilot-admin-governance`. Source of truth: [`../../knowledge/copilot-security-purview-2026.md`](../../knowledge/copilot-security-purview-2026.md). Runbook template: [`../../templates/oversharing-remediation-runbook.md`](../../templates/oversharing-remediation-runbook.md).

## The cardinal rule
**Remediate BEFORE enabling Copilot.** Copilot surfaces everything a user can already reach; enabling it over an over-permissioned tenant turns latent oversharing into active discovery.

## The sequence

1. **Assess the blast radius** — which sites/libraries are over-permissioned ("everyone"/EEEU), which carry sensitive content, who can reach what. Use SharePoint Advanced Management / access reports.
2. **RCD / RSS — reduce Copilot's reach** (NOT a boundary). Restricted Content Discovery / Restricted SharePoint Search shrink what Copilot crawls/surfaces while you do the real cleanup. **Never present them as access control** — a user with a direct link still gets in.
3. **Purview** — apply **sensitivity labels** + **DLP-for-Copilot** (E5/Suite-gated). Remember: DLP blocks *processing*, not citation titles/URLs; the EXTRACT right governs content pull-in.
4. **Cleanup** — the real fix: remove "everyone"/EEEU grants, fix inheritance, owner attestation. This is the work; steps 2–3 buy time.
5. **Enable** — turn on Copilot for the remediated scope; verify with test identities.

## Owners + verification
Each step has an owner (SharePoint admin / compliance / site owners) and a verification check (access report delta, test-identity query, DLP policy simulation). Plan comms + a rollback (re-tighten RCD/RSS) before flipping Copilot on.

## Licensing impact
RSS + Purview DLP-for-Copilot are E5 / Copilot-Suite-gated — state it.

## The seam
The security **verdict** (is this sufficient? injection risk?) is `ravenclaude-core/security-reviewer`'s. Connector ACL mechanics → `graph-connector-engineer`.

## Anti-patterns
- Enabling Copilot before cleanup; selling RSS/RCD as a boundary; assuming DLP hides citation titles; no test-identity verification; no rollback.
