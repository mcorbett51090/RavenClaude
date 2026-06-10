---
id: sleipnir
title: "Sleipnir — worktree traversal"
category: "Marketplace engineering"
kind: ravenclaude-built
order: 67
summary: "A labeling convention for parallel, isolated git-worktree work: the agent says 'I'll send Sleipnir to that branch' instead of narrating raw worktree calls; a read-only widget lists current worktrees."
see_also: [copilot-bridge, layout-hook]
last_verified: 2026-06-08
refresh_when: "The worktree-traversal labeling convention or the read-only Sleipnir's stables widget changes."
sources:
  - label: "ravenclaude-core constitution §Sleipnir — the worktree-traversal labeling convention"
    url: "plugins/ravenclaude-core/CLAUDE.md"
---

**Sleipnir** is the name for worktree traversal — Odin's eight-legged horse, the one mount that crosses realm boundaries safely. When the Team Lead fans work across several git branches in parallel, each branch gets its own **isolated worktree**, and in user-facing prose the agent prefers *"I'll send Sleipnir to that branch"* over narrating the raw worktree mechanics. The label anchors your intuition about what's happening (a safe crossing into a separate branch's working tree) while the underlying mechanism is unchanged.

This is **labeling only** — there is deliberately no `/sleipnir` slash command, no Sleipnir agent, and no new component. The convention surfaces in the worktree skills (new-worktree, cleanup-worktrees, spawn-team) and, on the dashboard's Activity tab, as a **read-only "Sleipnir's stables"** widget showing the current list and count of worktrees. The widget writes nothing; on a static host it shows an honest empty state rather than pretending to have live data.

The convention pairs with a load-bearing dispatch rule about worktrees: reading a branch needs no isolation and can be fanned out freely across sub-agents, but **writing** a branch (checkout / commit / push) needs an approval only the main interactive session can obtain — background sub-agents are auto-denied git writes. So Sleipnir carries reads out in parallel, while branch-mutating work stays in the main session, sequentially.

```mermaid
flowchart TD
  TL[Team Lead] --> SL[Send Sleipnir<br/>to a branch]
  SL --> WT[Isolated worktree<br/>per branch]
  WT --> RD[Reads: fan out freely]
  WT --> WR[Writes: main session only]
  WT --> WID[Read-only<br/>Sleipnir's stables widget]
  class TL,SL,WT,RD,WR,WID built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  S[Sleipnir] --> W[isolated worktree] --> V[stables widget]
  class S,W,V built
```
