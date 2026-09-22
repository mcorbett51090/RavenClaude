---
name: compliance-policy-authoring
description: "Draft or refresh a compliance policy that survives an exam and an annual refresh — scope the regime, keep policy separate from procedure, frame conduct as outcomes, give every layer a cite + named owner + exceptions. Used by policy-and-procedure-writer. Gap analysis against a new regulation stays in regulatory-mapping."
---

# Skill: compliance-policy-authoring

> **Invoked by:** `policy-and-procedure-writer` (primary); `aml-kyc-analyst` and `bermuda-insurance-specialist` as reviewers on AML / Bermuda adaptation.
>
> **When to invoke:** new policy drafting, an annual refresh, or a jurisdictional adaptation. NOT the operational walkthrough/evidence an exam needs (`examination-readiness`) and NOT whether a commitment creates legal liability (counsel). Gap analysis vs a new regulation is `regulatory-mapping` — run that first, then this skill drafts the delta.
>
> **Output:** a policy (and, if needed, a sibling procedure) that matches [`../../templates/policy-template.md`](../../templates/policy-template.md), with cites, named owners, a review cycle, and a real exceptions section.

The slash command `/regulatory-compliance:write-compliance-policy` is the same playbook on the user surface. This file is what spawned agents auto-load.

Layer-selection (policy vs procedure vs standard vs guideline) stays in [`../../knowledge/compliance-decision-trees.md`](../../knowledge/compliance-decision-trees.md). This skill is the drafting procedure.

## Flow

1. **Scope the jurisdiction and regime first** ([`scope-the-jurisdiction-before-you-map`](../../best-practices/scope-the-jurisdiction-before-you-map.md)): name the regulator + regime. What diverges across borders is usually definitions, thresholds, and escalation paths — not the principle. Route BMA/Bermuda terminology to `bermuda-insurance-specialist`.

2. **If this is a regulatory-change refresh, run `regulatory-mapping` first.** A refresh that copies last year's text without re-checking current regulation is an anti-pattern. Cite the regulator's primary source, not a summary blog.

3. **Separate policy from procedure** ([`policy-separate-policy-from-procedure`](../../best-practices/policy-separate-policy-from-procedure.md)): principles + board-level commitments in the policy (approver = board/committee, changes rarely); operational steps in the procedure (approver = exec owner, changes with the process). Burying procedure inside policy guarantees drift.

4. **Frame conduct and consumer obligations as outcomes** ([`policy-frame-conduct-and-consumer-outcomes`](../../best-practices/policy-frame-conduct-and-consumer-outcomes.md)): required *outcome* in customer terms, then the evidence the outcome was achieved — not a checklist of disclosures sent. Scope whether a consumer-duty regime applies first.

5. **Give every layer a cite, a named owner, and a review cycle** ([`no-control-without-a-cite-and-evidence`](../../best-practices/no-control-without-a-cite-and-evidence.md)): each layer cites the regulator's actual section, names an accountable person/role (not "the team"), and carries a defined review cadence + last-reviewed date.

6. **Include a real definitions section and a real exceptions section.** Definitions that actually define ("customer", "material"); exceptions naming who authorizes a deviation, on what basis, with what record. A policy without an exceptions section makes every deviation a violation.

7. **Write what the firm actually does, then fix the gap** — not the aspirational version. One source of truth (no floating copies). Don't ship vendor-template text with the vendor's name left in. Never write "the firm complies with all applicable laws" — name the law and how.

8. **Annual-refresh extras:** change-log of what moved, named sign-off, and a re-check against *current* primary sources.

## What this skill does NOT cover

- Control-to-citation gap analysis → `regulatory-mapping`
- Exam PBC / walkthroughs → `examination-readiness`
- Risk-register construction → `risk-register-build`
- Legal liability of a commitment → counsel

## References

- Template: [`../../templates/policy-template.md`](../../templates/policy-template.md)
- Command (same playbook, user-invoked): [`../../commands/write-compliance-policy.md`](../../commands/write-compliance-policy.md)
- Layer tree: [`../../knowledge/compliance-decision-trees.md`](../../knowledge/compliance-decision-trees.md)
- Gap analysis: [`../regulatory-mapping/SKILL.md`](../regulatory-mapping/SKILL.md)
