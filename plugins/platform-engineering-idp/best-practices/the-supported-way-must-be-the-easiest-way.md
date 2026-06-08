# The supported way must be the easiest way

**Status:** Absolute rule
**Domain:** Golden-path design
**Applies to:** `platform-engineering-idp`

---

## Why this exists

Developers follow the path of least resistance. If doing it the supported way is harder, slower, or
more confusing than rolling their own, they'll roll their own — and no amount of documentation,
evangelism, or policy will durably win against ergonomics. A paved road is defined by being easier,
not by being blessed.

## How to apply

- Measure the friction of the supported path against the DIY path honestly (steps, time, decisions).
- Remove friction until the supported way wins on ergonomics: one command / one button / sane
  defaults / no yak-shaving.
- If you can't make it easier than DIY yet, it isn't paved — keep working before you promote it.

**Do:**

- Time the "create a new service" journey end-to-end; drive it down.
- Bake in defaults so the team gets CI/observability/security/ownership for free.
- Treat every manual step on the happy path as a defect.

**Don't:**

- Promote a path that's harder than the DIY alternative.
- Rely on mandates/docs to compensate for poor ergonomics.
- Add config knobs that re-introduce the decisions the path was meant to remove.

## Edge cases / when the rule does NOT apply

Early on, a path may be only *marginally* easier; that's fine if it's improving — but never promote a
path that is *harder* than DIY.

## See also

- [`./pave-the-80-keep-an-escape-hatch.md`](./pave-the-80-keep-an-escape-hatch.md)
- [`./reduce-cognitive-load-is-the-charter.md`](./reduce-cognitive-load-is-the-charter.md)

## Provenance

Codifies the golden-path/paved-road ergonomics principle from platform-engineering practice (Spotify,
Netflix) and the DevEx literature on minimizing friction in the inner loop.

---

_Last reviewed: 2026-06-08 by `claude`._
