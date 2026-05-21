---
name: Proposed lesson / house opinion
about: Propose a new "house opinion" or specialist insight to add to the marketplace. Mirrors the staging-contribution flow (contribute-finding / review-staged-contributions).
title: "[lesson] "
labels: proposed-lesson
assignees: mcorbett51090
---

> **Prefer the in-session flow when you can.** If you're in a consumer project that has `ravenclaude-core` installed and Claude is the one who noticed this, ask Claude to run the **`contribute-finding`** skill — it'll produce a canonical `RAVENCLAUDE-STAGING-SUBMISSION` block. Paste that block at the bottom of this issue (or send it to Matt directly). The maintainer-side `/review-staged-contributions` flow does security sweep + topic-expert routing and lands it in the right plugin folder. See [`docs/staging/README.md`](../../docs/staging/README.md) for the full path.
>
> **This issue template is the fallback** for proposing a lesson when you're not in a consumer session — or when the lesson is meta (about the marketplace itself, not a specific domain).

---

## What's the lesson?

State the rule in one sentence, imperative form. Example: "Always pin connection references in solution-aware flows, never the connection itself."

## Why does it matter? (a.k.a. the "I would have wanted to know this two months ago" test)

What problem did you (or Claude) hit that made this lesson worth keeping? Give enough story for a future reader to judge whether the rule still applies in their situation.

## Where should it live?

Pick one — the routing matters for review:

- [ ] **Cross-domain** — applies to any Claude work regardless of stack. Lands in `docs/best-practices/<slug>.md` (rule) and/or `docs/memory-bank/lessons-learned.md` (the story).
- [ ] **`ravenclaude-core` specific** — applies to the neutral team but not a specific domain. Lands in `plugins/ravenclaude-core/rules/` or as a `CLAUDE.md` update.
- [ ] **`power-platform` specific** — Lands in `plugins/power-platform/CLAUDE.md` §3/§4 (house opinions / anti-patterns) and/or a skill `resources/` doc.
- [ ] **Other plugin** (specify): ____
- [ ] **Both cross-domain and plugin-specific** — write the rule cross-domain, the deep-dive in the plugin, cross-link.

## The provenance

Where did this lesson come from?

- [ ] A real incident (briefly describe; scrub client identifiers)
- [ ] Official documentation (link)
- [ ] A trusted blog post / expert opinion (link)
- [ ] Claude noticed it during a session and surfaced it
- [ ] Pattern observed across multiple projects

Citation:

## Scrub check

Before submitting:

- [ ] No client names, tenant IDs, real GUIDs, email addresses, or internal URLs
- [ ] Reads as general guidance, not a war story about one customer
- [ ] If you're quoting a third-party source, you've actually linked it

## Optional: paste a `RAVENCLAUDE-STAGING-SUBMISSION` block

If Claude generated one via `contribute-finding`, paste it here. Otherwise leave blank — Matt will format it during review.

```
RAVENCLAUDE-STAGING-SUBMISSION
…
```
