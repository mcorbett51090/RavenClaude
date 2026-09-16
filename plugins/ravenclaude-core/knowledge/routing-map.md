# Routing map — which doc answers which question

**Last reviewed:** 2026-09-16 · **Owner:** ravenclaude-core (domain-neutral).  
**Purpose:** stop wrong-first-pick among four overlapping "routing" surfaces.  
**Non-goal:** do **not** collapse these trees into one mega-file.

| # | Question | SSOT | Path |
|---|---|---|---|
| 1 | **Surface / whether / playbook** — slash vs skill vs agent vs FORGE? Spawn at all? | `spawn-team` Step 1.25 | [`skills/spawn-team/SKILL.md`](../skills/spawn-team/SKILL.md) |
| 2 | **Which specialist** — which of the 17 agents? | Agent routing decision tree | [`agent-routing.md`](agent-routing.md) |
| 3 | **Which host × model for task shape** — Claude vs Codex vs Copilot vs Grok? | Agent routing matrix (heuristic) | [`agent-routing-matrix.md`](agent-routing-matrix.md) (+ `.json`) |
| 4 | **Which tier × surface cell** — fast/balanced/top + archival pins | **Unified Model Matrix (UMM)** | [`unified-model-matrix.md`](unified-model-matrix.md) (+ `.json`) |

## How to use

1. Start at row **1** unless the surface is already decided.  
2. Only when Step 1.25 selects the **agent** surface → row **2**.  
3. When choosing a **coding host** for a task shape (not Claude role→tier) → row **3**.  
4. When choosing **tier / pin / cheap-lane cell** → row **4** (UMM is SSOT).

## Orthogonal levers (not rows above)

- **Caveman verbosity/mode** (`caveman_routing`) ≠ model tier — do not toggle UMM to change prose mode.  
- **Cheap-lane** is opt-in (`cheap_lane.mode` default **off**); cells live in UMM when on.  
- **Handoff cluster** (`/handoff`, nudge, precompact, session-relay) — see [`handoff-taxonomy.md`](handoff-taxonomy.md); not a routing matrix.

## Related

- Stub: [`model-tier-delegation.md`](model-tier-delegation.md) → UMM  
- Boundary: agent-routing-matrix **≠** UMM (see banners on both files)  
- Comfort seed: `templates/comfort-posture-balanced.yaml`
