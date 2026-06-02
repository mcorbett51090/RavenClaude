# project-management

Project & delivery management for AI agent teams — four specialists spanning the **predictive (PMBOK/PMP)** and **agile (Scrum/Kanban)** tracks and the **hybrid** in between.

This plugin **deepens** `ravenclaude-core`'s domain-neutral `project-manager` agent (which stays the lightweight RAID/status-hygiene default) — it does not replace it. Use the core agent to keep a repo's RAID log and weekly status honest; use this plugin's specialists to actually *run* the project: baselines and earned value, sprint facilitation, scored risk registers, and stakeholder/PMO communications.

## Agents

| Agent | Track | Owns |
|---|---|---|
| `delivery-lead` | Predictive | Charter, scope + WBS, schedule/critical path, baselines, integrated change control, earned value |
| `scrum-master` | Agile | Backlog, sprint planning, ceremonies, velocity/capacity, impediment removal, Scrum vs Kanban |
| `risk-and-raid-analyst` | Both | Scored risk register (qual + quant/EMV), responses, issue triage, dependencies |
| `stakeholder-comms-lead` | Both (PMO) | Stakeholder map, comms plan, status/exec reporting, escalation memos, steering packs |

## Start here

Ask **"how should we run this project?"** and the team traverses the delivery-approach decision tree ([`knowledge/pm-decision-trees.md`](knowledge/pm-decision-trees.md)) — predictive vs agile vs hybrid (and Scrum vs Kanban within agile) — then routes to the right lead.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install project-management@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Layout

- `agents/` — the four specialists (each with scenario-authoring frontmatter)
- `skills/` — one playbook per agent (project-charter-and-baseline, sprint-planning, raid-facilitation, status-and-steering-pack)
- `templates/` — deeper-artifact skeletons (charter, change-request, sprint-plan, risk-register, steering-pack)
- `knowledge/` — the delivery-approach decision tree
- `best-practices/` — named, citable rules (single-owner, baseline-before-change, narrative-first status)
- `CLAUDE.md` — the team constitution (roster, routing, hybrid stance, the house-rule carve-out)

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and the why-its-own-plugin rationale.

## Portfolio report (BI)

A self-contained, Power-BI/Tableau-style **project-portfolio report — status donut, burndown, velocity, RAID drill-downs** ships with this plugin. Open [`report.html`](report.html) for the demo (synthetic data); rebuild from real data by editing [`bi-report/data.json`](bi-report/data.json) and running `python3 scripts/generate-bi-report.py --plugin project-management`. Charts are inline SVG (no CDN); the engine + data shape are documented in [`edtech-partner-success/skills/health-report-dashboard`](../edtech-partner-success/skills/health-report-dashboard/SKILL.md).
