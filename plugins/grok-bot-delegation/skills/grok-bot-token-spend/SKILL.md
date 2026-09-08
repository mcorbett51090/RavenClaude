---
name: Grok Bot token spend
description: >-
  Use when optimizing Grok Bot / multi-bot fleet token spend — condensed
  returns, effort ladder, routine hygiene, connectors over browser, CPCT
  measurement.
---
# Grok Bot token spend

Use after research or when fleet usage is tight / on-demand pressure is up. Companion to fleet-pattern-routing.

## Hard rules

1. **Condensed returns:** specialists → CoS ≤~1.5–2k digest + file paths; no raw dumps.
2. **Effort ladder before spawn:** fact 0–1 | compare 2–4 | breadth ≤8–10 | serial = 0 parallel.
3. **Routines:** prefer events; skip when noop; never broad “every message” listeners (consume usage per docs.x.ai).
4. **Connectors > browser/vision;** one owner per stage; no duplicate handoffs.
5. **CPCT** = Σ(spend including failures) / successful tasks — not $/token vanity.
6. **No Grok Bot model picker** — cut overhead; don’t hunt Settings for a cheaper model.

## Do / don’t

Do: lean Bot descriptions; enable skills only where needed; file-back large outputs; fresh thread per distinct task; set account on-demand limits.

Don’t: assume API cache/compaction knobs in Bot UI; fan out for “more reasoning”; synthesizer-only bots after specialists already answered; leave image-heavy threads open.

## RavenClaude placement

Prefer adding/updating skill under **`grok-bot-delegation`** (not a new plugin; not Max `token-budget-playbook` which is Claude Code idle-quota). Distinct from `claude-app-engineering` context-budget (Claude apps) and `ai-coding-model-guidance` (model SKUs).
