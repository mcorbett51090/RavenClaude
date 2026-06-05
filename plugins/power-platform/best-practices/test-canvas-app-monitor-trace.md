# Run Monitor traces against canvas apps before calling them performant or correct

**Status:** Primary diagnostic
**Domain:** Power Platform testing / canvas apps
**Applies to:** `power-platform`

---

## Why this exists

Canvas apps have no console log, no developer tools network tab in the production player, and no test-coverage percentage. The only window into what formulas are evaluating, which connectors are firing, and how long each operation takes is the **Power Apps Monitor** (formerly App Checker). Engineers who declare a canvas app "good enough" without a Monitor trace are flying blind: they cannot see delegation fallbacks, connector call duplication, or silent `IfError` swallows. A single Monitor session adds five minutes to a review and can find a two-second connector call that fires on every keystroke in a search box.

## How to apply

1. Open the app in **Edit mode** → Monitor → Start monitor session.
2. Play the app in a browser tab connected to the monitor session.
3. Exercise every screen and every user action path (including error paths).
4. In the Monitor results, look for:

| Signal | What to check |
|---|---|
| `Network` rows with > 500 ms latency | Is this call triggered correctly, or on every keystroke? |
| `Delegated` = false | Is the delegation fallback understood and accepted? |
| The same connector call appearing > once per user action | Cache the result with a collection, not a raw call |
| `Error` severity rows | Are `IfError` handlers swallowing real errors silently? |
| `Publish` event timing | App OnStart is the most common slow-path — check its duration |

**Do:**
- Export the Monitor trace as JSON and attach it to the PR for any performance-affecting canvas change.
- Use `Trace("label", TraceSeverity.Information, {key: value})` to emit structured trace events for business-logic checkpoints.
- Establish a baseline Monitor trace on a known-clean build so regressions are immediately visible.

**Don't:**
- Use the Monitor as a replacement for Test Studio automated tests — Monitor is a diagnostic tool, not an assertion framework.
- Dismiss `Delegated = false` rows without confirming the table is small enough for the 500-row fallback to be safe.
- Close the monitor session before exercising the error path — the error path is where silent swallows hide.

## Edge cases / when the rule does NOT apply

Canvas apps deployed as embedded components inside model-driven apps may not support the full Monitor network view in some environments. Use the browser developer tools Network tab alongside Monitor for those.

## See also

- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — owns canvas app testing and Monitor workflow
- [`./apps-canvas-performance-budget.md`](./apps-canvas-performance-budget.md) — the performance budget this diagnostic validates

## Provenance

Codifies `power-platform-tester`'s diagnostic discipline from CLAUDE.md §1 and the `canvas-app-performance` skill; Microsoft Learn Power Apps Monitor documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
