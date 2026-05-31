---
description: Build a Copilot Studio agent the right way — route topic vs generative deliberately, select and scope grounding sources, and add escalation + guardrails so the agent hands off cleanly and never answers outside its grounding.
argument-hint: "[the agent's job, e.g. 'answer HR policy questions']"
---

# Build a Copilot Studio agent

You are running `/power-platform:build-copilot-studio-agent`. Design a Copilot Studio agent for the capability the user described (`$ARGUMENTS`), following this plugin's `copilot-studio-engineer` discipline. The craft is in routing, grounding, and guardrails — not in wiring topics.

## When to use this

A conversational agent over Microsoft/Dataverse data is wanted. If the task is a fixed, deterministic workflow, a cloud flow or app is cheaper and more reliable — recommend that instead.

## Steps

1. **Topic vs generative routing** (`copilot-studio` `copilot-topic-vs-generative-routing`): high-stakes / must-be-exact paths → authored **topics** (deterministic); open-ended Q&A → **generative** answers over grounding. Decide per intent, not globally.
2. **Grounding source selection** (`copilot-grounding-source-selection`): choose the narrowest authoritative sources (specific SharePoint/Dataverse/website scopes), not "everything" — broad grounding hallucinates and leaks.
3. **Escalation + guardrails** (`copilot-escalation-and-guardrails`): define the hand-off to a human/queue, the refuse-and-escalate path for out-of-scope or low-confidence, and the content guardrails. The agent never answers outside its grounding.
4. Produce: the topic/generative routing map, the grounding scope, the escalation design, and a small eval set of representative + adversarial utterances.

## Guardrails

- Don't ground on "all of SharePoint" — scope tightly or it will surface the wrong/confidential thing.
- A deterministic, high-stakes path belongs in an authored topic, not generative.
- Define escalation before launch — an agent with no human off-ramp is a support liability.
