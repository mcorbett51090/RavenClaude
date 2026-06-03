---
name: lean-waste-analysis
description: "Find and remove waste using the 8 wastes (DOWNTIME), value-add analysis, takt/cycle time comparison, bottleneck/constraint identification, and quick-win prioritization. Feeds the DMAIC Improve phase with a ranked elimination roadmap."
---

# Skill: lean-waste-analysis

> **Invoked by:** `process-improvement/lean-six-sigma-blackbelt` (primary — owns the Improve-phase waste-elimination roadmap). Also used by `process-analyst` during current-state mapping when the team wants to classify waste before the formal Analyze phase.
>
> **When to invoke:** after a current-state value-stream map or swimlane exists; when the primary complaint is speed or cost (not variation/defects — that routes to `process-capability-and-spc`); Kaizen / rapid-improvement events; lean transformation kickoffs.
>
> **Output:** a classified waste inventory (8 wastes × process steps), a takt / cycle-time comparison identifying the bottleneck, a value-add ratio, and a prioritized quick-win list with effort/impact estimates.

## Lean vs. Six Sigma — pick the right tool

| Primary symptom | Lean or Six Sigma? |
|---|---|
| Process is **slow** — too much wait time, too many hand-offs | Lean — remove waste and flow-blockers |
| Process is **variable / unpredictable** — results are inconsistent | Six Sigma — reduce variation (SPC + root-cause analysis) |
| Process is **both slow and inconsistent** | Both — lean first for quick wins, Six Sigma to stabilize what remains |

This skill addresses the Lean side. Use `process-capability-and-spc` and `root-cause-analysis` for the Six Sigma side.

## The 8 wastes — DOWNTIME

The DOWNTIME mnemonic covers all eight waste categories:

| Letter | Waste | Definition | Office / operational example |
|---|---|---|---|
| **D** | Defects | Output that fails to meet CTQ; requires rework or causes downstream failure | Invoice with wrong GL code; hire paperwork missing I-9; deployment that fails smoke test |
| **O** | Overproduction | Doing more than the next step needs, sooner than it needs it | Generating 50 monthly reports when only 5 are read; sending all applicants to phone screen before résumé review |
| **W** | Waiting | Work paused waiting for input, approval, information, or capacity | Support ticket waiting for Tier-2 availability; deployment queued for release window approval |
| **N** | Not utilizing talent | Skills, knowledge, or experience not used in the process | Senior engineer manually provisioning environments when automation exists; analyst re-typing data available via API |
| **T** | Transportation | Moving work, information, or material unnecessarily | Emailing attachments between systems that could integrate directly; physical documents shipped for signatures |
| **I** | Inventory | Work-in-process accumulating in queues between steps | 200 unreviewed claims; 40 onboarding packets awaiting manager signature; sprint backlog of 6 months of work |
| **M** | Motion | People searching for information, navigating between systems, or physically moving to perform a task | Switching between 4 tools to resolve one ticket; walking to a printer to collect a document to scan back in |
| **E** | Excess processing | Doing more work than the customer requires or than the process needs | Generating a 30-page audit report for a 2-page deliverable; running a multi-level approval for a $50 purchase |

## Step-by-step

### Step 1 — Set up the waste walk

A **waste walk** (Gemba walk) is an observation of the process as it actually runs. Prerequisites:

1. The current-state map exists (from `process-mapping` skill).
2. The team has access to at least one person who performs each step.
3. The observation is **watching and asking**, not auditing or criticizing.

The waste walk question for each step: "Is there anything in this step that does not directly move the output closer to meeting the customer's CTQ?"

### Step 2 — Classify waste by step

For each step on the current-state map, fill in the waste inventory table:

| Process step | Waste type (DOWNTIME) | Description of the waste | Estimated impact |
|---|---|---|---|
| Receive hiring requisition | Waiting, Defects | Requisition often missing salary band; avg 3-day rework loop to get it | 3 days added to cycle time in 60% of cases |
| Route to recruiter | Motion | Recruiter manually checks shared inbox every 2 hours; no automated assignment | Avg 4-hour delay before recruiter sees it |
| ... | ... | ... | ... |

**Estimated impact** can be qualitative (H/M/L) if time data is unavailable, or quantitative (days, %, FTE-hours) if data exists.

### Step 3 — Value-add ratio

From the current-state map's VA / BNVA / NVA annotation (see `process-mapping` skill):

```
Process efficiency = sum of VA step cycle times / total lead time (end-to-end)
```

A 5–10% process efficiency is common in office processes — 90–95% of elapsed time is non-value-add. This number is visceral and compelling for sponsors.

If cycle times are not yet measured, flag it: the VSM data-collection step (from `process-mapping`) is needed before computing efficiency.

### Step 4 — Takt time and bottleneck identification

**Takt time** = available working time ÷ customer demand rate.

