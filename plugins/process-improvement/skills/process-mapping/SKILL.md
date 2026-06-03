---
name: process-mapping
description: "Build the current-state process map: SIPOC, swimlane/flowchart, and value-stream map. Mark value-add vs. non-value-add steps and handoffs. Identify where to instrument and measure. Used in the DMAIC Measure phase before root-cause analysis begins."
---

# Skill: process-mapping

> **Invoked by:** `process-improvement/process-analyst` (primary — owns discovery + mapping). Also used by `lean-six-sigma-blackbelt` when a quick current-state sketch is needed before routing to the analyst.
>
> **When to invoke:** Measure phase of a DMAIC after the charter is signed; any time the team disagrees about "how the process actually works" (vs. how it is supposed to work); before a waste walk or lean event; before placing measurement points.
>
> **Output:** a current-state map (SIPOC + swimlane or VSM as appropriate), a value-add / non-value-add annotation, and a list of handoff points + recommended measurement locations.

## Why map before you measure

You cannot place a measurement at the right step if you don't know where the steps are. You cannot find waste if you don't know what the process does. The map is not the goal — it is the prerequisite.

Two failure modes to avoid:

1. **Mapping the ideal process** (the org-chart version that management wishes existed). The useful map is what the people actually do today — every workaround, every rework loop, every "we email it to Finance manually on Fridays."
2. **Over-mapping** — 80-step Visio diagrams no one reads. Keep maps at the level of granularity that serves the question. SIPOC is enough for scoping. A swimlane works for most Measure phases. A full VSM is needed when takt / cycle-time / inventory analysis is the goal.

## Map selection guide

| Map type | Use when | Granularity |
|---|---|---|
| **SIPOC** | Scoping (Define phase); setting boundaries; all stakeholders need a one-pager | High — 5–7 process steps |
| **Swimlane / flowchart** | Understanding which team / role does what; finding handoffs and rework loops | Medium — 10–30 steps |
| **Value-stream map (VSM)** | Lean event — quantifying flow time, inventory, push vs. pull; takt analysis | Medium + time data — cycle time, queue time, %C&A per step |

## Step-by-step

### Step 1 — Agree on scope before starting

Confirm from the charter:
- **Start step** — the trigger event that begins the process (e.g., "customer submits a support ticket")
- **End step** — the completion event that ends it (e.g., "ticket marked resolved and customer confirms")
- **Customer** — who receives the process output and defines "done"

Do not start mapping before the start and end steps are agreed. Scope drift during mapping is the most common mapping failure.

### Step 2 — Build the SIPOC first

Always. Even if a swimlane is the primary deliverable. The SIPOC forces the team to name the customer and the output before drawing steps.

Use the `sipoc.md` template. Five columns:

| S — Suppliers | I — Inputs | P — Process (5–7 steps) | O — Outputs | C — Customers |
|---|---|---|---|---|
| Who provides inputs | What enters the process | Major steps | What is produced | Who receives the output |

The CTQ (Critical-to-Quality) note: ask "what does the customer in column C care about most?" That becomes the CTQ to carry into measurement.

### Step 3 — Walk the process with the people who do it

Rules for a process-discovery walk:

- Talk to the **people who do the work** — not their manager, not the documented procedure. The manager often describes the intended process; the worker describes the actual one.
- Use **"walk me through the last time you did this"** — specific past instances surface workarounds; "what do you normally do" surfaces the ideal.
- Ask: **"What happens when it goes wrong?"** — the rework loop is usually the biggest source of cycle-time waste.
- Look for: **wait time** (work sitting, not moving), **rework loops** (yes/no forks that loop back), **handoffs** (the step changes hands), **manual steps** (a human doing something that could be tracked automatically).

### Step 4 — Draw the swimlane

Rows = roles or teams (not people — roles). Columns = time sequence.

Symbols to use consistently:

| Symbol | Meaning |
|---|---|
| Rectangle | Activity / task |
| Diamond | Decision point |
| Arrow | Flow |
| Curved arrow | Rework loop |
| D-shape / triangle | Queue / wait / inventory |
| Lightning bolt or star | Known pain point |

Mark every **handoff** (step crosses a swimlane boundary) — these are where defects hide and where cycle time accumulates while work waits to be picked up.

