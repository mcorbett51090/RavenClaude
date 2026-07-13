---
name: brand-strategy-and-naming
description: "Author the brand strategy substrate BEFORE any visual generation — a discovery questionnaire → positioning statement, value proposition, target audience, and archetype — then bulk-draft business/product names + taglines and hand a human-curated shortlist. Owns the strategy-before-visuals gate artifact. Naming availability + trademark collisions route to security-reviewer; not legal advice."
---

# Brand Strategy & Naming

The first and most expensive brand decision: what the brand *means* and what it's *called*. Everything
downstream — the logo, the palette, the type, the brand book — is directed against this. Author it
deliberately, because a fuzzy position generates slop no matter how good the model is.

> **Strategy is authored, naming is curated. Neither is auto-generated as a final answer.** AI explores;
> the human decides. Any naming-availability or trademark-collision judgment is routed to
> `ravenclaude-core:security-reviewer` (and counsel) — this skill states facts, not legal conclusions.
> Prices `[unverified]`.

## Workflow

1. **Discovery (before anything).** Answer the questionnaire below with the client. Do not skip to a name.
2. **Author the strategy brief.** Fill [`../../templates/brand-strategy-brief.md`](../../templates/brand-strategy-brief.md):
   positioning statement, value proposition, target audience, competitive frame, and archetype (with the
   rejected alternatives named). This file **is** the strategy-before-visuals gate artifact — no visual
   concept is generated until it exists.
3. **Bulk-draft names + taglines.** Generate a longlist (20–40), screen against the shortlist rubric, hand a
   **shortlist to a human**. Never present one auto-picked name.
4. **Flag legal.** For every shortlisted name, flag any obvious trademark collision and recommend a formal
   USPTO clearance search before promising availability — route to `security-reviewer`.
5. **Hand off.** The strategy + voice go to `identity-systems-designer` to direct the visual system against.

## Discovery questionnaire

| # | Question | Why it matters |
|---|---|---|
| 1 | What does the business actually do, in one sentence a stranger understands? | Kills jargon; forces clarity |
| 2 | What is the real alternative the customer is choosing you over (incl. "do nothing")? | Positioning is against the alternative, not a category |
| 3 | Who is the target customer — specifically (not "everyone")? | Audience precision drives voice + visual register |
| 4 | What emotional job does the brand do (status, safety, belonging, rebellion)? | Picks the archetype |
| 5 | Three brands you admire and why — and three you never want to resemble | Constraint donors: "like Stripe but warmer, avoid blue" |
| 6 | What must NEVER be true of this brand? | Negative constraints escape the legible middle |
| 7 | Where does the brand live (site, packaging, app, retail)? | Fixes which identity assets are in scope |

## Positioning statement (the shape)

> For **[target audience]** who **[need/context]**, **[brand]** is the **[category/frame]** that
> **[key benefit / point of difference]** — unlike **[the real alternative]** — because **[reason to believe]**.

Write it, then pressure-test: could a competitor claim the same sentence? If yes, it's not a position.

## Archetype selection (priors)

The 12 brand archetypes (Hero, Sage, Explorer, Creator, Ruler, Magician, Innocent, Everyman, Jester, Lover,
Caregiver, Outlaw) are a **starting lens**, not a horoscope. Pick one primary + at most one secondary; name why
the tempting alternatives were rejected. The archetype constrains voice and visual register — it is a design
input, not a personality quiz. Traverse the **tier-selection** tree in
[`../../knowledge/brand-decision-trees.md`](../../knowledge/brand-decision-trees.md) if the engagement scope is
still open.

## Naming — shortlist rubric

Screen each candidate on:

- **Distinctiveness** — memorable, not a descriptive commodity term (descriptive marks are weak trademarks).
- **Meaning-fit** — supports the position/archetype; no unfortunate second meanings (check other languages).
- **Availability plausibility** — `.com`/handle plausibly obtainable; **obvious** TM collision flagged to
  `security-reviewer` (a real clearance search is counsel's job, not this skill's).
- **Sayability** — spellable on hearing it, pronounceable, works as a verb/handle.
- **Longevity** — doesn't box the company into today's single product.

Present the **shortlist with the rubric scores + the trade-offs**, and let a human choose. Naming types:
coined (Kodak), real-word (Apple), compound (Facebook), descriptive (weak TM), evocative (Nike). Note the type
per candidate.

## Anti-patterns

- Jumping to names/logos before the positioning is authored (the slop factory).
- Presenting one name as "the answer" instead of a curated shortlist.
- Promising a name is "available" without a counsel clearance search.
- A positioning statement a competitor could sign — that's a category description, not a position.
- Picking an archetype and never saying why the others were rejected.

## See also

- Template: [`../../templates/brand-strategy-brief.md`](../../templates/brand-strategy-brief.md)
- Skill: [`../brand-voice-and-messaging/SKILL.md`](../brand-voice-and-messaging/SKILL.md)
- Best-practice: [`../../best-practices/strategy-before-visuals-or-it-reads-as-slop.md`](../../best-practices/strategy-before-visuals-or-it-reads-as-slop.md)
- Knowledge: [`../../knowledge/brand-identity-anatomy-2026.md`](../../knowledge/brand-identity-anatomy-2026.md)
