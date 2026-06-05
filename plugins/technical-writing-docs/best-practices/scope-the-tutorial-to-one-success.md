# Scope a Tutorial to Exactly One Successful Outcome

**Status:** Pattern
**Domain:** Technical Writing — Tutorials (Diataxis)
**Applies to:** `technical-writing-docs`

---

## Why this exists

A tutorial that promises "you'll learn the whole SDK in this guide" sets the reader up to fail or quit halfway. Tutorial completion rates collapse when the path is too long and the finish line is invisible. The tutorial's job is to give a learner their *first success* — a concrete, observable result that proves the system works and builds their confidence to explore further. One tutorial, one success, one result the learner can see. Everything else is a separate tutorial or a how-to guide.

## How to apply

**Tutorial scope checklist:**

- [ ] The success outcome is defined in one sentence before writing begins ("by the end, the user has uploaded their first file and can see it listed in the dashboard").
- [ ] The tutorial can be completed in 15–30 minutes; if it takes longer, split it.
- [ ] Every step produces a visible, observable result the reader can check.
- [ ] No step requires the reader to understand *why* — that is an explanation doc.
- [ ] The tutorial ends at the first success, not at "and now you know everything."
- [ ] The learner environment is controlled: a sandbox, a CLI quickstart, or a starter template; not "install these 12 prerequisites."

**Good tutorial anatomy:**

```markdown
## What you'll build

<One sentence: the concrete thing the reader will have working when they're done.>

## Before you start

<Minimum prerequisites — numbered, specific, testable.>

## Step 1 — [Action verb] [thing]

<Do this. Then run: `<exact command>`. You should see: `<exact output>`.>

## Step 2 — [Action verb] [thing]

<…>

## You did it

<State what they built. Link to the next tutorial or to how-to guides for next steps.>
```

**Do:**
- Use a verified "definition of done" for the tutorial: run through it in a fresh environment and confirm the stated outcome is achievable in the stated time.
- End every step with an observable check ("you should see…", "the output should contain…").
- Link to the explanation docs for "why this works" — do not embed them inline.

**Don't:**
- Add "bonus exercises" or "advanced variations" at the end — that blurs the tutorial into a course.
- Require the reader to make design decisions ("choose between option A or B") — tutorials are linear.
- Update a tutorial to cover a new feature without verifying that the complete tutorial still works end-to-end.

## Edge cases / when the rule does NOT apply

- **Learning paths / series**: a series of focused tutorials each scoped to one success is correct; the series title can span a broader topic as long as each individual tutorial is still one outcome.
- **Platform-specific variations**: if the same tutorial exists for AWS, GCP, and Azure, each is a separate tutorial document — do not merge them into one with conditional branches.

## See also

- [`../agents/docs-architect.md`](../agents/docs-architect.md) — scopes the tutorial against the overall docs strategy
- [`./know-which-diataxis-kind.md`](./know-which-diataxis-kind.md) — confirms this is a tutorial (learning), not a how-to (task)

## Provenance

Codifies house opinion #1 ("Know which of the four kinds you're writing") applied to the tutorial kind. Tutorial design from Diataxis (Procida, diataxis.fr — "Tutorials are learning-oriented and must land the learner in a place where they can do something"). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
