---
name: delegate-via-expert-bots
description: "Standing CoS loop for every Matthew ask: match purpose-built expert Grok Bots, create any missing ones (token-efficient + autonomous via create-grok-bot), port or upstream RavenClaude skills, then SendToAgent a tight brief and coordinate — escalate to Matthew only for decisions, auth, or irreversible actions. Reach for this when routing work across Grok Bots, deciding whether CoS should do specialist deep-work, or briefing a newly created expert bot."
---

# Skill: delegate-via-expert-bots

> **Invoked by:** Chief of Staff (primary).
>
> **When to invoke:** every Matthew ask that could belong to a specialist; creating missing expert bots; drafting a SendToAgent brief; deciding whether CoS should keep the work.
>
> **Output:** matched/created bot(s) + a tight delegation brief + coordination notes (what stays with CoS vs Matthew).

## Loop (every ask)

1. **Match bots.** Do we already have expert bot(s) purpose-built for this? Check teammates / agent profiles.
2. **Create if missing.** CreateAgent using [`create-grok-bot`](../../grok-bot-creation/skills/create-grok-bot/SKILL.md): token-efficient, mostly autonomous specialists.
3. **Enhance from RavenClaude.** Search `mcorbett51090/RavenClaude` for matching plugins; port skills. If the skill is net-new to Grok, also upstream it into RavenClaude in the same plugin format (via GitHub Sage).
4. **Delegate.** SendToAgent with a tight brief: goal, constraints, success criteria, skills to apply. Prefer one clear ask over multi-turn ping-pong (token cost).
5. **Coordinate.** Synthesize; pull Matthew only for decisions, auth, or irreversible actions.

## Rules

- Don't do specialist deep-work when a bot should own it.
- Parallelize independent specialists.
- Never relay Matthew's unfiltered venting; paraphrase the actionable ask.
- Skills are global — don't "assign"; bots pull them when relevant.
