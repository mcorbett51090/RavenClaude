---
description: "Forge any idea into a gated, two-panel-reviewed, critic-checked, tiebroken, routed plan. Runs the FORGE pipeline (depth-scaled gates) and ends at ExitPlanMode or an Ultraplan cloud handoff. Backed by skills/forge-pipeline."
allowed-tools: Bash, Read, Write, Edit, Task, AskUserQuestion, WebSearch, WebFetch
argument-hint: <idea> [--depth micro|quick|standard|deep] [--models A=opus,B=sonnet] [--auto-route] [--no-redteam] [--resume <slug>]
---

# /forge

Run the **FORGE** gated-planning pipeline on `$ARGUMENTS`.

**Load `skills/forge-pipeline/SKILL.md` and follow it exactly.** It owns the artifact contract, the
depth ladder, and every gate. This file is the entry point only — it deliberately does **not** restate
the gates, because restating them means paying for the pipeline's description twice on every run.

## Steps

1. **Parse args.** idea, `--depth` (default `quick`), `--models` (B **must** ≠ A), `--auto-route`
   (act on G7's verdict without pausing — else present it to Matt), `--no-redteam` (skip G5 at
   quick/micro only; emits a waiver), `--resume <slug>` (deep only).
2. **Mint** a `<slug>` and the Sága run dir `.ravenclaude/runs/forge/<slug>/`.
3. **Load the skill**, then load **only** the reference files your depth reaches (the skill's table
   says which). Loading a reference file the depth doesn't reach defeats the split.
4. **Run the gates the depth includes**, honoring the skill's §0 artifact contract on every dispatch:
   subagents **write** their artifact to the run dir and return a **receipt**; downstream gates get a
   **path** and read it themselves. Never relay artifact text through this session.
5. **Write the Sága run record** — one entry per gate: pass/fail/waiver, who ran it, model, cost.

## Guardrails (reused, not rebuilt)

- Subagents are dispatched by **this** session only — `guard-recursive-spawn.sh` keeps the call graph
  a tree (a worker can't fan out a second generation), matching Codex's explicit-only spawn.
- `runaway-brake.sh` caps total/consecutive tool calls — a thrashing gate trips the brake, not Matt.
- Don't re-author the two-panel lens/severity/routing rubric (tiebreak F7) — see the skill's
  `reference/provenance.md` for where it lives and what's actually verified about it.
