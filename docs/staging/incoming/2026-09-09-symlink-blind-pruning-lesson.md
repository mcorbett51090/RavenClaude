<!-- RAVENCLAUDE-STAGING-METADATA
type: lesson
topic: architecture
proposed-by: consumer project managing a Copilot Chat/CLI context-budget overflow
proposed-on: 2026-09-09
target-file: docs/memory-bank/lessons-learned.md
status: pending
-->

## 2026-09-09 — A skill-catalogue prune script that skips symlinks doesn't shrink anything `ravenclaude setup` wired

**Context:** A consumer project hit "prompt token count exceeds the limit" in GitHub Copilot Chat / Copilot CLI. Both surfaces read `.claude/skills/*/SKILL.md` directly and inject name+description into every turn (VS Code's native "Agent Skills" feature). The project had a local prune script to shrink the catalogue, and had run it the day before — the error recurred anyway.

**What we tried first:** Trusted the prune script's own report ("0 entries to cut") as proof the catalogue was already minimal, and looked elsewhere for the regression (session history growth, instruction-file bloat, MCP overhead).

**Why it failed:** The prune script explicitly skipped every symlink (`[ -L "$d" ] && continue`, comment: "leave the marketplace wiring alone"). It could only ever shrink in-repo copies of marketplace bundles. In this project, symlinks made up 208 of 231 entries (90%) — everything `ravenclaude setup --with-plugin <name>` wires in bulk via `wire_plugin_skills()`. The script's "0 to cut" report was true and also completely misleading: the overwhelming majority of the injected cost was sitting in a category the tool structurally couldn't see. Any local pruning of that symlinked content is undone on the next `ravenclaude setup`/update, because `wire_plugin_skills()` re-wires the full plugin roster unconditionally every time, with no concept of a persisted exclusion.

**What works:** Treat wholesale-wired content (symlinks, generated files, bulk-copied templates — anything a setup/install script regenerates on every run) as a *first-class* category in any local curation tool, not an exempted one. A curation tool that only touches what it directly owns, while silently reporting "0 to fix" on the majority of the actual cost, is worse than no tool — it creates false confidence. The durable fix isn't a better prune script; it's making the *wiring step itself* consult a persisted, project-level policy (an allow/deny list) so exclusions survive every re-wire instead of needing to be manually re-applied after each update.

**How to apply:**
- When a repeatable install/setup/generate step writes into a directory a human or a downstream tool also curates, check whether that step is idempotent-and-full-overwrite (re-wires everything, every time) or additive-only. If it's full-overwrite, any exclusion policy needs to live *inside* that step (read a policy file, skip what's denied), not as a separate pass that runs once and gets silently reverted on the next regeneration.
- Before trusting a "nothing to do" report from a curation/audit tool, verify the tool's own scope — ask what category of content it structurally cannot see, not just what it found.

**Trace:** Originated while diagnosing a Copilot Chat/CLI "prompt too long" recurrence one day after an apparent fix; generalized from the specific fix (a symlink-aware prune script) to the underlying pattern (bulk-wiring steps need built-in exclusion policy, not after-the-fact pruning).
