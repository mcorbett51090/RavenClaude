---
name: prompt-pattern-library
description: Curated, applied prompt-pattern catalog used across this marketplace — decision-tree traversal pre-action prior, alternate-methods-before-blocked, Structured Output Protocol `---RESULT_START---` block, scenario-retrieval inline prior, escalation-by-mandatory-phrasing, citation-aware research, environment-context preamble, orchestrator-worker reinforcement, agent-scenario-authoring frontmatter, claim-grounding/source-honesty marker. Each pattern includes when to use it, what it composes with, an example block, and the failure mode it prevents. Reach for this skill when authoring a new agent, when an existing agent shows a behavior gap that a known pattern would close, or when the `prompt-engineer` is consulting on an agent revision. Used by `prompt-engineer` (primary).
---

# Skill: prompt-pattern-library

You are about to author or revise an agent file and need to compose its behavior from the marketplace's already-extant patterns. This skill is the catalog. Each pattern has a documented failure mode it prevents — that's the unit of justification for including it in an agent.

The patterns below are not theoretical. Every one of them is already in production use somewhere in `plugins/`; the references are real. **Do not fabricate patterns** — if a behavior you want isn't here, that's a signal to either compose from existing patterns or propose a new pattern via the `prompt-engineer` rather than inventing one inline.

## Pattern catalog

### 1. Pre-action decision-tree traversal

**What it is.** Before selecting a method for a domain action, the agent traverses the relevant `## Decision Tree: <Domain> — <Situation>` Mermaid graph in the active plugin's knowledge files top-to-bottom, resolving condition nodes against the user's stated context, defaulting to the smaller-blast-radius leaf.

**What it prevents.** The wrong-branch-from-the-start failure mode — the agent picks the wrong method on first try because the available branches were never visible to it. Reactive alternate-methods enumeration catches the case where the chosen method failed; this pattern catches the case where a better method existed and was never tried.

**When to compose.** Any agent whose domain has multiple methods for the same outcome (e.g. Power Platform: import via pac CLI vs. PA Management API vs. Dataverse Web API). Compose with: alternate-methods (pattern 2) — the tree picks the entry method; alternates kick in on failure.

**Example block (drop into agent body):**

```markdown
## Decision-tree traversal (priors)

Before selecting a method for [domain action], traverse the relevant
`## Decision Tree:` section in `plugins/<plugin>/knowledge/<file>.md`:

1. Match the user's situation to the tree's entry condition.
2. Resolve each condition node against the user's stated context, not
   keyword pattern-matching.
3. Default to the leaf with the smaller blast radius when multiple branches apply.
4. Escalate to a higher-blast-radius leaf only after the smaller one demonstrably failed.

See [`docs/best-practices/decision-trees-in-knowledge-files.md`](...).
```

**Anti-pattern.** Skipping the tree because "the user said X, so it's obviously branch Y." Pattern-matching on user words instead of resolving conditions against context produces the wrong-branch failure 30%+ of the time.

---

### 2. Alternate-methods-before-blocked

**What it is.** The §5 Capability Grounding Protocol rule: when the chosen tool/method/path fails, the agent enumerates ≥2-3 alternate paths to the same outcome, ranks by cost, tries the next-easiest before reporting blocked. The eventual blocked report lists what was tried *and* what was considered-and-ruled-out.

**What it prevents.** The "did you try X?" round-trip — the user shouldn't have to prompt for the second attempt; the agent should make it autonomously.

**When to compose.** Every agent that calls external tools, APIs, or CLIs. Mandatory for `dataverse-architect`, `flow-engineer`, `power-platform-admin`, `solution-alm-engineer`. Compose with: pre-action decision-tree traversal (pattern 1), mandatory-phrasing block (pattern 5).

**Example block:**

```markdown
## Capability Grounding — alternate methods

When a chosen tool, API, or path fails:

1. Enumerate ≥2-3 alternate paths to the same outcome (different API on the same
   platform, lower-level surface, different tool, semi-manual procedure with
   automation around the boring parts).
2. Rank by cost (time, dependencies, permissions, irreversibility). Easiest first.
3. Try the next-easiest BEFORE reporting blocked.
4. In the blocked report, list:
   - What was tried (with one-line outcomes)
   - What was considered and ruled out (with reason)
   - The remaining options and their cost
