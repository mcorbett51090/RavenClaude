# Lessons-learned vs best-practice docs: when to use which

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Documentation discipline, lessons-loop meta-process.

**Applies to:** Anyone adding content to `docs/memory-bank/lessons-learned.md` or `docs/best-practices/` in this repo (collaborators and Claude sessions alike).

---

## Why this exists

The lessons-loop produces two artifacts that look similar from a distance but serve different readers:

- `docs/memory-bank/lessons-learned.md` — one file, **reverse-chronological log** of trial-and-error findings. Each entry has a date and a story: *we tried X, it failed because Y, so we now do Z*.
- `docs/best-practices/<slug>.md` — **one file per named rule**. Each doc has a Status, a Domain, How to apply, Edge cases, Provenance. Stable reference, organized by topic.

Mixing the two makes both harder to use. The log gets cluttered with timeless rules that have no story behind them. The best-practices folder collects fading anecdotes that should have been dated log entries. This doc names the decision rule so it stops being a judgment call.

## How to apply

**Decision rule:**

| Shape of the finding | Where it goes |
|---|---|
| **Story** — *we tried X, it failed because Y, so we now do Z* | Lessons-learned entry |
| **Rule** — timeless guidance that applies going forward | Best-practice doc |
| **Both a story AND a rule** | Write both, cross-link in See also / Trace |

**Quick test:** if you tried to put the artifact into the *other* directory, what would feel wrong?

- A rule in lessons-learned → the "What we tried first" and "Why it failed" sections would be empty or invented. The rule is just floating in the log with a date stamp it didn't earn.
- A story in best-practices → no "Status" or "How to apply" structure fits — the doc becomes a narrative with no clear forward-looking takeaway.

**Today's lessons-loop has all three shapes in one session — use them as the canonical examples:**

| Finding | Lessons-learned? | Best-practice doc? |
|---|---|---|
| Mermaid for conceptual diagrams | ✅ `2026-05-11` entry — we tried ASCII first, it looked ragged on GitHub | ✅ [`diagrams-in-docs.md`](./diagrams-in-docs.md) — the rule with examples |
| Rebase orphans require `git branch -D` | ✅ `2026-05-11` entry — concrete incident with PR #1 reconciliation | ❌ no rule doc — the underlying knowledge is standard git, no project-specific policy |
| Bump plugin version on every shipped change | ❌ no story — we didn't try-fail-fix, we just need to remember | ✅ [`plugin-versioning.md`](./plugin-versioning.md) — the rule with semver semantics |

**Do:**
- Write the **lesson first** when the finding has a clear try-fail-fix story. The story is the evidence the rule is needed.
- Write a **best-practice doc** when the rule stands on its own without an incident — a discipline rule, a convention, a default.
- When you produce both: cross-link them. The lesson's `Trace` cites the best-practice doc. The best-practice's `Provenance` cites the lesson.
- Treat **both files as growing assets** — the log accumulates entries, the best-practices folder accumulates files.

**Don't:**
- Convert every lesson into a best-practice. Some lessons are *"this is what happened once"* and don't generalize. Leave them standalone.
- Write a best-practice doc with a date in the title or a "what we tried" section. If you reach for those, you're writing a lesson, not a rule.
- Edit old lessons-learned entries except for typos. They're a log — they're frozen in time. New findings get new entries.
- Duplicate content across both files. Each doc owns its piece (story in the lesson, rule in the best-practice); cross-link instead of copy-paste.

## Edge cases / when the rule does NOT apply

- **Personal preferences that won't generalize** (one user's working style, an individual's editor config) — don't write either. Save to personal memory in `~/.claude/projects/<project>/memory/` instead.
- **Domain-specific findings** (Power Platform-specific, finance-specific, EdTech-specific) — don't go in this repo's cross-domain `docs/`. They belong inside the relevant plugin folder, e.g. `plugins/power-platform/skills/<skill>/resources/<rule>.md`. The cross-domain `docs/` tree is for findings that apply to *any* Claude work.
- **Architectural decisions** that need a written rationale but aren't reusable rules (e.g. *"we picked plugins over Expert repos"*) — those go in [`docs/memory-bank/decision-log.md`](../memory-bank/decision-log.md), not lessons-learned and not best-practices.
- **Process improvements to the lessons-loop itself** (like this doc) — best-practice. It's a rule about authoring, no incident behind it.

## See also

- [`docs/architecture.md` §How knowledge is captured](../architecture.md) — the three-layer memory model (consumer auto-memory, lessons, best-practices) and the flow from one to another.
- [Mermaid for conceptual diagrams (lesson)](../memory-bank/lessons-learned.md) — paired with [`diagrams-in-docs.md`](./diagrams-in-docs.md) (best-practice). Canonical example of both shapes for one finding.
- [Rebase orphans (lesson, standalone)](../memory-bank/lessons-learned.md) — canonical example of a lesson with no companion best-practice.
- [Plugin versioning (best-practice, standalone)](./plugin-versioning.md) — canonical example of a best-practice with no companion lesson.
- [`_TEMPLATE.md`](./_TEMPLATE.md) — the best-practice doc template this file follows.

## Provenance

Codified 2026-05-11 after the lessons-loop scaffold (commit `8f9421e`) had been used four times — four lessons (`2026-05-07` PMP, `2026-05-07` PSM, `2026-05-11` mermaid, `2026-05-11` rebase-orphans) and two best-practice docs ([`diagrams-in-docs.md`](./diagrams-in-docs.md), [`plugin-versioning.md`](./plugin-versioning.md)). The implicit pattern across all six entries was *story → lesson, rule → best-practice, both → both with cross-links*. This doc names the pattern so future entries don't have to re-derive it.

---

_Last reviewed: 2026-05-11 by `mcorbett51090`_
