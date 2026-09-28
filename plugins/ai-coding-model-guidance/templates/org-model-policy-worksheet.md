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

## Claude Code (managed settings — `availableModelsMatch` / `deniedModels`)

> Claude Code 2.1.283 added a managed **model allowlist** with an exact-match mode. Document it here so a release of a new model does not silently become unavailable (or stay available when it should not). [angle `release-claude-code-2.1.283`]

| Setting | Current value | Notes |
|---|---|---|
| `availableModels` (managed) | [list or "not set"] | The models this org may select. |
| `availableModelsMatch` | [`exact` / not set] | **With `"exact"`, ONLY the named versions are allowed — a NEW model release stays BLOCKED until its id is added to `availableModels`.** This is the "blocked until listed" footgun: every release-compare model adapt (a new Opus/Sonnet/etc.) must also add the id here. |
| `deniedModels` | [list or "not set"] | Blocks specific models **even when `availableModels` allows them** — the cost/risk deny lever. |
| New-model add-to-allowlist process owner | [name / role] | Who updates `availableModels` when a new model ships (only needed under `exact`). |

- Escalate any allowlist/deny-list *policy* change to `ravenclaude-core/security-reviewer` (cost/risk posture).

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
