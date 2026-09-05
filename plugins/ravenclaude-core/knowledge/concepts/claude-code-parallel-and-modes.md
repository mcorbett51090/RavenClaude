---
id: claude-code-parallel-and-modes
title: "There is no /max-parallel — remap to documented Claude Code knobs"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 930
summary: "Org slang \"max parallel\" is not a Claude Code command; the skill remaps it to plan mode, subagents, worktrees/batch, ultracode workflows, ultrathink, and /effort."
last_verified: 2026-09-05
covers:
  - plugins/ravenclaude-core/skills/claude-code-parallel-and-modes/SKILL.md
covers_digest: "sha256:bb4c3cd18fc262fb097c0816d87ee1b328a353e3ee3b50887fec61069420a73e"
nuance: "Official Claude Code docs and /help list no /max-parallel mode; ultrathink is a one-turn in-context keyword and does not change API /effort, while ultracode is a separate setting that sends xhigh plus dynamic workflows."
nuance_evidence:
  measured: 2026-09-05
  control: "model-config docs distinguish ultrathink from /effort; no /max-parallel appears in /help or documented slash commands"
  falsifier: "an official Claude Code release shipping a /max-parallel command or equating ultrathink to API effort"
  probe: "plugins/ravenclaude-core/skills/claude-code-parallel-and-modes/SKILL.md"
nuance_source: "plugins/ravenclaude-core/skills/claude-code-parallel-and-modes/SKILL.md"
verify:
  tier: "none"
  rationale: "The skill is a remap table over documented CLI knobs; re-verification is reading code.claude.com model-config + /help on the installed version, not a staged CI probe."
sources:
  - label: "rc-deep-research DIGEST + VERIFY (2026-09-05) + PLUGIN-DECISION lock to ravenclaude-core"
    url: https://github.com/mcorbett51090/RavenClaude/pull/1114
---

## What a reader would have assumed instead

That "max parallel" names a first-class Claude Code mode or slash command, so operators should search for `/max-parallel` or raise session effort globally whenever they want fan-out.

## The discriminator

control: model-config docs distinguish ultrathink from /effort; no /max-parallel appears in /help or documented slash commands
Measured 2026-09-05: the research DIGEST/VERIFY for this skill found no official `/max-parallel`. The correct remaps are plan mode, subagents, worktrees/`/batch`, ultracode/workflows, one-turn `ultrathink`, and `/effort` — and ultrathink must not be confused with ultracode or API effort.

## Why it matters

Inventing `/max-parallel` wastes operator time and produces unsafe shared-checkout parallel writes. Putting the remap table in `ravenclaude-core` (CLI operator home) keeps it beside worktree/orchestrate/spawn-team skills rather than in app-build plugins.
