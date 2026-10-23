---
name: rubric-gate
description: "Use before applying any CreateAgent/UpdateAgent profile or shared-skill change: score on the 6-dim agent-quality-rubric, then refine-to-rubric with a different-model judge, max 6 rounds."
---
# Rubric gate (profiles + shared skills)
Source: RavenClaude `ravenclaude-core/skills/agent-quality-rubric`, `refine-to-rubric`, `draft-agent-brief` @52fcb08.
Used by: Bot Architect 53953b50 (author), Prompt Engineer f3399be9 (craft), Independent Reviewer caed63ab (judge of record).

## Rubric — 6 dims × 1–5 (/30)
Mission · Scope · Capability Grounding · Output Contract · Escalation · Scenarios.
Block if ANY dim = 1 or Mission ≤2. Total ≤9 → re-author from a brief (outcome, context, domain, success, out-of-scope, hard constraints, personality, judgment level). Pass bar: ≥24/30, no dim <4.
Fleet extra check (deterministic, before judge): core standing-rules line present and ≤40 words; `fleet-standing-rules` named; any JSON examples parse.

## refine-to-rubric loop
1. Deterministic gates first (word counts, rule-line regex, JSON parse). Fail → fix, no judge call.
2. Judge = a DIFFERENT model from the author (no self-grading). Follow the model order + Cursor ≤80% rule; heavy CLI runs via box-run (reserve 2.5 GB).
3. Keep-best: retain highest-scoring draft; stop when pass, plateau (no gain 2 rounds), or **6 rounds max**.
4. Verdict ∈ rubric-pass | capped | plateaued | budget-exhausted. Never say "perfect".
5. Return a RESULT block (completion-contract skill) with score table + verdict. Bot Architect applies only after pass or Matthew override.
