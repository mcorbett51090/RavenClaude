---
id: forge
title: "FORGE — the gated planning pipeline"
category: "Planning & contribution"
kind: ravenclaude-built
order: 60
summary: "Dashboard card for /forge: depth-scaled, fail-closed planning gates. Gate depth lives in the forge-pipeline skill — this card is one screen + cite."
see_also: [command-review-tribunal, wrap-and-scenarios]
last_verified: 2026-09-16
refresh_when: "The FORGE gate set, the depth ladder, or the routing/exit logic changes."
sources:
  - label: "forge-pipeline skill (gate SSOT)"
    url: "plugins/ravenclaude-core/skills/forge-pipeline/SKILL.md"
  - label: "/forge command (thin entry)"
    url: "plugins/ravenclaude-core/commands/forge.md"
---

**FORGE** is RavenClaude's gated planning pipeline — what `/forge` runs. Raw idea → clarify → research/verify → divergent panels → critic/tiebreak/red-team (depth-scaled) → synthesize → deterministic route/exit. Gates are **fail-closed**; artifacts land in the run dir.

**Depth ladder (summary):** `micro` → scope + synthesize + route · `quick` (default) + research + panels · `standard` + critic/tiebreak/red-team · `deep` uncapped conflict + checkpoint/resume.

**Two differentiators:** cross-model panels (catches same-model blind spots) and a fact-verification gate (load-bearing outside-repo claims need a this-session source or `[unverified]`).

⛔ **This card is thin on purpose (0.323.12).** Gate scripts, waivers, receipt shape, and worktree rules live exclusively in [`skills/forge-pipeline/SKILL.md`](../../skills/forge-pipeline/SKILL.md). `/forge` stays a thin command entry. FORGE raises plan-quality odds — it does **not** guarantee correctness.

```mermaid
flowchart TD
  I[Raw idea] --> G0[Scope / clarify]
  G0 --> G1[Research + verify facts]
  G1 --> P[Two panels<br/>different models]
  P --> C[Critic + tiebreak + red-team]
  C --> S[Synthesize plan]
  S --> R{Route}
  R -- local --> EX[ExitPlanMode]
  R -- cloud --> UP[Ultraplan handoff]
  class G0,G1,P,C,S,R,EX,UP built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  I[Idea] --> G[Gated review] --> R[Routed plan]
  class G,R built
```
