# Strategy before visuals, or it reads as slop

**Status:** Absolute rule
**Domain:** Brand strategy / process
**Applies to:** `brand-identity-studio`

> Process rule. The anti-slop mechanism is durable; provider/model specifics are `[verify-at-use]`.

---

## Why this exists

AI is great at exploration and terrible at refinement — asked for "a modern logo," it returns the *legible
middle*: the average of everything, which reads as slop. Distinctiveness does not come from the model; it comes
from a **specific strategy** and a **specific constraint** ("like Stripe but warmer, avoid blue" — not
"modern/clean/professional"). If you generate visuals before the positioning, archetype, and voice are
authored, you are generating against nothing, and no amount of prompting rescues it. The strategy substrate is
what a Looka-class tool skips and what makes the engagement worth its tier.

## How to apply

- Author the `brand-strategy-brief.md` — positioning, value prop, audience, archetype — **before** any concept
  generation. This file is the gate artifact.
- Make it a **hard precondition**: `logo-and-visual-system-direction` and `/generate-identity-concepts` refuse
  without it. If asked for logos first, decline and author strategy first.
- Write the generation brief with **specific + negative constraints** derived from the strategy, not vibes.
- Keep positioning/archetype **human-authored** — the model explores; the human decides.

**Do:** author strategy, then direct generation against it with specific constraints.
**Don't:** generate concepts to "see what the AI comes up with" before the position exists.

## Edge cases / when the rule does NOT apply

A quick throwaway moodboard to *stimulate* the discovery conversation is fine — but it is not a concept, is not
shown to the client as a direction, and does not substitute for the authored strategy brief.

## See also

- Skill: [`../skills/brand-strategy-and-naming/SKILL.md`](../skills/brand-strategy-and-naming/SKILL.md)
- Template: [`../templates/brand-strategy-brief.md`](../templates/brand-strategy-brief.md)

## Provenance

Codifies the `brand-strategist` house opinion and B11 (humanagency.com; superside.com; typeface.ai — AI is
exploration-only + human-curated). Retrieval 2026-07-13.

---

_Last reviewed: 2026-07-13 by `claude`_
