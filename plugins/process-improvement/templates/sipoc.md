# SIPOC — {{Process Name}}

> A SIPOC is the first artifact of every DMAIC project. Build it before any swimlane or value-stream map. It forces the team to agree on the customer, the output, and the boundary before drawing steps.
>
> **Process:** {{name}}
> **Date:** {{YYYY-MM-DD}}
> **DMAIC phase:** Define (or early Measure)
> **Author:** {{...}}

---

## SIPOC table

| Suppliers | Inputs | Process (5–7 steps) | Outputs | Customers |
|---|---|---|---|---|
| {{Who provides the inputs}} | {{What enters the process — data, materials, forms, requests}} | **1.** {{First step — start of scope}} | {{What is produced or delivered}} | {{Who receives the output}} |
| {{...}} | {{...}} | **2.** {{...}} | {{...}} | {{...}} |
| {{...}} | {{...}} | **3.** {{...}} | {{...}} | {{...}} |
| {{...}} | {{...}} | **4.** {{...}} | {{...}} | {{...}} |
| {{...}} | {{...}} | **5.** {{...}} | {{...}} | {{...}} |
| | | **6.** {{optional}} | | |
| | | **7.** {{optional — last step, end of scope}} | | |

> **Five-to-seven process steps only.** A SIPOC is a boundary tool, not a detailed flowchart. If you need more than seven steps, you are mapping, not scoping. Build the swimlane separately using the `process-mapping` skill.

---

## Boundary definitions

| Boundary | Statement |
|---|---|
| **Start step** | {{Trigger event that begins the process — e.g., "Customer submits support ticket"}} |
| **End step** | {{Completion event that ends the process — e.g., "Customer confirms ticket resolved"}} |
| **In scope** | {{What this project / map covers}} |
| **Out of scope** | {{Explicitly excluded — adjacent processes, upstream causes, downstream consequences}} |

---

## Critical-to-Quality (CTQ) note

> The customer in the rightmost column defines what "good" looks like. Capture their most important requirement here — it becomes the primary CTQ for the DMAIC charter.

**Primary customer:** {{internal team / external customer / downstream process / end user}}

**What the customer cares about most (VOC — Voice of the Customer):**

| Customer says (raw) | Translated CTQ (measurable) |
|---|---|
| {{Verbatim complaint, request, or requirement}} | {{Metric: name, direction, target — e.g., "Resolve ticket within 4 hours at the 95th percentile"}} |
| {{...}} | {{...}} |
| {{...}} | {{...}} |

**Primary CTQ carried into the charter:** {{metric name, operational definition, target}}

---

## Supplier / input quality notes

> Surface known input-quality problems here — these often show up as "Materials / Information" causes on the fishbone later.

| Supplier | Input | Known quality issue (if any) |
|---|---|---|
| {{...}} | {{...}} | {{e.g., "Hiring requisitions arrive without salary band in ~60% of cases"}} |
| {{...}} | {{...}} | {{...}} |

---

## Notes

- {{Any context the team agreed on during the SIPOC session that doesn't fit above}}
- {{Assumptions made in defining scope}}
- {{Cross-references to related SIPOCs or processes if this one has known upstream/downstream dependencies}}

---

*Produced by the `process-improvement/skills/dmaic-project-charter` skill (Step 5) or the `process-improvement/skills/process-mapping` skill (Step 2). Feed this into the swimlane or VSM for the full current-state map.*
