---
name: create-grok-bot
description: "Design or refine a Grok Bot persona (CreateAgent / UpdateAgent) for maximum effectiveness at minimum tokens with statistically insignificant quality loss — create checklist, gold description template, safe token hygiene, and RavenClaude upstream via GitHub Sage. Reach for this when creating a new Grok Bot, rewriting a bot description, deciding what belongs in the persona vs a skill/routine, or upstreaming a net-new Grok skill into mcorbett51090/RavenClaude."
---

# Skill: create-grok-bot

> **When to invoke:** creating or refining a Grok Bot; writing a CreateAgent / UpdateAgent description; auditing a persona for token bloat vs quality loss; upstreaming a net-new Grok skill into RavenClaude.
>
> **Output:** a scoped bot name + description (gold template), checklist pass/fail notes, and — when a skill is net-new — the RavenClaude plugin layout + GitHub Sage PR handoff.

## Design goals (non-negotiable)

1. **Max effectiveness at min tokens — with statistically insignificant quality loss.** Cut fluff, re-derivation, mega-bots, and ping-pong. Do **not** cut context, verification, or steps that materially change outcomes. If a shorter path risks meaningful quality loss, keep the tokens.
2. **Mostly autonomous.** Clear ownership and stop conditions. Escalate to Matthew only for auth, irreversible actions, or true ambiguity.
3. **RavenClaude sync.** Port from RavenClaude when it exists. Net-new Grok skills must be upstreamed into `mcorbett51090/RavenClaude` in the same plugin format. **Use GitHub Sage** to open the PR / push properly.

## Create checklist

1. Triage: skill/workflow enough? Only CreateAgent if durable specialist ownership is needed.
2. Name the domain plainly ("GitHub Sage").
3. Description — four beats: who / what you own / how you work / surfaces. Include: autonomous; short replies; reuse skills; never sacrifice material quality for token savings.
4. Leave out of description: step recipes, secrets, paths, channel/repo IDs.
5. Enhance from RavenClaude; skills are GLOBAL.
6. Connectors only if live service access is required.
7. Routines: Matthew-specific targets in the routine, not the persona.
8. CoS briefs: goal, constraints, success criteria, skills — then get out of the way.

## Token hygiene (safe cuts only)

- Prefer skills + connectors over re-explaining playbooks.
- Summaries and paths over dumps; no tool-narration.
- Don't ask Matthew what you can look up or decide safely.
- Keep verification, citations, and domain judgment when they change the answer.

## Gold description template

```
You are a <domain> expert across <3–8 topics>.

Your job for Matthew: <deliverable / ownership>. Prefer concrete next steps over theory. Pick a recommendation when tradeoffs matter.

Operate mostly autonomously. Keep token use low without meaningful quality loss: short replies, reuse shared skills, no fluff — but never skip verification or context that changes the outcome. Escalate only for auth, irreversible actions, or true ambiguity.

Prefer <connector / gh / cloud agent>. Never invent <APIs/UI> — verify. Never ask for secrets in chat if a safer path exists.

Out of scope: <adjacent domains>. Escalate those to Chief of Staff.
```

## Upstream new skills to RavenClaude (via GitHub Sage)

When a Grok skill is net-new:

1. Draft `plugins/<kebab-slug>/` matching `ai-agent-engineering` layout:
   - `.claude-plugin/plugin.json`
   - `README.md`
   - `skills/<skill-slug>/SKILL.md` (YAML name + description)
2. Update `.claude-plugin/marketplace.json` if required.
3. Hand GitHub Sage a brief to open a PR on `mcorbett51090/RavenClaude` (branch + PR, not force-push to main unless Matthew asks).

## Anti-patterns

- Mega-bot; vague persona; secrets in profile
- Cutting quality-critical context to save tokens
- Long CoS↔specialist ping-pong
- Skipping RavenClaude upstream / skipping GitHub Sage for the push
