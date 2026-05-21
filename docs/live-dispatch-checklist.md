# Live-Dispatch Validation Checklist

**Status:** open. **Owner:** marketplace maintainer (Matt). **Created:** 2026-05-21 after Round-4 internal review.

## Why this file exists

Four rounds of internal review moved the repo from ~57/100 to ~89/100 (architect's verdict; Team Lead 86). The remaining ~11 points are gated on **live consumer dispatch**, not more internal review. Per the Plan agent's Round-4 call: *"Continuing to drive the score upward via internal review cycles without a real user putting the marketplace through a dispatch will produce false confidence."*

This checklist enumerates the live exercises that can actually validate the marketplace, ranked by information yield. None of them are runnable by an agent inside the marketplace's own development session — they require either a slash-command invocation (`/plugin install`, `/plugin marketplace update`, `/reload-plugins`) or a separate Claude Code session in a throwaway project.

## Observed gap as of 2026-05-21

The Structured Output Protocol contract is declared in the constitution (`plugins/ravenclaude-core/CLAUDE.md`) and embedded in all 23 specialist agents' Output Contract sections. **But every sub-agent dispatched during the four review rounds (architect, deep-researcher, Plan agent) pulled from the v0.1.0 cache at `~/.claude/plugins/cache/ravenclaude/ravenclaude-core/0.1.0/` — installed 2026-05-09, pre-SOP-retrofit.** None of them emitted a `---RESULT_START--- … ---RESULT_END---` block.

This means the contract is technically aspirational from a runtime perspective. The v0.4.0 retrofit is shipped on disk and CI-validated, but no live dispatch has confirmed:

1. Agents actually emit the SOP block when their definition is loaded from current.
2. The Team Lead actually parses the JSON for routing.
3. The Cited-Adjudicator Escalation pattern triggers on `confidence ≥ 0.7` claims of inter-agent conflict.

Until one of these exercises runs, the constitution's "active and implemented" claim should be read as "declared and CI-validated; runtime untested."

## Exercises (ranked by information yield)

### 1. SOP smoke test — install + non-trivial dispatch (HIGHEST YIELD)

**Estimated points recoverable:** 3-4 (action-readiness +1, consumer experience +1-2, test/verification depth +1).

**Procedure:**

```bash
# 1. Update the installed plugin to current dev version
/plugin marketplace update ravenclaude
/reload-plugins
# Confirm installed version matches plugin.json
cat ~/.claude/plugins/installed_plugins.json | jq '.plugins["ravenclaude-core@ravenclaude"][0].version'
# Expected: "0.4.0" or higher

# 2. Spawn a non-trivial dispatch
# In the same Claude Code session, prompt:
#   "Have the ravenclaude-core architect produce a design plan for adding a
#    new layout-enforcement check that blocks Markdown files larger than 200 lines."
```

**Acceptance criteria:**

- [ ] The architect's response ends with a `---RESULT_START--- … ---RESULT_END---` JSON block.
- [ ] The JSON `status` field is one of `"complete"`, `"partial"`, `"blocked"`.
- [ ] The JSON `handoff_recommendation` uses the `to_specialist` key (not `specialist` — that was R3's example/implementation drift bug, now fixed).
- [ ] The Team Lead's follow-up uses the JSON to route (e.g., calls the recommended specialist via `Agent(subagent_type="ravenclaude-core:<role>")`).

**If any criterion fails:** the SOP retrofit (PR 3) needs a follow-up. Likely cause: the agent model receives the Markdown contract before the SOP appendix and treats the SOP as optional. Mitigation: move the SOP block up, or restate it in the dispatch brief.

### 2. Cited-Adjudicator Escalation trigger test (MEDIUM YIELD)

**Estimated points recoverable:** 1-2 (action-readiness +1, boundary clarity +0.5).

**Procedure:** trigger a real inter-agent disagreement.

```
1. Spawn ravenclaude-core:architect to review a load-bearing claim
   (e.g. "this regex matches only HEAD-anchored refs").
2. Spawn ravenclaude-core:code-reviewer to re-review the same claim
   with a counter-hypothesis embedded in the brief.
3. Observe whether the Team Lead spawns deep-researcher in citation-only
   mode when the two agents disagree, per the rule added to
   plugins/ravenclaude-core/rules/agent-collaboration.md.
```

**Acceptance criteria:**

- [ ] If both agents report `confidence ≥ 0.7` and disagree, the Team Lead spawns deep-researcher.
- [ ] The deep-researcher's brief explicitly requests a citation-backed verdict.
- [ ] The final verdict is binary (one agent correct, or both partially).

**If criterion 1 fails:** the rule is documented but not internalized. The Team Lead needs the rule promoted into the `spawn-team` skill's Step 6 as a hard-routing rule (currently it is — verify it's being read at dispatch time).

### 3. `/plugin marketplace update` round-trip (LOW YIELD, HIGH ASSURANCE)

**Estimated points recoverable:** 1.

**Procedure:**

```bash
# In any consumer project where the plugin is installed at an old version:
/plugin marketplace update ravenclaude
/reload-plugins

# Verify:
cat ~/.claude/plugins/installed_plugins.json | jq '.plugins["ravenclaude-core@ravenclaude"]'
ls ~/.claude/plugins/cache/ravenclaude/ravenclaude-core/

# Both should reflect the latest version with the latest installed_at timestamp.
```

**Acceptance criteria:**

- [ ] `installed_plugins.json` shows the new version.
- [ ] The new cache directory exists with `hooks.json`, all 13 agents, etc.
- [ ] Hooks fire from the new cache, not the old one (test by making an edit and watching for the format/layout banners).

### 4. Consumer fresh-install dry run (HIGHEST EFFORT)

**Estimated points recoverable:** 2-3.

**Procedure:**

```bash
# In a fresh throwaway directory:
mkdir /tmp/rcl-consumer && cd /tmp/rcl-consumer
git init
# Open Claude Code in this directory, then:
/plugin marketplace add /workspaces/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/init-agent-ready
```

**Acceptance criteria:**

- [ ] `/init-agent-ready` creates `AGENTS.md`, `CLAUDE.md`, `.repo-layout.json`, `docs/team-constitution.md`, optionally `.github/workflows/validate-layout.yml`.
- [ ] The generated `CLAUDE.md` includes both `@AGENTS.md` and `@docs/team-constitution.md` imports.
- [ ] The Team Lead (top-level Claude session in this fresh project) loads the team roster from `docs/team-constitution.md` without being prompted.
- [ ] A dispatch of `ravenclaude-core:architect` works (validates plugin-runtime agent registration outside the marketplace's own dev session).

## When to revisit this checklist

- Before any public release (private remote → public remote transition).
- After landing any change that touches `spawn-team.md`, `agent-collaboration.md`, the Output Contract section of any agent, or the SOP block schema.
- Whenever a real consumer project reports unexpected agent behavior — the test cases above are the diagnostic baseline.

## What "done" looks like

All four exercises run, all criteria met. The score moves from ~89 to mid-90s. Beyond that the ceiling is set by limitations of the underlying Claude Code platform (no `requires` field for MCP servers, no filesystem-discovery plugin loading), not by anything this marketplace can fix internally.
