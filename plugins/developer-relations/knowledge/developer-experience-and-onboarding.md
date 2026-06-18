# Knowledge — Developer experience & the onboarding (time-to-first-success) path

> **Last reviewed:** 2026-06-18 · **Confidence:** High (DX golden-path principles are
> well-established and product-agnostic). The `developer-advocate` and `devrel-strategist` both use
> this for the onboarding audit; it underwrites the `developer-onboarding-funnel` skill and the
> `developer-onboarding-audit` template.

The single highest-leverage surface in DevRel is the path from *landed* to *first working result*.
This file is the method for finding and fixing the leaks in it.

---

## The golden path

The **golden path** is the one, blessed, shortest sequence that gets a brand-new developer to a first
working result. It is not "all the ways you *can* use the product" — it is the one you *guarantee*
works, end to end, from a clean machine.

Properties of a good golden path:

- **Linear.** No "choose your adventure" before first success. Branch *after* they've won once.
- **Copy-paste-runnable.** Every command/snippet runs unmodified. No "set your config first" without
  showing exactly what to set.
- **Honest about prerequisites.** State the runtime/version/account needs up front, not at step 7.
- **Ends in a visible win.** The developer *sees* something work (a response, a rendered page, a
  printed result) — not "you have now configured the client."

---

## The time-to-first-success (TTFS) audit

Walk the golden path as a hostile first-timer on a clean environment and count:

1. **Steps to first success** — every discrete action (install, sign up, get a key, copy code, run).
   Each step is a place to lose someone; the count *is* the metric.
2. **Friction per step** — anything that makes a developer stop and think:
   - an unstated prerequisite,
   - a secret/key with no obvious place to get it,
   - a copy-paste block that doesn't actually run,
   - a step that requires reading something elsewhere,
   - an error with no recovery path.
3. **The first dead end** — where does a reasonable developer get stuck and have no next move? Fix
   this before anything downstream; nothing past the first dead end matters.

Output a **drop-off map**: a numbered list of steps, the friction on each, and the fix. The template
[`../templates/developer-onboarding-audit.md`](../templates/developer-onboarding-audit.md) is the
fill-in form.

---

## DX principles (the checklist)

- **Get the key into the code as fast as possible.** Auth/setup is where developers churn; minimize it.
- **One teaching goal at a time.** A quickstart that also explains your architecture teaches neither.
- **Errors are a DX surface.** A good error says what's wrong *and* what to do next; a sample's errors
  are part of the demo.
- **Defaults that work.** The zero-config path should do something useful before any tuning.
- **Don't make them read to act.** Show the runnable thing first; explain after they've seen it work.
- **No placeholder secrets in a sample.** `YOUR_API_KEY` is acceptable as a clearly-marked
  substitution; a real-looking fake key or a `TODO: add auth` in the happy path is a defect
  (the hook flags this).

---

## Where DX hands off

- The **docs system** that hosts the golden path (IA, Diátaxis, the docs site) → `technical-writing-docs`.
- The **API contract** whose errors and shapes the golden path exercises → `api-engineering`.
- The **product decision** that the golden path should exist at all → `product-management`.
- This file owns the *developer-experience read* of the path: is it short, honest, and runnable?

---

## Provenance

Codifies developer-relations CLAUDE.md §3 house opinions #3 (sample code runs as shipped) and #4
(time-to-first-success is the product). The golden-path / TTFS framing is standard DX practice; the
audit method is a concrete application, not a quoted external benchmark.

---

_Last reviewed: 2026-06-18 by `claude`_
