---
name: copilot-surface-audit
description: "Audit a developer's GitHub Copilot configuration across all surfaces (completions, chat IDE, coding agent, cloud agent, mobile) to identify model gaps, plan mismatches, and org-policy constraints. Reach for this skill before recommending a Copilot model — surface and plan scope the answer, not just the model name."
---

# Skill: Copilot Surface Audit

A Copilot model recommendation is only as good as its surface scope. "Model X is available in Copilot" is an incomplete claim until the surface (completions vs. chat vs. coding agent vs. cloud agent vs. mobile) and the plan (Free/Pro/Business/Enterprise) are both confirmed. This skill ensures every recommendation is surface-scoped and plan-gated.

## Step 1 — Identify the active surface(s)

Ask or infer from context which Copilot surface(s) the developer actually uses:

| Surface | Entry point | Model picker location |
|---|---|---|
| Completions | IDE inline ghost-text | No picker — org policy or default applies |
| Chat IDE | IDE sidebar / slash commands | Model picker in chat header |
| Coding agent | IDE-initiated autonomous run | Separate agent surface — plan-gated |
| Cloud agent | GitHub.com / Copilot Workspace | Separate cloud picker — may differ from IDE |
| Mobile | GitHub Mobile app | Mobile-specific subset — narrowest picker |

**Do not conflate surfaces.** A model available in chat IDE may not be available for the coding agent; cloud agent has its own availability list.

## Step 2 — Confirm plan tier

| Plan | Key capabilities | Notes |
|---|---|---|
| Free | Subset of models; monthly usage cap | Narrowest model picker |
| Pro | Full IDE model picker; no monthly cap | Baseline for professional use |
| Business | Org policy controls; team seat management | Adds model rules + audit log |
| Enterprise | Full controls; org model allow/deny list; GHEC required | Broadest governance surface |

> If the developer is on Business or Enterprise, check whether an org admin has applied a **model rules** policy before recommending a specific SKU. See [`../../agents/copilot-model-strategist.md`](../../agents/copilot-model-strategist.md).

## Step 3 — Cross-reference the verified lineup

For each surface × plan combination, confirm model availability in [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) under the Copilot section. Apply the **closed-world rule**: if a model is not in the verified lineup for that surface, do not confirm availability — offer to research.

```
For each candidate model:
  1. Is it in the verified Copilot lineup entry?    → if no: closed-world, do not confirm
  2. Is the plan gate met?                           → if no: explain the plan requirement
  3. Is the surface listed?                          → if no: check mobile/cloud-agent sub-lists
  4. Is there an org model rule that blocks it?      → if yes: escalate to security-reviewer
```

## Step 4 — Summarize the audit result

Produce a surface-scoped summary table:

| Surface | Plan required | Model available? | Gate | Verified date |
|---|---|---|---|---|
| Completions | Pro+ | [verify-at-use] | Plan gate | [retrieval date] |
| Chat IDE | Pro+ | [verify-at-use] | Plan gate | [retrieval date] |
| Coding agent | Business/Enterprise | [verify-at-use] | Surface + plan | [retrieval date] |

Always include the retrieval date and a `[verify-at-use]` marker on any availability claim — Copilot picker contents change weekly.

## Pitfalls

- Confirming model availability without specifying the surface: "X is in Copilot" is never a complete answer.
- Ignoring plan gates on Free-tier users — the Free sub-list is narrower than the full picker.
- Assuming coding-agent and cloud-agent availability matches the IDE chat picker.
- Forgetting to check org model rules for Business/Enterprise org members.
- Quoting the Copilot picker without a retrieval date — it changes without deprecation notice.

## See also

- [`../../agents/copilot-model-strategist.md`](../../agents/copilot-model-strategist.md) — the agent this skill supports
- [`../../knowledge/ai-coding-decision-trees.md`](../../knowledge/ai-coding-decision-trees.md) — the Copilot surface/plan decision tree
- [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) — the dated Copilot lineup
