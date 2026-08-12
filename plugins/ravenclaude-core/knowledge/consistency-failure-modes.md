# Consistency failure modes — the ones that ship green

> **Provenance.** Every entry was found empirically in `RavenPower-Website`
> (2026-08-06) by measurement, not review. It is kept here because the failure
> modes are **substrate-level, not project-level**: nine of the ten reproduce in
> any Astro/CSS/SSR site, and the tenth (SSR pages never reaching `dist/`) is a
> property of every server-rendered route this org ships.
>
> Companion to `raven-site-kit/floor.json`, which states the BARS. This states
> the ways a bar is met on paper and missed in fact.

Every failure below was found in this codebase by **measurement**, not by review.
Each one passed `astro check`, passed the full test suite, and produced a clean
build while being broken in production. That is the defining property: if a
failure mode announced itself, it would not need a catalogue.

This is the companion to `raven-site-kit/floor.json`, which states the *bars*.
This file states the *ways a bar is met on paper and missed in fact*.

**The honesty rule, inherited from `floor.json` and restated because it is the
thing most often forgotten:** a green run of any check below proves the
mechanized subset held. It does not prove the property held. Six of the ten
entries here exist *because* someone read a green check as the broader claim.

---

## 1. Imported but never rendered

**What happened.** `PortalLayout.astro` carried
`import { ClientRouter } from 'astro:transitions'` with no `<ClientRouter />`
anywhere in the markup. Every portal navigation was a full page reload for weeks.

**Why nothing caught it.** An unused import is legal TypeScript and legal Astro.
Clean build, `astro check` 0 errors, 2246 tests passing. Worse, the failure has
*no rendered trace*: `transition:persist` stamps `data-astro-transition-persist`
at **compile** time, so the DOM looked exactly like a working setup and a probe
counting persisted nodes returned the right answer. The only thing missing was
the client that swaps them.

**Cost.** Two user-visible bugs — page flash on every navigation, and the rail
collapsing on every click — each "fixed" more than once against the wrong cause.

**The check.** Assert the **tag**, not the import:

```ts
const markup = src.slice(src.indexOf('---', src.indexOf('---') + 3) + 3);
expect(markup).toMatch(/<ClientRouter\b/);
```

**Generalizes to:** any component whose only job is a side effect — routers,
analytics, service-worker registrars, theme scripts. Importing one is not using
one, and the compiler cannot tell the difference.

---

## 2. Presence is not visibility

**What happened, five separate times in one session:**

- Rail icons were "present" (9 nodes, non-zero bounding boxes) and invisible.
- A probe reported `.nav__auth` = 0 visible on the site, concluding auth was
  removed — while a second, independent sign-in button sat in the homepage hero.
- A hit-test probe reported `.portal` blocking taps; it was probing point
  `(0,0)`, because a `display:none` element returns a 0×0 rect.

**Why nothing caught it.** `querySelectorAll().length` and
`getBoundingClientRect().width > 0` both answer questions adjacent to the one
being asked. An SVG drawn with `fill="none"` + `stroke="currentColor"` has a
full-size bounding box with nothing painted.

**The check.** Assert the property that *defines* the effect:

```ts
// not: does it exist?          not: does it have a box?
// but: does it paint pixels, and is the computed stroke visible?
const distinctColours = new Set(pixelsOf(await el.screenshot())).size;
expect(distinctColours).toBeGreaterThan(1);
```

**Generalizes to:** anything where the visual result is the requirement. Scope
the probe to the whole page, not the component you suspect — the hero button was
invisible to a nav-scoped query that was otherwise correct.

---

## 3. Comment-blind checks

**What happened, five times in one session.** A check read documentation as if it
were code:

- A test asserted `not.toMatch(/white-space:\s*normal/)` and failed on *correct*
  code, because the rule's own comment quoted `white-space: normal` as the old,
  wrong value.
- A CSS parser treated the literal `@media` inside a comment as a real at-rule
  and re-pointed five assertions.
- An edit anchored on `.psurface {` matched the header comment, which quotes
  `.portal, .psurface { --pane: … }` as an **anti**-pattern. The insertion split
  the comment, unbalanced the parser, and made `--pane` count 2 and
  `--portal-rail` count 4.

**Why it recurs.** Well-documented code quotes the thing it forbids. The better
the comment, the more likely it contains the exact string a naive check greps
for. Heavily-commented codebases are *more* exposed, not less.

**The check.** Strip comments before matching — in tests, in parsers, and in
edit anchors:

```ts
const stripComments = (s: string) => s.replace(/\/\*[\s\S]*?\*\//g, '');
```

---

## 4. Scoped CSS that can never match (P2-2)

**What happened.** A rule in one Astro component targeting another component's
element. Astro compiles scoped selectors with a `data-astro-cid-*` attribute on
the subject, so `.prail__link-icon` compiled to
`.prail__link-icon[data-astro-cid-<this-file>]` — an attribute the element does
not carry, because a different file emitted it.

