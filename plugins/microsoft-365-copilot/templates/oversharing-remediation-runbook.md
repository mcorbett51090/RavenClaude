# Template — pre-Copilot oversharing remediation runbook

Copy + fill. Source of truth: [`../knowledge/copilot-security-purview-2026.md`](../knowledge/copilot-security-purview-2026.md) + the [`oversharing-remediation-playbook`](../skills/oversharing-remediation-playbook/SKILL.md) skill. **Remediate BEFORE enabling Copilot.**

## Scope
- Tenant / sites in scope: <...>
- Target Copilot enablement date: <...>
- Owners: SharePoint admin <...> · Compliance <...> · Site owners <...>

## Step 1 — Assess blast radius
| Site / library | Over-permissioned? (everyone/EEEU) | Sensitive content? | Reachable by | Owner |
|---|---|---|---|---|
| | | | | |

Tooling: SharePoint Advanced Management access reports; sensitivity-label coverage report. Output: the prioritized cleanup list.

## Step 2 — Reduce Copilot's reach (RCD / RSS) — NOT a boundary
- [ ] Enable Restricted Content Discovery / Restricted SharePoint Search on the worst offenders.
- [ ] **Documented to stakeholders that RSS/RCD are reach-reduction, not access control** — a user with a direct link still gets in.

## Step 3 — Purview (labels + DLP)
- [ ] Apply sensitivity labels to sensitive content.
- [ ] Configure DLP-for-Copilot (E5/Suite) — note: blocks *processing*, not citation titles; EXTRACT right governs pull-in.

## Step 4 — Permission cleanup (the real fix)
- [ ] Remove "everyone"/EEEU grants; fix broken inheritance.
- [ ] Owner attestation on each remediated site.

## Step 5 — Enable + verify
- [ ] Enable Copilot for the remediated scope.
- [ ] **Verify with test identities** (a high-privilege and a low-privilege user) that trimming is correct.
- [ ] DLP policy simulation reviewed.

## Comms + rollback
- Comms plan: <who/when>
- Rollback: re-tighten RCD/RSS / disable Copilot for the scope if verification fails.

## Sign-off
- [ ] Security **verdict** obtained from `ravenclaude-core/security-reviewer`.

**Licensing impact:** RSS + Purview DLP-for-Copilot are E5 / Copilot-Suite-gated. <state seats + add-ons>
