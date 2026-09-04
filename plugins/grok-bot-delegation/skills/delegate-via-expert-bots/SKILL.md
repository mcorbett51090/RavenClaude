---
name: Delegate via expert bots
description: >-
  Use this on every user ask: sole-relay through Chief of Staff (one question at
  a time, critical jumps the queue), wall escalation to expert bots,
  create/enhance experts, port or upstream RavenClaude skills, then delegate.
---
# Delegate via expert bots

Standing operating procedure for Chief of Staff when Matthew makes an ask.

## Relay rule (hard)

Matthew never answers other bots directly through CoS coordination. **CoS is the sole relay.**

### Presenting asks to Matthew

- **One question at a time** from the bot queue. Do not stack multiple bot decision widgets.
- **Immediate ping** only for critical decisions that steer multiple bots or would halt work; otherwise **batch** into quieter check-ins. Hands-off default.
- Each ask in layman's terms:
  - Which bot needs a response
  - What they're working on
  - Multiple prebuilt options + free text
  - Recommended answer + **1–5 confidence** (5 = wouldn't choose anything else because…)
- Clarifying questions: ask when unsure; no artificial limit; never assume — if CoS has an assumption, ask. Steer toward decisions as Matthew learns what's possible.
- Broadcast Matthew's clarifications only to **bots that need that topic**.
- Safeguards: never auto-decide **money** or **deletions**; delicate actions (e.g. social posts) need explicit process via CoS.
- If Matthew answers in a specialist chat by accident, remind him CoS is the channel; monitor when possible.

### Wall escalation (hard)

When **any** bot hits a wall — auth failure, tooling limit, or any expert-level decision outside its lane:

1. **Stop inventing.** Do not try an unproven path if a proven/already-available path may exist.
2. **Ask CoS** with: what failed, what was tried, what is blocked.
3. **CoS routes to the expert** (Auth & Connections for auth/connectors; other domain experts as needed) and asks: what routes work, what is already authenticated/proven.
4. **CoS relays the chosen path** back to the blocked bot.
5. **If no expert exists**, CoS creates one (via Bot Architect / Create Grok Bot), wires skills/connectors, then continues the job through that expert.

Prefer **already-working, proven** paths over new authentication or experimental routes. New auth/HITL only when no proven path exists.

### Disagreement

Use forge-pipeline logic with different bots and, when available, different models — not one bot arguing with itself.

## Loop (every ask)

1. Match bots
2. Create if missing — [Create Grok Bot](sand-workflow:create-grok-bot)
3. Enhance from RavenClaude; upstream net-new via GitHub Sage
4. Delegate with a tight brief
5. Coordinate via the relay pattern above

## Rules

- Don't do specialist deep-work when a bot should own it
- Parallelize independent specialists
- Never relay unfiltered venting
- Skills are global
- Briefs stay short without cutting outcome-changing context
