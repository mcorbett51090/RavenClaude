---
scenario_id: 2026-06-05-project-status-misattributed-across-repos
contributed_at: 2026-06-05
plugin: team-portfolio
product: reports
product_version: "n/a"
scope: likely-general
tags: [project-filter, over-match, label, title-prefix, cross-repo-attribution]
confidence: medium
---

## Problem

The `project-status.md` roll-up showed the "Website Redesign" project absorbing PRs and issues that clearly belonged to an unrelated internal-tooling effort — the project's count was inflated and the supervisor's "what shipped for the website this week" read was wrong. Separately, a handful of genuine website PRs were **missing** from the project entirely. Over-match and under-match, same project, same run.

## Context

- Shared repos: the website work and the internal-tooling work both live partly in `org/platform`, with no dedicated website repo.
- The project filter in `team-portfolio.json` used a `title_prefixes` rule of `["[web]"]` plus a `labels` rule of `["website"]`.
- Two collisions: an internal-tooling team had started prefixing PRs `[web-hooks]` (which `startswith("[web")`-adjacent titles caught because the prefix `[web]` is a substring people typed loosely as `[web hooks]`), and some real website PRs carried only a `frontend` label, never `website`.

## Attempts

- Tried: re-read how the collector actually classifies (the source of truth, CLAUDE.md §4). `classify_project()` returns the **FIRST** project whose match rules cover an event, and a project matches if **ANY** of: the event's repo is in `match.repos`, OR any event label is in `match.labels` (case-insensitive), OR the title **`startswith`** any `match.title_prefixes` entry (case-insensitive). Outcome: confirmed the over-match was the title-prefix rule — `"[web hooks] add retry".startswith("[web")` is **false** for prefix `"[web]"` but **true** for a looser prefix; the team had also added `"[web"` (no closing bracket) to the config during an earlier edit, which is what actually caught `[web-hooks]`. The closing bracket matters: `"[web]"` is precise, `"[web"` over-matches.
- Tried: confirmed the under-match was the label rule — events labeled only `frontend` never matched `["website"]`, and there was no repo-level rule to catch them because the repo is shared. Outcome: an unlabeled/differently-labeled real event falls through to the `unmatched` bucket (which is **normal, not an error** — CLAUDE.md §5), so it silently dropped out of the project view.
- Tried (the disciplined fix, not a guess): per [`../best-practices/project-filters-must-be-tested-with-a-dry-run-before-production.md`](../best-practices/project-filters-must-be-tested-with-a-dry-run-before-production.md), ran the collector on the existing window and inspected which events got `project: "Website Redesign"` **before** changing anything. Then tightened `title_prefixes` back to the exact `"[web]"` (closing bracket), added `"frontend"` to `match.labels` to catch the real misses, and re-ran to confirm the over-matched `[web-hooks]` items dropped and the `frontend`-labeled website PRs joined. Did NOT manually list individual PRs — the plugin's house rule is filters, not hand-curated membership ([`../best-practices/cross-repo-project-tracking-uses-filters-not-manual-lists.md`](../best-practices/cross-repo-project-tracking-uses-filters-not-manual-lists.md)).

## Resolution

The attribution wasn't a bug in the scripts — the **filter was both too loose (a clipped `"[web"` prefix) and too narrow (one label where the team used two)**. The fix was a precise prefix plus the second label, verified by a dry-run diff of the `project` field, not by editing membership by hand.

**Action for the next operator:** before trusting a project's count, **dry-run the filter and read the `project` field on the resulting events** — never tune a filter blind. Traverse the "Project Filter Design" tree in [`../knowledge/team-portfolio-decision-trees.md`](../knowledge/team-portfolio-decision-trees.md): dedicated repo → repo-level match (cleanest, no per-item discipline); shared repos + consistent labels → label match; shared repos + naming convention → title-prefix match; no convention → recommend the team adopt one before tracking. Remember `title_prefixes` is `startswith` (anchor it with the full bracketed token), `labels` is case-insensitive exact-membership, and the **first** matching project wins — so order matters when two projects could both claim an event.
