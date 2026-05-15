# Knowledge Categorization Schema

This schema is used by the Researcher and all agents when handling domain knowledge.

## Goal
Prevent dogmatic responses. Give agents clear tiers so they default to widely accepted practices while still having access to alternative approaches when needed.

## Tiers (Use in This Order)

### Tier 1: Consensus / Widely Accepted (Default)
**Definition**: Information supported by official documentation and broad expert agreement.

**How agents should use it**:
- Present this as the primary recommendation.
- Assume this is correct unless the user provides specific constraints that contradict it.

**Examples**:
- Using solution layers properly in Power Platform ALM
- Dataverse security model best practices (business units, roles, teams)

### Tier 2: Strong but Contextual
**Definition**: Generally recommended but depends on specific conditions.

**How agents should use it**:
- Mention the main approach + key caveats.
- Ask clarifying questions if context is unclear.

### Tier 3: Divergent / Contrarian Views (Important Fallback)
**Definition**: Credible experts or successful practitioners who recommend different approaches.

**How agents should use it**:
- Do **not** lead with these views.
- Surface them when:
  - Tier 1 approaches are not working or causing problems
  - User has unusual constraints (compliance, legacy systems, extreme scale)
  - User explicitly asks for alternatives
- Always attribute the view and explain the reasoning

**Why this tier exists**:
This prevents hallucinated limitations and gives the system intellectual honesty. Many "best practices" have legitimate exceptions that experts quietly use.

### Tier 4: Emerging / Experimental
**Definition**: New or preview features with promising early signals but limited production validation.

**How agents should use it**:
- Clearly label as experimental.
- Discuss risk vs reward.
- Only recommend for greenfield or low-risk scenarios unless user accepts the risk.

### Tier 5: Deprecated or Risky
**Definition**: Approaches that were once common but are now discouraged.

**How agents should use it**:
- Actively warn against these.
- Explain why they became deprecated.
- Suggest migration paths.

## How to Apply When Researching
When the Researcher updates knowledge:
1. Default all statements to Tier 1 where evidence supports it.
2. Explicitly call out Tier 3 (Divergent) views with attribution.
3. Never bury important dissenting information.
4. Update the relevant knowledge file or agent definition with clear tier labels.