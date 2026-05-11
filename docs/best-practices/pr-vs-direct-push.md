# PR vs direct-push: when to open a pull request

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Marketplace workflow, git discipline.

**Applies to:** This marketplace (RavenClaude) and any plugin or project with a similar **single-collaborator-or-trusted-pair** profile. Multi-contributor projects (≥3 active writers) should default to PR-for-everything; this doc does not apply there.

---

## Why this exists

Pull requests add visibility, audit trail, and a review surface. They also add overhead — branch creation, push, PR open, render-check, merge, branch cleanup. For a multi-contributor project, that overhead is worth it on every change. For a one-or-two-person project, ceremony on every change actively makes the git history harder to read: every PR squashes context into a merge commit, every small doc fix becomes a 5-step workflow. The goal is to pick the right shape per change so the history stays both clean and reviewable.

Today's session is the canonical case study: **2 PRs** (the original lesson, the mermaid-conversion sweep) and **5 direct pushes to main** (config tweaks, follow-up best-practice docs). Each choice was made on an unwritten rule. This doc writes it down.

## How to apply

**Open a PR when ANY of these apply:**

- The change is substantive enough to **benefit from rendered review** — multi-file diffs, visual artifacts (mermaid, screenshots), or anything where eyeballing GitHub's render is more useful than reading the raw diff in a terminal.
- The change touches **shipped plugin code** (anything in `plugins/<name>/`) and isn't a trivial typo. Consumers will receive this after the next `marketplace update`.
- You want a **permanent paper trail of *why*** in PR description form. The PR body outlives commit messages in the GitHub UI and is the easiest place for future-you to find rationale.
- Multiple commits land **as one logical unit** and you want them merged together (or squashed) with shared context.
- The change is **risky or reversible only with effort** — schema changes, hook contract changes, breaking removals.

**Commit directly to main when ALL of these apply:**

- The change is a **small doc add, config tweak, or follow-up** to a just-merged PR.
- You're the **sole active collaborator** on this branch (or working with a trusted pair who has visibility).
- You've **already iterated and confirmed** in the current session — the commit isn't speculative.
- The **commit message alone** captures all the context needed (no separate PR body required).
- The change touches **only meta-repo files** (`docs/`, `README.md`, `.claude/settings.json`, `.github/`), OR shipped plugin files in a way that's been just-discussed in the same session.

**Today's session, by way of example:**

| Change | Shape | Why |
|---|---|---|
| PR #1 — `propose-lesson-diagrams-in-docs` | PR | First lesson, visual artifact (mermaid demo), wanted GitHub render-check |
| PR #2 — `chore/apply-mermaid-lesson` | PR | 8 files modified across 7 power-platform skills; rendered diagrams worth eyeballing |
| `chore(ravenclaude-core): allow git branch -D` | Direct | Small config tweak, just-approved in conversation, no rendered review value |
| `docs(lessons): add rebase-orphan lesson` | Direct | Small doc add, meta-repo only, just-approved |
| `docs(best-practices): add plugin-versioning rule` | Direct | Same pattern — new file, meta-repo, follow-up to the rebase lesson |
| `docs(best-practices): add lessons-vs-best-practices` | Direct | Same pattern |
| `docs(best-practices): add hook-authoring patterns` | Direct | Same pattern |

**Do:**
- **Default to direct-push** for the small-doc-add shape. Branch + PR + merge + delete is ~5 steps; commit + push is 2. The 3-step delta matters when you're shipping five docs in an hour.
- **Default to PR** the moment a change touches `plugins/<name>/` in a non-trivial way. Consumers will see it; the audit trail is worth the ceremony.
- Use **PR description as the primary rationale doc** for substantive changes — better than commit body alone, because GitHub renders it and links to the diff.
- **Delete the feature branch** (locally and on origin) after merge — `gh pr merge --delete-branch` handles both.

**Don't:**
- **Don't PR every commit.** If you find yourself opening PRs for one-line typo fixes in your own repo with no other collaborators, you're paying ceremony tax with no return.
- **Don't direct-push** a change you're uncertain about. Branches are free; reverting `main` is not.
- **Don't mix** PR-worthy and direct-push-worthy work in one commit. Split them — the small fix goes direct, the substantive change opens a PR.
- **Don't direct-push** during a multi-collaborator phase or anything review-worthy *just* because the project rule allows it. The rule is permissive, not prescriptive.

## Edge cases / when the rule does NOT apply

- **Multi-collaborator phase begins** — once a second active writer is on the project (check `docs/access.md` and `git shortlog -sn --since=30.days.ago`), default to PRs for everything. PRs are also a courtesy: they let the other person see what's incoming and surface intent before the diff hits main.
- **Hotfix to fix a broken main** — direct push is fine; speed matters more than ceremony. Follow up with a retrospective lesson if the break was non-obvious.
- **Change is reversible only with database migration / external system effect** — PR regardless of size. The review trail is the only place to record the migration rationale.
- **CI is gating merges** — if `main` is protected by required checks, direct push isn't possible; you're in PR-for-everything mode by infrastructure default. Honor it.
- **You're writing this from an agent session and the user hasn't explicitly approved direct push** — default to PR. Direct push is a delegated authority; if it wasn't delegated, branch + ask first.

## See also

- [`CLAUDE.md` §4 Git workflow for the marketplace](../../CLAUDE.md) — the branch-naming conventions and the *main is always green, always installable* invariant this rule sits on top of.
- [`plugins/ravenclaude-core/CLAUDE.md` §3 Git Workflow](../../plugins/ravenclaude-core/CLAUDE.md) — the team-level commit/branch/PR conventions the consumer projects inherit.
- [Plugin versioning rule](./plugin-versioning.md) — version bumps go in the **same commit** as the content change, regardless of PR vs direct-push.
- [Lessons-vs-best-practices](./lessons-vs-best-practices.md) — companion meta-process rule on where the *content* of a change lives.

## Provenance

Codified 2026-05-11 at the end of a single session that produced 2 PRs and 5 direct pushes to main. The implicit rule above governed every choice — the mermaid PRs earned ceremony because rendering mattered and 7 files moved together; the four follow-up best-practice docs went direct because they were sequential, small, just-approved, and meta-repo only. No incident drove the rule into existence; it was already operating quietly. This doc is the name being put on the pattern so the next collaborator (or future-Claude) starts from the same default.

---

_Last reviewed: 2026-05-11 by `mcorbett51090`_
