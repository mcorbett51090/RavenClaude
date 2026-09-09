# G0 — Scope

## Scoped intent

Design and land the **mechanism** that catches Incident 1's shape — *unbounded construction on an
unfalsified premise* — at the point where it is still cheap: **before the build phase, not after**.
The mechanism must work both inside FORGE (planned work) and in ordinary agentic work (where all
three incidents actually happened). Secondary: close Incidents 2 and 3 where the same checkpoint or
an adjacent cheap gate covers them.

**Owner:** Matt Corbett. **Repo:** `RavenClaude`, branch `feat/verification-discipline` (PR #849 open
on the same theme — this extends it rather than opening a second PR).

## The one-line success signal

Replaying Incident 1, the mechanism forces the `/cdn-cgi/trace` control probe (or a browser render
check) **before** `Email.astro` is written — not after 16 files have changed.

## Explicitly in scope

- A FORGE gate or gate-amendment that separates **observation** from **inference** and requires a
  disconfirming probe for any inference a build phase depends on.
- A trigger sized by **blast radius** (files touched, new abstraction introduced, existing working
  behaviour changed) — the checkpoint must be proportional, not universal friction.
- Wiring into the non-FORGE path: agent definitions (`architect`, coders) and/or hooks, since
  Incident 1 happened outside FORGE.
- Cheap mechanized gates where they exist: a knowledge-file orphan check, a pre-commit diff-budget
  trip. Both are directly evidenced by Incidents 2 and the `consistency-failure-modes.md` orphan.

## Explicitly OUT of scope

- Restating the seven prose rules (shipped in PR #849). Prose is the thing that failed.
- Anything requiring Cloudflare dashboard access, or changes to `RavenPower-Website` product code.
- Rebuilding FORGE's depth ladder or artifact contract. Amend, do not restructure — an ironic
  restructure is the one outcome this run must not produce.
- Model-behaviour speculation ("the model should think harder"). Mechanisms only.

## Hard constraints any proposal must satisfy

1. **Fail-closed** — consistent with every other FORGE gate.
2. **Proportional** — must not add meaningful friction to a `micro`/`quick` run that touches one
   file. A gate that makes every trivial run expensive will be disabled, and then it protects
   nothing.
3. **Fits the §0 artifact contract** — payload on disk, receipt back.
4. **Must handle the un-testable premise.** Sometimes the kill-shot needs prod access or the owner.
   The mechanism must have a defined path for that case, not just block.
5. **Must survive the honest objection**: at the moment of Incident 1 I was *confident and wrong*,
   with a real tool call behind me. A mechanism that relies on the author noticing their own
   uncertainty will not fire, because there was none.

## Assumptions recorded rather than asked

The owner said "keep going", so no blocking questions were raised. Two forks were resolved by
recommendation and are flagged for reversal:
- **Friction**: proposals should default to *fail-closed but narrowly triggered* rather than
  advisory. An advisory checkpoint is prose with extra steps.
- **Landing**: extends PR #849 rather than opening a second PR on the same theme.
