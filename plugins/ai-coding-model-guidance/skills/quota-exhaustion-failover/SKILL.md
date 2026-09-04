---
name: quota-exhaustion-failover
description: "Hard gate when a coding agent/surface returns quota, rate-limit, weekly/monthly cap, spend-limit, or tokens-exhausted. Never silent-fail or blind-retry — try param/effort/scope levers before vendor failover, then traverse the vendor-neutral tier tree before naming a substitute SKU."
---

# Skill: Quota / token exhaustion failover (HARD GATE)

Use when any coding agent or surface returns a quota, rate-limit, weekly/monthly cap, spend-limit, or "tokens exhausted" error.

**Rule:** never silent-fail and never burn the same exhausted surface with blind retries. Try **param/effort/scope levers** before vendor failover. Then traverse the vendor-neutral tier tree + closed-world lineup before naming a substitute SKU.

Full tree: [`../../knowledge/ai-coding-quota-exhaustion-decision-tree.md`](../../knowledge/ai-coding-quota-exhaustion-decision-tree.md).

## Ladder

1. **Classify** — context overflow | rate limit | soft quota | hard weekly/monthly/spend
2. **Record** — surface, model, error, reset time, task state, remaining headroom
3. **Levers on usable surface (before vendor hop)**
   1. Lower effort / thinking / fast flags to stretch quota if quality OK
   2. Raise reasoning dial on same model before bigger SKU
   3. Tighten prompt/scope; decompose into smaller runs
   4. Shrink context; avoid max window params unless required
4. **Failover order (same tier first)**
   1. Same vendor, different surface (CLI ↔ cloud agent)
   2. Same tier, different vendor (closed-world lineup)
   3. Lower-cost tier that still fits the task leaf
   4. Wait until reset if deadline allows
   5. Escalate (Team Lead / human) for plan upgrade / spend-limit raise / true ambiguity
5. **Deliverable** — levers tried + chosen failover + reset time + what NOT to retry

## Lever catalog (summary)

| Lever | When |
|---|---|
| Lower effort / fast / thinking off | Soft quota left; quality bar still met |
| Raise reasoning dial same model | Quality insufficient; not hard-capped |
| Tighten prompt / scope | Token burn from sprawling asks |
| Decompose | One big agentic run burning quota |
| Shrink context / window param | Context overflow or expensive max window |
| Same vendor, other surface | Hard cap on one meter only |
| Same tier, other vendor | Cap is hard; task still needed |
| Lower tier that fits leaf | Prestige SKU unaffordable under cap |
| Wait for reset | Soft deadline; alternates miss quality bar |
| Escalate plan upgrade | Alternates fail + hard deadline |

## Anti-patterns

- Identical retry on the exhausted surface
- Jumping SKU before effort/scope levers
- Hiding the limit from the Team Lead / human
- Inventing SKUs outside the verified lineup
- Using max context "just in case" under quota pressure

## Credit

Companion to [`ai-coding-quota-exhaustion-decision-tree.md`](../../knowledge/ai-coding-quota-exhaustion-decision-tree.md); mirrors the Grok Bot hard-gate workflow (Matthew-approved effort levers, 2026-09).
