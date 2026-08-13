# Validating a measuring instrument before you act on it

**Status:** **Primary diagnostic** — when a newly-written checker reports a batch of
findings, verify the checker before you fix the subject.

**Domain:** Agent design, verification discipline, cross-domain.

**Applies to:** `any Claude Code project` — any code whose *output is a claim about other
code*: an audit script, a linter, a render test, a coverage report, a benchmark, or an
ad-hoc analysis harness written for one investigation.

---

## Why this exists

A newly-written measuring tool produced **3,337 findings**, each with precise, credible
numbers ("contrast 1.00:1", "target 46x24 and crowded"). **About 99% were false.** Acting
on the batch would have:

- "fixed" a badge that renders perfectly well, making it worse,
- rewritten 15 inputs whose `<label for>` markup was already correct,
- added focus rings to 3,187 elements that already had them,
- restyled 2,397 diagram toggles that met the criterion via a documented exception.

Nothing crashed. Every number had the right *type* and the wrong *value*. The tool ran,
exited 0, and lied fluently.

This is the same shape as the nine
[silent-green defects](../../plugins/ravenclaude-core/CLAUDE.md) that passed build, tests
and CI — moved up one level, into the thing you were going to use to *find* defects. It
is worse there, because a wrong gate corrupts every conclusion drawn from it.

## How to apply

> **A new measuring tool's first output is a claim about the tool, not about the subject.**
> Before acting on a batch of findings, verify a sample of them against a source that did
> not come from the same code path.

"A different source" means: read the source the finding names, do the arithmetic by hand,
check the primary doc, or ask the platform directly. It does **not** mean re-running the
tool, adding logging, or reasoning about whether the check "should" work.

### Three cheap triage steps, in order

**1. Implausible volume is a bug report about the checker.**
2,397 findings on one component. 3,187 on one CSS property. 185 "overlapping" targets.
Real defects cluster, but they do not carpet. Before reading a single finding, ask whether
the *count* is credible for a codebase people use every day. This step costs nothing and
caught three of the six bugs below.

**2. Trace exactly one finding to its source.**
Not the batch — one. Pick the highest-severity or highest-count finding and follow it to
the line of source that supposedly causes it. Six of six harness bugs were caught this
way, each in a single lookup. The corollary: **do not fix anything until one finding has
survived this.**

**3. Ask the platform instead of modelling it.**
Every one of the bugs below encodes an assumption about browser behaviour that was
confident, plausible, and wrong. Where the platform exposes an API that answers the
question — `Element.checkVisibility()` here — use it. Your reimplementation encodes your
beliefs; the platform's encodes the behaviour.

### The six wrong checks, and why the wrong version is the obvious one

Kept concrete on purpose: in each case the wrong implementation is what a competent
person writes first.

| The check | What it claimed | Why it was wrong |
|---|---|---|
| Backdrop by DOM-ancestor walk | a badge was invisible at 1.00:1 | An `absolute; bottom:-16px` badge paints over the *page*, not its parent's fill. Escaping the parent box is normal. |
| Backdrop by `elementsFromPoint` | amber/green backdrops behind ordinary body copy | It returns elements *above* the target too. A `position: fixed` banner became the "backdrop" of the header it was covering. |
| Accessible name from text/ARIA | 15 correctly-labelled inputs were "unnamed" | It never resolved `<label for>` or an ancestor `<label>` — the two most common ways a field gets its name. |
| `el.focus()` then diff computed style | 3,187 elements had "no focus indicator" | `.focus()` does not match `:focus-visible` in Chrome; and an **unfocused** element's computed `outlineStyle` is `none` for nearly everything, so "outline is none" is not evidence of suppression. |
| Bounding box `< 24×24` | 2,397 diagram toggles failed WCAG 2.5.8 | The criterion has spacing / inline / user-agent-control exceptions. A criterion implemented without its exceptions is a different, stricter criterion. |
| Hand-rolled visibility test | 185 targets "overlapped" each other | Chrome implements a **closed `<details>`** with `content-visibility: hidden`, not `display: none`, so its contents keep non-zero layout boxes. 126 of 128 collapsed cards' invisible contents piled up at the same coordinates. |

## Edge cases

### Two further traps, both of which nearly landed

**A true finding can name a false cause.** A real 45px horizontal overflow was reported
with a correctly-scrolling 881px table as its widest offender — because elements inside an
`overflow-x: auto` container are *legitimately* wider than the viewport. The detection was
right; the attribution was wrong; the fix it implied was wrong. **Check the cause, not just
the finding.**

