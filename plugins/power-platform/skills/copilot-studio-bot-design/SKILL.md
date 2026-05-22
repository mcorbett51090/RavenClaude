---
name: copilot-studio-bot-design
description: Design Copilot Studio bots — topic vs generative-answers boundaries, knowledge-source hygiene, trigger-phrase design, slot-filling patterns, escalation-to-human criteria, AI Builder vs prompt-flow vs direct Azure OpenAI decisions, and the test-set discipline that catches regressions on every authoring change. Used by `copilot-studio-engineer` (primary).
---

# Copilot Studio Bot Design Skill

**Purpose:** Senior-maker playbook for `copilot-studio-engineer` covering the architecture decisions that determine whether a Copilot Studio bot is a useful coworker or a hallucinating embarrassment in front of customers. The decisions are made on day one — topic vs generative-answers boundaries, knowledge sources, escalation criteria — and the test discipline that keeps them honest as the bot evolves.

## When to Use

- **Starting a new bot** — before the first topic is built, work through the architecture decisions here.
- **A deployed bot is misbehaving** — hallucinating answers, dropping conversations, escalating too often or not often enough, ignoring intent. This skill covers the diagnostic playbook.
- **Adding a new knowledge source or topic to an existing bot** — verify it doesn't blow up the existing test set.
- **Deciding AI implementation path** — Copilot Studio vs AI Builder vs prompt-flow vs direct Azure OpenAI. The trade-off matters for cost, governance, and freshness.

## Core Principles

1. **A bot is a contract about what the org will answer**, not a wrapper around an LLM. Treat it like a product surface — versioned, tested, owned.
2. **Topics for high-stakes, regulated, or specific-format answers. Generative-answers for everything else.** The line is "would I want a human to read this exact response before it shipped?" If yes, it's a topic.
3. **Knowledge-source hygiene is the #1 hallucination prevention.** Garbage in, confidently-wrong out. Stale, duplicated, or contradictory sources poison the bot worse than no source.
4. **Every authoring change re-runs the regression set.** A 20-prompt test set is the difference between "we improved the bot" and "we hope we improved the bot."
5. **Escalation to human is a feature, not a failure.** Bots that never escalate are usually hallucinating instead of saying "I don't know."
6. **Premium connector cost is real** — Copilot Studio messages are licensed; AI Builder credits are counted; direct Azure OpenAI is metered. Every architecture choice has a unit-economics consequence.

## Playbook

### 1. Copilot Studio architecture in plain English

A Copilot Studio bot has four kinds of building blocks:

- **Topics** — authored conversations with explicit trigger phrases, slot-filling, branching, and exit conditions. Deterministic. You wrote it; the bot says exactly what you wrote.
- **Generative answers** — retrieval-augmented generation (RAG) over the bot's knowledge sources. The bot reads from sources at query time, an LLM composes the answer. Non-deterministic but grounded.
- **Knowledge sources** — websites, SharePoint, documents, Dataverse, custom data — pointed at the bot, indexed, queryable by generative answers.
- **Plugins / actions** — calls into Power Automate flows, custom connectors, AI Builder prompts, or external APIs. Executes work; not just speech.

The bot router decides per-utterance: matches an authored topic? Run it. Otherwise hand to generative answers, or escalate.

### 2. Topic vs generative-answers — the boundary

| Use a **topic** when… | Use **generative answers** when… |
|---|---|
| Regulated content (legal, HR policy, financial disclosure) | Informational FAQ over public-ish content |
| High-blast-radius actions (file a claim, place an order, transfer money) | Synthesizing across many docs to answer a question |
| The answer has a specific format (table, JSON, exact wording) | The answer space is broad and slow-changing |
| Slot-filling required (you need 5 fields to do anything) | The user's question is usually one-shot |
| Compliance demands logged determinism | Variation in phrasing is acceptable |

**Test for the line**: "if a user gets a wrong answer here, who explains it to compliance / legal / the customer?" If the answer is a real person, it should be a topic.

### 3. Knowledge-source hygiene

The most common cause of bot hallucination is bad sources, not bad models.

- **Curate over collect.** Pointing the bot at the whole intranet is a recipe for stale, contradictory answers. Pick canonical sources per topic area.
- **Publish-to-bot vs reference.** Some sources should be authoritative; others should be reference-only. Mark them accordingly so the bot can cite confidence-weighted.
- **Freshness control.** Each source has a refresh interval. If a SharePoint page changes daily but indexes weekly, users see stale answers. Set the cadence deliberately.
- **De-duplicate and resolve contradictions.** If three pages explain the same policy differently, the bot will pick one — often the wrong one. Fix the source content before adding more.
- **Test each source in isolation.** Add it, run a topic-specific test set, verify no regression.

### 4. Trigger-phrase design

Trigger phrases are intent classes, not synonyms. Each topic should have 8-15 trigger phrases representing the *range* of how users would express that intent.

- **Bad**: "reset password", "reset my password", "password reset" (3 variants of one phrase)
- **Good**: "reset password", "forgot password", "can't log in", "locked out", "need to change my password", "my password isn't working", "request a new password" (range of intent expressions)

The Copilot Studio NLU model generalises from the range. Narrow training data = brittle triggering.

### 5. Slot-filling patterns

For any topic that requires inputs:

