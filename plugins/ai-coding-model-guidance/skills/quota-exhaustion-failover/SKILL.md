---
name: quota-exhaustion-failover
description: "Hard gate when a coding agent/surface returns quota, rate-limit, weekly/monthly cap, spend-limit, or tokens-exhausted. Never silent-fail or blind-retry the exhausted surface — traverse the quota decision tree, then the vendor-neutral tier tree, before naming a substitute SKU."
---

# Skill: Quota / token exhaustion failover (HARD GATE)

Use when any coding agent or surface returns a quota, rate-limit, weekly/monthly cap, spend-limit, or "tokens exhausted" error (Claude Code weekly limit, Codex/ChatGPT caps, Cursor cloud-agent spend limit, Copilot premium requests).

**Rule:** never silent-fail and never burn the same exhausted surface with blind retries. Traverse [`../../knowledge/ai-coding-quota-exhaustion-decision-tree.md`](../../knowledge/ai-coding-quota-exhaustion-decision-tree.md) before picking a substitute SKU (still apply the vendor-neutral tier tree + closed-world lineup after).

## Ladder

1. **Classify limit type** — context overflow → `context-window-planning`; short rate limit → backoff once (repeats → soft quota); soft hourly/daily → wait OR failover; hard weekly/monthly/spend → failover required until reset.
2. **Record** — surface, model, error text, reset time if known, task state.
3. **Failover order (same tier first — right-size, don't jump to frontier)**
   1. Same vendor, different surface
   2. Same tier, different vendor (closed-world lineup)
   3. Lower-cost tier that still fits the task tree leaf
   4. Wait until reset if deadline allows
   5. Escalate (Team Lead / human) for plan upgrade / spend-limit raise / true ambiguity
4. **Deliverable** — chosen failover + why + reset time + what NOT to retry

## Anti-patterns

- Identical retry on the exhausted surface
- Prestige upgrade only because the cheap path is capped when a same-tier alternate exists
- Hiding the limit from the Team Lead / human
- Inventing SKUs outside the verified lineup

## Credit

Companion to [`ai-coding-quota-exhaustion-decision-tree.md`](../../knowledge/ai-coding-quota-exhaustion-decision-tree.md); mirrors the Grok Bot hard-gate workflow.
