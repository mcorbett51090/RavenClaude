# Embedded & IoT Engineering Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Battery won't hit its target

```mermaid
flowchart TD
    A[Battery-life miss] --> B{Power budget<br/>built?}
    B -- "No / active-only" --> B1[Build the duty-cycled profile<br/>FIRST — it's the spec, §3 #1]
    B -- "Yes" --> C{Dominant sink?}
    C -- "Sleep floor high" --> C1[Missed/shallow sleep state;<br/>deepen sleep, route firmware, §3 #1 #4]
    C -- "Radio TX burst" --> C2[Chatty radio — cut airtime /<br/>change protocol, §3 #1 #6]
    C -- "Active duty too high" --> C3[Lower wake rate / sampling;<br/>route firmware, §3 #1]
    B1 --> D[Avg current + battery life ·<br/>datasheet dated + measured, §3 #8]
    C1 --> D
    C2 --> D
    C3 --> D
```

## Tree 2 — Will the deadline hold?

```mermaid
flowchart TD
    A[Real-time risk] --> B{Timing from<br/>WCET or average?}
    B -- "Average-case" --> B1[Re-characterize WCET +<br/>ISR latency, §3 #2]
    B -- "Worst-case" --> C{Schedulable under<br/>worst-case load?}
    C -- "No" --> C1[Shed/repartition work or<br/>raise priority, §3 #2]
    C -- "Yes" --> D{Non-determinism<br/>on the path?}
    D -- "Dyn alloc / blocking" --> D1[Remove dynamic alloc +<br/>unbounded blocking, §3 #4]
    D -- "Priority inversion" --> D2[Priority inheritance /<br/>restructure, §3 #4]
    D -- "Deterministic" --> D3[Deadline holds — record margin]
    B1 --> E[Worst-case timing verdict +<br/>at-risk path named]
    C1 --> E
    D1 --> E
    D2 --> E
    D3 --> E
```

## Tree 3 — Which radio fits?

```mermaid
flowchart TD
    A[Pick connectivity] --> B{Range needed?}
    B -- "Wide-area / km" --> C{Data rate?}
    C -- "Low (telemetry)" --> C1[LoRa(WAN) / NB-IoT —<br/>long-range low-power, §3 #6]
    C -- "High (stream)" --> C2[Cellular — high power+cost;<br/>confirm budget, §3 #6]
    B -- "Local / room" --> D{Power budget tight?}
    D -- "Battery, tight" --> D1[BLE — low power, moderate<br/>rate, §3 #6]
    D -- "Mains / high rate" --> D2[Wi-Fi — high rate, high<br/>power, §3 #6]
    C1 --> E[Protocol on power/range/<br/>bandwidth/cost trade · airtime<br/>into power budget, §3 #1 #6]
    C2 --> E
    D1 --> E
    D2 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
