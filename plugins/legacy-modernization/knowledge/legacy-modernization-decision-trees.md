# Legacy Modernization — Decision Trees

_Decision trees for choosing a modernization strategy and a cutover approach. Traverse the relevant tree top-to-bottom before recommending — the proactive complement to the Capability Grounding Protocol. Last reviewed: 2026-06-19._

## Decision Tree: Which of the 6 R's?

Most estates are a *portfolio* of R's, decided capability by capability. No driver → retain.

```mermaid
graph TD
  A[A legacy capability] --> B{Is there a named driver to change it now?}
  B -- No --> C[RETAIN - do nothing, on purpose; revisit when a driver appears]
  B -- Yes --> D{Is the business value of this capability still real?}
  D -- No --> E[REPLACE - retire it, or repurchase a SaaS/COTS equivalent]
  D -- Yes --> F{Is the problem only where it runs cost/EOL infra/ops?}
  F -- Yes, infra only --> G{Needs reshaping to fit the new platform?}
  G -- No --> H[REHOST - lift and shift]
  G -- Yes, minor --> I[REPLATFORM - lift and reshape e.g. managed DB/containers]
  F -- No, the code/design is the problem --> J{Is the architecture fundamentally wrong for the need?}
  J -- No, code quality/upgrade only --> K[REFACTOR - improve in place behind tests]
  J -- Yes, structural --> L[REARCHITECT - restructure significantly, usually via strangler fig]
```

_Name the trade: each R up the chain (rehost -> replatform -> refactor -> rearchitect -> replace) buys more improvement and pays more risk + cost. Pick the lowest R that clears the driver._

## Decision Tree: Rewrite from scratch, or modernize incrementally?

Rewrite-from-scratch is the default *wrong* answer — it must earn its risk (§2 #2).

```mermaid
graph TD
  A[Pressure to replace the system] --> B{Can the old system keep running while you change it?}
  B -- Yes --> C{Can you carve it into capabilities with seams?}
  C -- Yes --> D[INCREMENTAL - strangler fig / branch-by-abstraction]
  C -- No, seams unclear --> E[Get codebase-archaeologist to find seams FIRST, then incremental]
  B -- No, platform is truly dead/unbuildable --> F{Is the domain well understood and small?}
  F -- No --> G[STILL incremental where possible; a blind rewrite repeats the same bugs]
  F -- Yes, small + understood + old tech unsupportable --> H[Rewrite is defensible - keep characterization tests as the spec]
```

_The embedded edge-case knowledge in a working legacy system is its most valuable and least documented asset; a from-scratch rewrite discards it and ships nothing until the end._

## Decision Tree: Which cutover strategy?

```mermaid
graph TD
  A[Ready to switch a capability to the new implementation] --> B{Can traffic be split incrementally?}
  B -- Yes --> C{Stateful data behind it?}
  C -- No --> D[CANARY - shift a % of traffic, watch SLOs, ramp]
  C -- Yes --> E[PARALLEL-RUN - dual-write + shadow reads, reconcile, then ramp]
  B -- No, all-or-nothing switch --> F{Is a tested rollback available?}
  F -- No --> G[STOP - do not cut over; build + rehearse the rollback first]
  F -- Yes --> H[BIG-BANG with go/no-go gates + rehearsed rollback - last resort]
```

_Prefer parallel-run/canary; big-bang is the fallback only when traffic genuinely can't be split, and never without a rehearsed rollback (§2 #6)._
