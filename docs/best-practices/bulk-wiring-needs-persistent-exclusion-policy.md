# Bulk-wiring steps need a persisted exclusion policy, not after-the-fact pruning

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Agent design, cross-domain.

**Applies to:** Any tool with a "setup / install / sync / generate" step that writes many files or symlinks into a project directory in bulk, especially one designed to be safely re-run (idempotent). Includes RavenClaude's own `wire_plugin_skills()` (`scripts/ravenclaude`), but generalizes to any codegen/scaffolding/vendoring tool.

---

## Why this exists

An idempotent bulk-wiring step (re-run it any time, it re-materializes everything) is good design for correctness — it means you never have to diagnose "is my install stale." But it has a blind spot: if a consumer wants to exclude some of what gets wired (because it's irrelevant to their project, or because it costs something real — disk, token budget, review surface), a separate exclusion pass applied *after* wiring is fighting the tool's own idempotency. Every re-run of the wiring step silently undoes the exclusion, because the wiring step has no concept that an exclusion was ever applied — it just re-writes its full, unconditional output.

This produces a specific, easy-to-miss failure: the exclusion tool *works* (it reports success, moves/deletes the right things), and then quietly stops working again the next time the wiring step runs, with no error and no warning — because from the wiring step's point of view, nothing went wrong. It did exactly what it always does.

This is not a hypothetical. `wire_plugin_skills()` in `scripts/ravenclaude` did exactly this until `ravenclaude-core` 0.321.0 (2026-09-09) added `is_skill_wiring_denied()` plus a `skills.deny_plugins` posture key, so the wiring step itself can consult a persisted policy before re-wiring the full roster. That shipped fix is the reference implementation for the rule below — read this doc as documenting *why* that mechanism exists and what its remaining gaps are, not as a proposal to build it.

## How to apply

**Do:**
- Give the bulk-wiring step itself an optional, persisted policy input (a project-level config file it reads before writing) — an allow-list or deny-list of what to wire. Absent policy file = today's unchanged full-roster behavior, so this is purely additive and never a breaking change for existing consumers.
- Choose the policy's granularity deliberately, not by default: a deny-only list (can suppress, can't reorder or replace) is simpler to reason about than an allow-list and fails safer — a typo in a deny-list silently under-suppresses (you get more than expected, a visible surplus), while a typo in an allow-list can silently under-wire something load-bearing. Decide which pieces of the wired content are non-deniable (RavenClaude treats core, non-plugin content as always-wired) and say so explicitly in the policy's own documentation.
- Make the policy's effect **fail loud, not silent**, at every layer where it can fail: a malformed policy file should block wiring (or wire the full unfiltered roster with a visible warning) — never fail open *silently*. Every suppression the policy causes should be logged/echoed at wiring time, so a security-relevant skill or plugin being silently excluded is visible in the wiring step's own output, not just inferable after the fact from an empty directory.
- Surface the active policy's effect at session start, not only at wiring time — if a consumer opens a new session and a plugin they expect is missing because of a stale or forgotten deny entry, they should be able to see that from session-start context, not have to re-run the wiring step's own verbose output to find out.
- Validate the policy against cross-artifact references before or during wiring: denying a plugin can leave another plugin's skill pointing at (or a doc cross-linking) content that no longer exists on disk. A policy check that only asks "did I wire what the policy allows" and never asks "did this deny leave anything else dangling" will silently produce broken cross-references with no error at wiring time.
- Make any post-hoc curation/pruning tool for the same content aware of ALL the ways that content can arrive (symlinks *and* copies *and* generated files), not just the one it was originally written to handle. If the tool structurally cannot see a whole category of the content, its "nothing to fix" report should say so explicitly rather than implying completeness.
- When a curation tool acts on the same output directory as a wiring step, document the interaction explicitly: what does a re-run of the wiring step do to the curation tool's prior decisions?

**Don't:**
- Don't treat "the curation script ran and reported success" as proof the underlying cost is actually reduced, without checking whether the script's own scope covers the majority of what's actually there.
- Don't rely on "remember to re-run the prune script after every update" as the durable fix — it's a process step a human (or a future agent session) will eventually skip, and the failure mode when they do is silent, not loud.
- Don't let a missing optional dependency (e.g. a YAML parser) used to read the policy file fail the policy check open without at least a visible warning — a policy mechanism that can be silently defeated by an absent parser is not a policy mechanism a security-relevant exclusion can be trusted to enforce.

## Edge cases / when the rule does NOT apply

- One-shot, non-idempotent installers (run once, never re-wire) don't have this problem — a post-hoc exclusion pass is stable because nothing regenerates the excluded content later.
- If the wiring step's output volume is small enough that manual curation is genuinely cheap and low-risk to forget (a handful of files, not hundreds), the added complexity of a policy-file mechanism may not be worth it — judge by blast radius of "someone forgets to re-apply," not by principle alone.

## See also

- Lesson: ["A skill-catalogue prune script that skips symlinks doesn't shrink anything `ravenclaude setup` wired"](../memory-bank/lessons-learned.md#2026-09-09--a-skill-catalogue-prune-script-that-skips-symlinks-doesnt-shrink-anything-ravenclaude-setup-wired) (dated 2026-09-09) — the concrete story this generalizes from.
- `scripts/ravenclaude` — `is_skill_wiring_denied()` and `wire_plugin_skills()`, the shipped reference implementation (`ravenclaude-core` 0.321.0, `skills.deny_plugins` posture key).

## Provenance

Generalized from a concrete incident: a project's local skill-catalogue prune script explicitly skipped symlinked content ("leave the marketplace wiring alone"), which turned out to be 90% of the actual catalogue — all of it wired unconditionally by a setup script's bulk-symlink step on every run, with no way for an exclusion to persist across re-runs. The generalized mechanism has since shipped as `ravenclaude-core` 0.321.0's `is_skill_wiring_denied()` / `skills.deny_plugins`; this doc was revised to cite that landed implementation and to add the fail-open-observability, cross-artifact-validation, and discoverability requirements the shipped version does not yet fully cover.

---

_Last reviewed: 2026-09-10 by consumer-project session_