- **Required vs optional** — explicitly mark. Optional slots have a default.
- **Validation** — every slot has a validation expression. "Email" requires regex; "Order Number" requires format check; "Date" requires date parse.
- **Re-prompt** — when validation fails, the re-prompt should explain *why* it failed and give an example. "I didn't understand — could you provide your order number in the format ABC-12345?"
- **Maximum attempts** — after 3 failed attempts, escalate. Looping forever frustrates users and hides bugs.
- **Confirmation** — before any irreversible action, show the user the collected values and ask "is this right?" Slot-filling without confirmation is how the wrong record gets updated.

### 6. Guardrails (system prompt, content moderation, off-topic redirection)

- **System prompt** at the bot level establishes voice, scope, and refusal patterns. "You are a customer service assistant for ACME. You only answer questions related to ACME products and orders. For anything else, politely redirect to live chat."
- **Content moderation** — Copilot Studio has built-in moderation; verify it's on. For sensitive domains, layer Purview labels and a custom moderation flow.
- **Off-topic redirection** — when generative answers return low-confidence or the user asks about an obvious off-topic (weather, news, jokes), respond with the redirection pattern, not an attempt.
- **Hallucination guardrails** — turn on "moderate" or "strict" grounding mode for generative answers; raise the confidence threshold; require citations.

### 7. Escalation to human — when, how, context

- **When**: explicit user request ("talk to a person"), N failed slot-fill attempts, low-confidence generative answer in a sensitive topic, any topic explicitly marked "always escalate" (legal, complaints, billing disputes).
- **How**: Teams channel handoff, Dynamics Customer Service queue, third-party live-chat integration, or email-the-conversation. Pick one and instrument it.
- **Context handoff**: the human picks up with the full conversation transcript, the detected intent, the values collected in slots, and any actions the bot took. A handoff with no context is worse than no bot — the user has to re-explain everything.

### 8. AI Builder vs prompt-flow vs direct Azure OpenAI

Decision matrix for "where should the AI step live?":

| Path | Best for | Cost shape | Governance |
|---|---|---|---|
| **Copilot Studio generative answers** | RAG-style Q&A over curated sources | Per-message licensing | Within Copilot Studio's roof, includes content moderation |
| **AI Builder Prompts** | Reusable single-shot prompt within a flow or topic | AI Builder credits per call | Authored as a Dataverse component; visible in CoE Kit |
| **Custom prompt-flow** | Multi-step LLM workflow with branching, RAG, tool use | Compute + LLM tokens | Hosted in Azure ML; separate identity surface |
| **Direct Azure OpenAI** | Maximum control, custom RAG, fine-tuning, real-time streaming UX | Tokens directly; cheapest at scale | You own everything — moderation, abuse prevention, prompt logging |

**Default**: stay inside Copilot Studio / AI Builder for governance. Only step out to prompt-flow / Azure OpenAI when there's a concrete requirement (cost at scale, custom RAG with vector store, fine-tuning, streaming UX) that justifies the operational overhead.

Premium connector / capacity note — every option here has cost. Call it out in the recommendation per §3 #8.

### 9. Regression test sets (the discipline)

Build a test set of **10-30 canonical prompts** covering:
- Each topic's trigger-phrase range (2-3 prompts per topic).
- Each generative-answer scope (5-10 known questions with known correct answers).
- Adversarial / out-of-scope prompts (5+ — verify the bot redirects, doesn't hallucinate).
- Escalation triggers (verify escalation fires).
- Slot-filling validation (verify validation rejects bad input).

Re-run the entire set on **every authoring change**. Manually if necessary; automated via the Copilot Studio testing pane or Power Automate where possible. Save the test transcripts. A regression in test set = block the release.

### 10. Measurement (containment, escalation, resolution, CSAT)

- **Containment rate** — % of conversations the bot completes without escalating. Higher isn't always better; a bot that "contains" by hallucinating is worse than escalating.
- **Escalation rate** — % escalated. Track *appropriate* vs *failure* escalations.
- **Resolution rate** — for transactional bots, did the user actually complete the task?
- **CSAT** — end-of-conversation feedback. Two scales: was the answer accurate; was the experience good.

Watch trends, not absolutes. A drop after a release usually points to a knowledge source change or trigger phrase regression.

## Anti-Patterns to Flag

- One mega-topic with 47 branches instead of decomposed topics
- "Set the bot loose on the intranet" knowledge configuration
- No regression test set ("we'll test it manually each release")
- No escalation path ("the bot will figure it out")
- System prompt copy-pasted from a tutorial, doesn't match the org voice or scope
- Slot-filling without confirmation before irreversible actions
- Trigger phrases that are all variants of one phrasing
- Hard-coded URLs, IDs, or secrets in topic responses (§3 #2 — env vars)
- Premium AI Builder / generative-answer usage without explicit licensing call-out (§3 #8)

## Escalation

- **Bot will handle PII / PHI / regulated content** → `ravenclaude-core` `security-reviewer` on the data flow before any deployment.
- **Bot calls flows that touch transactional systems** → `flow-engineer` + `power-automate` skill for resilient action wiring; `dataverse-architect` if it writes to Dataverse.
- **Need to ship via solution ALM** → `solution-alm-engineer` + `alm-pipeline-design` skill. Bots are solution-aware; treat as code.
- **Tenant DLP blocks the bot's required connector** → `power-platform-admin` + `dlp-policy-design` skill, not a hallway exemption.
- **Stuck on which AI path** → `architect` in `ravenclaude-core` for the cost / governance / data-residency conversation.

When in doubt, ship narrower scope with stronger guardrails than wider scope with looser guardrails. A bot that handles 5 things well is a product. A bot that handles 500 things badly is a liability.
