---
scenario_id: 2026-06-05-hydration-mismatch-locale-date
contributed_at: 2026-06-05
plugin: frontend-engineering
product: nextjs
product_version: "unknown"
scope: likely-general
tags: [hydration, ssr, rsc, nextjs, mismatch, date]
confidence: high
reviewed: false
---

## Problem

A Next.js App Router dashboard threw `Hydration failed because the server rendered HTML didn't match the client` on the first paint of every page that showed a "last updated" timestamp. In production the symptom was worse than the warning: the timestamp text flickered from one value to another on load, and an `aria-live` region announced the change to screen readers, so assistive-tech users heard the date read twice. The team's first instinct was to suppress the warning with `suppressHydrationWarning` and move on.

## Constraints context

- Server-rendered (RSC + a client island) — the same component runs once on the server and once in the browser.
- The timestamp was rendered with `new Date(updatedAt).toLocaleString()` directly in JSX, with no explicit `timeZone` or `locale`.
- The server ran in UTC; the user's browser ran in `America/Chicago`. `toLocaleString()` with no options resolves the host's timezone and locale, so the two renders produced different strings — a guaranteed mismatch.
- A second, smaller offender on the same page: `Math.random()` used for a "tip of the day" key, which also differs server-vs-client.

## Attempts

- Tried: `suppressHydrationWarning` on the timestamp node. Silenced the console warning but kept the bug — React still discarded the server text and re-rendered on the client, so the flicker and the double `aria-live` announcement remained. Suppressing the warning hides the diagnostic, not the mismatch.
- Tried: moving the whole component to `"use client"` and formatting in a `useEffect`. Removed the mismatch but reintroduced a flash of empty/placeholder content (the timestamp was blank until the effect ran) and shipped the formatting JS to every client — wrong trade for a value that is known at request time.
- Tried (the fix): made the rendered string deterministic across both environments. Formatted the date with an explicit, fixed `Intl.DateTimeFormat(locale, { timeZone, ... })` so the server and client produce byte-identical output, choosing the timezone deliberately (the org's business timezone for this dashboard, with the user-locale variant computed in a client island only where it genuinely had to be user-local). Replaced `Math.random()` keys with a stable id from the data.

## Resolution

**A hydration mismatch is a correctness bug, not a warning to mute.** The rule that fixed it: *the server render and the first client render must be a pure function of the same inputs.* Any value that differs between the two environments — host timezone, host locale, `Date.now()`, `Math.random()`, `window`/`document` reads — will mismatch.

The decision order:

1. **Is the value known at request time and the same for everyone?** Then render it deterministically on the server: pass an explicit `locale` + `timeZone` to `Intl.DateTimeFormat` so the output doesn't depend on the host. This keeps the value in the server HTML (good for first paint and SEO) with no client JS.
2. **Does it genuinely have to be user-local (their timezone/locale)?** Then it depends on the client, so render a stable placeholder on the server and fill it in a client island after mount — and reserve the space so filling it in doesn't shift layout (CLS).
3. **Never** seed render output from `Math.random()` / `Date.now()` / uncontrolled `Date` formatting and then suppress the warning. `suppressHydrationWarning` is for the rare, genuinely-unavoidable single node (e.g. a server-stamped build time you accept differs), not a blanket silencer.

**Action for the next engineer:** when you see a hydration mismatch, don't reach for `suppressHydrationWarning` — find the non-deterministic input. It's almost always an unpinned `Date`/locale/timezone, a random value, or a `typeof window` branch. Pin the input or move the genuinely-client-dependent part into a post-mount island.

Cross-reference: the server-vs-client boundary is the [`../knowledge/frontend-engineering-decision-trees.md`](../knowledge/frontend-engineering-decision-trees.md) "Server component or client component?" tree; the placeholder-reserves-space point is [`../best-practices/avoid-layout-shift-reserve-space-for-async-content.md`](../best-practices/avoid-layout-shift-reserve-space-for-async-content.md). `Intl.DateTimeFormat` options are documented on MDN (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat, retrieved 2026-06-05).
