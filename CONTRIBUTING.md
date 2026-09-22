# Contributing to RavenClaude

This repository is private and limited to a named list of collaborators (see [`docs/access.md`](docs/access.md)). If you have write access, this document is how you propose changes.

Maintainer: **Matt Corbett** (`@mcorbett51090`). All merges to `main` go through Matt.

---

## What you can contribute

There are three common kinds of change. Pick the one that fits and follow the flow for that section.

| Kind | Lands in | Approval |
|---|---|---|
| **Proposed lesson** — a non-obvious finding or rule worth remembering across projects | `docs/best-practices/<slug>.md` and/or `docs/memory-bank/lessons-learned.md` | Matt reviews for clarity, scrubbing, and cross-references |
| **Plugin change** — a fix or new feature inside `plugins/<plugin-name>/` | The plugin's `agents/`, `skills/`, `rules/`, etc. | Matt reviews for plugin quality + version bump |
| **Marketplace / meta change** — root `README.md`, `marketplace.json`, this file, devcontainer, etc. | Repo root, `.claude-plugin/`, `.github/` | Matt reviews for repo-wide impact |

---

## How to propose a lesson

A "lesson" is a finding worth keeping — a rule, a diagnostic, a pattern that paid for itself. Think: *"I would have wanted to know this two months ago."*

There are two paths in. Pick the one that fits where you are.

| You are… | Use this path |
|---|---|
| **A collaborator with write access**, working directly on this repo | Branch → write → PR (the steps below) |
| **In a consumer project** that has `ravenclaude-core` installed, and Claude has spotted something worth contributing | The staging workflow — see [`docs/staging/README.md`](docs/staging/README.md). Claude formats the submission for you; the maintainer reviews via `/review-staged-contributions`. No PR required from the consumer side. |

### 1. Branch

