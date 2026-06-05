> **Use for:** documenting an organization's AI coding tool model-access policy before a rollout or compliance review. One worksheet per org. Fill in each `[placeholder]` with the org's current configuration. Hand to the security-reviewer for any compliance verdicts.

---

# Org Model Policy Worksheet

**Org name:** [GitHub org / OpenAI org name]
**Date audited:** [YYYY-MM-DD]
**Audited by:** [agent or human]
**Review cadence:** [quarterly / on-change / other]

---

## GitHub Copilot (Business / Enterprise)

**Plan:** [Business / Enterprise / Not applicable]

### Model access configuration

| Setting | Current value | Last changed | Changed by |
|---|---|---|---|
| Model availability mode | [Allow all / Allow selected / Block specific] | [YYYY-MM-DD] | [name or role] |
| Allowed models (if allow-list) | [list or "n/a"] | | |
| Blocked models (if deny-list) | [list or "n/a"] | | |
| Policy applies to surfaces | [All / Completions only / Chat only / Other] | | |

### Access control

- Admin role held by: [name / role]
- Audit log enabled: [yes / no]
- Model rules reviewed against current lineup: [yes / no / [YYYY-MM-DD]]

---

## OpenAI Codex / API

**Org plan:** [Free / Pay-as-you-go / Enterprise]

| Attribute | Value | Notes |
|---|---|---|
| Project-scoped API keys in use | [yes / no] | |
| Models accessible via active keys | [list or "all"] | |
| Spending limit in place | [yes / no / amount] | |
| Usage policy restrictions | [none / [specific restriction]] | [verify-at-use] |
| API key rotation cadence | [period] | |

---

## xAI Grok API

| Attribute | Value | Notes |
|---|---|---|
| API key rotation cadence | [period] | |
| Keys scoped to specific use cases | [yes / no] | |
| Retirement alert process in place | [yes / no] | |

---

## Findings and actions

| Finding | Platform | Risk | Action | Owner | Due date |
|---|---|---|---|---|---|
| [description] | [platform] | [High / Medium / Low] | [specific action] | [name / role] | [YYYY-MM-DD] |

---

## Escalation to security-reviewer

- Escalation required: [yes / no]
- Reason: [compliance concern / API key scope / other]
- Escalated to: [ravenclaude-core/security-reviewer or named person]
- Date escalated: [YYYY-MM-DD]
