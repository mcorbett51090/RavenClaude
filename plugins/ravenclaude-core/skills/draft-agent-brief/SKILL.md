---
name: draft-agent-brief
description: Use this skill when the user wants to create a new agent and has a clear business goal but isn't fluent in the agent's target domain. Walks them through producing a strong brief by filling in `templates/agent-brief.md` from their plain-language description, then iterating once or twice before building or dispatching the agent. Triggers when the user asks for "a new agent that does X" without already supplying the technical spec, or when they've filled the brief template and left blanks where they didn't know.
---

# Skill: draft-agent-brief

A repeatable workflow for **producing a strong agent brief when the user knows what they want in business terms but doesn't yet have the domain expertise to write the technical spec themselves.**

## When to use this skill

- The user asks for a new agent and isn't fluent in the agent's target domain.
- The user has filled in `templates/agent-brief.md` and left blanks where they didn't know.
- The user has described a goal in plain words and asked Claude to *"draft a strong request for me."*

## The workflow

1. **Listen for the goal in business terms.** What does the user actually want this agent to do for them? Keep them out of technical territory if they're new to the domain.

2. **Identify the domain.** What world does this agent live in (Power Platform, Salesforce, web dev, iOS, etc.)? If unclear, ask **once**.

3. **Draft a strong brief** — fill in the eight fields of [`templates/agent-brief.md`](../../templates/agent-brief.md):
   - **Outcome** (in business terms)
   - **Context** (the user's situation, including their experience level)
   - **Domain familiarity** (so the agent knows whether to over-explain)
   - **Success criteria** (concrete, in business terms)
   - **Out of scope** (anti-goals)
   - **Constraints** (hard requirements)
   - **Personality / style** (terse, conservative, asks-when-ambiguous, etc.)
   - **Judgment level → model tier** (`haiku` for read-a-lot-return-a-little, `sonnet` for bounded well-specified work, `opus` only for design / adjudication / merge gates — the tier table in [`knowledge/model-tier-delegation.md`](../../knowledge/model-tier-delegation.md); when the user is unsure, describe the output shape and default to the cheaper tier)

4. **Show the draft to the user** with a clear *"here's what I wrote based on what you told me — does this fit?"* prompt.

5. **Iterate.** Expect one or two rounds of *"yes, but change X."* Don't push back on changes that move toward the user's actual intent.

6. **Once approved, build (or dispatch) the agent.** The brief becomes the system prompt or the agent definition, depending on whether this is a one-shot dispatch or a permanent role. Field 8 becomes the `model:` line — a permanent agent **must** carry it (a tier alias, never a full model id; `scripts/check-frontmatter.py` fails the build without it), and a one-shot dispatch passes it as the `model` parameter so the worker does not silently inherit the session's frontier model.

## The principle

**The user brings the *what* and *why*. Claude brings the *how*.**

A non-domain-expert user can absolutely write a strong brief — they just need help filling in the domain-specific bits. This skill keeps that division of labor explicit so neither side is asked to do the other's job.

## See also

- [`templates/agent-brief.md`](../../templates/agent-brief.md) — the eight-field template the user fills in (or leaves blank for Claude to fill).
- [`templates/agent-definition-template.md`](../../templates/agent-definition-template.md) — the gated frontmatter block (`name` / `description` / `tools` / `model` / scenarios) a permanent agent is built from.
- [`agents/architect.md`](../../agents/architect.md) — example of a finished, role-style agent definition produced by this kind of brief.
