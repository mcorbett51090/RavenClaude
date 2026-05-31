---
description: Write a compliance policy that survives an exam and an annual refresh — scope the regime first, keep policy (principles) separate from procedure (steps) on their own approval cadences, frame conduct obligations as outcomes with outcome evidence, and give every layer a cite, a named owner, and an exceptions section.
argument-hint: "[the policy + regime, e.g. 'an AML policy refresh for a Bermuda insurer']"
---

# Write a compliance policy

You are running `/regulatory-compliance:write-compliance-policy`. Draft or refresh the policy the user described (`$ARGUMENTS`), following this plugin's `policy-and-procedure-writer` discipline. A 100-page policy nobody reads is worse than a 12-page policy everyone reads — and the extra length is usually procedure that doesn't belong there.

## When to use this

New policy drafting, an annual refresh, a gap analysis against new regulation, or a jurisdictional adaptation. Not for the operational walkthrough/evidence work an exam needs (that's the examination command) and not for whether a commitment creates legal liability (counsel).

## Steps

1. **Scope the jurisdiction and regime first** (`scope-the-jurisdiction-before-you-map`): name the regulator + regime; what diverges across borders is the definitions, thresholds, and escalation paths — not usually the principle. Route BMA/Bermuda terminology to `bermuda-insurance-specialist`.
2. **Separate policy from procedure** (`policy-separate-policy-from-procedure`): principles + board-level commitments in the policy (approver = board/committee, changes rarely); operational steps in the procedure (approver = exec owner, changes with the process). Burying procedure inside policy guarantees drift and a stale in-force document.
3. **Frame conduct and consumer obligations as outcomes** (`policy-frame-conduct-and-consumer-outcomes`): state the required *outcome* in customer terms ("the customer understood the fee and it represented fair value"), then map operational steps and the evidence the *outcome* was achieved — complaint-root-cause trends, fair-value/target-market assessments — not a checklist of disclosures sent. (Scope whether a consumer-duty regime applies first.)
4. **Give every layer a cite, a named owner, and a review cycle** (`no-control-without-a-cite-and-evidence`): each policy/procedure/standard/guideline cites the regulator's actual section it implements, names an accountable person/role (not "the team"), and carries a defined review cadence + last-reviewed date.
5. **Include a real definitions section and a real exceptions section** (`policy-separate-policy-from-procedure`): definitions that actually define ("customer", "material"); an exceptions section naming who authorizes a deviation, on what basis, with what record — a policy without one makes every deviation a violation.

## Guardrails

- Write what the firm actually does, then fix the gap — not the aspirational version; one source of truth per policy (no floating copies).
- Don't ship copy-pasted vendor-template text (the vendor's name left in it is a real, recurring miss), and never write "the firm complies with all applicable laws" — name the law and how.
- A refresh re-checks against *current* regulation; copying last year's text without re-checking is a flagged anti-pattern. Cite the regulator's primary source, not a summary blog.
