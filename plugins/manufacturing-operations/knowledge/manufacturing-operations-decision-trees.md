# Manufacturing Operations — Decision Trees

_Decision trees + a dated method/standard map. Map rows are `[verify-at-build]` — re-check against the current standard/source before quoting. Last reviewed: 2026-06-08._

Traverse before committing a schedule, declaring a bottleneck, or reacting to a control-chart point.

## Decision Tree: Is this production plan buildable (plan to the constraint)?

A schedule that ignores finite capacity or material is a wish, not a plan.

```mermaid
graph TD
  A[Demand / forecast to schedule] --> B{Reconciled against supply/capacity in S&OP?}
  B -- No --> C[Reconcile first - an unreconciled forecast is a future stockout or WIP pile]
  B -- Yes --> D{Does the load exceed the bottleneck's finite rate?}
  D -- Yes --> E[Infeasible - level/push dates, add capacity, or re-lot; do NOT plan to infinite capacity]
  D -- No --> F{Is material available per a BOM that matches as-built?}
  F -- No, BOM drifted --> G[Fix the BOM first - phantom shortages and wrong material plans follow a drifted bill]
  F -- No, real shortage --> H[Route the lead-time/sourcing gap to procurement-sourcing; re-time the MPS]
  F -- Yes --> I[Release the constraint-respecting MPS - assumptions/lot-rules stated]
```

_The bottleneck sets the plant's rate (Theory of Constraints). Plan the schedule around the constraint and material availability, never to infinite capacity._

## Decision Tree: Where is the constraint, and is it worth optimizing?

Optimizing a non-bottleneck makes WIP, not throughput.

```mermaid
graph TD
  A[Line is slow / throughput below target] --> B{Is OEE defined - stated ideal cycle time + planned/unplanned split?}
  B -- No --> C[Define the denominators first - an undefined OEE number is theater]
  B -- Yes --> D{Where does WIP pile up / what starves downstream?}
  D -- Identified resource --> E{Is THAT the binding constraint for the whole line?}
  E -- No --> F[Stop - optimizing a non-bottleneck won't move plant throughput]
  E -- Yes --> G{Can you EXPLOIT it without spend - reduce its losses, stop starving it?}
  G -- Yes --> H[Exploit + subordinate the rest to the constraint; re-measure]
  G -- No, needs rework --> I[ELEVATE: route SMED/kaizen to process-improvement; re-plan rate with production-planner]
```

_Identify → exploit → subordinate → elevate the constraint. An hour at the bottleneck is plant throughput; an hour elsewhere is a mirage._

## Decision Tree: Is this control-chart signal special or common cause?

Tampering with common-cause noise adds variation; ignoring a special cause ships defects.

```mermaid
graph TD
  A[Control-chart point of concern] --> B{Are control limits from the PROCESS, not the spec?}
  B -- No --> C[Re-derive limits from the process - spec limits are the customer's voice, not the chart's]
  B -- Yes --> D{Does a run rule trip - point beyond 3-sigma, runs, trends, zone rules?}
  D -- No --> E[Common cause - do NOT adjust; tampering with a stable process adds variation]
  D -- Yes --> F{Assignable special cause found at the time of the signal?}
  F -- Yes --> G[Act on the special cause; containment if product affected; open NCR -> CAPA]
  F -- No --> H[Investigate before reacting; if recurring, escalate to a CAPA on the system]
```

_Control limits come from the voice of the process; specs from the voice of the customer. The first SPC question is always special vs common cause._

## Decision Tree: How do I size this lot (setup vs holding, and is it the constraint)?

A lot size is a trade, not a habit — and the trade changes on the bottleneck.

