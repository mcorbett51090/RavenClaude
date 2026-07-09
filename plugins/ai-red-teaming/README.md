# ai-red-teaming

> The **adversarial AI-security layer** for Claude Code — the team that answers *"can an adversary make this AI system do something harmful, leak data, or exceed its authority — and how do we harden it?"* and builds the threat model, attacks, harness, and remediations that make the answer defensible. Two agents: the **ai-redteam-lead** (scopes the threat model, rules of engagement, and prioritized attack taxonomy) and the **adversarial-testing-engineer** (executes the attacks, builds the automated harness, triages findings, and drives defense-in-depth remediation).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "How should we red-team this LLM feature before launch?" | A threat-modeled plan: assets/attackers/trust boundaries, rules of engagement, and a prioritized OWASP LLM Top 10 / MITRE ATLAS attack taxonomy |
| "Is this a safety problem or a security problem?" | The safety-vs-security split — model-behavior/harmful-content (safety, often trust-and-safety) vs adversary-induced boundary violations (security, this team) |
| "Run the jailbreak and prompt-injection attacks." | Reproducible attack runs (direct/indirect injection, roleplay/encoding/many-shot/crescendo jailbreaks, exfiltration) with payloads, transcripts, and a likelihood×impact severity each |
| "Can our agent be tricked into calling tools it shouldn't?" | Excessive-agency / tool-abuse test results: unauthorized tool calls, privilege escalation, exfiltration-via-tool, and the least-privilege + human-in-loop gaps found |
| "Set up an automated red-team suite for every model change." | A PyRIT / Garak / Promptfoo red-team / Giskard harness with attack datasets, a scorer/judge, pass-fail gates, and a CI regression baseline |
| "We have a pile of findings — what do we fix and how?" | Triaged findings + a defense-in-depth remediation plan (input/output guardrails, least privilege, allow-lists, human-in-loop) + a retest with the exact attack |

**Two rules it never breaks:** *threat model first, attacks second* (the taxonomy is derived from assets × attackers × trust boundaries, not a blog's jailbreak list), and *defense-in-depth, then retest* (no single filter is the defense, and a fix isn't done until the exact attack is re-run and it's baked into the regression harness).

## What's inside

- **2 agents** — `ai-redteam-lead` (scopes the threat model, rules of engagement, prioritized attack taxonomy, safety-vs-security split, and success/severity criteria) and `adversarial-testing-engineer` (executes the attacks, builds the automated harness, triages by likelihood×impact, and drives defense-in-depth remediation + retest).
- **3 skills** — `design-ai-redteam-plan`, `run-adversarial-attacks-and-jailbreaks`, `harden-and-remediate-ai-system`.
- **2 knowledge files** — a Mermaid AI attack-taxonomy decision tree (+ OWASP LLM Top 10 2025 map + MITRE ATLAS anchor + likelihood×impact severity table) and a 2026 AI-red-teaming-patterns reference (safety-vs-security, the jailbreak catalog, agentic tool-abuse, automated red-teaming, defense-in-depth, responsible disclosure, tooling map).
- **2 templates** — an AI red-team plan and an AI red-team findings report.

## Where it sits in the AI stack

```
claude-app-engineering    →  BUILD the AI app / agent            ("make it work")
ai-rag-engineering        →  retrieval / grounding architecture  ("ground it in our data")
llm-evaluation-engineering→  quality / capability regression     ("is it GOOD?")
trust-and-safety          →  content-moderation / T&S policy     ("is the CONTENT safe / on-policy")
ai-red-teaming (HERE)     →  can an ADVERSARY break / abuse it    ("can it be MADE to do harm / leak / over-reach")
```

This plugin is the **adversarial-security layer** *over* the others: it attacks the apps `claude-app-engineering` builds and the retrieval `ai-rag-engineering` grounds, stays distinct from the *quality* question `llm-evaluation-engineering` owns ("is it good?" ≠ "can it be broken?"), takes the *security* half of the safety-vs-security split while `trust-and-safety` takes the *safety*/content-policy half, and leaves the non-AI attack surface (network, auth, infra) to `security-engineering`.

## Tooling stance

Concept-first (OWASP LLM Top 10 2025, MITRE ATLAS, direct-vs-indirect injection, the jailbreak families, agentic tool-abuse, defense-in-depth, likelihood×impact severity, responsible disclosure), fluent across the automated red-team harnesses — **PyRIT**, **Garak**, **Promptfoo red-team**, and **Giskard**. Model-version behaviors, named jailbreak techniques, harness feature sets, and OWASP/ATLAS IDs are volatile and carry retrieval dates — the jailbreak landscape moves weekly, so re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ai-red-teaming@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
