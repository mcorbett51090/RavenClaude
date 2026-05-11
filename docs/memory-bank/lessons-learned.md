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

## 2026-05-11 — Mermaid for conceptual diagrams in markdown; ASCII only for folder trees

**Context:** Refreshing `docs/architecture.md` from the old central-hub + Expert-repos model to the plugin-marketplace model. The original doc used ASCII box-art diagrams (`┌──┐`, `└──┘`, etc.) and I had to decide whether to preserve that style or upgrade.

**What we tried first:** Kept the ASCII box-art format on the reasoning that "the rest of your docs use plain markdown and switching here would introduce a tooling dependency for one file." Flagged the choice as a judgment call I'd defer to Matt on.

**Why it failed:** GitHub renders `mermaid` code fences natively in markdown — no tooling dependency exists for the *reader*. The only "tooling" is the author learning mermaid syntax, which is shallow. ASCII box-art looks fine in a monospace editor and looks ragged in GitHub's web UI. For a repo whose primary collaborator access path is the GitHub web UI (per `docs/access.md`), defaulting to ASCII is the wrong tradeoff.

**What works:** **Use `mermaid` code fences for any conceptual or flow diagram** (system architecture, dispatch patterns, sequence diagrams, ER diagrams, state machines). **Keep folder trees as fenced code blocks** using the standard `├──` / `└──` characters — mermaid has no clean file-tree type and tree characters in monospace read fine. The architecture doc's marketplace diagram is the canonical example of the good shape (a `flowchart TB` with subgraphs for marketplace/plugins/consumer, plus `classDef` color coding).

**How to apply:**
- For new diagrams in any markdown doc, reach for `mermaid` first.
- Pick the diagram type that fits the content (`flowchart`, `sequenceDiagram`, `erDiagram`, `classDiagram`, `stateDiagram-v2`) instead of defaulting to `flowchart`.
- For file/folder trees, keep using fenced code blocks — don't try to coerce them into mermaid.
- See [`docs/best-practices/diagrams-in-docs.md`](../best-practices/diagrams-in-docs.md) for the full rule, including the "when to deviate" exceptions (e.g. agent prompt files read by Claude itself rather than viewed on GitHub).

**Trace:** Driven by Matt's directive ("I want the mermaid diagram") on 2026-05-11 during the lessons-loop scaffolding work. Codified in `docs/best-practices/diagrams-in-docs.md` and in personal memory under `feedback_diagrams.md`.

---

## 2026-05-07 — PSM discipline = quarterly QBR + per-partner success plan + visible health score (with EdTech overlay)

**Context:** Designed a `partner-success-manager` agent for an EdTech Partner Success Manager (communication / translation / rostering) who is also her team's AI champion.

**What we tried first:** A generic Partner Success Manager agent design with the standard PSM artifacts (profile, success plan, QBR, health, onboarding, touchpoints).

**Why it would have fallen short:** The generic version missed three context dimensions that turned out to dominate the role's reality: (1) **EdTech school-year cadence** — rostering crunch, EOY data, renewal cycles all map to the academic calendar, not Q1/Q2/Q3/Q4; (2) the user's **high-touch support background** — her instinct to invest time in upfront enablement to prevent downstream tickets is well-supported in PSM literature and should be reinforced, not flattened into a generic onboarding checklist; (3) her unique team responsibility as **AI champion** — every useful interaction with the agent is a candidate for a team-shared workflow library, not a one-off win.

**What works:** The PSM discipline rule is parallel to the PMP version: **quarterly QBR cadence + per-partner success plan + visible health scoring**. Plus three context overlays:
- **EdTech school-year awareness** baked into the onboarding checklist, success-plan milestones, and QBR prompts.
- **High-touch DNA reinforcement** in the onboarding flow (proactive demos, district IT alignment, integration validation up front).
- An **AI workflow library** that grows organically as useful patterns surface, with the agent prompting *"should this become a library entry?"* when it produces something reusable.

**How to apply:**
- For any role-design ask, hunt for the **discipline rule** first — the cadence + ownership + format triad that separates real practice from theater. PMP and PSM both have it; other roles likely do too.
- When the role lives in a specific industry (EdTech, healthcare, financial services), bake the industry's **calendar / cadence** into the templates, not just the agent description.
- When the user is the **AI champion** for their team, make the agent transparent about *how* it does things, so the user can replicate and teach the move. Treat agent interactions as training data for the team.
- A high-touch / proactive-setup philosophy is a real strength in PSM work — design for it explicitly, don't flatten it.

**Trace:** Researched 2026-05-07 against SaasPedia, Impartner, PartnerStack, PARTNERNOMICS, TSIA, and Gainsight QBR resources. Driven by Matt's request for an agent for his wife (new EdTech PSM, AI champion). Implemented in `.claude/agents/partner-success-manager.md` and 7 templates under `templates/partner-success/`.

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
