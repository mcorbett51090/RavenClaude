---
id: audit-gates
title: "The gate-audit meta-test"
category: "Marketplace engineering"
kind: ravenclaude-built
order: 52
summary: "Every CI gate is itself tested: audit-gates.sh proves each gate FAILS on a known-bad fixture and PASSES on a known-good one — so a gate can't silently rot into a no-op."
see_also: [layout-hook]
last_verified: 2026-05-26
refresh_when: "The gate-audit approach or its skip-is-not-a-pass policy changes."
sources:
  - label: "CI gate audit"
    url: "docs/best-practices/ci-gate-audit.md"
  - label: "AGENTS.md — Testing instructions"
    url: "AGENTS.md"
---

A CI gate that never fails is worse than no gate — it gives false confidence. So RavenClaude runs a **meta-test**: `scripts/audit-gates.sh` proves, for each gate, that it **fails on a known-bad fixture AND passes on a known-good one**. If a gate can't be made to fail on input it's supposed to reject, the gate is broken and the audit says so.

This is required reading before adding or changing any CI step — a new gate ships with its fail/pass fixtures, not just its happy path. And **a skip is not a pass**: when a gate can't run locally (e.g. the actionlint gate needs a Docker daemon), it **loudly** skips ("THIS IS NOT A PASS"), and in CI an unrunnable gate is a hard failure, never a silent skip.

```mermaid
flowchart TD
  G[For each CI gate] --> BAD[Run it on a known-BAD fixture]
  BAD --> FB{does it FAIL?}
  FB -- no --> BROKEN[Gate is broken · audit fails]
  FB -- yes --> GOOD[Run it on a known-GOOD fixture]
  GOOD --> FG{does it PASS?}
  FG -- no --> BROKEN
  FG -- yes --> TRUST[Gate trusted]
  class G,BAD,FB,GOOD,FG built
  class BROKEN built
  class TRUST built
```

<!-- step: For each CI gate... -->
```mermaid-step
flowchart LR
  N1[Each gate] --> N2[Known bad] --> N3[Must fail] --> N4[Known good] --> N5[Trusted]
  class N1 built
```

<!-- step: Run it on a known-BAD fixture. -->
```mermaid-step
flowchart LR
  N1[Each gate] --> N2[Known bad] --> N3[Must fail] --> N4[Known good] --> N5[Trusted]
  class N2 built
```

<!-- step: Does it FAIL? If not, the gate is broken and the audit fails. -->
```mermaid-step
flowchart LR
  N1[Each gate] --> N2[Known bad] --> N3[Must fail] --> N4[Known good] --> N5[Trusted]
  class N3 built
```

<!-- step: Run it on a known-GOOD fixture — does it PASS? -->
```mermaid-step
flowchart LR
  N1[Each gate] --> N2[Known bad] --> N3[Must fail] --> N4[Known good] --> N5[Trusted]
  class N4 built
```

<!-- step: Both hold and the gate is trusted. And a skip is NOT a pass (it skips loudly). -->
```mermaid-step
flowchart LR
  N1[Each gate] --> N2[Known bad] --> N3[Must fail] --> N4[Known good] --> N5[Trusted]
  class N5 built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  B[known-bad] --> F{fails?}
  F -- yes --> P[known-good passes → trusted]
  F -- no --> X[gate broken]
  class P,X built
```
