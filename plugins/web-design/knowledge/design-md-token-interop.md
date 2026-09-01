# DESIGN.md — an emerging cross-agent format for design tokens + visual identity

**Last reviewed:** 2026-09-01. **Trigger for re-review:** the spec leaves alpha, or `npx @google/design.md` bumps a major version.

## What it is

`DESIGN.md` is a file-format spec — **`google-labs-code/design.md`** on GitHub, published by Google
Labs — for describing a project's visual identity to coding agents in one file, the same way
`README.md` describes a project to humans `[docs-verified 2026-09-01: https://github.com/google-labs-code/design.md]`.

- **Shape:** YAML front matter holding machine-readable tokens (color hex values, named typography
  scales, spacing/border-radius as dimensions) followed by markdown prose explaining the *why* behind
  those values — tokens for the exact number, prose for when/how to apply it.
- **Tooling:** the `npx @google/design.md` CLI. `lint` validates token references, flags a missing
  primary color, and checks WCAG contrast — `export` converts the token set to a **Tailwind config**
  or **W3C DTCG format**.
- **Status:** **alpha, under active development** as of this review — treat anything beyond the core
  token/prose shape as subject to change. Full spec: `docs/spec.md` in the source repo.

## Why this repo already has half the story

This plugin's `design-tokens-scaffolding` skill already standardizes on the **W3C Design Tokens
Community Group draft format** (`$value`/`$type`/`$description`) as the token JSON layer, built by
Style Dictionary into CSS vars / Tailwind config / TS types (`SKILL.md` §5–6). `DESIGN.md`'s own
`export` command target is **the same W3C DTCG format** — the two pipelines speak the same token
vocabulary; `DESIGN.md` is not a competing token schema, it's a different *delivery envelope* for it.

**What `DESIGN.md` adds that the existing pipeline doesn't:** a single, git-committed, human-and-agent
readable file that ships the *rationale* alongside the values, and that a coding agent operating with
**no other context** (a different session, a different host — Codex, Cursor, Copilot CLI, Gemini
CLI — none of which read this repo's `tokens/tokens.json` build pipeline docs) can read and act on
directly. That is precisely the cross-tool legibility problem `AGENTS.md` / `host-support.json` /
`external-agent-onboarding` already solve for *process* conventions in this repo — `DESIGN.md` is the
same idea applied to *design* conventions.

## When to consider emitting one (optional — this is not a pipeline change)

Offer a `DESIGN.md` as an **additional, opt-in deliverable** — never a replacement for the token JSON
→ Style Dictionary → CSS/Tailwind pipeline, and never a default addition to every engagement — when:

- The brand system needs to stay consistent across sessions/hosts that won't share this repo's build
  tooling or `CLAUDE.md` (a client's own Codex/Cursor session, a separate marketing-site repo).
- `brand-identity-studio`'s `assemble-brand-book` command (step 3) already delegates the finished
  color roles + type decisions to `web-design:design-tokens-scaffolding` for the DTCG/Style-Dictionary
  build — a `DESIGN.md` export is a **zero-extra-authoring** by-product at that same handoff point,
  since the source tokens are already in DTCG shape.

Do **not** treat this as a reason to add a new required gate, agent, or default file to any existing
skill/command. It is a format to know about and reach for when the cross-agent-legibility need is
real, consistent with this repo's own opt-in-by-default posture for optional deliverables.

## Confidence notes

- **High confidence, verified this session:** the spec exists, is Google Labs-authored, is alpha, and
  its CLI does lint + Tailwind/DTCG export — confirmed against the `google-labs-code/design.md` GitHub
  repo and its own `docs/spec.md`.
- **Not verified / out of scope for this note:** production adoption numbers, whether any major coding
  agent (Claude Code, Copilot, Codex) reads `DESIGN.md` *automatically* the way they read `AGENTS.md`.
  Treat automatic pickup as **not proven** — the value today is "one file a human or agent can be
  pointed at," not "an agent will find this unprompted."

## Sources

- [google-labs-code/design.md](https://github.com/google-labs-code/design.md) — spec, CLI, examples (retrieved 2026-09-01)
- [design.md/docs/spec.md](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md) — full format spec
- Existing catalog of example `DESIGN.md` files already cited in [`design-references.md`](design-references.md) (VoltAgent's `awesome-design-md` teardown collection, `getdesign.md`) — those links predate this note and are examples of the format in the wild, not the spec itself.
