---
id: model-diversity
title: "Model diversity on the panel"
category: "Security"
kind: ravenclaude-built
order: 34
summary: "When ≥2 reviewer seats convene, the tribunal guarantees ≥2 distinct model backbones run — so one model's blind spot can't pass the whole panel."
see_also: [command-review-tribunal]
last_verified: 2026-05-26
refresh_when: "The model-diversity guarantee or its auto-reassignment behavior changes."
sources:
  - label: "ravenclaude-core constitution"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "Tribunal assessment & improvement plan"
    url: "docs/tribunal-assessment-and-improvement-plan.md"
---

A panel of reviewers is only as strong as its diversity. If every seat runs on the same model, a single model's blind spot — a shared hallucination or a class of injection it doesn't catch — can pass the **whole** panel unnoticed. That's the **anti-correlated-hallucination** failure mode.

So the engine enforces a **model-diversity rule**: whenever **two or more seats convene, at least two distinct model backbones run**. If a `panel:` config override happens to collapse the seats onto one model, the engine **auto-reassigns one seat to a different, equal-or-stronger model** rather than letting a monoculture review the command. It's proven by Gate 22.

```mermaid
flowchart TD
  P{≥2 seats convened?} -- no --> ONE[Single seat · its own model]
  P -- yes --> CHK{≥2 distinct models?}
  CHK -- yes --> OK[Panel runs as configured]
  CHK -- no --> RE[Auto-reassign one seat to a<br/>different equal-or-stronger model]
  RE --> OK
  class P,CHK fact
  class ONE,OK,RE built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  S[≥2 seats] --> D{≥2 models?}
  D -- no --> R[reassign one]
  D -- yes --> OK[run]
  class R,OK built
```
