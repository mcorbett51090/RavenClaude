# Researcher Skill (Meta-Skill)

## Purpose
The Researcher is a meta-skill responsible for keeping all agents, skills, and knowledge files in the RavenClaude marketplace current and honest.

It runs in two modes:
- **Daily Quick Check** — Recommended the first time the repo is opened each day (or manually invoked by Team Lead / Grok Captain).
- **Weekly Deep Research** — Comprehensive review of every agent + its associated skills and knowledge (recommended weekly, e.g. Sunday/Monday).

## How to Trigger

**Daily Quick Check**:
- Team Lead (or Grok when acting as orchestrator) should run a lightweight version on first meaningful work session of the day.
- Focus: Quick scan for any obviously outdated advice in active agents/knowledge areas.

**Weekly Deep Research**:
- Full sweep across all agents and knowledge files.
- Best done as a dedicated session.
- Can be triggered manually or via scheduled reminder.

## Core Principles
1. **Grounding First**: Before updating anything, apply the Capability Grounding Protocol.
2. **Consensus + Divergence**: Capture both the widely accepted expert view **and** credible dissenting views.
3. **Actionable Updates**: Research must result in specific, justified proposals to update agents, skills, or knowledge files.
4. **Transparency**: Every research output must clearly label information as Consensus, Divergent, Emerging, or Contextual.

## Research Scope
For each agent:
1. Review its current definition and responsibilities.
2. Identify all skills and knowledge files it relies on.
3. Research recent changes, best practices, gotchas, and expert opinions (official + community + divergent).
4. Categorize new information using the schema.
5. Propose concrete updates with justification.

## Categorization Schema (Mandatory)
All researched information must be categorized:

### Tier 1: Consensus / Widely Accepted (Default)
Backed by official Microsoft documentation + strong agreement among recognized experts and MVPs.

### Tier 2: Strong but Contextual
Generally recommended but has known limitations or scenario-specific caveats.

### Tier 3: Divergent / Contrarian Views (Critical Fallback)
Credible experts who successfully do things differently. Include their reasoning and when their approach may be better.

### Tier 4: Emerging / Experimental
New patterns or preview features with early positive signals.

### Tier 5: Deprecated or Risky
Previously common approaches now discouraged.

## Output
Produce a structured Research Report using `templates/research-report-template.md`.

The Researcher must apply the Grounding Protocol to its own conclusions before presenting updates.

## Sources
**Official**: Microsoft Learn, release notes, Microsoft 365 Roadmap, official samples.
**Community**: High-signal MVPs, forums, quality blogs/YouTube.
**Divergent**: Practitioners who publicly challenge common advice with demonstrated results.

Actively seek credible dissenting views rather than only confirming existing knowledge.

## Decision-tree staleness check (added 2026-05-21)

The Weekly Deep Research sweep MUST include a staleness check for decision trees per the convention in [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md).

**The check:**

1. Glob `plugins/*/knowledge/*.md` and `plugins/*/skills/*.md` for files containing `## Decision Tree:` section headers
2. Parse the `**Last verified:** YYYY-MM-DD` field within each
3. Flag any tree where `today - last_verified > 90 days`
4. For each flagged tree, run the categorization schema (Consensus / Contextual / Divergent / Emerging / Deprecated) against each leaf — has any leaf become inaccurate since the last verification?
5. Surface flagged trees in the Research Report with one of: `still-current` (refresh date only), `needs-update` (specific leaves to revise), `deprecate` (remove tree entirely).

**Why this check matters:** decision trees go stale faster than prose when underlying platforms change. A prose paragraph degrades gracefully ("the API used to return X, now Y" still reads fine). A decision tree with a `404 → reimport` leaf is wrong the moment the platform returns `409` instead. The `Last verified:` field + this check is the anti-staleness backstop the format requires.