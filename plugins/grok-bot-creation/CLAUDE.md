# grok-bot-creation — team constitution

> Team constitution for the `grok-bot-creation` Claude Code plugin — a **single skill**, zero agents,
> for designing Grok Bot personas: token-efficient, mostly autonomous specialists that escalate only via
> Chief of Staff, apply a problem-solver stance instead of one-and-done fixes, and upstream any net-new
> skill into RavenClaude via GitHub Sage rather than living only in Grok's own memory.
>
> **Orientation:** this file is domain-specific to Grok Bot creation. For the domain-neutral team
> constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 1. What this plugin is

A **CreateAgent / UpdateAgent design guide**, not a runtime. It does not create or manage bots itself —
it is the checklist + gold description template + token-hygiene rules a human or bot follows when
standing up a new Grok Bot persona, and the recipe for syncing a bot's net-new skills back into this
marketplace. The one skill, [`skills/create-grok-bot/SKILL.md`](skills/create-grok-bot/SKILL.md), carries
the whole contract.

## 2. House opinions

1. **Max effectiveness at minimum tokens — with statistically insignificant quality loss.** Cut fluff,
   re-derivation, mega-bot scope creep, and CoS↔specialist ping-pong. Never cut verification, context, or
   a step that materially changes the outcome to save tokens.
2. **Mostly autonomous, with one non-negotiable escalation path.** A bot's stop conditions are clear; when
   it hits one — auth, an irreversible action, or a decision outside its lane — it escalates via **Chief
   of Staff only**, never directly to Matthew.
3. **Problem-solver stance, never one-and-done.** First principles, Occam's razor, quantitative failure
   analysis, and game-theory/incentive reasoning when multiple parties interact — via the companion skills
   in [`grok-bot-delegation`](../grok-bot-delegation/) — before declaring a fix done.
4. **RavenClaude is the source of truth.** Port an existing RavenClaude skill into a bot rather than
   re-deriving it; upstream a genuinely new one back into this marketplace, in this marketplace's own
   plugin layout, via GitHub Sage.

## 3. Zero agents, deliberately

This plugin ships **no agents**. Designing a Grok Bot persona is a checklist + template exercise, not a
role a specialist needs to own — the skill is the whole deliverable, and a dedicated agent would just be
the skill wearing a heavier frame. Reachability is bought by the plugin's own README + skill trigger
phrasing ("create a Grok Bot for X"), not by a spawned specialist.

## 4. Seams

- **Delegating to (and coordinating) the bots this skill designs** → [`grok-bot-delegation`](../grok-bot-delegation/)
  (the Chief-of-Staff standing operating procedure; pairs with this plugin on every bot creation).
- **Building production agentic systems / frameworks** (LangGraph, multi-agent topology, evals) →
  `ai-agent-engineering` — this plugin is persona *design*, not agent-framework engineering.
- **Claude Code's own orchestrator-worker dispatch** → [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
  — a Grok Bot is a distinct, non-Claude runtime; this plugin does not govern Claude Code sub-agent
  dispatch.
- **Upstreaming a net-new skill's actual PR mechanics** → GitHub Sage (a Grok Bot, not a RavenClaude
  plugin) opens the PR; this skill only says when and in what layout.

## 5. Anti-patterns

- A mega-bot covering unrelated domains instead of a scoped persona with clear ownership.
- Secrets, paths, or channel/repo IDs written into a bot's description.
- Cutting verification or outcome-changing context to save tokens.
- A bot escalating to Matthew directly, bypassing Chief of Staff.
- A net-new skill left living only inside one bot's memory instead of upstreamed to RavenClaude.
