# Default to trunk-based development

**Status:** Pattern
**Domain:** CI/CD pipeline design
**Applies to:** `devops-cicd`

Long-lived feature branches are merge debt that compounds: the longer a branch lives, the more the trunk drifts, the scarier the merge, and the weaker continuous integration becomes. You are not integrating continuously if you integrate once a month. Default to short-lived branches merged to trunk daily, with incomplete work hidden behind feature flags rather than parked on a branch. Reserve long-lived branches for genuine release trains (regulated, multi-version-support products) where the cost is understood and the divergence is managed deliberately. GitFlow's release/develop/hotfix lattice is overhead most teams pay without the multi-version need that justifies it.

## The bar, with the sources

Retrieved 2026-11-05:

| Source | What it actually says |
|---|---|
| [DORA — Trunk-based development](https://dora.dev/capabilities/trunk-based-development/) | Higher delivery performance correlates with **three or fewer active branches**, **merging to trunk at least once a day**, and **no code freeze and no integration phase**. Branches in this pattern "typically last no more than a few hours." A feature branch that lives for days or weeks is the slower pattern the page contrasts. |
| [DORA — Continuous integration](https://dora.dev/capabilities/continuous-integration/) | Teams perform better when developers merge into trunk at least daily. Quick tests stay under about ten minutes. A broken trunk is fixed before the next feature. |
| [Fowler — Patterns for Managing Source Code Branches](https://martinfowler.com/articles/branching-patterns.html) | "You should never have more than a day's work sitting unintegrated." He quotes the 2016 State of DevOps report: branch lifetimes under a day, and fewer than three active branches, track with higher delivery performance. |
| [Software Engineering at Google, ch. 16](https://abseil.io/resources/swe-book/html/ch16.html) | Development branches "should be minimal, or at best be very short lived." Release branches, where they exist, are snapshots. Fixes land on trunk and are cherry-picked. |
| [Google's monolithic repository (CACM)](https://cacm.acm.org/research/why-google-stores-billions-of-lines-of-code-in-a-single-repository/) | Long-lived branches with parallel development on the branch and the mainline are "exceedingly rare." |

A week of drift is already the slow pattern. Do not teach "rebase once a week" as hygiene.

## How to apply

- Merge to the default branch the same day. If the change is not ready to release, land it behind a flag (`deploy-separate-deploy-from-release`) instead of holding the branch.
- An unshared agent branch may rebase onto current trunk. A branch anyone else has fetched is updated by merging the base in, not by rewriting history.
- A release branch is a snapshot plus cherry-picks. It is not a second place where features are written.
- When several pull requests are open, follow [`merge-behind-clean-tips-before-dirty-ones.md`](./merge-behind-clean-tips-before-dirty-ones.md) before you merge any of them.

The operating checklist, including the fleet's behind-first order, is [`../../ravenclaude-core/knowledge/source-control-operating-practices.md`](../../ravenclaude-core/knowledge/source-control-operating-practices.md).

## See also

- [`../knowledge/devops-cicd-decision-trees.md`](../knowledge/devops-cicd-decision-trees.md) — "Trunk-based vs branch strategy".
- [`./release-feature-flags-are-not-free.md`](./release-feature-flags-are-not-free.md) — a flag is how unfinished work stays on trunk, and it has a removal date.
