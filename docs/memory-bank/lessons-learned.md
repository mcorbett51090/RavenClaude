# Lessons Learned

> Running log of trial-and-error findings from work that touches the domains this hub covers. **Newest entries at the top.** Read this file at the start of any task touching a covered domain — the "we already learned this" cycle is what makes the hub valuable.

## Format

Each entry is a dated section. Reverse-chronological order (newest first).

```markdown
## YYYY-MM-DD — Short title naming the rule or finding

**Context:** What we were trying to do. 1–2 sentences.

**What we tried first:** The path that failed. 1–2 sentences.

**Why it failed:** The actual reason, with technical detail. 2–4 sentences.

**What works:** The canonical solution. 2–4 sentences.

**How to apply:** When this rule fires, what to do. 1–2 bullet points.

**Trace:** Origin project, origin session ID if useful. Optional.
```

---

## 2026-05-07 — PMP discipline = weekly cadence + single ownership + same format

**Context:** Building a PMP-grade `project-manager` agent for cross-domain consulting work.

**What we tried first:** An initial draft of a generic *"Tracker"* agent that maintained activity log, task list, and project tracker — useful but vague. No specific cadence, no ownership rules, no format constraints.

**Why it failed (would have failed in practice):** Without specific operational rules, *"tracking"* tools accumulate dust. A tool that's optional gets skipped; a tool that's vague gets gamed. The reason most consultants are *"not good at PM"* isn't laziness — it's that they have tracking artifacts but no enforcement around them.

**What works:** PMI's PMBOK 7 + the leading PM literature converges on three operational rules that make PM real:

1. **Weekly review cadence**, never skipped — when missed, the agent prompts.
2. **Single owner per item** — every RAID entry, every task, exactly one named person. No *"the team,"* no *"TBD."*
3. **Same format every time** — consistency is what makes status reports trusted.

Plus PMI's 7-element status report (overall status / timeline / achievements / upcoming milestones / active risks / budget / decisions needed) capped at ≤1 page.

**How to apply:**
- When building any tracking tool, agent, or skill: bake in the cadence + ownership + format rules. Don't make them optional.
- For consulting status reports: PMI's 7-element format, ≤1 page, every week.
- For RAID logs: weekly minimum review, immediate logging for critical items.
- For task lists: stale items (>7 days no update) flagged automatically; single owner enforced.

**Trace:** Researched 2026-05-07 against PMI's PMBOK 7 standard plus ProjectManagement.com / Asana / MPUG sources. Driven by Matt's request for a PMP-grade PM agent. Implemented in `.claude/agents/project-manager.md` and 5 templates under `templates/` (raid-log, task-list, status-report, activity-log, stakeholder-register).
