---
id: decision-review
title: "Decision-review tribunal"
category: "Security"
kind: ravenclaude-built
order: 36
summary: "A sibling tribunal votes yes/no/defer on yes-or-no DECISIONS before they reach you — binding only if you opt in, and high-blast calls always defer."
see_also: [command-review-tribunal, model-diversity]
node_links:
  PANEL: command-review-tribunal
last_verified: 2026-05-26
refresh_when: "The decision-review modes, the defer rules, or the high-blast carve-out change."
sources:
  - label: "Post-PR decision review"
    url: "docs/post-pr-decision-review.md"
  - label: "ravenclaude-core constitution"
    url: "plugins/ravenclaude-core/CLAUDE.md"
---

The command-review tribunal adjudicates *shell commands*; the **decision-review** tribunal adjudicates *yes/no decisions* — the kind an agent would otherwise interrupt you with. The `decision-review` skill convenes the same seats on a yes/no question (engine: `thing-decide.py`) and returns **`yes` / `no` / `defer`**. A binding yes/no is acted on without pausing you; a `defer` asks you. The panel defers genuine preferences, low-confidence or split calls, and anything high-blast.

Two guardrails: **high-blast / irreversible decisions never auto-resolve** — force-push, deletes, prod actions, the `security_deny` family always `defer` to you, regardless of mode. And the mode knob `decision_review: off | advisory | binding` is **off by default**, so nothing is auto-decided unless you opt in. (The seats run via `claude -p`; without it the panel abstains and fails safe to `defer`.) After each PR, a retrospective routes the PR's decisions through the same panel and logs the verdicts.

```mermaid
flowchart TD
  Q[A yes/no decision] --> HB{high-blast /<br/>irreversible?}
  HB -- yes --> DEFER[defer · always ask you]
  HB -- no --> MODE{decision_review mode}
  MODE -- "off (default)" --> ASK[ask you]
  MODE -- "binding" --> PANEL[convene seats · thing-decide.py]
  PANEL --> V{yes / no / defer}
  V -- yes/no --> ACT[act without pausing you]
  V -- defer --> DEFER
  class Q,HB,MODE fact
  class DEFER,ASK,PANEL,V,ACT built
```

<!-- step: A yes/no decision the agent would otherwise interrupt you with. -->
```mermaid-step
flowchart LR
  N1[Yes or no] --> N2[High blast defers] --> N3[Mode gate] --> N4[Panel votes] --> N5[Act or defer]
  class N1 built
```

<!-- step: High-blast or irreversible? It always defers to you (force-push, deletes, prod). -->
```mermaid-step
flowchart LR
  N1[Yes or no] --> N2[High blast defers] --> N3[Mode gate] --> N4[Panel votes] --> N5[Act or defer]
  class N2 built
```

<!-- step: Mode off (default) asks you; mode binding convenes the seats (thing-decide.py). -->
```mermaid-step
flowchart LR
  N1[Yes or no] --> N2[High blast defers] --> N3[Mode gate] --> N4[Panel votes] --> N5[Act or defer]
  class N3 built
```

<!-- step: The panel returns yes / no / defer. -->
```mermaid-step
flowchart LR
  N1[Yes or no] --> N2[High blast defers] --> N3[Mode gate] --> N4[Panel votes] --> N5[Act or defer]
  class N4 built
```

<!-- step: yes/no acts without pausing you; defer asks you. -->
```mermaid-step
flowchart LR
  N1[Yes or no] --> N2[High blast defers] --> N3[Mode gate] --> N4[Panel votes] --> N5[Act or defer]
  class N5 built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  Q[yes/no decision] --> P[panel]
  P --> V[yes / no / defer]
  class P,V built
```
