---
description: "Choose how to build a WordPress site: classic vs block/FSE theme, plugin vs theme vs must-use, headless vs traditional, single vs multisite."
argument-hint: "[what the site does + who edits + scale + front-end needs]"
---

You are running `/wordpress-cms-engineering:choose-wp-architecture`. Use `wordpress-architect` + the `choose-wordpress-architecture` skill.

## Steps
1. Identify the editing model (who composes layouts and how), scale, and front-end needs.
2. Traverse the relevant trees in `knowledge/wordpress-decision-trees.md` (classic-vs-block/FSE, plugin-vs-theme-vs-mu, headless-vs-traditional).
3. Decide the theme model, code placement, coupling, and single-vs-multisite; name the child-theme/update plan and what you will NOT do (e.g. no business logic in the theme).
4. Emit using `templates/wordpress-architecture-decision.md` + the Structured Output block.