Example — deployment pipeline: 8 hours/day available; customer (engineering team) demands 6 production deploys/day.
```
Takt = 8 hours / 6 deploys = 1.33 hours per deploy
```

Compare each step's cycle time to takt:

| Step | Cycle time | vs. Takt | Status |
|---|---|---|---|
| Code review | 45 min | < 1.33h | OK |
| Integration test | 55 min | < 1.33h | OK |
| Security scan | 1.50 h | > 1.33h | **Bottleneck** |
| Staging deploy | 20 min | < 1.33h | OK |

**The constraint (bottleneck)** is the step whose cycle time exceeds takt — or, when no step exceeds takt, the step with the highest cycle time relative to takt.

**Theory of Constraints corollary:** improving a non-bottleneck step does not increase throughput. Work on the bottleneck first.

### Step 5 — Prioritize waste by effort / impact

Not all waste is equally worth removing. Score each waste item on:

| Dimension | Rating |
|---|---|
| **Impact** — how much cycle time, cost, or defect rate does removing this waste save? | H / M / L |
| **Effort** — how hard is it to remove? (policy change, system change, behavior change) | H / M / L |

Priority matrix:

| | High impact | Low impact |
|---|---|---|
| **Low effort** | Quick wins — do immediately | Nice-to-have — do if time allows |
| **High effort** | Projects — plan and resource | Avoid — not worth it |

**Quick wins** (low effort, high impact) are the first wave of the Improve phase. They build momentum, demonstrate progress to the sponsor, and free up capacity for larger changes.

### Step 6 — Build the waste-elimination roadmap

Produce a prioritized list for the Improve phase:

| Priority | Waste item | Waste type | Proposed countermeasure | Effort | Estimated impact | Owner |
|---|---|---|---|---|---|---|
| 1 | Requisition missing salary band → rework loop | Defects | Add salary band as required field in HRIS requisition form | Low | Eliminate 3-day rework in 60% of cases | HRIS admin |
| 2 | Manual inbox check every 2 hours | Motion/Waiting | Auto-assign requisitions to recruiter via workflow rule | Low | Reduce avg handoff delay from 4h to < 15 min | Recruiting ops |
| 3 | 30-page audit report for 2-page need | Excess processing | Redesign report template to 2-page executive summary | Medium | 4 FTE-hours per close period | Finance |
| ... | ... | ... | ... | ... | ... | ... |

**Do not propose a countermeasure without confirming it addresses a proven cause.** For high-effort countermeasures, route to `root-cause-analysis` to confirm the waste source before committing resources.

## Lean waste analysis checklist

- [ ] All 8 DOWNTIME categories reviewed for every step (not just the obvious ones)
- [ ] Waste walk conducted with frontline workers, not from documentation alone
- [ ] Process efficiency (VA ratio) calculated or estimated
- [ ] Takt time calculated; bottleneck step identified
- [ ] Waste inventory table complete with estimated impact
- [ ] Quick wins (low effort / high impact) identified and separated from project-level changes
- [ ] Countermeasures confirmed against stated waste causes (not guessed)
- [ ] Roadmap has named owners for each item
- [ ] "Not utilizing talent" category checked — automation / skill-allocation waste is consistently under-identified

## Anti-patterns this skill flags

- **Skipping the waste walk** and filling in the waste table from a meeting room — the actual waste is always different from the perceived waste
- **Treating all waste as equal** — not prioritizing by effort/impact; the team spends effort on low-impact items
- **Working on a non-bottleneck step** — improving anything other than the constraint does not increase throughput
- **Eliminating BNVA waste** (required controls, audit steps) without authority and risk review — some steps that look like waste are legally required
- **Proposing "buy a new tool"** as a countermeasure without analyzing whether the current tool is misconfigured or misused — technology is rarely the root cause of waste
- **Confusing wait time with value-add time** — a step where work sits in a queue is Waiting waste, not VA time, even if the queue is in a "work management system"
- **Not-utilizing-talent waste consistently missed** — the most senior people doing the most automatable work is the highest-leverage waste in most knowledge-work processes

## See also

- Skill: [`../process-mapping/SKILL.md`](../process-mapping/SKILL.md) — provides the current-state map and VA/NVA annotation this skill builds on
- Skill: [`../root-cause-analysis/SKILL.md`](../root-cause-analysis/SKILL.md) — validate the root of high-effort waste items before committing resources
- Skill: [`../control-plan-and-sustain/SKILL.md`](../control-plan-and-sustain/SKILL.md) — sustain quick wins with standard work and poka-yoke
- Template: [`../../templates/sipoc.md`](../../templates/sipoc.md) — the SIPOC that provides the process boundary for the waste walk
- Knowledge: [`../../knowledge/dmaic-and-lean-toolkit.md`](../../knowledge/dmaic-and-lean-toolkit.md) — the full Lean overlay (8 wastes, value-stream mapping, takt analysis)

---

_Last reviewed: 2026-06-03 by `claude`_
