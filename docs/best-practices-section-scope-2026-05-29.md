# Scope — per-plugin/agent "Best practices" section (future PR)

> **Status:** SCOPE ONLY (2026-05-29). Requested by Matt; to be tackled as its own PR after scoping. Origin incident: an agent imported a `pac` solution but left the Power Automate flows/workflows **off** — Matt wants a **mandatory post-import activation step** in the deployment pipeline, generalized into a best-practices surface across plugins. Not a design doc yet — this frames the problem, what it must compose with, the recommended shape, and the open questions, so the build PR starts grounded.

## The ask (two layers)

1. **Structural:** add a "Best practices" section to each plugin — at the plugin level and/or the agent level. A *positive* "do this" surface, the counterpart to the existing *negative* anti-patterns surface.
2. **Specific trigger:** post-`pac solution import`, PA flows + workflows land **disabled** and must be turned on. Make **post-import activation a mandatory, first-class deployment step**, not just recovery knowledge.

## What it must compose with (don't duplicate — verify exact mechanics at build time)

The marketplace already has adjacent surfaces; a "best practices" section must slot beside them, not re-state them:

- **Power Platform `CLAUDE.md` §3 "house opinions" + §4 "anti-patterns"** — the *don't-do-this* surface, partly enforced by a house-opinions hook (`plugins/power-platform/hooks/…` — `[unverified — confirm the exact hook file + the "8 checks" count at build time]`). Best practices would be the *do-this* sibling.
- **Per-agent Output Contract** — already a per-agent structured surface; an agent-level best-practice could attach here.
- **Inherited protocols (core, do NOT restate):** Capability Grounding, Claim Grounding & Source Honesty, Last-Mile. Best practices are *domain-specific operational* guidance, distinct from these cross-cutting protocols.
- **Knowledge bank** — `programmatic-flow-creation.md` already carries the "PA flow recovery — stuck/broken/off" decision tree + toggle-on steps. The post-import-activation best practice should *point at* it, not duplicate the recovery detail. The gap is **promotion**: from "here's how to recover off flows" (reactive knowledge) to "activating flows is a required step of every import" (proactive best practice).

## Recommended shape (the marketplace's "prose is weak; enforce where you can" ethos)

A best practice is only as strong as its enforcement surface. Tier the items:

1. **Documented convention (all best practices):** a `## Best practices` section in each plugin's `CLAUDE.md` (plugin-level), with agent-level items in the relevant agent file. Positive, imperative, each with a one-line *why* and a pointer to the deeper knowledge/runbook.
2. **Enforced where mechanical (the high-value ones):** for a best practice that's a concrete, detectable step — like *"a deployment script that runs `pac solution import` must be followed by a flow-activation step"* — back it with the existing **house-opinions advisory hook** (flag an import script with no subsequent activation) and/or a **deployment runbook/checklist template**. This is the only way the post-import-activation ask actually changes behavior under Copilot/multi-model, where prose is weakest (the lesson from the v0.58.0 accuracy work).
3. **Checklist artifact:** a `templates/` deployment checklist that makes post-import activation a literal line item the human/agent ticks.

## The post-import-activation worked example (the proving case)

- **Best practice (prose, PP CLAUDE.md):** *"After every `pac solution import`, activate the solution's Power Automate cloud flows and workflows — they import disabled. Verify each is On before declaring the deployment done."*
- **Enforcement (advisory hook):** flag a deployment script / pipeline file that contains `pac solution import` with no subsequent activation step (`pac …` activation, a Web API `statecode` update, or a documented manual toggle).
- **Knowledge pointer:** `programmatic-flow-creation.md` for the recovery/toggle mechanics + the `0x80060467` / `For_a_selected_row_V2` 404 gotchas.
- **DoD tie-in:** if a consumer sets a `definition_of_done.cmd` that smoke-tests the deployed flows, the DoD gate (v0.56.0) catches "imported but not activated" at Stop.

## Open questions (decide at the start of the build PR)

1. **Plugin-level vs agent-level vs both?** Recommend plugin-level `## Best practices` as the home, with agent-level items only where an agent owns a distinct practice (e.g. `dataverse-architect` vs `power-bi-engineer`).
2. **Which plugins get it now?** Recommend starting with `power-platform` (the incident's home + the richest operational surface), then templatize for the others rather than big-bang all 11.
3. **How much enforcement?** Just prose, or prose + the house-opinions hook extension + a checklist template? (Recommend prose + the one enforced check for post-import activation as the proving case.)
4. **Is "best practices" a new section or a rename/reframe of "house opinions"?** "House opinions" already reads as positive-ish guidance — confirm whether to add a distinct `## Best practices` or fold into the existing §3. (Lean: distinct section; house-opinions are *opinions/conventions*, best-practices are *operational steps*.)
5. **Cross-plugin convention:** should this be codified in the root `AGENTS.md`/core `CLAUDE.md` as a marketplace convention (every plugin SHOULD have a best-practices section), with a layout/CI nudge — mirroring how the scenario-authoring frontmatter is gated?

## Rough plan (when tackled)

1. Decide the open questions (a short Keep/Update/Deny, or a brief panel if the enforcement design is contested).
2. Add `## Best practices` to `power-platform/CLAUDE.md` with the post-import-activation item (+ 2-3 others) as the worked example.
3. Extend the house-opinions advisory hook with the post-import-activation check + a gate-audit fixture (fires on an import-without-activation script, silent on one with activation).
4. Add a deployment-checklist template.
5. Version bump + regen + gates. Then templatize/roll out to other plugins in follow-ups.
