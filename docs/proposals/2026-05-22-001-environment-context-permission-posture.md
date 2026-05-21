---
proposal_id: 2026-05-22-001
proposed_at: 2026-05-21
proposed_by: matt
status: proposed
topic: cross-plugin / agent-priors / environment-awareness
last_updated: 2026-05-21
related_to:
  - 2026-05-21-001-decision-trees-in-memory-files.md (this proposal was split out during the architect+researcher review; both proposals share the "priors-before-action" unifying frame)
---

# Environment-context / permission-posture preamble

*Proposed by Matt 2026-05-21. Split out from `2026-05-21-001-decision-trees-in-memory-files.md` per architect + deep-researcher reviews (both 2026-05-21) — same root cause family ("decisions under partial context") but different problem shape requiring a different solution shape.*

---

## Problem

The agent forgets — sometimes mid-session, sometimes across sessions — that it is **system administrator in DEV and TEST environments via a configured service principal**, and that it can perform sysadmin-level activities (solution import/export, Web API calls, `pac` CLI operations, programmatic flow creation, temp solution lifecycle, plug-in registration) without asking the user for authorization.

The observed symptom: the agent defaults to "I can't do X" or pings the user with "can you authorize me to do X?" when it could have just done X itself. This is the **"did you try X?" round-trip** that the Capability Grounding Protocol (added 2026-05-21) is supposed to prevent — but isn't preventing reliably for this specific failure mode.

## Why the existing Capability Grounding Protocol doesn't cover this

The Capability Grounding Protocol's "Try alternative paths before declaring blocked" rule fires **after** the agent has tried something and failed. It does not pre-load "you are sysadmin in DEV right now" into the agent's working assumptions.

The failure mode here is different: the agent never tried Approach A, because it incorrectly assumed it didn't have authorization to attempt it. CGP has no failure to enumerate alternates from.

This is **proactive priors** territory, not reactive enumeration. Different shape, different solution.

## The unifying frame (from architect + researcher review)

Both reviewers converged on the same framing: **"priors the agent is required to consult before action."**

- **Procedural priors** = decision trees (proposal `2026-05-21-001`) — *which method should I pick?*
- **Environmental priors** = this proposal — *what am I authorized to do here?*
- **When-blocked priors** = Capability Grounding Protocol (already shipped) — *what alternates do I try when something fails?*

Each has a different file shape + invocation moment. They compose; they should not be merged into one artifact.

## Proposed solution

A new convention: `plugins/<plugin>/environment-context.md` per plugin.

Consumer-authored. Read by the Team Lead at session start when that plugin is active. Schema:

```markdown
# Environment Context — <plugin-name>

## Active environments (consumer's setup, <YYYY-MM-DD>)
- **DEV** (<env-name>): agent has <role> via <auth-mechanism>. Pre-authorized
  for: <comma-separated list of categories of action>.
- **TEST** (<env-name>): <same / different posture>.
- **PROD** (<env-name>): <READ ONLY / specific allowed actions>.

## Default assumption
In DEV/TEST, agent does NOT ask "can I do X?" for actions listed above.
In PROD, no write without explicit per-action user OK.
```

Example for Matt's setup:

```markdown
# Environment Context — power-platform

## Active environments (Matt's setup, 2026-05)
- **DEV** (BTCSI-DEV): agent has sysadmin via SPN raven-claude-dev. Pre-authorized
  for: solution import/export, Web API calls, pac CLI, programmatic flow creation,
  temp solution lifecycle, plug-in registration.
- **TEST** (BTCSI-TEST): same SPN, same posture.
- **PROD** (BTCSI-PROD): READ ONLY. Any write action requires user confirmation.

## Default assumption
In DEV/TEST, agent does NOT ask "can I do X?" for any action listed above.
In PROD, agent does NOT execute any write without explicit per-action user OK.
```

## Integration with existing Capability Grounding Protocol

One line added to `ravenclaude-core/CLAUDE.md` §"Try alternative paths":

> Before declaring blocked or asking authorization, check the active plugin's `environment-context.md` — if the action is listed as pre-authorized in the current environment, execute.

This is the bridge: the pre-action environment check happens FIRST, the reactive alternate-methods enumeration happens AFTER if the action still fails.

## House-rule alignment (added 2026-05-21)

This proposal does NOT add a new agent. The Team Lead (already in `ravenclaude-core`) handles session-start orchestration per the existing focused-task pattern. The new convention is one file per plugin + one line in the Capability Grounding Protocol. No new agent, no new skill, no new infrastructure.

## Why this needs to be a separate proposal (not bundled with decision trees)

Both reviewers explicitly flagged the bundling risk:

- **Architect:** *"Trying to unify them — e.g., putting 'I am sysadmin in DEV' inside the Power Automate decision tree — couples a session-level fact to a domain-level procedure. That coupling is what makes other systems (Helm value files that try to do both env-config and chart-logic) infamously brittle."*
- **Researcher:** *"Build them as two artifacts that reference each other, not one artifact that does both."*

The decision-tree proposal (`2026-05-21-001`) ships in v0.1.0 as a single-plugin pilot (power-platform `programmatic-flow-creation.md`). This proposal should ship after that observation is in — meaning: after the decision-tree mechanism has been observed in one real engagement, the same engagement can validate whether the environment-context file is needed as proposed, or whether a different shape (e.g., a frontmatter block in each plugin's CLAUDE.md) is better.

## Recommendation

- **Status:** proposed (awaiting first real engagement to validate the shape)
- **Decision needed:** does Matt want to spec this now and ship in parallel with the decision-tree v0.1.0, OR wait until the decision-tree mechanism is observed in an engagement before committing to the environment-context shape?
- **My read:** wait. Ship decision-trees alone; observe the next PA engagement; revisit this proposal with real signal in hand. The convention proposed above is plausible but not yet evidence-backed.

## Open questions

1. **Per-plugin or per-engagement?** The proposed file lives at `plugins/<plugin>/environment-context.md` (per-plugin). But the actual environment posture is per-engagement (Customer A might have different DEV/TEST/PROD setups than Customer B). Per-engagement files would live in the consumer's project root, not in the marketplace plugin. Decide which.
2. **Sensitivity boundary.** Environment-context files may contain identifying info (SPN names, env URLs). If shipped in `plugins/<plugin>/`, they're publicly visible. Per-engagement files in the consumer's project root keep them private. This is a strong argument for the per-engagement shape.
3. **What about credential-context?** This proposal explicitly scopes to *role identity*, not credentials. Credentials live in env vars or Key Vault per existing repo practice. Should the environment-context file cross-reference WHERE credentials live (without storing them)?

## References

- [`2026-05-21-001-decision-trees-in-memory-files.md`](2026-05-21-001-decision-trees-in-memory-files.md) — the partner proposal this was split out from
- [`../../plugins/ravenclaude-core/CLAUDE.md`](../../plugins/ravenclaude-core/CLAUDE.md) — Capability Grounding Protocol (where the bridge clause lands)
- [`../best-practices/decision-trees-in-knowledge-files.md`](../best-practices/decision-trees-in-knowledge-files.md) — the v0.1.0 best-practice for the procedural-priors sibling
- Researcher's sources on persona / role-card patterns:
  - Google Cloud Security "agent runbooks" — YAML role manifests
  - JasperHG90/persona toolkit — persona-as-software-artifact
  - Microsoft Learn workload team personas for AI workloads
