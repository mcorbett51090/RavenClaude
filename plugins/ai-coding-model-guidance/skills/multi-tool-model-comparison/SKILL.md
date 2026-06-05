---
name: multi-tool-model-comparison
description: "Compare model options across GitHub Copilot, OpenAI Codex, and xAI Grok for a single task when the developer has not committed to one ecosystem. Produces a structured side-by-side that surfaces availability, tier mapping, and key tradeoffs without naming specific volatile numbers."
---

# Skill: Multi-Tool Model Comparison

When a developer is evaluating AI coding tools and hasn't committed to one ecosystem, a comparison across Copilot/Codex/Grok is more useful than a deep dive into one. This skill structures that comparison so the result is methodology-grounded and resistant to lineup churn.

## Step 0 — Establish the task shape first

The comparison is only as useful as the task description is precise. Before comparing, pin:

1. **Use-case type** — inline completion, supervised chat, or autonomous multi-step run
2. **IDE surface** — VS Code, JetBrains, Neovim, terminal, or CI/cloud
3. **Team / org context** — individual developer, small team, enterprise org with policy controls
4. **Budget sensitivity** — tight per-token ceiling or best-quality-regardless-of-cost

These four pins determine which models on each platform are even in scope. Skip the comparison until they are established.

## Step 1 — Map the task to a vendor-neutral tier

Use the vendor-neutral task-shape tree (see `../../knowledge/ai-coding-decision-trees.md`) to identify the target tier before touching any vendor lineup:

| Tier | Inline/latency | Supervised chat | Autonomous/long |
|---|---|---|---|
| Fast inline | First choice | Not applicable | Not applicable |
| Balanced default | Fallback | First choice | First choice for routine |
| Frontier | Not applicable | Hard-reasoning tasks | Always start here |

## Step 2 — Map the tier to each ecosystem's current offering

For each of the three ecosystems, consult `../../knowledge/cross-tool-model-lineup-2026.md` and fill in this table. **Do not name a model without checking the lineup entry — mark every cell `[verify-at-use]`** because picker contents churn:

| Dimension | GitHub Copilot | OpenAI Codex | xAI Grok |
|---|---|---|---|
| Fast inline | [verify-at-use] | [verify-at-use] | [verify-at-use] |
| Balanced default | [verify-at-use] | [verify-at-use] | [verify-at-use] |
| Frontier | [verify-at-use] | [verify-at-use] | [verify-at-use] |
| Reasoning dial | No | Yes (Codex-specific) | No |
| Surface lock-in | IDE / GitHub.com | CLI + cloud | API |
| Org policy controls | Enterprise/Business | Org-level | API key only |

## Step 3 — Surface the differentiating axes

After filling the table, call out the axes that actually differentiate the three for this task:

- **Reasoning lever** — only Codex exposes an explicit reasoning-level dial; if the task is quality-limited (not cost-limited), this is often the deciding factor.
- **Surface coupling** — Copilot is tightly coupled to IDE + GitHub; Codex is terminal/API-first; Grok is API-first. If the developer lives in VS Code, Copilot's surface friction is zero.
- **Org policy** — enterprise teams using GitHub Enterprise Cloud can enforce model rules in Copilot; no equivalent in Codex or Grok at the org level.
- **Context window** — all three platforms have models with large windows, but the limits churn; verify at use and flag the task's actual context demand (see `../context-window-planning/SKILL.md`).

## Step 4 — Produce the recommendation

State a **primary recommendation** and a **fallback** — not a ranked list of seven options. The developer needs a decision, not a comparison table that passes the decision back.

Format:
```
Primary: [ecosystem] — [tier] tier — because [1-2 reasons from Step 3]
Fallback: [ecosystem] — [tier] tier — if [specific condition]
Verify before use: [any specific SKU mentioned] against the knowledge bank [retrieval date]
```

## Pitfalls

- Starting the comparison before the task shape is pinned — produces a generic answer the developer already knew.
- Comparing model names rather than tiers — names change; tiers are stable.
- Treating absence from the verified lineup as proof of absence — offer to research rather than confirming a negative.
- Letting surface preference masquerade as model quality: "Copilot is better" when the real answer is "Copilot's IDE coupling is better for your use case."

## See also

- [`../../agents/codex-model-strategist.md`](../../agents/codex-model-strategist.md) — deep Codex reasoning-level logic
- [`../../agents/copilot-model-strategist.md`](../../agents/copilot-model-strategist.md) — Copilot surface/plan scoping
- [`../../agents/grok-model-strategist.md`](../../agents/grok-model-strategist.md) — Grok lineup and retirements
- [`../../knowledge/ai-coding-decision-trees.md`](../../knowledge/ai-coding-decision-trees.md) — vendor-neutral tier tree
