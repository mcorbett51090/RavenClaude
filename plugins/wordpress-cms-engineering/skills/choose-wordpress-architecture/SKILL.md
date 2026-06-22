---
name: choose-wordpress-architecture
description: "Decide how to build a WordPress site: classic vs block/FSE theme, plugin vs theme vs must-use plugin for custom code, headless/decoupled vs traditional, and single vs multisite — matched to the editing model, not fashion."
---

# Choose WordPress Architecture

Match the build to the **editing model and what must survive a redesign**, not the buzzword.

## The splits

| Question | Default | Reach for the alternative when |
|---|---|---|
| Theme model | **Classic** (PHP templates) when design is developer-owned and pixel-tight | **Block/FSE** (`theme.json`, Site Editor) when editors compose layouts themselves |
| Where custom code lives | **Plugin** (portable, survives theme swaps) | **Theme functions** only for presentation; **must-use plugin** for always-on infrastructure |
| Front-end coupling | **Traditional** (themes render PHP) | **Headless** (REST/WPGraphQL + Next/Astro) when the front end genuinely demands a JS stack |
| Site count | **Single install** | **Multisite** for a true network sharing users/plugins/themes under one admin |

## Decisions that follow
- **Child theme boundary:** never edit core or a parent theme — see [`../../best-practices/never-edit-core-use-child-themes-and-hooks.md`](../../best-practices/never-edit-core-use-child-themes-and-hooks.md).
- **Logic placement:** keep business logic in plugins — see [`../../best-practices/keep-business-logic-in-plugins-not-themes.md`](../../best-practices/keep-business-logic-in-plugins-not-themes.md).
- **Building it:** scaffold blocks/themes with [`../build-blocks-and-themes/SKILL.md`](../build-blocks-and-themes/SKILL.md) and extend with [`../extend-with-hooks-and-plugins/SKILL.md`](../extend-with-hooks-and-plugins/SKILL.md).

## Anti-patterns
- Block/FSE chosen for a site no non-developer will ever edit (complexity with no payoff).
- Business logic (CPTs, integrations) baked into the theme, so a redesign deletes features.
- Headless adopted for the novelty, sacrificing the editor's live preview and the plugin ecosystem.
- Multisite for a few unrelated sites — it complicates backups, migrations, and per-site plugins.

Traverse the relevant trees in [`../../knowledge/wordpress-decision-trees.md`](../../knowledge/wordpress-decision-trees.md) before committing.
