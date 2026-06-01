# 🧭 RavenClaude — Strategy

**Status:** Stub. The content of this document is pending Matt's direction.

This file is reserved for RavenClaude's medium-term strategic direction: the boundary between the **public core** (the open marketplace of agents, skills, hooks, and templates that anyone can install) and any **private / internal extensions** (engagement-specific knowledge banks, partner-confidential templates, paid premium plugins, or productized consulting deliverables). It is also the home for packaging-and-distribution decisions — pricing model, free-vs-paid tiering, the Power Platform / Microsoft-stack consulting front-door, and the SaaS bet timeline.

The placeholder exists so the `.repo-layout.json` glob reservation is backed by a real file, the layout hook and CI don't drop a future write, and the link from [`GETTING_STARTED.md`](GETTING_STARTED.md) "Where to go next" table doesn't 404. Content arrives once direction is set.

**Until then:**

- The business direction in [memory](../../home/codespace/.claude/projects/-workspaces-RavenClaude/memory/project_business_direction.md) (consulting-first; $25–50k per engagement; SaaS a long bet) is the load-bearing prior.
- Plugin-versioning and compatibility-direction prose lives in [`docs/best-practices/plugin-versioning.md`](docs/best-practices/plugin-versioning.md).
- Public-vs-private posture for individual files is governed by the existing `.gitignore` + `.repo-layout.json` discipline plus the `email`-field-removal rule in [`AGENTS.md`](AGENTS.md) §PR conventions.

To author the content, open a follow-up PR titled `docs(strategy): author public-core/private-extension direction` and replace this file's body.

---

_Stub created 2026-06-01 as part of the P0–P2 gap-closure bundle (v0.101.0). See `docs/gap-closure-plan-2026-06-01.md` if present, or the PR body of the introducing commit for context._
