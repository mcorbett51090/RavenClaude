---
description: Build an Agentforce agent action the right way — tightly-scoped topics with explicit instructions, grounded actions with guardrails, a check that the use case actually earns non-determinism, and a test/eval plan run before and after ship.
argument-hint: "[the agent capability, e.g. 'answer order-status questions']"
---

# Build an Agentforce action

You are running `/salesforce:build-agentforce-action`. Design an Agentforce topic + action for the capability the user described (`$ARGUMENTS`), following this plugin's `agentforce-architect` discipline. The hardest part isn't wiring the action — it's scoping and guardrailing it so a non-deterministic agent stays safe and useful.

## When to use this

A conversational/agentic capability is wanted on top of Salesforce data. **First, sanity-check it earns non-determinism** (`agentforce-earns-its-non-determinism`): if the task is a deterministic lookup or a fixed workflow, a Flow/screen is cheaper, faster, and more reliable — recommend that instead.

## Steps

1. **Scope the topic tightly with explicit instructions** (`agentforce-scope-topics-tightly-with-explicit-instructions`): one clear job per topic, instructions that say what to do *and what to refuse*. Broad topics hallucinate and misroute.
2. **Ground the action + add guardrails** (`agentforce-action-grounding-and-guardrails`): the action calls real, permission-respecting Salesforce data/automation (Apex/Flow/API), never invents values; inputs validated; the action runs as a user whose CRUD/FLS bounds it. Destructive or high-value actions require confirmation.
3. **Define the eval set before building** (`agentforce-test-and-evaluate-before-and-after-ship`): write the representative + adversarial test utterances and expected outcomes *first*; you'll run them before and after ship to catch regressions.
4. Produce: the topic definition + instructions, the grounded action (and the Apex/Flow it calls), the guardrails, and the eval set.

## Guardrails

- Don't ship an agent for a job a Flow does deterministically — non-determinism is a cost, not a feature.
- An action must respect the running user's CRUD/FLS — never elevate to do something the user couldn't.
- No ship without the before/after eval run; surface the eval results to the user as the go/no-go.
