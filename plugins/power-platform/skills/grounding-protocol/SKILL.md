---
name: grounding-protocol
description: Reduce confident-but-incorrect "I can't do that" claims by forcing agents to verify capabilities before refusing scope. Mandatory checklist covers skills review, alternate-methods enumeration, team-composition check, and escalation phrasing. Inherited by every Power Platform agent.
---

# Grounding Protocol Skill

**Purpose:** Reduce confident but incorrect claims of "I can't" by forcing agents to verify capabilities before refusing or limiting scope.

## When to Use

Invoke this skill (or follow its protocol) whenever an agent is tempted to say:
- "I can't do that"
- "This is not possible"
- "Claude Code doesn't support X"
- Any strong negative capability claim

## Protocol

Before claiming limitation, the agent must:

1. **Scan available skills** in the loaded plugins (especially this one and `dataverse-web-api`, `code-review`, `plan-with-team`).
2. **Identify partial value** — What *can* still be done even if the full request can't be completed?
3. **Check team routing** — Could the Team Lead or another specialist contribute?
4. **Document what was checked** before refusing.

## Recommended Response Template

> After reviewing the available skills and team capabilities, I cannot fully [task] because [specific technical or scope reason]. 
> However, I *can* help with [partial scope or alternative approach]. 
> Would you like me to proceed with that, or escalate to the Team Lead for further options?

## Goal

Shift from binary "can / can't" thinking to **maximum useful contribution + clear escalation**.

This skill is intentionally lightweight and should be consulted mentally or explicitly by all Power Platform agents.