---
id: grok-bot-orchestration-skill-restates-core
title: "A Grok Bot skill restates core protocols instead of citing them, on purpose"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 921
summary: "The skill duplicates CGP/dispatch prose as freestanding text, against this repo's cite-not-restate convention, since a Grok Bot cannot resolve a cross-plugin markdown link."
last_verified: 2026-09-04
covers:
  - plugins/ravenclaude-core/skills/game-theory-basics/SKILL.md
  - plugins/ravenclaude-core/skills/quantitative-problem-solving/SKILL.md
  - plugins/ravenclaude-core/skills/ravenclaude-core-orchestration/SKILL.md
covers_digest: "sha256:03238cda6ad23a7dcc14129d14959ffd868cc0197c3dc91326cb5de95f195261"
nuance: "ravenclaude-core-orchestration/SKILL.md restates the single-orchestrator and Capability Grounding rules as freestanding prose instead of linking to ravenclaude-core/CLAUDE.md -- the opposite of this repo's own 'cite, not restate' convention -- because a Grok Bot cannot resolve a cross-plugin markdown link the way a Claude Code agent can."
nuance_evidence:
  measured: 2026-09-04
  control: "read ravenclaude-core/CLAUDE.md's 'Multi-Agent Coordination & Dispatch Rules' and 'Capability Grounding Protocol' sections side by side with this skill's 'Non-negotiable house rules' -- both restate the same orchestrator-worker and CGP invariants in the skill's own words rather than a markdown link, unlike every other cross-plugin reference in this repo (e.g. forms-engineering's inherited-rules table, which links)"
  falsifier: "a future Grok Bot runtime that can resolve a live cross-plugin markdown link, at which point this skill should be re-cut to cite ravenclaude-core/CLAUDE.md instead of restating it"
  probe: "plugins/ravenclaude-core/skills/ravenclaude-core-orchestration/SKILL.md"
nuance_source: "plugins/ravenclaude-core/skills/ravenclaude-core-orchestration/SKILL.md"
verify:
  tier: "none"
  rationale: "This is a documentation-duplication fact, not offline-stageable in CI -- re-verifying it means re-reading this skill against ravenclaude-core/CLAUDE.md's current dispatch/CGP sections, not running a script."
sources:
  - label: "PR #1104 -- grok-bot-creation + grok-bot-delegation plugins"
    url: https://github.com/mcorbett51090/RavenClaude/pull/1104
---

## What a reader would have assumed instead

That a new skill referencing "RavenClaude Core Orchestration" in its title would link into `ravenclaude-core/CLAUDE.md` the way every other cross-plugin reference in this marketplace does (e.g. `forms-engineering`'s inherited-rules table, which links rather than restates).

## The discriminator

control: read `ravenclaude-core/CLAUDE.md`'s "Multi-Agent Coordination & Dispatch Rules" and "Capability Grounding Protocol" sections side by side with this skill's "Non-negotiable house rules" -- both restate the same invariants in freestanding prose, with no markdown link back to the source file.

## Why it matters

A Grok Bot is a separate, non-Claude-Code runtime -- it has no mechanism to `@`-import or traverse a relative markdown link into another plugin's `CLAUDE.md` the way a Claude Code sub-agent can. So `ravenclaude-core-orchestration/SKILL.md` deliberately copies the relevant protocols as a portable, self-contained recipe instead. This is a one-time, hand-adapted copy (its own "Credit" section says "Adapted from RavenClaude plugin `ravenclaude-core`"), not a live link -- so it will drift from `ravenclaude-core/CLAUDE.md` as that file's dispatch/CGP/SOP sections evolve, and nothing re-syncs it automatically.
