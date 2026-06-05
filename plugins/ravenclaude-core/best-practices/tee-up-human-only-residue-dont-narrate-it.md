# Tee up the human-only residue with a deep link — never narrate a navigation path

**Status:** Absolute rule
**Domain:** Agent design / Last-Mile Completion
**Applies to:** `ravenclaude-core`

---

## Why this exists

An agent that finishes its automatable work and then writes "go to the portal, navigate to Settings, then click Deploy" has shifted assembly work to the human. Navigation prose requires the human to follow a recipe step-by-step, which fails whenever the UI has changed and provides no context for what to do when step 3 looks different from the instructions. A deep link — a URL that deposits the human at the exact destination, ideally with values pre-filled as query parameters — reduces the human's job to a single confirm-or-click. This is the Last-Mile Completion Protocol's rule 4 operationalized: "a click beats a recipe."

## How to apply

**Pattern for the final report section:**

```markdown
## ✅ Done
- Created PR #123: [Refactor auth layer](https://github.com/org/repo/pull/123)
- Staged the migration script: `scripts/migrate-auth.sql`
- Drafted the rollback plan: `docs/rollback-plan.md`

## 👉 Your turn (2 steps)
1. Review and merge the PR:
   https://github.com/org/repo/pull/123
2. Trigger the migration in the staging environment:
   https://github.com/org/repo/actions/workflows/migrate.yml
   → Click "Run workflow" → select branch `staging`
```

**Construction rules:**
- For GitHub PRs: construct the "create PR" URL with branch, title, and body as query params — drop the user at a pre-filled form, not the PR list.
- For GitHub Actions: link to the specific workflow file's "Run workflow" page, not the Actions tab root.
- For settings pages: link to the specific settings section path, not the settings root.
- If no deep link can be constructed, give the shortest navigation path AND the exact search term to paste ("go to Settings → search 'Deploy keys'").

**Do:**
- Separate the final output into a `Done` section and a `Your turn` section — the split forces you to identify what is actually the human residue.
- Keep the `Your turn` list short, ordered, and one action per item.
- Pre-fill every field that the agent already knows — branch name, title, labels, assignee — so the human reviews, not assembles.

**Don't:**
- Write "navigate to the deploy portal and find the correct pipeline" — this is un-actionable.
- Leave a `Your turn` item that the agent could have executed (check against the Last-Mile rule: "do everything automatable").
- Produce a long numbered procedure under `Your turn` when a single deep link would replace it.

## Edge cases / when the rule does NOT apply

- Informational outputs (knowledge summaries, design documents, code reviews for human reading) that have no action residue do not require a `Your turn` section — they are deliverables, not task completions.
- When the deep link genuinely cannot be constructed (a portal that doesn't support parameterized URLs), the navigation path is the fallback — not the default.

## See also

- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the Last-Mile Completion Protocol is the third of the three epistemic protocols.
- [`../CLAUDE.md`](../CLAUDE.md) — "Last-Mile Completion Protocol" §"Deep-link, don't narrate" (rule 4).

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Last-Mile Completion Protocol (added 2026-05-28)", specifically rules 3 ("Tee up the human-only residue") and 4 ("Deep-link, don't narrate").

---

_Last reviewed: 2026-06-05 by `claude`_
