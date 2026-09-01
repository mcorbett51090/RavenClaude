# DESIGN.md resolution — the house default for ad-hoc HTML, and its override

**Last reviewed:** 2026-09-01.

## What this governs (and what it does not)

Any agent, in any plugin, sometimes generates a **standalone HTML artifact for the user to look
at** that is not a client deliverable — a diagnostic report, an audit summary, a status dashboard,
an explainer of what changed and why, a one-off page built via the `Artifact` tool. This file
governs **that** case: what such a page should look like by default, so it's visually consistent
across repos instead of reinventing a look every time.

**It does NOT govern a client's own branded product or marketing site.** Building or theming an
actual deliverable for a client is `web-design`/`brand-identity-studio`'s job, is always
project-specific to *that client's* brand, and has **no house default** — see
`plugins/web-design/knowledge/design-md-token-interop.md` (PR #1063, landing separately).
Confusing the two is the failure this split exists to prevent: a client's marketing page must
never accidentally inherit RavenClaude's own house look, and an internal diagnostic report gains
nothing from per-engagement brand work.

## The two-tier resolution rule

When an agent is about to generate an ad-hoc informational HTML artifact and needs a visual
identity to draw from:

1. **Check for a project-root `DESIGN.md`** in the current repo (or `.ravenclaude/DESIGN.md` if the
   repo root is already crowded with a different `DESIGN.md` for another purpose — name the choice
   in one clause so it's not silently ambiguous). If present, that file's tokens win for **this**
   repo, full stop — no merge with the house default.
2. **Otherwise, use the shipped house default**:
   [`../templates/DESIGN.md`](../templates/DESIGN.md) — RavenClaude's own look (the same tokens
   `dashboard-assets/shared-tokens.css` uses for `index.html`/`dashboard.html`, expressed here as a
   portable, human-and-agent-readable file instead of Python-generated CSS).

This mirrors the `.ravenclaude/comfort-posture.yaml` / `environment-context.md` pattern already
used elsewhere in this repo: a shipped default, overridable per-repo by dropping a file at the
expected path — never the other way around (a repo's own choice is never silently overwritten by
the house default).

**Deliberately not auto-scaffolded.** Unlike `AGENTS.md`/`CLAUDE.md`, `/init-agent-ready` does
**not** copy this file into every new consumer repo by default — most consumer repos never
generate ad-hoc HTML at all, and pre-seeding a `DESIGN.md` everywhere would be unused file bloat.
A repo picks up the override only when someone deliberately wants a different look and adds their
own `DESIGN.md`; absent that, resolution falls through to the shipped template with zero setup.

## Format

The file format itself — YAML frontmatter of tokens (`colors`/`typography`/`spacing`/`rounded`/
`components`) followed by `##`-headed prose (Overview / Colors / Typography / Layout / Elevation &
Depth / Shapes / Components / Do's and Don'ts) — is
[`google-labs-code/design.md`](https://github.com/google-labs-code/design.md)'s alpha-stage spec,
verified against its own [`docs/spec.md`](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md)
this session. Using the real spec (rather than an invented schema) means a repo's override file is
also readable by that project's own `npx @google/design.md lint`/`export` CLI if a consumer ever
wants that tooling — a side benefit, not the reason for the choice.

## Why this lives in `ravenclaude-core`, not `web-design`

`ravenclaude-core` stays domain-neutral by house rule — this qualifies because *every* plugin's
agents occasionally produce a diagnostic/report artifact, not just `web-design`'s. A finance
compliance check, a Power Platform solution audit, a PM status report rendered as HTML — all of
them are the same "agent shows the user something" case this file resolves, regardless of which
plugin produced it. `web-design`'s DESIGN.md note is the opposite case: a per-client brand
artifact, which is domain-specific by construction and correctly stays in that plugin.

## Confidence notes

- **High confidence, verified this session:** the DESIGN.md format spec (fetched from the source
  repo's own `docs/spec.md`), and the token values here (copied from
  `dashboard-assets/shared-tokens.css`, which is itself WCAG-2.2-contrast-verified per its own
  header comments).
- **Behavioral, not mechanically enforced:** resolution is a convention an agent follows, the same
  way `design_checkins`/`decision_review` are behavioral commitments rather than hook-gated. No
  hook currently checks that a generated HTML artifact actually consulted this file — if that
  becomes a recurring miss, a lint over generated `.html` (checking for the resolved token values,
  the same shape as `claim-grounding-lint.sh`) would be the enforceable sliver, not yet built.
