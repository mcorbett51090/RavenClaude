<!-- RAVENCLAUDE-STAGING-METADATA
type: best-practice
topic: architecture
proposed-by: consumer project managing a Copilot Chat/CLI context-budget overflow
proposed-on: 2026-09-09
target-file: docs/best-practices/bulk-wiring-needs-persistent-exclusion-policy.md
status: pending
-->

# Bulk-wiring steps need a persisted exclusion policy, not after-the-fact pruning

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Agent design, cross-domain.

**Applies to:** Any tool with a "setup / install / sync / generate" step that writes many files or symlinks into a project directory in bulk, especially one designed to be safely re-run (idempotent). Includes RavenClaude's own `wire_plugin_skills()`, but generalizes to any codegen/scaffolding/vendoring tool.

---

## Why this exists

An idempotent bulk-wiring step (re-run it any time, it re-materializes everything) is good design for correctness — it means you never have to diagnose "is my install stale." But it has a blind spot: if a consumer wants to exclude some of what gets wired (because it's irrelevant to their project, or because it costs something real — disk, token budget, review surface), a separate exclusion pass applied *after* wiring is fighting the tool's own idempotency. Every re-run of the wiring step silently undoes the exclusion, because the wiring step has no concept that an exclusion was ever applied — it just re-writes its full, unconditional output.

This produces a specific, easy-to-miss failure: the exclusion tool *works* (it reports success, moves/deletes the right things), and then quietly stops working again the next time the wiring step runs, with no error and no warning — because from the wiring step's point of view, nothing went wrong. It did exactly what it always does.

## How to apply

**Do:**
- Give the bulk-wiring step itself an optional, persisted policy input (a project-level config file it reads before writing) — an allow-list or deny-list of what to wire. Absent policy file = today's unchanged full-roster behavior, so this is purely additive and never a breaking change for existing consumers.
- Make any post-hoc curation/pruning tool for the same content aware of ALL the ways that content can arrive (symlinks *and* copies *and* generated files), not just the one it was originally written to handle. If the tool structurally cannot see a whole category of the content, its "nothing to fix" report should say so explicitly rather than implying completeness.
- When a curation tool acts on the same output directory as a wiring step, document the interaction explicitly: what does a re-run of the wiring step do to the curation tool's prior decisions?

**Don't:**
- Don't treat "the curation script ran and reported success" as proof the underlying cost is actually reduced, without checking whether the script's own scope covers the majority of what's actually there.
- Don't rely on "remember to re-run the prune script after every update" as the durable fix — it's a process step a human (or a future agent session) will eventually skip, and the failure mode when they do is silent, not loud.

## Edge cases / when the rule does NOT apply

- One-shot, non-idempotent installers (run once, never re-wire) don't have this problem — a post-hoc exclusion pass is stable because nothing regenerates the excluded content later.
- If the wiring step's output volume is small enough that manual curation is genuinely cheap and low-risk to forget (a handful of files, not hundreds), the added complexity of a policy-file mechanism may not be worth it — judge by blast radius of "someone forgets to re-apply," not by principle alone.

## See also

- The companion lesson entry (same date) with the concrete story this generalizes from.

## Provenance

Generalized from a concrete incident: a project's local skill-catalogue prune script explicitly skipped symlinked content ("leave the marketplace wiring alone"), which turned out to be 90% of the actual catalogue — all of it wired unconditionally by a setup script's bulk-symlink step on every run, with no way for an exclusion to persist across re-runs.

---

_Last reviewed: 2026-09-09 by consumer-project session_
