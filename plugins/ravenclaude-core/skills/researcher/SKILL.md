# Researcher Skill (Meta-Skill)

## Purpose
The Researcher is a meta-skill responsible for keeping all agents, skills, and knowledge files in the RavenClaude marketplace current and honest.

It runs in two modes:
- **Daily Quick Check** — Triggered the first time the repo is opened each day (or manually invoked).
- **Weekly Deep Research** — Comprehensive review of every agent + its associated skills and knowledge (scheduled or manually triggered).

## Core Principles
1. **Grounding First**: Before updating anything, apply the Capability Grounding Protocol.
2. **Consensus + Divergence**: Capture both the widely accepted expert view **and** credible dissenting views.
3. **Actionable Updates**: Research must result in specific, justified proposals to update agents, skills, or knowledge files.
4. **Transparency**: Every research output must clearly label information as Consensus, Divergent, Emerging, or Contextual.

## When to Invoke
- Automatically recommended on first repo open of the day (documented in CLAUDE.md).
- Every Sunday/Monday for Weekly Deep Research.
- Manually by Team Lead when working in a fast-moving domain (especially Power Platform).
- After major Microsoft releases or community shifts.

## Research Scope
For each agent:
1. Review its current definition and responsibilities.
2. Identify all skills and knowledge files it relies on.
3. Research recent changes, best practices, gotchas, and expert opinions.
4. Categorize new information.
5. Propose concrete updates.

## Categorization Schema (Mandatory)
All researched information must be categorized using this schema:

### Tier 1: Consensus / Widely Accepted
- Backed by official Microsoft documentation + strong agreement among recognized experts and MVPs.
- Default position for agents unless context clearly indicates otherwise.

### Tier 2: Strong but Contextual
- Widely recommended but has known limitations, prerequisites, or scenario-specific caveats.

### Tier 3: Divergent / Contrarian Views
- Credible experts or practitioners who successfully operate differently from the consensus.
- Must include their reasoning and the conditions under which their approach may be superior.
- Agents should surface these options when Tier 1 approaches are failing or when the user has specific constraints.

### Tier 4: Emerging / Experimental
- New patterns, preview features, or community experiments with early positive signals.
- Clearly marked as higher risk.

### Tier 5: Deprecated or Risky
- Previously accepted approaches that are now discouraged or carry significant downsides.

## Output Format
The Researcher must produce a structured Research Report using the template in `templates/research-report-template.md`.

Key sections:
- Summary of changes since last research
- Per-agent findings with categorized updates
- Specific file change proposals (with before/after where relevant)
- Sources (official + community)
- Divergent views highlighted
- Recommended actions for Team Lead

## Integration with Grounding Protocol
Before claiming any knowledge is outdated or recommending changes, the Researcher must run the Grounding Protocol checklist on its own findings.

## Sources to Check (Non-Exhaustive)
**Official / Primary:**
- Microsoft Learn / Power Platform documentation
- Microsoft 365 Roadmap
- Release notes and "What's New" blogs
- Official Microsoft GitHub repos and samples

**High-Signal Community:**
- Recognized MVPs and community leaders (specific names can be maintained in knowledge files)
- Power Platform community forums
- High-quality YouTube channels and blogs

**Divergent / Independent Voices:**
- Practitioners who publicly disagree with common advice and demonstrate results at scale
- Reddit threads (r/PowerPlatform, r/PowerApps) with strong technical discussion
- X/Twitter threads from credible accounts

The Researcher must actively seek out credible dissenting views, not just reinforce existing knowledge.