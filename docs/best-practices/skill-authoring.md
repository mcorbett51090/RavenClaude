# Authoring a SKILL.md (progressive disclosure)

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Plugin authoring, skill design, context economy.

**Applies to:** Anyone adding a skill to a plugin's `skills/<name>/SKILL.md` (today mostly `plugins/ravenclaude-core/skills/`; the same patterns apply to every plugin). This is the missing sibling of [`hook-authoring.md`](./hook-authoring.md), [`authoring-plugin-slash-commands.md`](./authoring-plugin-slash-commands.md), and [`agent-scenario-authoring.md`](./agent-scenario-authoring.md) — the marketplace ships **660+ skills** and had no authoring rule for the most-produced component type.

---

## Why this exists

A skill is the marketplace's unit of reusable, on-demand procedure: a `SKILL.md` with YAML frontmatter (and optional sibling files) that Claude **discovers by its description** and loads **only when the work calls for it**. That last property — load-on-demand — is the whole point, and it's the one new authors quietly break.

The mechanism is **progressive disclosure**: Claude does not read every skill body at session start. It reads each skill's `name` + `description` (cheap, always resident), and pulls the full `SKILL.md` into context **only when the description matches the task** — and pulls a referenced sibling file (`reference/forms.md`, `driver.py`) only when the body says to. So two authoring mistakes have an outsized, invisible cost:

1. **A vague description** → the skill is never discovered (it may as well not exist), or it's discovered for the wrong tasks (noise on every unrelated session).
2. **A bloated `SKILL.md`** → once discovered, it dumps hundreds of lines of edge-cases-you-rarely-need into the window, competing with the files and reasoning the task actually needs.

At 660+ skills, both failure modes compound. This doc captures the patterns the repo's own well-shaped skills already demonstrate so the next skill starts from a known-good shape — the skill-side analog of the agent-`description` ≤300-char discipline (`AGENTS.md` § "The agent-description token budget") and the MCP-tool-context budget rule.

## How to apply

### Frontmatter is the discovery surface — write it for the router, not for humans

Every `SKILL.md` opens with YAML frontmatter. Two fields do the work:

```yaml
---
description: <what it does + WHEN to reach for it — this is the only text loaded for discovery>
allowed-tools: Bash, Read   # optional; least-privilege the skill's tool grant
---
```

- **`description` carries the entire discovery decision.** Lead with the capability and the **trigger condition** ("Use when …"), in the user's vocabulary, not yours. A good one names the situation that should fire it; a bad one describes the implementation. Compare the repo's [`decision-review`](../../plugins/ravenclaude-core/skills/decision-review/SKILL.md) ("Route a yes/no decision through the tribunal … **Use before asking the user any yes/no question**") — the trigger is explicit — against a description that only says "tribunal routing logic." Same skill; only the first gets invoked.
- **Keep it tight.** The description rides in the routing budget alongside every other enabled skill's, the same count→cost shape as agent descriptions and MCP schemas. Be specific and stop; don't paste a feature list.
- **`allowed-tools` is least-privilege, not a formality.** Grant only what the skill runs (`decision-review` declares `Bash, Read`). Omit it only when the skill is pure prose with no tool calls.

### Keep the SKILL.md body lean — split, don't stuff

Treat `SKILL.md` as the **high-level spine**, not the manual. The widely-cited ceiling is **~500 lines**; past that, performance degrades and the body is carrying detail that doesn't earn its resident cost. When a section grows heavy, move it to a sibling file and **reference** it, so Claude loads that detail only when it reaches that step:

- Procedural depth → `reference/<topic>.md`, pulled in only when the body points at it.
- Runnable logic → a sibling script the body invokes, not pseudo-code inlined into prose. The repo's [`visual-feedback-loop`](../../plugins/ravenclaude-core/skills/visual-feedback-loop/SKILL.md) is the worked example: a lean `SKILL.md` (the discipline + when to use it) **plus** `driver.py` (the deterministic referee). The body explains; the script does. [`brand-extraction`](../../plugins/ravenclaude-core/skills/brand-extraction/SKILL.md) follows the same split (`SKILL.md` + `extract_brand.py`).

