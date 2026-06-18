# Sample code must run as shipped

**Status:** Absolute rule
**Domain:** Developer content / sample apps
**Applies to:** `developer-relations`

---

## Why this exists

A developer who copies your example and hits an error doesn't file a bug — they leave, and they
remember. A sample with a placeholder secret in the happy path, a `TODO`, or a "left as an exercise"
step is not a stylistic shortcut; it's a trust-destroying defect at the exact moment you're trying to
earn trust. Every snippet, example, and demo must run **unmodified** from a clean environment.

## How to apply

**The runs-from-clean checklist:**
- Clones/installs with the stated prerequisites only (and the prerequisites are stated up front).
- Runs unmodified to a visible win.
- No real-looking fake secret or hard-coded key in the golden path. `YOUR_API_KEY` is acceptable
  *only* as a clearly-marked substitution the developer obviously must replace.
- No `TODO` / "implement this yourself" on the happy path.
- The error states are part of the teaching (good messages, recovery paths), not dead ends.

**Do:**
- Test the sample on a clean machine/container before shipping.
- Read secrets from env/config and show exactly how to set them.
- Assign a maintenance owner; a sample that rots is worse than no sample.

**Don't:**
- Ship a snippet you haven't run end-to-end.
- Commit a real secret to make the demo "just work" (the hook flags hard-coded keys).
- Leave a `TODO` on the path the quickstart promises will work (the hook flags this).

## Edge cases / when the rule does NOT apply

- A **deliberately incomplete starter/scaffold** is fine *if it's labeled as one* and its "fill this
  in" points are outside the first-success path.
- Pseudo-code in a *conceptual* explainer is fine — but it must be clearly not a runnable sample.

## See also

- [`../skills/sample-app-and-demo-design/SKILL.md`](../skills/sample-app-and-demo-design/SKILL.md) — the demo-design procedure
- [`../hooks/flag-devrel-antipatterns.sh`](../hooks/flag-devrel-antipatterns.sh) — flags placeholder secrets / TODOs in samples

## Provenance

Codifies developer-relations CLAUDE.md §3 house opinion #3 and §4 anti-patterns. A security verdict
on a sample's actual code routes to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-06-18 by `claude`_
