---
id: command-review-tribunal
title: "Command-review tribunal (the Thing)"
category: "Security"
kind: ravenclaude-built
order: 30
summary: "An opt-in panel of reviewer seats that votes ALLOW/EDIT/DENY on shell commands instead of interrupting you."
see_also: [comfort-posture, permission-layers, hook-lifecycle]
try_it:
  label: "Run a command through it in Test a command"
  href: "#/simulator"
last_verified: 2026-05-26
refresh_when: "The tribunal's tier model, seat roster, or gate_floor semantics change."
sources:
  - label: "thing skill (operating reference)"
    url: "plugins/ravenclaude-core/skills/thing/SKILL.md"
  - label: "Tribunal design"
    url: "docs/tribunal-review-feature-design.md"
---

**Command review** — codename *the Thing* — is an opt-in panel of reviewer agents that adjudicates shell commands instead of stopping to ask you. It sits **on top of** comfort-posture: posture sets the policy (allow/ask/deny per category); the tribunal is the adjudicator you switch on for a category so a verdict lands in seconds.

Routing is **tiered**. Every command resolves to `low → medium → high → extreme` (its category base tier, bumped by a deterministic high/critical concern). A clean `low` read runs **no panel at all** (zero cost); seat count and the confidence bar escalate with the tier. Up to three seats run in parallel — **Forseti** (security), **Mímir** (code), **Heimdall** (injection) — with **Thor** (architect) convened only on a split.

The **`gate_floor`** knob (default `high`) is the lowest tier whose *confident ALLOW* is surfaced to you as an `ask`. DENY still blocks and EDIT still rewrites autonomously, so the tribunal pre-filters the dangerous and the fixable before either reaches you. Two hard overrides ignore the knob: **reads are never surfaced**, and **irreversible high-blast allows always are**. An abstaining panel always fails **closed**. It can never relax the `security_deny` floor.

```mermaid
flowchart TD
  A[Bash PreToolUse] --> B{category toggled on?}
  B -- no --> Z[normal flow]
  B -- yes --> C[classify: category · tier · routing]
  C -- unarguable critical --> DENY[DENY · no LLM]
  C -- clean low read --> ALLOW[allow · no panel]
  C -- tier ≥ medium --> E[convene seats in parallel]
  E -- split / low confidence --> T[convene Thor]
  T --> AGG[aggregate]
  E --> AGG
  AGG -- deny / critical --> DENY
  AGG -- edit safe --> EDIT[allow + rewrite]
  AGG -- allow --> GATE{tier ≥ gate_floor<br/>or high-blast?}
  GATE -- yes --> ASK[ask · you confirm]
  GATE -- no --> ALLOW
  DENY & ALLOW & EDIT & ASK --> L[(Sága log)]
  class DENY,ALLOW,EDIT,ASK,E,T built
  class GATE fact
```

<!-- mini -->
```mermaid-mini
flowchart LR
  C[Command] --> P[Panel<br/>1–3 seats]
  P --> V{Verdict}
  V --> A[allow / edit / deny / ask]
  class P,A built
```
