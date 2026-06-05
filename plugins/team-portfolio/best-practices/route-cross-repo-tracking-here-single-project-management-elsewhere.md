# Route cross-repo activity tracking here — single-project management elsewhere

**Status:** Absolute rule
**Domain:** Team portfolio / routing / plugin boundaries
**Applies to:** `team-portfolio`

---

## Why this exists

Two failure modes appear when the plugin boundary is unclear. The first: a user asks "how is the website project going?" and the agent uses this plugin to read GitHub event counts instead of routing to the `project-management` plugin or `ravenclaude-core/project-manager` for the scored risk register and sprint status that actually answer the question. The second: a user asks "who did what across my repos last week?" and the agent routes to `project-manager` and gets RAID hygiene when they wanted a multi-repo activity roll-up. Getting the routing wrong wastes a round-trip and produces a deliverable the user cannot act on.

## How to apply

Apply this routing table before spawning or selecting any capability:

| Request signal | Route to |
|---|---|
| "who did what across repos", "activity summary", "team tracker" | `team-portfolio` — this plugin |
| "cross-repo project status", "the website spans 3 repos" | `cross-repo-project-tracking` skill — this plugin |
| "run my portfolio refresh", "update the dashboard" | `/portfolio-refresh` command — this plugin |
| "sprint velocity", "EVM", "risk register", "stakeholder report" | `project-management` plugin |
| "RAID log", "action items for this effort", "status hygiene" | `ravenclaude-core/project-manager` |
| "polish the weekly narrative prose" | `ravenclaude-core/documentarian` |
| "is the token scoped correctly" | `ravenclaude-core/security-reviewer` |

The distinguishing question: **does the user need to observe GitHub activity across many repos, or do they need to run or govern a specific project?** Observation routes here. Running a project routes out.

**Do:**
- Ask one clarifying question if the request is ambiguous between "show me what happened" and "help me manage this."
- Use the `cross-repo-project-tracking` skill (still this plugin) when a user wants to track a named project that spans multiple repos — it adds a project-matching layer on top of the base collection.
- Hand the narrative polish on any generated report to `ravenclaude-core/documentarian` if the user asks for improvements to the prose.

**Don't:**
- Start sprint facilitation or scored risk ranking from inside this plugin — those belong to `project-management`.
- Produce a per-developer performance evaluation from GitHub activity counts — the plugin reads observable events, not individual performance.
- Route to `ravenclaude-core/project-manager` when the user is asking for a cross-repo view; that agent owns a single effort's hygiene, not a multi-repo roll-up.

## Edge cases / when the rule does NOT apply

- A user who runs a single-repo project and wants "what happened in my repo this week" technically could use either `team-portfolio` or the project management plugins; offer `team-portfolio` if they want a dashboard and automation, and `ravenclaude-core/project-manager` if they want structured status hygiene.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — routing table in §3; seams to neighbouring plugins in §8.
- [`../skills/cross-repo-project-tracking/SKILL.md`](../skills/cross-repo-project-tracking/SKILL.md) — the skill that adds project-level structure on top of the base GitHub activity collection.

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §3 routing rules and §8 seams. The boundary rule is architectural: this plugin observes; project-management plugins govern.

---

_Last reviewed: 2026-06-05 by `claude`_
