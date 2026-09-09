# Repo review — design questions (2026-09-06)

One item from the [2026-09-06 review](2026-09-06-repo-review-findings.md) needs a maintainer
decision before it can be implemented. Everything else was either fixed autonomously or
confirmed a non-defect.

## Q1 — How should generated Copilot agent projections resolve their cross-reference links?

**What happens now.** `scripts/generate-copilot-plugin.py` projects each source agent
(`plugins/ravenclaude-core/agents/<name>.md`) into
`plugins/ravenclaude-core/copilot/agents/<name>.agent.md`, copying the markdown body
verbatim. The bodies contain relative links written for the **source** layout, e.g.:

- `../knowledge/verification-discipline.md`
- `../rules/security.md`, `../rules/agent-collaboration.md`
- `../skills/structured-output/SKILL.md`
- `../templates/raid-log.md`, `../templates/task-list.md`
- `../CLAUDE.md`
- cross-plugin: `../../data-platform/skills/rls-policy-authoring/SKILL.md`

From `plugins/ravenclaude-core/agents/` those resolve correctly. From
`plugins/ravenclaude-core/copilot/agents/` they resolve to `copilot/knowledge/…`,
`copilot/rules/…`, `copilot/CLAUDE.md`, etc. — none of which exist in the projection. The
sweep counted **149** such broken links across the projected agents plus `copilot/AGENTS.md`.

**Why it wasn't auto-fixed.** The files carry a `GENERATED … do not edit by hand` header and
a `--check` freshness gate fails CI on drift, so any hand-edit is overwritten. The fix must
live in the generator, and the right transform depends on a policy call that affects Copilot
consumers.

**Impact:** low-to-medium. These are documentation cross-references, not executable wiring;
Copilot CLI still runs the agent. But a consumer who follows a link gets a 404, and it
undercuts the "same discipline, projected" story.
**Effort:** small–medium (one generator, plus regenerating the projection + passing the
freshness gate).

**Options:**

1. **Rewrite to point back into the source plugin tree** — rewrite `../X` → `../../X`
   (i.e. `plugins/ravenclaude-core/X`) during projection. Cheapest; keeps one canonical copy
   of knowledge/rules/skills. Cross-plugin `../../other/…` links become `../../../other/…`.
2. **Make links repo-absolute** (`/plugins/ravenclaude-core/knowledge/…`). Robust to layout,
   but only meaningful when browsed at the repo root, not in an installed consumer repo.
3. **Strip the links, keep the link text** — projection becomes self-contained prose with no
   dangling references. Loses the cross-references entirely.
4. **Also project the referenced trees** into `copilot/` — highest fidelity, largest
   footprint and most duplication; probably overkill.

**Recommendation:** Option 1 (rewrite `../` → `../../` for in-plugin links, `../../` →
`../../../` for cross-plugin), because it preserves the references against a single source of
truth with the smallest generator change. Option 3 is the fallback if the projected docs are
meant to be install-portable (where no relative target is guaranteed to exist).

**Relevant code:** `scripts/generate-copilot-plugin.py` (projection + freshness `--check`);
projected output under `plugins/ravenclaude-core/copilot/agents/`.

---

_No other design-input items this run — the tree passes every one of its own gates; see the
findings doc for the full green sweep._
