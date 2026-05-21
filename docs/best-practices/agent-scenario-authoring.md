# Agent scenario authoring

> **Status:** rule. **Why it exists:** the `repo-guide.html` is the user-facing surface for the marketplace — but until now, agent files only had a generic `description:` field. Users couldn't see *what an agent actually does in a session* without reading the full agent file. Per the deep-researcher's 2026-05-21 brief, every mature plugin/agent catalog ships per-item example scenarios + a use-case index. **How to apply:** when adding or updating an agent file, fill in `audience`, `works_with`, `scenarios`, and `quickstart` in the YAML frontmatter (see schema below). The repo-guide generator picks them up automatically.

This rule was extracted from Matt's earlier ask + deep-researcher 2026-05-21 brief during the repo-guide-scenarios work.

---

## The schema (YAML frontmatter — additions to existing fields)

```yaml
---
name: <existing>
description: <existing>
tools: <existing>
model: <existing>

# NEW fields (all optional but strongly recommended for shipped agents):
audience: [consultant, dev, ...]   # 1-3 values from the 7-value taxonomy below
works_with: [agent-name, ...]      # 2-5 agents this one composes with
scenarios:
  - intent: "<short user-voice 'I want to...' sentence>"
    trigger_phrase: "<the literal phrase the user types — angle-brackets for placeholders>"
    outcome: "<what the user gets back, in 1 sentence>"
    difficulty: starter | advanced | troubleshooting
  - intent: "..."
    trigger_phrase: "..."
    outcome: "..."
    difficulty: ...
quickstart:
  - "<line 1 — typically the trigger phrase shape>"
  - "<line 2 — expected output shape>"
  - "<line 3 — common follow-up: which agent to dispatch next>"
---
```

## The audience taxonomy (fixed at 7 values)

These are the categories users browse the marketplace by. **Do not invent new values** — extend the taxonomy explicitly if a real new user profile surfaces.