```mermaid
graph TD
  A[Planned order to lot-size] --> B{Is the resource the binding constraint?}
  B -- Yes --> C{Is each setup lost throughput you can't recover?}
  C -- Yes --> D[Favor larger lots / lot-for-period - protect constraint time; route SMED to process-improvement to make small lots economic]
  C -- No --> E[Treat like a non-constraint - balance on cost only]
  B -- No --> F{Demand steady enough for an EOQ basis?}
  F -- Yes --> G[EOQ - balance setup/order cost vs holding cost; state both cost inputs]
  F -- No, lumpy/bucketed --> H{Holding cost the dominant concern?}
  H -- Yes --> I[Lot-for-lot - minimize inventory, accept the setups]
  H -- No --> J[Fixed-period - batch the bucket's demand; state the period]
```

_State the lot rule and its cost basis (setup cost, holding cost, constraint or not). A setup at the bottleneck is throughput you never get back._

## Decision Tree: Where does this nonconformance disposition stop (draft vs human sign-off)?

This plugin drafts; the accountable human signs a regulated or safety-critical disposition.

```mermaid
graph TD
  A[Nonconformance to disposition] --> B{Containment in place - product affected isolated?}
  B -- No --> C[Contain first - stop the bleeding before anything else]
  B -- Yes --> D{Root cause proven, not just asserted?}
  D -- No --> E[Investigate - 5-Whys/fishbone/is-is-not; an asserted cause is a guess with a budget]
  D -- Yes --> F{Preventive action defined + control plan/FMEA updated?}
  F -- No --> G[Not a CAPA yet - add the preventive action and the control change, or it recurs]
  F -- Yes --> H{Safety-critical or regulated record - ISO/IATF/AS9100/FDA?}
  H -- Yes --> I[DRAFT the disposition + escalate to the accountable human; never auto-close]
  H -- No --> J[Close with effectiveness check scheduled; verify before final closure]
```

_Containment ≠ corrective ≠ preventive. On regulated/safety-critical product the agent drafts and escalates — it does not sign._

---

## Method & standard map (2026, `[verify-at-build]`)

| Area | Method / metric | Notes |
|---|---|---|
| Master planning | MPS, MRP (netting through the BOM), S&OP | Plan to finite capacity + material; reconcile demand vs supply `[verify-at-build]` |
| Lot sizing | EOQ, fixed-period, lot-for-lot | Trades setup vs holding cost; on a constraint, setups are lost throughput `[verify-at-build]` |
| Line rate | OEE = Availability × Performance × Quality | Denominators (ideal cycle time, planned downtime) must be stated `[verify-at-build]` |
| Loss model | The six big losses | Breakdowns/setup (A), minor stops/reduced speed (P), scrap/rework (Q) `[verify-at-build]` |
| Flow | Takt time = available time ÷ demand; cycle time | Produce to takt, not max speed; the gap is the signal `[verify-at-build]` |
| Constraint | Theory of Constraints (identify/exploit/subordinate/elevate) | The bottleneck governs plant throughput `[verify-at-build]` |
| Quality control | SPC (X̄-R, I-MR, p/np/c/u), run rules | Control limits from the process; special vs common cause `[verify-at-build]` |
| Capability | Cp / Cpk (and Pp/Ppk) | Meaningless on an unstable process; state sample size + MSA basis `[verify-at-build]` |
| Defect loop | NCR → containment → CAPA → effectiveness check | Corrective (this batch) ≠ preventive (the cause) `[verify-at-build]` |
| Risk | FMEA (S × O × D → RPN / Action Priority) | Must drive a control change, or it's paperwork `[verify-at-build]` |
| Inspection | Inspection plan, AQL sampling, control plan, PPAP | Prevention > detection > scrap; final inspection is the weakest control `[verify-at-build]` |
| Quality systems | ISO 9001, IATF 16949 (automotive), AS9100 (aero) | Regulated dispositions escalate to a human; never auto-close `[verify-at-build]` |

_Theory-of-Constraints reference: identify → exploit → subordinate → elevate → repeat. OEE world-class is often cited near 85% but is context-dependent — state your denominators, don't chase a benchmark. Re-verify any standard clause or metric definition before quoting it to a consumer._
