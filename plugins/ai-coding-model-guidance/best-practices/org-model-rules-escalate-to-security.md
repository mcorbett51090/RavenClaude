# Escalate org model-rule and API-key questions to security-reviewer

**Status:** Absolute rule
**Domain:** Compliance / escalation
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

GitHub Copilot org model rules, API-key handling, and compliance posture
decisions (which models are permitted in an enterprise, which are blocked,
how keys are rotated) are security and governance verdicts. This plugin's agents
are model-selection strategists — they can describe what org model rules are and
how to configure them, but they are not qualified to issue a compliance verdict.
An agent that says "it's fine to allow all models for your org" without a
security review has issued a compliance opinion it shouldn't have.

## How to apply

When a developer's question touches org model rules, API-key governance,
or compliance posture:

1. Answer the **technical mechanics** (how to set an org model policy, what the
   rule options are, how to restrict a model).
2. Explicitly hand the **compliance verdict** to `ravenclaude-core/security-reviewer`.

```
Technical mechanics (this plugin):
  GitHub Copilot Business/Enterprise admins can set an org model policy via
  Settings → Copilot → Policies → Model options [verify-at-use].
  Available controls include: allow-list, deny-list, default model.

Compliance verdict (not this plugin):
  Whether the policy you choose satisfies your org's compliance requirements
  (data residency, model provider contracts, regulatory posture) is a
  security/compliance review question — escalate to ravenclaude-core/security-reviewer.
```

**Do:**
- Answer the mechanics; don't avoid the topic entirely.
- Draw the line clearly between "how to configure it" and "whether this
  configuration is compliant."
- Name the escalation path explicitly: `ravenclaude-core/security-reviewer`.

**Don't:**
- Issue compliance verdicts ("this configuration is compliant for GDPR").
- Advise on API-key rotation schedules without noting the security-reviewer
  escalation.
- Let a developer conflate a model availability explanation with a compliance
  clearance.

## Edge cases / when the rule does NOT apply

- The developer is asking about mechanics only (how to navigate the UI, what
  the available options are) with no compliance dimension: answer fully without
  the escalation qualifier.

## See also

- [`../agents/copilot-model-strategist.md`](../agents/copilot-model-strategist.md) — owns Copilot org model rules mechanics
- [`./scope-availability-surface-plan-date.md`](./scope-availability-surface-plan-date.md) — plan-gated availability is a mechanics question; compliance is not

## Provenance

Codifies the seam in `CLAUDE.md` §2 routing rules ("org model rules / API-key /
compliance verdict → ravenclaude-core/security-reviewer") and the plugin's house
rule against forking core review roles.

---

_Last reviewed: 2026-06-05 by `claude`_
