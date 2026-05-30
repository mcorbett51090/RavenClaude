# Write microcopy that acts: verb CTAs, fix-named errors, unified terms

**Status:** Pattern — CTAs are verbs with destination context, error messages name the fix, and terminology stays consistent across every surface.

**Domain:** Content / Microcopy

**Applies to:** `web-design`

---

## Why this exists

Microcopy is load-bearing: the CTA text, the error message, the empty-state line, the button label are where the user decides and acts — they convert or they don't. The `content-strategist`'s positions are specific and testable: CTAs are verbs ("Create account," not "Submit"), error messages name the fix not the problem ("Email must include @" beats "Invalid email"), microcopy is unified across surfaces ("Sign in" everywhere, not "Log in" on one page). It also intersects a11y directly: "click here"/"read more" link text gives screen-reader users (who often navigate by a list of links out of context) no destination, and directional/sensory language ("the green button on the right") breaks for screen readers and color-blind users.

## How to apply

Make every CTA an action verb that says where it goes; write errors that tell the user what to do; pick one term per concept and use it everywhere.

```html
<!-- CTA: a verb with destination context, not "Submit" / "click here" -->
<button type="submit">Create account</button>
<a href="/pricing">See pricing plans</a>          <!-- not "click here" / "read more" -->

<!-- Error: names the fix, carries icon + text (never color alone), associated to field -->
<p id="pw-err" class="error" role="alert">
  <svg aria-hidden="true">…</svg> Use at least 8 characters, including a number.
</p>
```

**Do:**
- Make CTAs verbs with context ("Start free trial," "Download the report"); keep the same term for the same action site-wide.
- Write errors that name the fix and pair the state with an icon + text (color is never the only signifier, SC 1.4.1).
- Write link text that describes its destination out of context; expand acronyms on first use.

**Don't:**
- Ship "Submit"/"click here"/"read more" or directional language ("the button below/on the right").
- Drift terminology ("user" / "customer" / "member" used interchangeably on the same site).
- Name the problem without the fix ("Invalid input") or rely on red text alone to signal an error.

## Edge cases / when the rule does NOT apply

- **Established platform conventions** (a "Search" button, a standard "Cancel") are verbs/terms users already know — don't reinvent them for novelty.
- **Destructive-action confirmations** want explicit, slightly heavier copy ("Delete 3 projects permanently") — clarity outranks brevity when the action is irreversible.
- **Branded voice moments** (a playful empty state) are fine *as long as* the action remains unambiguous; personality never costs comprehension.

## See also

- [`./ux-form-design-and-error-handling.md`](./ux-form-design-and-error-handling.md) — where these error messages attach (`aria-describedby`)
- [`./ux-one-cta-and-state-coverage.md`](./ux-one-cta-and-state-coverage.md) — the CTA this copy fills, and empty-state copy
- [`./content-readability-and-hierarchy.md`](./content-readability-and-hierarchy.md) — the larger content hierarchy these units sit in
- [`../agents/content-strategist.md`](../agents/content-strategist.md) (CTA verbs, fix-named errors, unified terms), [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) (link text, color-only signifiers)

## Provenance

Distilled from the `content-strategist` opinions/anti-patterns (CTAs are verbs; "Submit" is an anti-pattern; errors name the fix; microcopy unified across surfaces; terminology drift; directional/sensory language) and the `accessibility-auditor` anti-patterns ("click here" link text; color-only status). Retrieved 2026-05-28.

---

_Last reviewed: 2026-05-30 by `claude`_