```

**Anti-pattern.** Reporting "this can't be done" after one failed attempt. Inventing alternatives that don't exist to look thorough.

---

### 3. Structured Output Protocol `---RESULT_START---` block

**What it is.** Every handoff-bearing agent report ends with reasoning/Markdown PLUS a delimited JSON block:

```
---RESULT_START---
{
  "status": "complete | partial | blocked",
  "summary": "one sentence",
  "deliverables": [...],
  "handoff_recommendation": {...} | null,
  "confidence": 0.0-1.0,
  "risks_or_open_questions": [...],
  "next_actions": [...]
}
---RESULT_END---
```

**What it prevents.** Unparseable handoffs. Lost reasoning when output is JSON-only. Lost machine-readability when output is Markdown-only.

**When to compose.** Every agent that hands off to the Team Lead or to a downstream specialist. Skippable for informational chatter ("file read," "test ran") but never for status reports.

**Example block:** see [`structured-output.md`](../structured-output/SKILL.md) for the canonical template. Inherit by reference, not by copy — agents that copy the block end up drifting from the canonical shape.

**Anti-pattern.** Embedding the JSON block inside a Markdown code fence (breaks delimiter parsing). Omitting one of the seven canonical keys. Producing the JSON without the preceding reasoning paragraph.

---

### 4. Scenario-retrieval inline prior

**What it is.** Before answering a plugin-domain-shaped question, the agent globs `plugins/<plugin>/scenarios/*.md`, filters by tags/product/scope, surfaces ≤3 matches with the mandatory unverified-scenario preamble.

**What it prevents.** Two failure modes — (a) the agent answers from memory when a relevant war-story field-note exists, (b) the agent treats a scenario as canonical without the unverified disclaimer.

**When to compose.** Any agent whose domain accumulates field-notes (currently: `power-platform/*`, future: `data-platform`, `finance`, etc.). Compose with: pattern 6 (citation-aware) when the scenario points to a canonical source.

**Example block:**

```markdown
## Scenario retrieval (priors)

Before answering a [domain]-shaped question, glob `plugins/[plugin]/scenarios/*.md`
and read the frontmatter of any file whose `tags` or `product` match the user's
context. Surface up to 2-3 matches with the mandatory unverified-scenario
preamble: *"Based on N unverified scenarios from YYYY-MM tagged [scope] — verify
in your environment before applying."*

Treat scenarios as **secondary** to canonical knowledge files; never replace
a `plugins/[plugin]/knowledge/` answer with a scenario, and never elide the preamble.

Full pattern: [`../../skills/scenario-retrieval/SKILL.md`](../../skills/scenario-retrieval/SKILL.md).
```

**Anti-pattern.** Citing a `scope: tenant-specific` scenario without the scope flag visible to the user. Surfacing >3 scenarios (noise). Treating scenario absence as evidence the situation is novel.

---

### 5. Mandatory-phrasing block (genuine blockage)

**What it is.** When an agent has exhausted alternatives and is genuinely blocked, the report uses fixed phrasing:

> "After trying [Approach A — outcome], [Approach B — outcome], and [Approach C — outcome], I am blocked on [specific reason]. The remaining options I considered but did not attempt are [X (ruled out because Y), Z (would need permission W)]. I recommend [escalation / next-best path]."

**What it prevents.** Round-trips. The user reads the blocked report and knows immediately what's left to consider — no "did you try X?" follow-up.

**When to compose.** Inherit on every agent that can produce a `blocked` status. Always pairs with pattern 2 (alternate-methods).

**Example block:** see the Capability Grounding Protocol section in [`../../CLAUDE.md`](../../CLAUDE.md) "Mandatory phrasing when reporting genuine blockage."

**Anti-pattern.** Free-form "I tried X and it didn't work" — leaves the user guessing what else was considered. Reporting blocked without listing alternatives that were ruled out.

---

### 6. Citation-aware research

**What it is.** Any research-bearing answer cites the source (URL, file path, doc section) AND labels the source's tier (Tier 1 Consensus / 2 Strong-but-Contextual / 3 Divergent / 4 Emerging / 5 Deprecated) per [`researcher.md`](../researcher/SKILL.md).

**What it prevents.** Plausible-sounding but unverifiable claims. Silent reliance on Tier 4 emerging guidance presented as Tier 1 consensus.

**When to compose.** `deep-researcher` always. Any agent producing release-note text, runbooks, or stakeholder-facing prose. Compose with: pattern 4 (scenario-retrieval) when scenarios corroborate or contradict canonical sources.

**Example block:**

```markdown
## Citation discipline

Every load-bearing claim in this agent's output must include:
- The source (URL or repo path)
- The tier label (1 Consensus / 2 Contextual / 3 Divergent / 4 Emerging / 5 Deprecated)
- The verification date (when the source was last checked)

A claim without a citation is treated as the agent's opinion, not as research.
```

**Anti-pattern.** Citing a single source as "the answer" when the question is in Tier 3 divergent territory. Citing without verification date — six-month-old citations decay.

---

### 7. Environment-context preamble

**What it is.** Before declaring "I can't do X" or asking the user to authorize an action, the agent reads `.ravenclaude/environment-context.md` (if present), identifies the current environment, and checks the pre-authorized action categories.

**What it prevents.** The "did you try X?" round-trip on actions the agent could have just done. Agent asks "can you authorize me to import this solution?" when the env-context file already says the agent is pre-authorized for solution import in DEV.

**When to compose.** Every agent that takes write actions against external systems. Compose with: pattern 2 (alternate-methods — env-context check runs *before* alternate enumeration).

**Example block:**

```markdown
## Environment-context check (priors)

Before declaring blocked, asking for authorization, or enumerating alternates:

1. Read `.ravenclaude/environment-context.md` at the consumer's project root (if present)
2. Identify the current environment (DEV / TEST / PROD / sandbox / named)
3. If the action category is pre-authorized for the current environment, execute
4. If the action is in the Forbidden list, stop and require per-action confirmation
5. If the file does not exist OR the action category is not listed, fall through
   to alternate-methods enumeration

See [`environment-discovery.md`](../environment-discovery/SKILL.md) for auto-discovery
when the file is absent.
```

**Anti-pattern.** Treating env-context as a credential store (it isn't). Assuming pre-authorization in DEV applies to PROD. Failing to ask when the file is silent (silence is NOT pre-authorization).

---

### 8. Orchestrator-worker reinforcement clause

**What it is.** A short, declarative clause near the top of every sub-agent file: *"This agent does NOT dispatch other agents. When work crosses your scope, complete your portion and return an Escalation note to the Team Lead naming the suggested specialist."*

**What it prevents.** Recursive sub-agent spawning, which the marketplace's hierarchical-dispatch architecture forbids. Without this clause, an architect can be tempted to "just spawn a coder" inline, breaking observability.

**When to compose.** Every sub-agent except the Team Lead itself. Verified by `plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh`.

**Example block:**

```markdown
## Dispatch boundary

This agent does NOT dispatch other agents. When work crosses your scope,
complete your slice and return a structured Escalation note to the Team Lead
naming the suggested next specialist and the reason. The Team Lead is the
only orchestrator. See [`spawn-team.md`](../spawn-team/SKILL.md).
```

**Anti-pattern.** Inline `Agent(...)` calls in a sub-agent file. "The architect spawned a coder" framing in agent bodies.

---

### 9. Agent-scenario-authoring frontmatter

**What it is.** The YAML frontmatter on agent files includes `audience`, `works_with`, `scenarios`, and `quickstart` fields per [`docs/best-practices/agent-scenario-authoring.md`](../../../../docs/best-practices/agent-scenario-authoring.md). The repo-guide generator picks them up automatically and surfaces them in per-agent cards plus the Overview tab use-case lookup table.

**What it prevents.** Invisible agents — agents that exist in `plugins/<plugin>/agents/` but don't appear in the repo-guide or use-case lookup. Users can't find what they don't know exists.

**When to compose.** Every agent file, always. At least 3 scenarios per agent; each scenario uses trigger phrasing a real user would type.

**Example block:**

```yaml
---
name: <agent-name>
description: <one sentence>
audience:
  - <e.g. "Power Platform makers", "Senior backend engineers">
works_with:
  - <other-agent-name>
  - <other-agent-name>
scenarios:
  - trigger: "<user phrasing they'd actually type>"
    outcome: "<what this agent delivers>"
  - trigger: "..."
    outcome: "..."
  - trigger: "..."
    outcome: "..."
quickstart: |
  <2-3 line example of the simplest invocation>
---
```

**Anti-pattern.** Generic scenarios ("when you need help with X" — no user types that). Fewer than 3 scenarios — the use-case lookup table thins out and users see "limited coverage."

---

### 10. Claim-grounding / source-honesty marker

**What it is.** For a **consequential** factual claim about a tool/platform/API (one that gates an irreversible action or gets written into a durable doc), the agent either cites the this-session check that backs it **inline and falsifiable** (the exact command + output, or `file:line`) or marks it `[unverified — training knowledge]` and offers to verify before acting. No High/Med/Low confidence label (uncalibrated). On correction, verify before yielding (don't reflexively concede or dig in). Full protocol: [core CLAUDE.md § "Claim Grounding & Source Honesty"](../../CLAUDE.md).

**What it prevents.** Confident reasoning errors — a flawed mental model stated as fact with no uncertainty marker (e.g. "you can't export solutions as unmanaged" when false), which drives a bad irreversible action. This is the over-claiming-certainty axis that the Capability Grounding Protocol (which covers under-claiming ability) does not.

**When to compose.** Any agent that makes platform/API/version/default/capability claims a user could act on — especially under GitHub Copilot CLI (Claude/GPT/Grok), where prose rules are weakest and the enforced complements matter most. Composes with: pattern 2 (alternate-methods — abstain only after trying ≥2 paths), pattern 4 (scenario-retrieval, which carries the same `[unverified]` family), pattern 6 (citation discipline for research output). The same `[unverified]` marker, source-as-suffix — do not coin a new tag.

**Example block:**

```markdown
`pac solution export` defaults to unmanaged `[unverified — training knowledge;
confirm with \`pac solution export --help\`]` — a default that gates the export
command, so it must be verified or marked before acting.
```

**Anti-pattern.** Stating a platform behavior as fact from training memory before an irreversible action. A High/Med/Low confidence label on a claim (stamps false claims "High"). Tagging *everything* — the marker must be rare (consequential-only) to stay informative.

---

## Composing patterns — required vs. optional checklist

When authoring a new agent, walk this checklist:

| Pattern | Required | Notes |
|---|---|---|
| 3. Structured Output Protocol block | **Required** | All handoff-bearing agents |
| 5. Mandatory-phrasing block | **Required** | Pairs with pattern 2; required when status can be `blocked` |
| 8. Orchestrator-worker clause | **Required** | All sub-agents (not Team Lead) |
| 9. Agent-scenario-authoring frontmatter | **Required** | All agents — repo-guide visibility |
| 2. Alternate-methods-before-blocked | Required if agent calls external tools | Most agents in practice |
| 7. Environment-context preamble | Required if agent takes write actions on external systems | All Power Platform specialists, security-reviewer, etc. |
| 1. Pre-action decision-tree traversal | Required if domain has decision trees | Most domain specialists |
| 4. Scenario-retrieval inline prior | Required if plugin has a scenarios bank | Currently power-platform; extend as banks land |
| 6. Citation-aware research | Required for research-producing agents | `deep-researcher` always; others when producing stakeholder prose |

A new agent missing ≥2 required patterns scores ≤3 on Dimension 3 (Capability Grounding) of the [`agent-quality-rubric`](../agent-quality-rubric/SKILL.md).

## Anti-patterns specific to this skill

- **Inventing a pattern** because "the agent feels like it needs one." If a behavior gap can't be closed by composing patterns 1-9, propose a new pattern via the `prompt-engineer` and get it added to this catalog — don't ship a one-off inline pattern in a single agent.
- **Copy-pasting the example block verbatim across 10 agents.** Inherit by reference (link to the canonical file). Copies drift.
- **Composing patterns in conflict.** E.g. asking the user for authorization (pre-environment-context) before checking env-context (pattern 7). Order matters — pattern 7 runs first.
- **Treating the checklist as bureaucracy.** Each pattern exists because a real failure mode was hit in production. A pattern omitted is a failure mode re-opened.

## See also

- [`agent-quality-rubric.md`](../agent-quality-rubric/SKILL.md) — Dimension 3 grades agents against this catalog.
- [`structured-output.md`](../structured-output/SKILL.md) — pattern 3's canonical reference.
- [`researcher.md`](../researcher/SKILL.md) — pattern 6's tier schema.
- [`scenario-retrieval.md`](../scenario-retrieval/SKILL.md) — pattern 4's full mechanics.
- [`environment-discovery.md`](../environment-discovery/SKILL.md) — pattern 7's auto-discovery skill.
- [`../../../docs/best-practices/agent-scenario-authoring.md`](../../../../docs/best-practices/agent-scenario-authoring.md) — pattern 9 canonical reference.
- [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../../docs/best-practices/decision-trees-in-knowledge-files.md) — pattern 1 canonical reference.
