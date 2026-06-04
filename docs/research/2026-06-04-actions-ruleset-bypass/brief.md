# Research brief — letting CI push to a ruleset-protected main (solo personal repo)
Date: 2026-06-04 · Researcher: deep-researcher (15 tool calls) · Decision: ACCEPT-AND-MONITOR (Matt)

## TL;DR
- `github-actions[bot]` is a built-in SYSTEM IDENTITY GitHub deliberately does NOT allow as a
  ruleset bypass actor (UI omission is by design). HIGH confidence.
  Sources: https://github.com/orgs/community/discussions/25305 ·
  https://github.com/orgs/community/discussions/175332 (both retrieved 2026-06-04)
- The actor_id 15368 REST trick (PUT bypass_actors Integration 15368) is UNVERIFIED on personal
  repos; authoritative threads point against it working. LOW confidence — do not build on it
  without a throwaway-repo repro.
- Consensus patterns 2025-2026: (1) dedicated GitHub App + actions/create-github-app-token
  (best practice; bypass list accepts installed apps), (2) deploy key (lighter; "Deploy keys"
  IS a UI bypass option), (3) fine-grained PAT (most discouraged).
  Sources: discussions/25305 · medium.com/ninjaneers (2025-12-08) ·
  docs.github.com/en/authentication/connecting-to-github/managing-deploy-keys
- LOAD-BEARING GOTCHA (HIGH confidence): only GITHUB_TOKEN pushes are exempt from re-triggering
  on:push workflows. App tokens, PATs, AND deploy-key pushes all DO re-trigger — switching
  credentials removes the implicit recursion guard regenerate-artifacts.yml relies on today.
  Required guard if ever switching: paths-ignore on artifact paths or [skip ci] commit message
  (concurrency group alone does NOT prevent recursion; deploy-key pushes don't set a bot
  github.actor so the actor-name guard won't catch them).
  Sources: docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow ·
  deku.posstree.com/en/github_actions/github-actions-workflow-retrigger/ (2026-03-03) ·
  github.com/actions/checkout/discussions/1270
- Sept 2025 "ruleset exemptions" changelog = a bypass MODE on already-eligible actors, not a new
  way to add the Actions bot. Source: github.blog/changelog/2025-09-10-github-ruleset-exemptions...

## Decision record
Matt chose ACCEPT-AND-MONITOR (2026-06-04): no credential change. Rationale: gated PRs hard-block
stale artifacts (self-heal = no-op on that path); failures are loud (Actions tab + Heimdall).
Re-open trigger: second self-heal push failure → deploy-key route + paths-ignore recursion guard.
Recorded in: docs/plans/2026-06-04-pipeline-settings-merge-gate.md §Decisions #1 (PR #294).
