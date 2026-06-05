---
scenario_id: 2026-06-05-blocked-report-skipped-alternate-methods
contributed_at: 2026-06-05
plugin: ravenclaude-core
product: orchestration
product_version: "n/a"
scope: likely-general
tags: [capability-grounding, alternate-methods, blocked-report, read-the-error, mcp-deferred-tool, false-negative]
confidence: medium
reviewed: false
---

## Problem

A session was asked to open a PR from a remote/web environment. It ran `gh pr create`, got `command not found`, tried the direct GitHub API, got a `403`, and reported back: *"I can't create a PR in this environment."* That report was a **false negative** — the costliest CGP failure, because it silently abandons work and burns a round-trip. Two routes failing is evidence about *two routes*, never proof the capability is absent: the sanctioned path here was the GitHub **MCP** tool (`mcp__github__create_pull_request`), which was *deferred and not yet schema-loaded*, so it looked absent. The blocked report skipped the alternate-methods enumeration entirely — it never named the third path, never read the `403` body, and never loaded the MCP route before concluding "can't."

## Context

- Surface: domain-neutral, `ravenclaude-core`. The governing rule is the Capability Grounding Protocol (CLAUDE.md §"Capability Grounding Protocol" + §"Try alternative paths before declaring blocked").
- The specific clause violated is the **"absent tool / unloaded tool" variant** — "a `command not found`, an HTTP 401/403, or a deferred MCP tool whose schema isn't loaded yet — **none of these is proof the capability is absent — each is evidence about one route.**" A deferred MCP tool returns a validation error / shows name-only until tool-discovery runs; a missing schema is "not loaded yet," never "doesn't exist."
- The skipped step-0 is **"Read the error before you re-route"**: name the *specific mechanical cause*, not the error class. A `command not found` means the tool is absent *on this host* (→ find the sanctioned route); an insufficient-scope `403` means a surface that already holds the scope; an expired-token `401` means re-auth then **retry the same route**. The cause selects the next move and is not interchangeable.
- Why it slipped: a CLI dead-end *feels* like a verdict on the goal. It isn't — it's a verdict on the CLI.

## Attempts

- Tried: `gh pr create` → `command not found`; direct API → `403`; reported "blocked." Outcome: false-negative blocked report — the round-trip wasted, the third path never named or tried.
- Tried: step-0 diagnosis — read what was already in hand. `command not found` = `gh` absent on *this* host (not "PRs impossible"); the `403` body = a surface/permission limit on *that* route, not the goal. Outcome: the causes select different next moves; neither closes the goal.
- Tried (the move that worked): load the *sanctioned* route before concluding anything. The MCP github tool was deferred — run tool-discovery first (it awaits the connecting server and loads the schema), then call `mcp__github__create_pull_request`. Outcome: the PR was created via the route the two dead-ends never ruled out, with no human round-trip.

## Resolution

The defect was **generalizing two route failures into a missing capability** — and skipping the alternate-methods enumeration that would have surfaced the third route. CGP's floor is: read the error (name the mechanical cause), enumerate ≥2 alternative paths, try the next-easiest, and report blocked *only* with the this-session checks you ran and the alternatives tried. A wrong/absent-looking route is not a missing capability; a deferred MCP schema is "not loaded yet," not "doesn't exist."

**Action for the next session that hits a wall:** before any "I can't" leaves the agent — (0) read the actual error and name its *specific* cause (status code + body/stderr, not the headline); (1) load the sanctioned route first — a deferred/"still connecting" MCP tool must be searched/awaited before you call it, and a missing-schema error is a not-loaded-yet signal; (2) enumerate ≥2 alternatives and try the next-easiest; (3) report blockage only with the mandatory-phrasing shape ("After trying A — outcome, B — outcome, I am blocked on [specific reason]; the remaining options are X, Z"). `[verify-at-use]` which PR route is live in the active environment — `gh`, the direct API, and the github MCP path each work or fail per-host (see root CLAUDE.md §"Remote-environment PR mechanics").