This is progressive disclosure applied within the skill: metadata is tier 1, the body is tier 2, the linked files/scripts are tier 3 — each loaded only when the prior tier routes to it.

### Structure the body so Claude can act, not just read

The repo's skills converge on a shape worth copying:

- **`## What this is`** — one paragraph; what the skill produces.
- **`## When to use it` / `## When NOT to use it`** — the boundaries the description hinted at, spelled out. The negative case prevents over-firing.
- **Numbered steps** for the procedure — imperative, checkable, each a thing to *do*.
- **Cross-links** to the canon it distills (a `knowledge/` file, a sibling skill), so the skill stays the *action* surface and the knowledge file stays the *reference*.

### Test it the way it will actually be invoked

A skill that reads well can still fail to fire or mislead in use. Before shipping:

1. **Discovery check** — would the `description` match the tasks you intend, and *not* match unrelated ones? Read it as the router will: does it name the trigger?
2. **Cold-run check** — invoke it on a real task and watch where Claude goes. Missed references (it never opened `reference/x.md`), ignored sections, or unexpected exploration mean the structure isn't carrying its intent — fix the body, not the prompt around it.
3. **Gates** — a new skill must satisfy the repo's frontmatter/layout gates (`skills/*/SKILL.md` is already allow-listed; descriptions feed the same discovery budget the gates protect). Bump the owning plugin's version per [`plugin-versioning.md`](./plugin-versioning.md) when the skill is consumer-visible.

## Edge cases / when the rule does NOT apply

- **A genuinely small, single-step skill** doesn't need sibling files — the ≤500-line ceiling is an upper bound, not a target. Don't split for its own sake.
- **A skill that is mostly a runnable engine** (the work is in the script) keeps `SKILL.md` thin by design — that's the visual-feedback-loop shape, not a violation.
- **Architecture choice precedes authoring.** "Should this be a skill at all, vs. a sub-agent or a plugin agent?" is answered first by [`domain-plugins-extend-via-skills-not-parallel-agents.md`](../../plugins/ravenclaude-core/best-practices/domain-plugins-extend-via-skills-not-parallel-agents.md). This doc is about authoring a skill *once you've decided it is one*.

## See also

- [`hook-authoring.md`](./hook-authoring.md) · [`authoring-plugin-slash-commands.md`](./authoring-plugin-slash-commands.md) · [`agent-scenario-authoring.md`](./agent-scenario-authoring.md) — the rest of the component-authoring family.
- [`../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](../../plugins/ravenclaude-core/best-practices/mcp-tool-context-is-a-budget-enable-only-what-you-need.md) — the same count→cost discipline on the MCP surface; a skill `description` is one more line item in that budget.
- [`../../AGENTS.md`](../../AGENTS.md) § "The agent-description token budget" — the sibling cap on the agent-description surface (descriptions are preloaded for routing; bodies load lazily). Skill descriptions behave the same way.
- [`../../plugins/ravenclaude-core/skills/prompt-pattern-library/SKILL.md`](../../plugins/ravenclaude-core/skills/prompt-pattern-library/SKILL.md) — the catalog of marketplace prompt patterns a skill body can reuse.

## Provenance

Distilled from the recurring Claude-community scan (the [2026-06-23 subreddit scan](../research/2026-06-23-claude-subreddit-scan/README.md)), grounded against this repo's own skills (`visual-feedback-loop`, `brand-extraction`, `decision-review` — read this session) and Anthropic's skill-authoring guidance ([Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices), [Agent Skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview), [Extend Claude with skills](https://code.claude.com/docs/en/skills)). The ~500-line ceiling is a community/Anthropic guideline (verify-at-use — the exact number moves); the durable, load-bearing part is the **mechanic**: descriptions are always-resident and drive discovery, bodies and sibling files load on demand, so lean-and-split beats stuff-it-all-in.

---

_Last reviewed: 2026-06-23 by `claude`_
