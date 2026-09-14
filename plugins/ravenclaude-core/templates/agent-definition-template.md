# Agent Definition Template

> **Purpose**: This is the required template for all agents in ravenclaude-core and domain plugins. It ensures consistency, clear dispatch conditions, integration with the Capability Grounding Protocol, and structured tiered knowledge.

## Frontmatter (gated — the marketplace's `check-frontmatter.py` CI gate fails the build on any missing field)

```yaml
---
name: <kebab-case, matches the filename>
description: "<≤ 300 chars: what it is for + its keywords + the ONE most important 'NOT for X → other-agent' boundary>"
tools: <explicit least-privilege allowlist, e.g. Read, Grep, Glob, Write — or "*" only when every tool is genuinely intended>
model: <haiku | sonnet | opus — a TIER ALIAS, never a full model id>
audience: [dev, consultant]
works_with: [<agent>, <agent>]
scenarios:
  - intent: "<what the user is trying to do>"
    trigger_phrase: "<the sentence that should route here>"
    outcome: "<what comes back>"
    difficulty: starter | intermediate | advanced | troubleshooting
quickstart:
  - "Trigger phrase: '…'"
  - "Expected output: …"
  - "Common follow-up: …"
---
```

**Pick `model:` from the role, not from habit** — the tier table in
[`knowledge/model-tier-delegation.md`](../knowledge/model-tier-delegation.md) is the rule:
`haiku` for read-a-lot-return-a-little work (search, grep, classify, extract, inventory);
`sonnet` for bounded edits, known API calls, tests for a stated contract, first-draft
prose from supplied inputs; `opus` only for judgment — decomposition, adjudication, and
the gates that hold merge (`security-reviewer`, `code-reviewer`, `architect`), which are
never de-escalated to save money. An omitted `model:` silently inherits the main
session's model (an Opus worker for grep-shaped work); a full model id goes stale when
the SKU rotates. In the marketplace the roster-wide frontier share is ratcheted (CI's `check-model-tier-ratchet.py`,
Gate 287): a new `opus` agent that raises the share fails the PR unless the loosening is
stamped and said out loud — and the tier must fit the role (CI's `check-model-tier-fit.py`, Gate 288):
if the `name` ends `-implementation-engineer` / `-implementer` / `-coder` / `-developer`, or the
`description` *opens* with `Use to BUILD` / `IMPLEMENT` / `Use for X implementation`, `model: opus`
fails the PR. Name the role honestly and the tier follows.

## Role
[Short, precise description of what this agent is and what it owns.]

## When the Team Lead (or Grok Captain) Should Spawn This Agent
- Clear trigger conditions (e.g., "When the task involves Dataverse schema design...")
- Explicit conditions for when *not* to use it

## Core Responsibilities
- Bullet list of primary duties

## Integration with Capability Grounding Protocol
This agent **must** follow the Capability Grounding Protocol before claiming any limitation. See `plugins/ravenclaude-core/skills/grounding-protocol/SKILL.md` and core CLAUDE.md.

## Knowledge Base (Tiered Categorization)

The Researcher maintains this section. Agents default to Tier 1 and fall back gracefully.

### Tier 1: Consensus / Widely Accepted
[What most experts and official documentation agree on. This is the default recommendation.]

### Tier 2: Strong but Contextual
[Approaches that work well in most cases but have important limitations or prerequisites.]

### Tier 3: Divergent / Contrarian
[Credible expert views that differ from the mainstream consensus. Surface these when Tier 1 does not fit the user's constraints.]

### Tier 4: Emerging / Experimental
[New patterns with early promise. Clearly label risk and maturity.]

### Tier 5: Deprecated or Risky
[Old advice or patterns that should generally be avoided. Warn explicitly.]

## How This Agent Uses the Researcher
- On first open of the day or weekly deep research, the Researcher reviews and updates this knowledge base.
- The agent should request Researcher updates when it detects stale information or conflicting signals.

## Output Expectations
- Be decisive and opinionated within your domain.
- Always state grounding checks performed before any limitation claim.
- Prefer partial progress + clear next steps over clean refusal.
- Use structured handoffs when collaborating with other agents.

## Anti-Hallucination & Reliability Rules
- Never confidently claim "I can't do X" without first running the Grounding Protocol checklist.
- If uncertain, escalate to Team Lead with context rather than refusing.
