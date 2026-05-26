---
id: decision-trees
title: "Decision trees in knowledge files"
category: "Orientation & capability"
kind: ravenclaude-built
order: 44
summary: "Knowledge files carry Mermaid decision trees the agent traverses BEFORE picking a method — preventing wrong-branch-from-the-start, with a mandatory staleness date."
see_also: [environment-context]
last_verified: 2026-05-26
refresh_when: "The decision-tree convention or its last-verified staleness discipline changes."
sources:
  - label: "Decision trees in knowledge files"
    url: "docs/best-practices/decision-trees-in-knowledge-files.md"
  - label: "ravenclaude-core constitution"
    url: "plugins/ravenclaude-core/CLAUDE.md"
---

When a knowledge file contains a `## Decision Tree: <Domain>` section, the agent must **traverse the Mermaid graph top-to-bottom before selecting a method** — resolving each condition node against the user's actual context (not keyword-matching the request), defaulting to the **leaf with the smaller blast radius**, and escalating to a higher-blast leaf only after the smaller one demonstrably fails.

This closes the **wrong-branch-from-the-start** failure mode (the agent picks the wrong method on the first try because the branches weren't visible). It composes with alternate-methods enumeration (which handles "method failed, try the next") and the environment-context check (which handles "I'm already authorized"). Every diagram-bearing knowledge file carries a mandatory **`last-verified` date**, and the Researcher's sweep flags any tree older than 90 days — the same discipline these Learn concepts follow.

```mermaid
flowchart TD
  SIT[Situation matches a tree's entry] --> TRAV[Traverse the graph top-to-bottom]
  TRAV --> RES[Resolve each node against real context]
  RES --> LEAF[Default to the smaller-blast leaf]
  LEAF --> TRY[Try it]
  TRY -- works --> DONE[Done]
  TRY -- fails --> ESC[Escalate to higher-blast leaf]
  class SIT,TRAV,RES,LEAF,TRY,ESC,DONE built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  S[Situation] --> T[traverse tree]
  T --> L[smaller-blast leaf first]
  class T,L built
```