### Step 5 — Annotate value-add vs. non-value-add

For every step, apply the three-way test:

| Category | Test | Example |
|---|---|---|
| **Value-add (VA)** | Transforms the product/service toward the customer's CTQ; the customer would pay for it if asked | "Review claims for medical necessity" in a claims process |
| **Business non-value-add (BNVA)** | Does not transform toward the CTQ but is required by regulation, audit, or control | "Supervisor approval for expenditures > $500" |
| **Non-value-add (NVA) — waste** | Neither transforms nor is required; pure waste to eliminate | "Re-enter data from email into the ticketing system" |

Color-code or annotate every step. NVA steps are the primary targets for the Improve phase. BNVA steps are candidates for challenge or simplification, not elimination. VA steps get variation-reduced and stabilized.

### Step 6 — Build a value-stream map (when takt analysis is needed)

Add to each step:
- **Cycle time (CT)** — time to complete the step once work arrives (not including wait)
- **Lead time (LT)** or queue time — time work waits between steps
- **%Complete and Accurate (%C&A)** — percentage of work that arrives ready to process without rework

Rolled throughput yield (RTY) = product of all step %C&A values. A process with 10 steps each at 95% %C&A has an RTY of 0.95¹⁰ = 59%.

**Takt time** = available working time ÷ customer demand rate. If a step's cycle time exceeds takt time, it is a bottleneck.

**Process efficiency** = total VA time ÷ total lead time. An efficiency of 5% (common in office processes) means 95% of elapsed time is wait/NVA.

### Step 7 — Identify measurement locations

Mark every location on the map where a measurement will be placed in the Measure phase:

- The **output CTQ measurement point** — where the charter's primary metric is recorded (e.g., "timestamp when ticket is resolved" for a cycle-time CTQ)
- **Defect detection points** — where defects are identified (not just where they are fixed)
- **Queue measurement points** — where work accumulates waiting (used in takt / throughput analysis)

If the measurement point doesn't exist yet (no system captures the timestamp), flag it: instrumenting the process is a data-platform task — route to `data-platform` for the ELT + tracking infrastructure.

## Map quality checklist

Before closing the Measure-phase map:

- [ ] Start and end steps match the charter's SIPOC boundary exactly
- [ ] Every step was validated with someone who actually does the work, not just documented from the SOP
- [ ] Every handoff is visible (step crosses a swimlane boundary)
- [ ] Every rework loop is drawn, not assumed away
- [ ] VA / BNVA / NVA annotation on every step
- [ ] At least one NVA category (waste) identified per swimlane
- [ ] CTQ measurement location marked on the map
- [ ] VSM cycle times added if takt / throughput analysis is in scope
- [ ] Map version-dated and owner listed

## Anti-patterns this skill flags

- **Drawing the org-chart, not the process** — swimlanes labeled by department seniority, not by role in the process
- **Steps with no verb** — "Accounting" is not a step; "Accounting team reviews invoice for GL coding" is
- **Map that skips rework loops** — every "it depends" in the process is a decision diamond, not a missing step
- **Starting the VSM without asking who does the work** — floor/desk observation beats procedure manuals
- **Annotating every step as "value-add"** — some steps are always NVA; if the map has zero NVA, it wasn't done honestly
- **Measurement point placed at the wrong step** — "resolved" timestamp at IT's close, not at customer confirmation, over-counts performance

## See also

- Skill: [`../dmaic-project-charter/SKILL.md`](../dmaic-project-charter/SKILL.md) — produces the scope (start/end step) this skill maps
- Skill: [`../root-cause-analysis/SKILL.md`](../root-cause-analysis/SKILL.md) — Analyze phase; the map identifies *where* to investigate
- Skill: [`../lean-waste-analysis/SKILL.md`](../lean-waste-analysis/SKILL.md) — uses the VA/NVA annotation to quantify and prioritize waste
- Template: [`../../templates/sipoc.md`](../../templates/sipoc.md) — Step 2 artifact
- Best-practice: [`../../best-practices/measure-the-baseline-before-you-change-anything.md`](../../best-practices/measure-the-baseline-before-you-change-anything.md)

---

_Last reviewed: 2026-06-03 by `claude`_
