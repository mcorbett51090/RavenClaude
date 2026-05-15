## Plugin Architecture: Core vs Domain Plugins (Updated)

- `ravenclaude-core` is the **foundational plugin**. It provides the Team Lead, generalist agents, skills, hooks, Capability Grounding Protocol, and now the **Researcher** meta-skill.
- Domain plugins (e.g. `power-platform`) **extend** core. They add specialist agents and domain-specific knowledge.
- The Team Lead is responsible for detecting domain-specific work and dispatching specialists from installed domain plugins.

## Knowledge Freshness & Researcher (New)

The marketplace includes a **Researcher** meta-skill located in `plugins/ravenclaude-core/skills/researcher/`.

**When to invoke the Researcher**:
- On first opening the repo each day (quick check mode)
- Weekly for deep research across all agents and knowledge areas
- After major platform updates or when you notice agents giving outdated advice

The Researcher is responsible for:
- Checking every agent + its skills and knowledge files
- Researching both official sources and credible community/expert opinions (including divergent views)
- Categorizing information using the defined schema (Consensus / Divergent / Emerging / etc.)
- Proposing specific, justified updates to keep knowledge current

This system exists to reduce hallucination and keep the entire agent team intellectually honest and up-to-date, especially in fast-moving domains like Power Platform.

When working with Grok or other models, copy the relevant portable files so they also benefit from the Researcher discipline.

## Capability Grounding Protocol (Updated with Researcher reference)

Before any agent claims it cannot do something or that information is outdated, it must:
1. Check available skills (including the new Researcher skill when appropriate).
2. Consider whether partial progress is possible.
3. Run the Grounding Protocol checklist.
4. Only then state limitations clearly.

The Researcher itself must apply this protocol to its own findings.