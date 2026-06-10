---
id: nidhoggr
title: "Níðhöggr — debt watch"
category: "Observability"
kind: ravenclaude-built
order: 44
summary: "A low-noise maintenance card inside the Heimdall tab: stale plugins, uncovered hooks, superseded decisions, and TODO/FIXME in commit subjects — the slow debt that never trips an alarm."
see_also: [heimdall, event-substrate, vidarr, norns, audit-gates]
last_verified: 2026-06-08
refresh_when: "Níðhöggr's four debt signals, its served reader, or its promote-to-tab threshold change."
sources:
  - label: "ravenclaude-core constitution — Níðhöggr 'Debt watch'"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "generate-dashboards.py (the Níðhöggr card + reader)"
    url: "scripts/generate-dashboards.py"
---

**Níðhöggr** is the dragon gnawing at the roots of the world-tree — and the "Debt watch" card surfaces exactly that: the slow, quiet decay that no perimeter alarm ever catches. It lives as a **card inside the Heimdall tab** (not its own tab), and it carries both labels: "Debt watch" primary, "Níðhöggr" parenthetical.

Four low-noise signals. **Stale plugins** — any plugin not version-bumped in 120+ days. **Uncovered hooks** — hooks referenced by neither a CI workflow nor the gate-audit harness; cross-checking *both* is what cuts the false positives down to the genuinely undercovered set. **Superseded decisions** — decision-log entries marked as superseded (none today). And **TODO/FIXME in commit subjects** — debt the team literally wrote into the history.

It reads **live** through a served endpoint rather than inlining at build time, because two of its signals are git-derived (commit dates, log history) and vary by clone depth — which would otherwise break the exact-match dashboard freshness gate, the same trap Norns navigates. Every source is guarded so a git failure yields an empty signal, never an error. It is a small card today; the plan is to promote it to a full tab only if the marketplace grows past roughly five plugins or the debt signals exceed about twenty entries.

```mermaid
flowchart TD
  A[stale plugins] --> N[Níðhöggr reader]
  B[uncovered hooks] --> N
  C[superseded decisions] --> D[Debt watch card]
  E[TODO/FIXME commits] --> N
  N --> D
  class N,D built
  class A,B,C,E fact
```