You have write access to this repo (you're a collaborator), so you can branch directly here — no fork needed.

```bash
git checkout main
git pull
git checkout -b propose-lesson-<short-slug>
```

### 2. Write the lesson

Lessons can live in two places, depending on shape:

- **Detailed rule** → new file in `docs/best-practices/<slug>.md` using [`_TEMPLATE.md`](docs/best-practices/_TEMPLATE.md) as the starting point.
- **Trial-and-error finding** → new dated section at the top of `docs/memory-bank/lessons-learned.md`, following the format already defined at the top of that file.

Use both if the lesson has a teachable rule AND a story behind it: write the rule in `best-practices/`, the story in `lessons-learned.md`, and cross-link them.

### 3. Scrub before you commit

- Remove any project-specific identifiers (client names, tenant IDs, real GUIDs, email addresses, internal URLs).
- Replace specifics with placeholders (`<CLIENT>`, `<TENANT_ID>`, `contoso.crm.dynamics.com`).
- Make sure the lesson reads as *general guidance*, not a war story about one customer.

### 4. Open the PR

```bash
git push -u origin propose-lesson-<short-slug>
gh pr create  # or use the GitHub web UI
```

The PR form will load the default template — fill in the checkboxes honestly. Matt will review, request changes, or merge.

---

## How to propose a plugin change

Plugin changes (`plugins/ravenclaude-core/`, `plugins/power-platform/`, future plugins) follow the same branch → PR flow, with two extras:

1. **Bump the plugin's `version`** in `plugins/<name>/.claude-plugin/plugin.json`. Use semver: patch (`0.2.0 → 0.2.1`) for fixes, minor (`0.2.0 → 0.3.0`) for new agents or skills, major for breaking changes.
2. **Note any consumer impact** in the PR body: if existing installs will see different agent behavior, prompts, or skill paths after `marketplace update`, call that out so Matt can decide whether to add a migration note.

Other than that: same branch naming (`fix/<plugin>-<slug>`, `feat/<plugin>-<slug>`), same template.

---

## Keeping a branch caught up with `main`

If your branch stays open for more than a day or two, `main` will move — and *how* you catch up matters, not just that you do.

**Do this:**
```bash
git fetch origin
git merge origin/main
# resolve any conflicts, then:
git commit
bash scripts/premerge-refresh.sh   # regenerates derived files + re-stamps freshness against the real merge
git push
```

**Never re-create your branch by cherry-picking your own commits onto a fresh `origin/main`:**
```bash
git checkout origin/main -b my-branch-v2
git cherry-pick <sha1> <sha2> ...   # ⛔ don't do this to catch up
```

A real `git merge` makes `origin/main`'s current tip a direct ancestor of your branch, so any check that measures "how far behind is this branch" (`check-ratchet-freshness.py`, via `scripts/_base_ref.py`) moves forward with it. Cherry-picking onto a brand-new branch gives your commits a *different* ancestry whose fork point freezes at whatever `origin/main` was the moment you cut that new branch — permanently, no matter how many more times you re-fetch or re-stamp afterward. The resulting failure ("measured against the wrong SHA") reads like a forgotten `--stamp`, not like "this branch's ancestry can never reach main" — which is what makes it easy to lose real time re-running the wrong fix. Full mechanics + a real incident: the 2026-09-09 addendum in `scripts/_base_ref.py`.

**`scripts/premerge-refresh.sh`** is the one command to run once your branch is genuinely caught up (a real merge committed, no conflicts left). It regenerates the artifacts a long-open branch tends to drift on — the concepts registry, dashboards, `docs/concepts.md`, the `copilot/` package — then re-stamps ratchet freshness, in that order, and refuses to run while a merge is still unresolved so it can't mis-time the stamp.

**After that refresh (or on any ordinary push), do not guess at CI from `git status`.** `python3 scripts/ci-preflight.py` is the read-only preview of the recurring freshness / lint / ratchet classes CI will compute. It never writes the tree; a failing row names the remediation instead. Exit **1** means something was `UNAVAILABLE` (missing tool, blocked network, unresolvable base) — that is **not** a pass. `scripts/audit-gates.sh` remains the required pre-PR check (must-fail fixture teeth). Which command to reach for, the three-tier exit contract, and the #1145 stamp-during-merge pitfall: [`docs/best-practices/ci-preflight-vs-premerge-refresh.md`](docs/best-practices/ci-preflight-vs-premerge-refresh.md).

---

## How approval works

1. You open the PR. CI (if configured) runs format checks.
2. Matt reviews — typically within a few days for non-urgent items.
3. Outcome is one of:
   - **Approve & merge** — your change lands on `main` and is included in the next `marketplace update` consumers pull.
   - **Request changes** — Matt leaves comments; you push more commits to the same branch and re-request review.
   - **Close** — the change isn't going to land. Matt explains why in a comment.

No force-pushes to `main`. No bypassing the PR flow. If you're stuck on something urgent that needs to skip the queue, message Matt directly.

---

## House rules

- **One topic per PR.** Five small PRs beat one giant one. Easier to review, easier to revert if needed.
- **Plain language.** RavenClaude users include non-developers (financial analysts, partner success managers). Define jargon on first use; lead with the outcome, not the implementation.
- **No secrets.** Never commit `.env` files, credentials, tokens, or anything you wouldn't want a future collaborator to see in `git log`.
- **Cite sources.** If a lesson comes from a specific Microsoft Learn doc, blog post, or incident, link it in the **Provenance** section. Future-you will thank past-you.
- **Update cross-references.** If your new lesson supersedes or relates to an existing one, edit both files so the trail is navigable.

---

## Troubleshooting

### "I got `permission denied` trying to push to RavenClaude"

This is expected — GitHub permissions are **per-repo**. Being a collaborator on another repo (even one Matt owns) does NOT grant push access here. The list of people who can push directly to RavenClaude is in [`docs/access.md`](docs/access.md); if you're not on it, direct push is blocked.

If you're working in a consumer project that has `ravenclaude-core` installed and you discovered something cross-domain worth contributing back:

1. In that project's Claude Code session, ask Claude to use the **`contribute-finding`** skill on the finding.
2. Claude produces a copyable `RAVENCLAUDE-STAGING-SUBMISSION` block in canonical lesson or best-practice shape.
3. Send the block to Matt (Slack, email, paste in a shared doc).
4. He drops it into RavenClaude's `docs/staging/incoming/` and runs `/review-staged-contributions` — security sweep + topic-expert analysis, then keep/update/deny.

This is the **design-intent path** for consumer contributions — see [`docs/staging/README.md`](docs/staging/README.md) for the full flow. You don't need any GitHub permission on RavenClaude to use it.

### "I don't have `ravenclaude-core` installed in my consumer project"

```bash
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

Once installed, the `contribute-finding` skill becomes available in that session.

---

## Questions

If something in this guide is unclear, the answer is to ask Matt rather than guess. Open an issue with the `question` label, or message him directly.
