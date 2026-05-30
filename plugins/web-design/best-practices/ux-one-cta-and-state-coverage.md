# One CTA per screen, and design all five states of every screen

**Status:** Pattern — at most one dominant call-to-action per screen (two max), and every screen ships its default, empty, loading, error, and success states.

**Domain:** UX / Conversion

**Applies to:** `web-design`

---

## Why this exists

Conversion design is choosing what to **remove**, not what to add (house opinion #8: one CTA per screen, two at most, one visually dominant). Five competing CTAs split attention and lower the action rate of all of them. The companion failure is shipping only the happy path: a screen that looks finished in the mock but has no designed empty state ("No items yet" with no path forward), no loading state (a full-screen spinner blocking everything), and no error state. Every screen has at minimum five states — default, empty, loading, error, success — and each is a real surface, with the empty state often the highest-leverage conversion moment.

## How to apply

Decide the single primary action for the screen, give it visual dominance, and demote everything else. Then enumerate and design all five states — empty and error included.

```html
<!-- One dominant CTA; secondary action is visibly subordinate, not equal weight -->
<section class="hero">
  <h1>Ship your site in a day</h1>
  <a class="btn btn-primary" href="/start">Start building</a>     <!-- the one CTA -->
  <a class="btn btn-ghost" href="/demo">Watch the 2-min demo</a>   <!-- subordinate -->
</section>

<!-- Empty state as a conversion surface: tell the user how to start + ONE action -->
<div class="empty-state">
  <h2>No projects yet</h2>
  <p>Create your first project to see it here.</p>
  <a class="btn btn-primary" href="/projects/new">Create a project</a>
</div>
```

**Do:**
- Pick the single primary action per screen; make it the visually dominant element; demote secondary actions.
- Design the empty state as a conversion surface ("here's how to start" + one CTA), not a dead end.
- Show progress for loading (skeleton screens that match the final layout > spinners) and design the error state.

**Don't:**
- Ship 3+ competing CTAs of equal weight, or give a destructive action the same weight as cancel (`ux-designer` anti-patterns).
- Leave an empty state as "No items," a loading state as a blocking full-screen spinner, or an error state undesigned.
- Use "click here"/"read more" for CTA copy — CTAs are verbs with destination context (see microcopy doc).

## Edge cases / when the rule does NOT apply

- **Dashboards / data tables** legitimately expose many actions — the rule is about the *primary* conversion action per screen, not a ban on toolbars; one action still leads.
- **Pricing pages** present multiple tiers by design — one tier is highlighted as recommended (the dominant CTA), the rest are visibly secondary.
- **Navigation menus** aren't CTAs — the one-CTA rule governs conversion actions, not wayfinding.

## See also

- [`./ux-form-design-and-error-handling.md`](./ux-form-design-and-error-handling.md) — the error/empty discipline for forms specifically
- [`./content-microcopy-cta-and-errors.md`](./content-microcopy-cta-and-errors.md) — CTA wording (verbs, destination context)
- [`../agents/ux-designer.md`](../agents/ux-designer.md) (one-CTA, five-states, empty-as-conversion), [`../agents/content-strategist.md`](../agents/content-strategist.md) (CTA copy)

## Provenance

Distilled from house opinion #8 (one CTA per screen, two max) and the `ux-designer` opinions/anti-patterns (every screen has 5 states minimum; empty states are conversion surfaces; skeletons > spinners; disabled-CTA pattern is dead; destructive vs cancel must differ in weight). Retrieved 2026-05-28.

---

_Last reviewed: 2026-05-30 by `claude`_
