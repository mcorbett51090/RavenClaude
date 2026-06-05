---
scenario_id: 2026-06-05-entra-over-privileged-owner-assignment
contributed_at: 2026-06-05
plugin: azure-cloud
product: azure-rbac
product_version: "n/a"
scope: likely-general
tags: [entra, rbac, owner, pim, least-privilege, group-assignment]
confidence: high
reviewed: false
---

## Problem

A pre-migration access review of a 3-subscription estate found **17 standing `Owner` assignments at subscription scope**, most of them on individual user accounts, plus a CI/CD service principal that held `Contributor` at the management-group root "so the pipeline doesn't break." Nobody could say which assignments were still needed. The client wanted to "just remove the ones we don't recognize," which is exactly how you lock yourself (or the break-glass account) out mid-engagement.

## Constraints context

- Segment: independent ISV, single Entra tenant, no PIM in use (Entra ID P2 was licensed but never configured).
- The estate had grown workload-first — RBAC was granted reactively at whatever scope made the immediate error go away (almost always the subscription), never scoped down afterward.
- Standing `Owner` includes the ability to grant *further* RBAC, so each one is a privilege-escalation root, not just an access grant.
- This is an **identity/security-posture** finding, so it routes to `ravenclaude-core/security-reviewer` for the verdict — `entra-identity-engineer` supplies the Entra craft, core signs off (CLAUDE.md §10).

## Attempts

- Tried: bulk-removing the unrecognized assignments first. Stopped before executing — there was no confirmed break-glass account with standing access, so a wrong delete could have left no one able to re-grant. **Establish break-glass before you prune.** Outcome: aborted, correctly.
- Tried: enumerating the actual assignments as the ground truth instead of guessing — `az role assignment list --all --include-inherited --include-groups -o table` per subscription, then separating *inherited-from-MG* from *direct*, and *user* from *group* from *service-principal*. Outcome: the real picture — most "Owner" grants were direct-to-user and never needed `Owner` (they needed `Contributor` on one RG).
- Tried (the moves that worked):
  1. Confirmed/created **two break-glass cloud-only accounts** excluded from Conditional Access, with standing `Owner` and monitored sign-in — the safety net before any pruning.
  2. Re-scoped each human assignment to the **least built-in role at the least scope** that covered their actual work (`Contributor`/`Reader`/a job-specific role on the RG, not `Owner` on the subscription).
  3. Moved privileged roles to **PIM eligible** (JIT, MFA + justification + time-box) instead of standing — `Owner`/`User Access Administrator` became eligible-only.
  4. Replaced the pipeline's MG-root `Contributor` with a **workload-identity-federation** service principal scoped to the specific deployment RG (no client secret).
  Outcome: zero standing `Owner` on humans, JIT for the privileged roles, the SP scoped down and secretless.

## Resolution

The root cause was **scope creep by default** — every grant defaulted to subscription `Owner` because that always cleared the immediate error, and nothing ever walked it back. The fix is the team's standing posture: **least-privilege built-in role at the least scope (RG/resource, not subscription/MG), PIM-eligible for anything privileged, no standing `Owner`** (house opinions #5 + PIM). The non-negotiable sequencing lesson: **establish and verify break-glass access before removing any privileged assignment** — the cleanup is reversible only if someone can still grant roles.

**Action for the next consultant hitting this pattern:** enumerate with `az role assignment list --all --include-inherited --include-groups` (don't trust the portal's per-scope view alone — inherited grants hide), separate user/group/SP, confirm break-glass first, then re-scope to the RG and move privileged roles to PIM-eligible. Prefer **group-based** assignment over per-user so the next review is auditable. Route the posture decision to `ravenclaude-core/security-reviewer`. Verify current PIM licensing (Entra ID P2) and the exact built-in role definitions `[verify-at-use]` — role contents change.

**Sources (retrieved 2026-06-05):**
- Azure RBAC best practices — https://learn.microsoft.com/azure/role-based-access-control/best-practices
- Microsoft Entra PIM (configure eligible assignments) — https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure
- Break-glass / emergency-access accounts — https://learn.microsoft.com/entra/identity/role-based-access-control/security-emergency-access

Role definitions, PIM licensing tiers, and Conditional Access behavior are version-volatile — `[verify-at-use]` against the current tenant before acting.