| Value | Who | Example agents |
|---|---|---|
| `consultant` | Solo consultant building client deliverables (Matt's profile) | architect, deep-researcher, documentarian, partner-success-manager, project-manager |
| `psm` | Partner Success Manager (Matt's wife's profile) | partner-success-manager, documentarian, project-manager |
| `dev` | Software developer | backend-coder, frontend-coder, code-reviewer, security-reviewer, tester-qa, architect |
| `power-platform-maker` | Power Platform low-code maker | (all `power-platform/*` agents) |
| `data-engineer` | Data engineering / ELT / dbt / Cube | data-engineer, architect, backend-coder |
| `analyst` | Financial / FP&A / business analyst | (all `finance/*` agents), documentarian, deep-researcher |
| `compliance` | Compliance / regulatory / audit-prep | (all `regulatory-compliance/*` agents), security-reviewer |

## Scenario authoring guidance

### 2-3 scenarios per agent (not more, not fewer)

- **1 starter** — the most-common, lowest-cognitive-load way to invoke the agent. The "if you only knew one thing about this agent" scenario.
- **1 advanced** OR **1 troubleshooting** — a less-obvious use case that shows the agent's depth.
- Optionally a 3rd scenario covering the remaining axis (advanced vs troubleshooting).

### The `intent` field

- Written in the **user's voice** (first person, present tense)
- Concrete enough that a user with the same need recognizes themselves
- ~10-20 words; if it's longer than that, the scenario is probably two scenarios

**Good:** *"Diagnose a production metric drop that doesn't match source data"*

**Bad:** *"Help with data quality issues"* (too vague; users don't search for "data quality issues")

### The `trigger_phrase` field

- The **literal phrase the user types** to invoke the agent
- Use `<angle-brackets>` for placeholders the user fills in
- This is the headline differentiator — it tells users exactly what to type, not just what the agent does

**Good:** *"Profile and fix the memory leak in `<handler>` — load test repros it at 50 req/s"*

**Bad:** *"Ask the agent for help with performance"*

### The `outcome` field

- 1 sentence describing what comes back
- Concrete — name the artifact (plan / diff / brief / report / memo)
- Mention what makes it "done" — tests pass / commit ready / verified in browser

### The `difficulty` field — fixed three values

| Value | Meaning | When to tag |
|---|---|---|
| `starter` | First-time invocation; lowest-cognitive-load way to use this agent | The headline scenario every agent should have |
| `advanced` | Non-obvious use case demonstrating depth | The second scenario for most agents |
| `troubleshooting` | Diagnostic / debugging / firefighting | Reserved for agents whose job genuinely includes triage (backend-coder, frontend-coder, project-manager, security-reviewer, tester-qa, etc.) |

## Quickstart authoring guidance

3 lines, in this order:

1. **Trigger phrase template** — the shape of what the user types ("Trigger phrase: '...'"). May summarize multiple scenarios.
2. **Expected output** — what comes back; mention any artifact-shape promise (plan / brief / diff)
3. **Common follow-up** — which agent to dispatch next, or what the next step looks like

Keep each line under ~120 chars. The block renders as a numbered list in the repo-guide.

## Works-with authoring guidance

- 2-5 agents that this one composes with in the marketplace
- Use the agent's `name` field (kebab-case), not file path
- Order by relevance — the most-common collaborator first
- Cross-plugin works-with is allowed (e.g., a `power-platform/*` agent listing `ravenclaude-core/architect`)

## What the repo-guide does with these fields

The `scripts/generate-repo-guide.py` script reads the YAML frontmatter and produces:

- **Per-agent card:** audience chips (top), scenarios block (starter visible, others in `<details>`), quickstart (numbered list), works-with chips (bottom)
- **Overview tab use-case table:** "I want to…" lookup aggregating every `intent` across every agent — sorted starter-first then alphabetically. Each row links to the plugin section.
- **Per-plugin Last-updated badge:** auto-derived from `git log -1 --format=%cs -- plugins/<name>` — no schema field needed

## When to update scenarios

- **Whenever the agent's responsibilities materially change** — new tool added, new domain covered, new escalation path
- **When `/wrap` surfaces a scenario that the agent's current set doesn't cover** — promote the scenario from the engagement-feedback loop into the agent's authoritative scenarios
- **On the Researcher's Weekly Deep Research sweep** — confirm the trigger phrases still match how users actually invoke the agent

## Plugin-by-plugin status

| Plugin | Agents | Backfilled? |
|---|---|---|
| `ravenclaude-core` | 14 | ✅ v0.1.0 of this convention (PR #36) |
| `power-platform` | 11 | Pending backfill |
| `edtech-partner-success` | 6 | Pending backfill |
| `data-platform` | 4 | Pending backfill |
| `finance` | 7 | Pending backfill |
| `regulatory-compliance` | 6 | Pending backfill |
| `web-design` | 7 | Pending backfill |

**The repo-guide gracefully handles missing fields** — an un-backfilled agent renders with just its description, like before. Backfill is non-breaking and can happen incrementally.

## Anti-patterns to avoid

- **Vague intents that could mean any agent.** "Help with X" is not a scenario; "Build a new X with Y constraint" is.
- **More than 3 scenarios per agent.** Users won't scan past the first 2-3. Pick the most-useful ones.
- **Trigger phrases that nobody would actually type.** The phrase should be recognizable speech, not invented dialect.
- **Outcomes that just restate the intent.** "Outcome: the user's intent is satisfied" — useless. Name the artifact.
- **Audience inflation.** Tagging every agent `[consultant, dev, psm, analyst, ...]` defeats the filtering purpose. Pick 1-3 most-relevant.
- **Stale scenarios.** Scenarios go stale when the underlying agent's responsibilities shift; the Researcher staleness sweep catches this.

## References

- [`../proposals/`](../proposals/) — Matt's proposals folder where the original ask lived
- `scripts/generate-repo-guide.py` — the generator that consumes this schema
- `repo-guide.html` — the artifact (always re-generated, never edited by hand)
- The deep-researcher's 2026-05-21 brief is the source for the format + audience taxonomy + use-case-table pattern
