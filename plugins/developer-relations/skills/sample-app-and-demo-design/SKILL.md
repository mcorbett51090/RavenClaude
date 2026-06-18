---
name: sample-app-and-demo-design
description: Design a sample app or demo that runs as shipped and teaches one thing well — scope it to a single teaching goal, define the runs-from-clean checklist (no placeholder secrets, no TODOs), pick the format for the funnel stage, and name a maintenance owner before it ships. Reach for this on "design a sample app for X" or "build a demo of Y". Used by `developer-advocate` (primary).
---

# Skill: sample-app-and-demo-design

> **Invoked by:** `developer-advocate` (primary).
>
> **When to invoke:** "design a sample app that shows X"; "we need a demo of Y"; reviewing an
> existing sample for runs-as-shipped and teaching focus.
>
> **Output:** a demo spec (one teaching goal + runs-from-clean checklist + maintenance owner) framed
> so the relevant engineering plugin can build it + the §6 Output Contract with a `Runs-as-shipped check:` line.

## Procedure

1. **Name the single teaching goal.** One thing this demo proves a developer can do. A demo that
   shows five capabilities teaches none ([`../../knowledge/developer-experience-and-onboarding.md`](../../knowledge/developer-experience-and-onboarding.md)).
2. **Pick the format for the funnel stage** (content-format tree in
   [`../../knowledge/devrel-strategy-decision-trees.md`](../../knowledge/devrel-strategy-decision-trees.md)):
   activation → runnable repo + quickstart; deeper → guided tutorial.
3. **Define the runs-from-clean checklist:**
   - clones/installs with the stated prerequisites only,
   - runs unmodified to a visible win (no placeholder secret in the happy path; `YOUR_API_KEY` only
     as a clearly-marked substitution),
   - no `TODO` / "left as an exercise" on the golden path,
   - the error states are part of the teaching, not dead ends.
4. **Decide the build seam.** The real implementation is built by the relevant engineering plugin
   (`backend-engineering`, `frontend-engineering`, `api-engineering`, etc.); this skill produces the
   *spec*, not the production code. A security verdict routes to `ravenclaude-core/security-reviewer`.
5. **Name a maintenance owner.** No owner, no ship — a broken sample at the top of search costs more
   trust than it earned (house opinion #9).
6. **Strip the marketing.** Every sentence should survive in a competitor's docs; if it only works in
   yours, it's an ad (house opinion #2).

## Worked example

> User: "Design a sample app showing our webhooks."

- Teaching goal (one): "receive and verify a webhook in 5 minutes."
- Format: runnable repo + 5-step quickstart (activation stage).
- Runs-from-clean: a tiny server, ngrok/tunnel instructions, HMAC verification shown in full, a
  printed "verified ✓" as the visible win. No real secret committed; signing secret read from env.
- Build seam: `backend-engineering` implements; `ravenclaude-core/security-reviewer` checks the HMAC code.
- Owner: the advocate who shipped it; review quarterly.

## Guardrails

- If you can't state the one teaching goal in a sentence, the demo is too big — cut it.
- `Runs-as-shipped check:` is mandatory in the output; "should work" is not a check.
- Don't ship a demo whose maintenance you can't commit to.
