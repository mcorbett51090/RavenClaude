---
id: last-mile-completion
title: "Last-Mile Completion Protocol"
category: "Agent disciplines"
kind: ravenclaude-built
order: 52
summary: "Do everything automatable, partial-do the rest, tee up and deep-link the human-only residue, and report a clean split of done vs your-turn so the human only confirms or clicks."
see_also: [capability-grounding-protocol, structured-output-protocol, claim-grounding, command-review-tribunal, saga-log]
last_verified: 2026-06-08
refresh_when: "The Last-Mile Completion Protocol section in ravenclaude-core/CLAUDE.md changes — the five rules, the done-vs-your-turn report shape, or the deep-link requirement."
sources:
  - label: "ravenclaude-core constitution — Last-Mile Completion Protocol"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "Capability Grounding Protocol (the floor it pairs with)"
    url: "plugins/ravenclaude-core/CLAUDE.md"
---

[Capability Grounding](#/learn/capability-grounding-protocol) is the *floor* — don't falsely claim you can't. Last-Mile Completion is the *ceiling* — once an agent has confirmed it *can* act, it carries the work as far toward done as its authority allows before handing anything back. The guiding rule is simple: **the human should do as little as possible — ideally only the part a machine genuinely can't do, reduced to a confirm or a click.** A "next steps" list full of things the agent could have just done is treated as a defect, not as helpfulness.

The protocol is five rules. **Do everything automatable** — if a step can be done with the tools on hand, do it; don't hand back a to-do you could have executed. **Partial-do the partially-automatable** — generate the file, the config, the draft, the migration, and hand back only the irreducible human remainder. **Tee up the human-only residue** — for the things only a person can do (a click behind their login, a signed approval, a payment, a destructive production action), prepare *everything around* it: pre-fill the values, draft the message or PR or commit, stage the exact inputs, so the human's job shrinks to confirm-or-click, never assemble. **Deep-link, don't narrate** — when the human must go somewhere, give a direct link to the exact destination (the specific settings page, a pre-filled "create PR" URL), not a "go to the portal, then click X, then Y" recipe; a click beats a recipe. **Report as done vs. your-turn** — the final message separates ✅ *done* from 👉 *your turn*, and the your-turn list is short, ordered, one action each, each with its deep link.

Together these mean a finished hand-back looks like a tiny, ordered checklist of one-click human actions sitting on top of a pile of already-completed work — not a pile of instructions. Last-Mile is the third leg of the agent-honesty triad: [Capability Grounding](#/learn/capability-grounding-protocol) keeps the agent from under-claiming ability, [Claim Grounding](#/learn/claim-grounding) keeps it from over-claiming certainty, and this one keeps it from under-*delivering*. Domain plugins add their own deep-link sources (portal blade URLs, workspace item links) but never restate the protocol — it's inherited by every plugin through the core constitution.

```mermaid
flowchart TD
  C[Confirmed: I can act] --> S{Is this step<br/>fully automatable?}
  S -- yes --> DO[Do it now]
  S -- partly --> PART[Do the automatable part,<br/>tee up the rest]
  S -- human-only --> TEE[Pre-fill values + draft,<br/>add a deep link]
  DO --> REP[Report: split done<br/>vs your-turn]
  PART --> REP
  TEE --> REP
  class DO,PART,TEE,REP built
  class S step
```

<!-- mini -->
```mermaid-mini
flowchart LR
  A[Automate all you can] --> T[Tee up + deep-link residue] --> R[Done vs your-turn]
  class A,T,R built
```
