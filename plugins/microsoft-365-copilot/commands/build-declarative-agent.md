---
description: Build a Microsoft 365 declarative agent — pinned manifest schema, instructions kept in-manifest under the 8K budget, minimal scoped capabilities, designed to ~66% of every hard limit, and gated on RAI + a golden-prompt regression set.
argument-hint: "[the agent, e.g. 'an HR-policy assistant over the policy library']"
---

# Build a declarative agent

You are running `/microsoft-365-copilot:build-declarative-agent`. Author (or review) the declarative-agent manifest for what the user described (`$ARGUMENTS`), following this plugin's `declarative-agent-engineer` discipline — declarative-first, designed under the wall, validated behaviorally not just structurally.

## When to use this

A Copilot agent fits the declarative model (grounds + answers, no loop). If the task needs iterative reasoning, proactive behavior, an off-M365 channel, or a non-Copilot model, **stop** — it's a custom-engine agent; run `/microsoft-365-copilot:design-copilot-extensibility` first.

## Steps

1. **Pin the manifest `$schema` + `version`** to a known version (currently v1.7), never "latest" — the manifest ships ~monthly and an unpinned version is a time bomb (the hook flags it) (`design-to-66-percent-of-the-declarative-agent-wall.md`).
2. **Keep all behavioral directives inside `instructions`, under the 8,000-char cap** — never offload overflow to a SharePoint doc or knowledge source; XPIA classifiers can silently sanitize it and anyone with edit access can hijack behavior (`da-keep-instructions-in-the-manifest-not-knowledge.md`). When over budget, compress and push *factual reference* into grounding.
3. **Declare only the capabilities the scenario needs, each scoped** to the named connection/site/mailbox — `People`/`Email`/`Meetings` are elevated reach that must be justified (`da-scope-capabilities-to-only-what-the-agent-needs.md`).
4. **Design to ~66% of every hard limit** — 50 grounding / 25 plugin-response items / ~4,096 tokens / 45s, all inclusive of overhead; single grounding op + single tool call, sequential, no loops (`design-to-66-percent-of-the-declarative-agent-wall.md`).
5. **Write `name`/`description`/`instructions` to pass RAI validation** — neutral, scoped, refusal-aware; never "persuade"/"prove"/"ignore the rules" (RAI reads all three, runs on sideload, publish, and at runtime) (`da-pass-rai-validation-design-the-prompt-for-it.md`).
6. **Source-control the Agents-Toolkit project; sideload for dev** — don't hand-edit in Agent Builder and lose the diffable source; SharePoint-built DAs can't reach the org catalog (`da-source-control-the-project-sideload-for-dev.md`). Run the golden-prompt regression set before declaring done (#15). Use the `templates/declarative-agent-manifest.md` shape.

## Guardrails

- Schema-valid is not done; RAI-pass is not done — only a green golden-prompt regression set is.
- State a `Licensing impact:` line — SharePoint/OneDrive knowledge and connectors are seat-gated.
- This plugin is advisory: emit the manifest + `atk`/`m365` steps the engineer runs in their own tenant. Capability data-exposure / ACL design routes to `ravenclaude-core/security-reviewer`.
