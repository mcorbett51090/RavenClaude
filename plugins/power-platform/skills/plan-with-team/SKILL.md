---
name: plan-with-team
description: >
  Spawns an Agent Team to collaboratively plan Power Platform / Dataverse applications.
  Three specialists (Data Architect, UX Designer, The Skeptic) debate and refine the plan
  before any code is written. Falls back to structured single-agent planning if agent teams
  are not enabled. Triggers on: "plan my app", "plan with team", "design my app",
  "architect this app", "plan the schema", "team planning", "agent team plan",
  "plan power app", "plan dataverse app", "design the data model".
license: MIT
compatibility: "Claude Code with Opus 4.6, optional CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1"
metadata:
  author: custom
  version: "1.0.0"
  requires-experimental: "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"
  platform: "Microsoft Power Platform / Dataverse"
---

# Plan With Team — Agent Team Planning Skill

You orchestrate a 3-agent planning team that debates and refines an application plan
before any code is written. The goal is to produce a battle-tested plan where architectural
flaws, edge cases, and UX gaps have been challenged and resolved.

## CRITICAL RULES

1. **No code is written during planning.** The output is a plan document only.
2. **The Skeptic writes NO artifacts.** Their only job is to challenge and find flaws.
3. **Every agent must reference the relevant skills.** Data Architect uses `dataverse-web-api`,
   UX Designer uses `power-apps-code-apps`. Load those skills for domain knowledge.
4. **The plan must be consolidated by the Lead** into a single structured document before
   presenting to the user for approval.
5. **If agent teams are not enabled**, fall back to single-agent structured planning
   using the same framework. Read `resources/fallback-mode.md`.
6. **Schema creation can be parallelized.** When implementation starts, reference
   `resources/parallelization.md` in the `dataverse-web-api` skill for the dependency graph.
   Multiple tables can be built simultaneously by separate agents.

## The Team

| Role | Agent Name | Mandate |
|---|---|---|
| Data Architect | `data-architect` | Design tables, columns, relationships, option sets, security model |
| UX/Flow Designer | `ux-designer` | Design app module, forms, views, sitemap, user journeys |
| The Skeptic | `the-skeptic` | Challenge everything. Find security holes, edge cases, ALM issues, performance traps |

## Workflow

### Phase 1 — Gather Requirements (Lead)

Before spawning the team, the Lead must understand:
- **Who** uses this app? (personas/roles)
- **What** data does it manage? (entities/relationships)
- **What** are the key workflows? (create, approve, report, etc.)
- **What** existing Dataverse tables/solutions already exist?

Ask the user these questions if the prompt is vague. Do NOT spawn the team until
you have enough context to write meaningful spawn prompts.

### Phase 2 — Spawn the Team

Spawn all three agents with detailed context. Each agent gets:
- The user's requirements (from Phase 1)
- Their role-specific instructions (from `resources/roles/`)
- Instructions to load the relevant domain skill

```
Spawn a teammate called "data-architect" with this prompt:
[Read resources/roles/data-architect.md and include its full content]

Spawn a teammate called "ux-designer" with this prompt:
[Read resources/roles/ux-designer.md and include its full content]

Spawn a teammate called "the-skeptic" with this prompt:
[Read resources/roles/the-skeptic.md and include its full content]
```

### Phase 3 — Parallel Design (Agents Work)

- Data Architect designs the schema and broadcasts their proposal
- UX Designer designs the app structure and broadcasts their proposal
- The Skeptic reads both proposals and challenges them with specific questions

Agents message each other directly to resolve issues. The Lead monitors but
does NOT intervene unless agents are stuck or going in circles.

### Phase 4 — Skeptic Review Round

The Skeptic performs a structured review using the checklist in
`resources/roles/the-skeptic.md`. They broadcast findings to both agents.

Data Architect and UX Designer must respond to every finding with either:
- **ACCEPTED** — change incorporated into their design
- **REJECTED (reason)** — justified pushback

### Phase 5 — Consolidation (Lead)

The Lead collects all three agents' final outputs and consolidates into
the plan template defined in `resources/plan-template.md`.

Present the consolidated plan to the user for approval.

### Phase 6 — Handoff

Once approved, the plan document serves as the implementation spec.
Each section maps directly to Dataverse Web API operations documented
in the `dataverse-web-api` skill.

**Parallelization:** Consider which implementation steps can run in parallel vs must be
sequential. Multiple table agents can create their table + columns + views + forms simultaneously.
Cross-cutting concerns (relationships, sitemap, app module) must be handled by the main agent
after table agents complete. See the `dataverse-web-api` skill's `parallelization.md` resource.

## Enabling Agent Teams

If the user hasn't enabled agent teams:

```json
// Add to .claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Then restart Claude Code.

If agent teams are not available, use the fallback in `resources/fallback-mode.md`.