**Your conclusion is bounded by your coverage.** "No `minmax` grid overflows — measured"
was true at 375px and false at 320px, where a 340px track blew the page out on every
route. State the widths, themes, and surfaces a negative result was measured at, or the
negative result is not a result.

### Corollaries worth their own line

**A found defect is a sample of a class — grep for the class.** The browser audit found
`--border` (a 7%-alpha hairline token) used as a text colour in one rule. A grep found a
second instance the browser could not see, because it coloured an SVG icon rather than
text. Two instances, one class, one of which no amount of browser auditing would reach.
After fixing any defect, spend one grep asking how many siblings it has.

**Audit the least-forgiving surface, and know which one that is.** When one surface embeds
another, the embedding surface can supply defaults the embedded one lacks. The portal
supplies a link colour; the standalone `dashboard.html` — the artifact consumers actually
receive — had none, so every inline link in it fell back to `#0000EE` at about 2:1. The
surface we look at daily was structurally incapable of showing the bug. This is the third
instance of the two-surface class in this repo; the first two were about routing and
placement, so the general form is: **check the shipped artifact on its own, never by proxy.**

**A finding is a question, not an instruction.** Two findings were verified *correct by
design* and deliberately left alone (routes that render identically because a section
resolves to its own default tab; the Help page's documented redirects). And a target
measuring 23.984375px against a 24px threshold — a 1/64-pixel artifact of Chrome snapping
an `inline-block` to its line box — was resolved with a documented tolerance in the
checker, **not** with `min-height: 25px`. The fix that silences the checker is not always
the fix that improves the product, and CSS that lies about its intent is a worse outcome
than a tolerance that states one.

**A verifier that caches its input will eventually lie in both directions.** A test harness
that embedded the page's text at creation time reported the old text after a real fix had
landed — nearly causing a correct change to be reverted. Its mirror also happened this
session: a string replacement silently no-opped and success was reported, because nothing
asserted the replacement had occurred. Both are the same defect. **Re-derive the input from
the source of truth on every run, and assert what you print** — the repo's
derive-don't-maintain principle applies to the verification layer, not just to product code.

## How this composes with the existing gate discipline

[`ci-gate-audit.md`](ci-gate-audit.md) requires every committed gate to prove it
**fails on known-bad and passes on known-good**. That is necessary and it is not
sufficient here, in two specific ways:

1. **It is fixture-scale; this failure is corpus-scale.** Every wrong check above would
   have passed a single known-good fixture while flagging thousands of real elements.
   A `pass-on-good` proof over one fixture does not bound the false-positive rate over a
   real codebase.
2. **The dangerous direction is inverted.** A gate's teeth-test asks *"does it catch
   bad?"* — false negatives. An audit tool's costly failure is *"does it invent bad?"* —
   false positives, because those get acted on. Test both directions explicitly; the
   `--must-fail` half of [`check-css-token-hygiene.py`](../../scripts/check-css-token-hygiene.py)
   asserts 7 known-bad caught **and** 8 known-good left alone for exactly this reason.

And the practice that made the loop trustworthy: **mutation-test between clean passes.**
Two consecutive zero-finding runs prove nothing if the checker broke in between. Reintroduce
two or three of the defects you just fixed, confirm each is caught, restore, and re-run.
Without that step, "0 findings" and "the tool is broken" are indistinguishable — which is
the entire failure mode this document exists to prevent.

## Provenance

Extracted 2026-07-29 from a looped browser-driven UI/UX audit of `index.html` and the
shipped `plugins/ravenclaude-core/dashboard.html` (21 routes x 4 viewports x 2 themes).
The audit found and fixed 24 real defects; it also produced ~3,300 false ones across six
successive versions of its own checks, each corrected before any product code changed.

- Story form (dated, with what was tried first): [`../memory-bank/lessons-learned.md`](../memory-bank/lessons-learned.md)
- The gate that came out of it: [`../../scripts/check-css-token-hygiene.py`](../../scripts/check-css-token-hygiene.py) (Gate 174)
- The complementary fixture-scale discipline: [`ci-gate-audit.md`](ci-gate-audit.md)
- Where this rule sits vs. the log: [`lessons-vs-best-practices.md`](lessons-vs-best-practices.md)
