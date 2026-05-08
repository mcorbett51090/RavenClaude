# Skill: draft-agent-brief

A repeatable workflow for **producing a strong agent brief when the user knows what they want in business terms but doesn't yet have the domain expertise to write the technical spec themselves.**

## When to use this skill

- The user asks for a new agent and isn't fluent in the agent's target domain.
- The user has filled in `templates/agent-brief.md` and left blanks where they didn't know.
- The user has described a goal in plain words and asked Claude to *"draft a strong request for me."*

## The workflow

1. **Listen for the goal in business terms.** What does the user actually want this agent to do for them? Keep them out of technical territory if they're new to the domain.

2. **Identify the domain.** What world does this agent live in (Power Platform, Salesforce, web dev, iOS, etc.)? If unclear, ask **once**.

3. **Draft a strong brief** — fill in the seven fields of [`templates/agent-brief.md`](../templates/agent-brief.md):
   - **Outcome** (in business terms)
   - **Context** (the user's situation, including their experience level)
   - **Domain familiarity** (so the agent knows whether to over-explain)
   - **Success criteria** (concrete, in business terms)
   - **Out of scope** (anti-goals)
   - **Constraints** (hard requirements)
   - **Personality / style** (terse, conservative, asks-when-ambiguous, etc.)

4. **Show the draft to the user** with a clear *"here's what I wrote based on what you told me — does this fit?"* prompt.

5. **Iterate.** Expect one or two rounds of *"yes, but change X."* Don't push back on changes that move toward the user's actual intent.

6. **Once approved, build (or dispatch) the agent.** The brief becomes the system prompt or the agent definition, depending on whether this is a one-shot dispatch or a permanent role.

## The principle

**The user brings the *what* and *why*. Claude brings the *how*.**

A non-domain-expert user can absolutely write a strong brief — they just need help filling in the domain-specific bits. This skill keeps that division of labor explicit so neither side is asked to do the other's job.

## See also

- [`templates/agent-brief.md`](../templates/agent-brief.md) — the seven-field template the user fills in (or leaves blank for Claude to fill).
- [`agents/architect.md`](../../agents/architect.md) — example of a finished, role-style agent definition produced by this kind of brief.
