# Define the Audience and Their Task Before Designing the Docs Architecture

**Status:** Pattern
**Domain:** Technical Writing — Docs strategy / IA
**Applies to:** `technical-writing-docs`

---

## Why this exists

A documentation site organized around the *system's* structure — one section per module, one page per class — is organized for the author, not the reader. Most readers arrive with a task in mind: "how do I authenticate?", "what are the rate limits?", "why is my import failing?" These tasks do not map cleanly onto module boundaries. Designing the IA from task-and-audience data (not from the codebase structure) produces a site where readers find what they need; designing from the codebase produces a site where only the engineers who wrote it can navigate.

## How to apply

**Audience-definition workshop (before any IA decision):**

| Question | What to capture |
|---|---|
| Who are the readers? | Developer personas (e.g., API consumer, SDK integrator, ops/devops, decision-maker) |
| What are their top 5 tasks? | Drawn from support tickets, onboarding feedback, search queries |
| What is their entry point? | Google, docs homepage, in-app link, error message, SDK README |
| What is their assumed prior knowledge? | (Avoid over-explaining to experts; avoid gaps for novices) |
| What does "success" look like for each task? | A running integration, a deployed config, a resolved error |

**IA mapping exercise (after audience definition):**

1. List the top 10 reader tasks.
2. For each task, identify which Diataxis kind it requires (tutorial / how-to / reference / explanation).
3. Group tasks by shared audience segment.
4. Draft a sitemap from the task groups — sections are audience journeys, not product modules.
5. Validate with 2–3 representative readers via a card-sort or tree-test.

**Do:**
- Return to the audience definition when any new section is proposed ("which reader task does this serve?").
- Use search query data and support ticket themes as evidence, not intuition.
- Name sections after what the reader is trying to do, not what the feature is called internally.

**Don't:**
- Mirror the codebase's package or module hierarchy in the nav.
- Combine multiple audiences in a single guide without explicit persona-scoped sections.
- Defer the audience definition until after the first draft is written — it's the input to the draft.

## Edge cases / when the rule does NOT apply

- **Internal team runbooks**: the audience is a single team with shared context; IA can follow operational sequence (deploy, monitor, rollback) rather than a reader-task mapping.
- **Reference documentation** (the Diataxis reference kind): structure follows the spec/schema, not user tasks, because look-up docs are navigated by fact, not by task sequence.

## See also

- [`../agents/docs-architect.md`](../agents/docs-architect.md) — the agent that leads docs strategy and IA
- [`./write-for-the-readers-task.md`](./write-for-the-readers-task.md) — the companion rule at the page level: organize individual pages around the reader's goal

## Provenance

Codifies house opinion #4 ("Write for the reader's task, not the system's structure") from `CLAUDE.md` §2. Audience-first IA methodology informed by Diataxis (Procida 2017–2026) and card-sort IA practice (Donna Spencer, "Card Sorting"). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
