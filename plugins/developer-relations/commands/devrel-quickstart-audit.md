---
description: Audit a quickstart for time-to-first-success — walk it with a timer, find each friction point (prerequisites, auth cliffs, copy-paste failures, hidden steps), check whether it's CI-tested against the real SDK, and return ranked fixes that shorten the path to first success.
argument-hint: "[the quickstart to audit, e.g. 'our Node SDK getting-started at docs/quickstart.md']"
---

# Audit a quickstart

You are running `/developer-relations:devrel-quickstart-audit`. Audit the quickstart the user
named (`$ARGUMENTS`) following this plugin's `docs-and-samples-engineer` discipline and the
`quickstart-authoring` skill. The quickstart is a product measured by **time-to-first-success
(TTFS)** — the wall-clock minutes from landing to seeing something real work.

## When to use this

A quickstart whose activation/completion rate is low, or one you suspect is too slow or has
silently rotted away from the real SDK.

## Steps

1. **Measure TTFS.** Walk the quickstart top to bottom with a timer (or estimate per step).
   Is a target even declared? If not, that's finding #1.
2. **Count the prerequisites.** Each "first install X / get a key / configure Y" before first
   success is a cliff. For each, ask: can it be cut, deferred past first success, or removed
   with a sandbox key / hosted try-it / one-line installer?
3. **Test copy-paste integrity.** Does every code block run as written, in order, with no hidden
   steps or `# configure this` gaps? Run them if you can.
4. **Check for a single happy path.** Does it branch (options, platform matrix, "you could
   also…") before the developer has succeeded once? Branches before first success kill activation.
5. **Verify the success signal is shown**, not just described — the developer must *know* it worked.
6. **Check the CI guard.** Are the snippets extracted and run against the real SDK on every
   release? If not, the quickstart can silently rot — the highest-leverage fix to recommend.

## Output

Lead with the measured/estimated TTFS and a friction-point list, then **ranked fixes** (highest
leverage first — usually: add a CI test, cut a prerequisite, fix a broken block). Reference
[`../templates/quickstart-template.md`](../templates/quickstart-template.md) for the target shape.
