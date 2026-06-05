---
name: org-policy-model-rules-audit
description: "Audit an organization's AI coding tool model-access policies across GitHub Copilot Business/Enterprise, OpenAI org-level controls, and xAI API governance. Reach for this skill when an enterprise team reports unexpected model access, when a compliance review requires documenting which models the org has allowed or blocked, or before rolling out a new model to a large org."
---

# Skill: Org Policy Model Rules Audit

Enterprise and business teams govern which models their developers can use. A model available in the public picker may be blocked by org policy; a policy intended to restrict a model may be misconfigured. This skill structures the audit so gaps are found before they produce compliance findings or unexpected bills.

**Security-reviewer escalation rule:** any finding that involves API key scope, token storage, or a compliance verdict (SOC 2 / FedRAMP / GDPR applicability) escalates immediately to `ravenclaude-core/security-reviewer`. This skill audits policy configuration; it does not produce compliance opinions.

## Step 1 — Identify the platforms in scope

The three ecosystems in this plugin have different governance surfaces:

| Platform | Governance surface | Scope |
|---|---|---|
| GitHub Copilot Business | GitHub org settings → Copilot → Model rules | Allow/deny specific models for all org members |
| GitHub Copilot Enterprise | Same as Business + GHEC-level policy | Broader controls; enterprise-managed users |
| OpenAI Codex / API | OpenAI org settings → Usage policies | Org-level model access; project-scoped API keys |
| xAI Grok API | API key ownership | No org-level picker controls as of this writing [verify-at-use] |

## Step 2 — Audit GitHub Copilot model rules (Business / Enterprise)

For each org on Business or Enterprise:

```
[ ] Navigate to: org → Settings → Copilot → Policies → Model availability
[ ] Document the current model access state:
    - "Allow all models" (default)
    - "Allow selected models only" (explicit allow-list)
    - "Block specific models" (explicit deny-list)
[ ] Cross-reference the allow/deny list against the verified lineup
    — are any models in the deny-list already unavailable (redundant)?
    — are any models the team needs blocked unintentionally?
[ ] Confirm whether model rules apply to all surfaces (completions, chat, coding agent)
    or only to specific surfaces [verify-at-use — Copilot org docs]
[ ] Document who has admin rights to change the policy
```

## Step 3 — Audit OpenAI org-level controls

```
[ ] Log into platform.openai.com → org settings → Usage
[ ] Document any project-scoped API keys (limited to specific models or rate limits)
[ ] Identify any spending limits that would cap access to frontier models
[ ] Confirm whether the org's usage policy restricts specific model families [verify-at-use]
[ ] Document API key rotation cadence — stale keys are a governance gap
```

## Step 4 — Produce the audit summary

```
Audit date: YYYY-MM-DD
Platforms audited: [list]
Findings:

| Platform | Policy state | Gap found? | Risk level | Recommendation |
|---|---|---|---|---|
| Copilot (org: X) | Allow all | No | Low | Maintain; review quarterly |
| Copilot (org: Y) | Block list | Yes — [model] unintentionally blocked | Medium | Update deny-list |
| OpenAI org | Project key scoped | Yes — frontier model unreachable | High | Add frontier model to project key scope |
| Grok API | API key only | No org controls [verify-at-use] | Low | Document key rotation schedule |

Escalation to security-reviewer: [yes/no — reason if yes]
```

## Step 5 — Flag escalation-worthy findings

Escalate to `ravenclaude-core/security-reviewer` when any of these are found:
- API keys with broader-than-needed scope
- Org policy blocks that appear designed for compliance but are misconfigured
- A model in the allow-list that has known security or data-handling concerns [verify-at-use]
- Any finding touching GDPR, SOC 2, FedRAMP, or a similar framework

## Pitfalls

- Auditing only the Copilot model picker without checking org policy — org policy overrides individual developer choices.
- Treating Grok API access as ungoverneable because it lacks a picker — API key scope and rotation are the governance levers.
- Marking a finding as resolved without documenting the person who changed the policy and when.
- Recommending a compliance verdict without escalating to security-reviewer.

## See also

- [`../../agents/copilot-model-strategist.md`](../../agents/copilot-model-strategist.md) — Copilot org model rules in depth
- [`../../CLAUDE.md`](../../CLAUDE.md) — §2 routing rule: org model rules escalate to security-reviewer
- [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) — the verified lineup to cross-reference against policy allow/deny lists
