# 🧭 RavenClaude — Strategy

**Status:** Intentionally minimal — closed 2026-06-02.

RavenClaude is built as a **private consulting-craft tool**, not a productized SaaS or a public marketplace play. There is no public-vs-private packaging decision the marketplace currently needs to surface, no pricing tier to design, and no SaaS bet to time. The repo is private; collaborators are named; engagements use the agents directly. Strategy lives in Matt's session memory and engagement notes — not in a versioned source file that risks rotting against shifting reality.

If that frame ever changes — public packaging, a paid tier, a partner program — this document gets rewritten with concrete direction at that point. Until then, **the absence of strategy prose is the strategy: ship craft, not a deck.**

## What this document is NOT trying to be

- A product roadmap (that's `CHANGELOG.md` + the deferred-decisions queue in memory).
- A pricing or licensing position (none exists publicly; engagements quote directly).
- A community / open-source pitch (the marketplace is private; collaborator access is gated).
- A competitive positioning piece (positioning happens at engagement time, not in a static doc).

## What governs strategic decisions today

- **Business direction** (consulting-first, $25–50k per engagement, SaaS a long bet) — Matt's session memory, not in-repo.
- **Plugin versioning + compatibility direction** — [`docs/best-practices/plugin-versioning.md`](docs/best-practices/plugin-versioning.md).
- **Public-vs-private file posture** — `.gitignore` + `.repo-layout.json` + the email-field-removal rule in [`AGENTS.md`](AGENTS.md) §PR conventions.
- **Aesthetic direction across surfaces** — [`plugins/ravenclaude-core/dashboard-assets/README.md`](plugins/ravenclaude-core/dashboard-assets/README.md) "Surface aesthetic map" section.

## Reopening criteria

Reopen this document only if one of these triggers fires:

1. A real consumer asks for a paid tier or public listing.
2. A potential partner asks "what's your roadmap for X" and the answer needs a written form.
3. The repo moves from private to public.
4. A capacity decision is needed (e.g., the marketplace adds a hard plugin limit).

Until then, this file remains intentionally short.

---

_Closed 2026-06-02 (v0.104.0) — after 3 PRs of deferral, the panel correctly identified this as queue debt rather than a real pending decision. Closing as "intentionally minimal" removes it from the decisions-deferred stack._
