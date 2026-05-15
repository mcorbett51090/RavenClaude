## Plugin Architecture: Core vs Domain Plugins (Updated)

- `ravenclaude-core` is the **foundational plugin**. It provides the Team Lead, generalist agents (Architect, Coder, Reviewer, etc.), skills, hooks, Capability Grounding Protocol, and the Researcher meta-skill.
- Domain plugins (e.g. `power-platform`) **extend** core. They add specialist agents and domain-specific knowledge.
- The Team Lead is responsible for detecting domain-specific work and dispatching specialists from installed domain plugins.

## Multi-Agent Coordination & Dispatch Rules (Core Principle)

This marketplace follows the **orchestrator-worker / hierarchical** pattern, which is the dominant recommended approach in production multi-agent systems (including Anthropic’s own research architecture).

**Core Rule:**

**Sub-agents should not freely spawn or directly invoke other sub-agents.** Only the Team Lead performs dispatching and orchestration.

**How cross-boundary work is handled:**

1. Each specialist stays focused on their domain and delivers a high-quality slice.
2. When work has clear relevance to another specialist, the agent should complete their portion and include a clear **escalation / recommended handoff** note to the Team Lead (naming the suggested specialist and providing relevant context).
3. The **Team Lead** decides whether and how to involve additional agents (in parallel or sequence) and synthesizes the combined output.
4. Limited structured handoff is acceptable when explicitly recommended, but actual dispatch and context management remains the responsibility of the Team Lead.

**Rationale**: This approach provides better observability, easier debugging, reduced risk of loops, and more reliable behavior — especially important when combining generalist agents from core with domain specialists.

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