**Why nothing caught it.** Valid CSS. Clean build. The rule simply never applied,
and the measured layout did not move by one pixel — which is the only reason it
was noticed at all.

**The check.** Any rule reaching outside its own component needs `:global()`, and
the assertion is behavioural: change the rule, measure the geometry, and require
it to move.

---

## 5. Equal specificity decided by source order

**What happened.** `.view-switcher--bar` and `.view-switcher` are both
single-class selectors — a tie at `(0,1,0)` — so source order won, and the base
rule was written later. The modifier's `padding` and `margin` were discarded
silently: the control rendered 48px against a 36px row and sat 20px off-centre.

**The check.** When a modifier must beat its base, raise specificity
(`.view-switcher.view-switcher--bar`) rather than relying on order. Reordering
works today and breaks the next time someone moves a block.

---

## 6. Drift that exists only *between* pages

**What happened.** Three console routes rendered 8 navigation destinations while
six others rendered 9, because those three passed
`hasOwnedSubscription={false}` as a literal.

**Why nothing caught it.** Every page rendered. Every page's own test passed. The
rail looks entirely plausible in isolation — the defect exists only in the
*comparison*, which is the one place a per-page test never looks.

**The check.** Iterate every surface, capture the chrome as a structure, and
compare each against the first:

```ts
const key = (r) => JSON.stringify([r.destinations, r.hrefs, r.groups, r.tools]);
expect(rows.every((r) => key(r) === key(rows[0]))).toBe(true);
```

**Generalizes to:** navigation, headers, footers, breadcrumbs, meta tags,
skip-links — anything that must read identically everywhere.

---

## 7. A literal asserting a fact the page never looked up

**What happened.** `hasOwnedSubscription={false}` — a page stating something
about the *viewer* that only a query can establish.

**The distinction that matters.** Not every literal is a bug.
`/account/brief` may state `briefSubmitted={true}` because the route renders
*only* when a submitted brief exists — the route is the proof of its own value.
The rule is therefore narrow, and a blanket ban was tried first and rejected: it
forced two pages to re-query a fact their own existence establishes.

**The check.** Refuse the direction that *removes* things
(`hasOwnedSubscription={false}`) everywhere, and allow route-established literals
only on the routes that establish them — as an explicit allow-list with the
reasoning attached.

---

## 8. New dependency outgrowing an old guard

**What happened.** Two console routes guarded on `!env`, a feature flag and
`isOperator` — but not `!env.DB`, unlike their sibling. Harmless for as long as
they read no database. Adding one line of derivation turned a clean 404 into a
potential 500.

**Why nothing caught it.** The diff that introduced the risk **touched neither
guard**. Nothing in it looked wrong in isolation.

**The check.** Not automatable as a rule. The review question is: *what does this
new code depend on that the old code did not, and is that dependency guarded?*
Recorded here because it is the class of defect a diff-shaped review is
structurally worst at.

---

## 9. One state split across two signals

**What happened.** The expanded rail is three rules — grid track, label
visibility, link alignment. Each was keyed on `:hover`, and browsers only
recompute `:hover` on pointer *movement*. After a soft navigation each lagged
until the mouse moved.

**Cost.** One defect, **three** separate bug reports, each fixed against the
wrong cause before the shared mechanism was found.

**The check.** Assert the invariant, not the instances — every rule keyed on the
open state must also accept the durable signal:

```ts
for (const list of src.matchAll(/([^{}]*portal__rail:hover[^{}]*)\{/g)) {
  expect(list[1]).toMatch(/data-rail-open/);
}
```

**Generalizes to:** any state with more than one visual consequence. If two
declarations describe one state, they must read one source.

---

## 10. SSR pages never reach `dist/`

**What happened.** Repeated attempts to verify portal behaviour by grepping the
build. `/account/**` is `prerender = false`; its markup is generated per request
and its CSS lands in the worker bundle, not `dist/_astro/`.

**The check.** For SSR surfaces, verify against a **running server** with a real
session, or against the worker bundle explicitly. A grep of `dist/` that finds
nothing is not evidence of absence — it is evidence you looked in the wrong place.

---

## How to use this

Before shipping a consistency check of any kind, ask the three questions this
catalogue keeps answering:

1. **Could this pass while the property is false?** (1, 2, 4) — assert the
   property that defines the effect, never a proxy for it.
2. **Could this match documentation instead of code?** (3) — strip comments.
3. **Does this look at one thing, when the defect lives between two?** (6, 9) —
   compare surfaces, and assert invariants over rule *sets*.

And the rule every entry above earns: **a new check's first output is a claim
about the check.** Mutate the source so it *should* fail, and watch it fail,
before trusting a green run. Four of the ten entries here were found exactly that
way — including two where the check was written, passed, and was measuring
nothing.
