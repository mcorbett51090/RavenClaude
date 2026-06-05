---
scenario_id: 2026-06-05-no-information-architecture
contributed_at: 2026-06-05
plugin: technical-writing-docs
product: generic
product_version: "unknown"
scope: likely-general
tags: [information-architecture, diataxis, navigation, search, findability]
confidence: high
reviewed: false
---

## Problem

A product had ~140 docs pages and a flat, alphabetical sidebar. Users "couldn't find anything" — the top support category was questions whose answer was already published. Analytics showed the in-docs search returned the right page in the top 3 only about a third of the time, and the most-visited page was the search results page itself (a findability smell: people land, can't navigate, and fall back to search). The team's first instinct was "we need better search" — but the navigation, not the index, was the problem.

## Constraints context

- Pages were organized by the **product's internal module structure** (mirroring the codebase), not by what a reader was trying to *do* — the exact `write-for-the-readers-task` anti-pattern.
- Nav labels were nouns matching internal feature names ("Orchestration Engine"), not reader tasks ("Schedule a job"), so a reader scanning the sidebar couldn't map their goal to a label (`navigation-labels-are-user-tasks`).
- The four Diátaxis kinds were interleaved: a single "Getting Started" page mixed a tutorial, three how-tos, and a reference table, so no page fully served any one need.

## Attempts

- Tried: tuning search (synonyms, weighting, a better index). Marginal — it treated the symptom. Search is a fallback *for when navigation fails*; a docs set where search is the primary path has an IA problem, not a search problem.
- Tried: a card-sort of the existing pages against the four Diátaxis kinds. Revealed that ~40% of pages were mixed-kind (a "tutorial" full of reference, a "guide" that lectured on concepts) and couldn't be cleanly filed — they had to be split before they could be filed.
- Tried (the move that worked): restructured the top-level IA around the **four Diátaxis kinds + reader tasks** (Tutorials / How-to guides / Reference / Explanation), split the mixed-kind pages, and rewrote nav labels as user tasks. Traversed the new `knowledge/diataxis-content-type-selection-decision-tree.md` for each ambiguous page. Search relevance recovered as a *side effect* once each page served one need and was titled by that need.

## Resolution

The fix was an **information-architecture** fix, not a search fix: organize around what the reader is doing (the four Diátaxis needs + task-named navigation), and split the pages that served more than one need so each could be filed and titled by a single job. Search improved because well-scoped, task-titled pages index and rank better — but it was the consequence, not the cause.

**Action for the next architect hitting "users can't find anything":** check whether **search is the primary navigation path** (a smell) before touching the search config. If the sidebar mirrors the codebase or uses internal feature nouns, the IA is author-shaped, not reader-shaped — fix that first. Card-sort against the four Diátaxis kinds, split mixed-kind pages, and re-label nav as user tasks. Canonical guidance: [`../knowledge/diataxis-content-type-selection-decision-tree.md`](../knowledge/diataxis-content-type-selection-decision-tree.md) and the [`audience-before-architecture`](../best-practices/audience-before-architecture.md) + [`navigation-labels-are-user-tasks`](../best-practices/navigation-labels-are-user-tasks.md) + [`write-for-the-readers-task`](../best-practices/write-for-the-readers-task.md) best-practices.

**Sources (retrieved 2026-06-05):**
- Diátaxis — the framework and the 2D needs grid: https://diataxis.fr/ and https://diataxis.fr/start-here/
- Diátaxis — "How to use Diátaxis as a guide to action" (apply it incrementally, page by page): https://diataxis.fr/how-to-use-diataxis/

These are stable framework sources; the analytics thresholds ("top-3 a third of the time") are this-engagement specific and not a benchmark — `[verify-at-use]` against the consumer's own analytics before quoting any number.
