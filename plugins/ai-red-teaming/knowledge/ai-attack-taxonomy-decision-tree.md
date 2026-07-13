# Knowledge — AI attack-taxonomy decision tree

> **Last reviewed:** 2026-07-13 · **Confidence:** Medium-High (consensus on the OWASP LLM Top 10 2025 categories, the MITRE ATLAS framing, and the direct-vs-indirect-injection / excessive-agency prioritization; **Medium on the newer, more-volatile OWASP Top 10 for Agentic Applications (ASI) 2026 edition — added 2026-07-13, carries a retrieval date; specific model-version behaviors, named jailbreak techniques, and harness feature sets are volatile — carry retrieval dates and re-verify before a client commitment**).
> The most-asked AI-red-team question is "what should we attack first?". This is the decision tree the `ai-redteam-lead` traverses **before** naming an attack, plus the OWASP LLM Top 10 (2025) mapping, the OWASP Top 10 for Agentic Applications (2026) companion map, the MITRE ATLAS anchor, the likelihood×impact severity table, and the seams to adjacent plugins.

The team's discipline: **derive the attack taxonomy from the system's assets × attackers × trust boundaries first, name the specific jailbreak/injection technique second.** Content-policy / harmful-content-at-scale questions are **safety**, not this security layer — they leave for `trust-and-safety`; quality-regression eval leaves for `llm-evaluation-engineering`; non-AI pentest leaves for `security-engineering`.

---

## Decision Tree: prioritizing the attack surface

Traverse top-to-bottom. Gate on **what the system READS** (untrusted content in the prompt), then **what it can DO** (tools/actions), then **what it KNOWS** (sensitive data / training set), then **what it ACCEPTS** (modalities), then **what it depends ON** (supply chain).

```mermaid
graph TD
  Start([What is the system's exposure?]) --> READS{Does it READ<br/>attacker-controllable content?}

  READS -->|Yes — web pages, docs, emails, RAG chunks, tool results| INDIRECT[Indirect prompt injection LLM01<br/>· untrusted data enters the prompt<br/>· HIGHEST priority for RAG/agents]
  READS -->|Only the user's own turn| DIRECT[Direct prompt injection / jailbreak LLM01<br/>· roleplay · encoding · many-shot · crescendo]

  INDIRECT --> DOES
  DIRECT --> DOES

  DOES{Can it DO things<br/>tools / actions / side effects?} -->|Yes — tools, code exec, email, payments, browsing| AGENCY[Excessive agency LLM06<br/>· unauthorized tool calls · privilege escalation<br/>· exfiltration via tools — HIGH impact]
  DOES -->|No — text output only| OUTPUT[Improper output handling LLM05<br/>· XSS/SSRF/SQLi if output is trusted downstream]

  AGENCY --> KNOWS
  OUTPUT --> KNOWS

  KNOWS{What sensitive data<br/>does it KNOW / reach?} -->|System prompt / config| LEAK[System-prompt leakage LLM07<br/>· extract instructions, keys, guardrails]
  KNOWS -->|User PII / business data| DISC[Sensitive info disclosure LLM02<br/>· data exfiltration · cross-tenant leakage]
  KNOWS -->|Training / fine-tune corpus| EXTRACT[Training-data extraction<br/>· memorized-secret / PII regurgitation]

  LEAK --> ACCEPTS
  DISC --> ACCEPTS
  EXTRACT --> ACCEPTS

  ACCEPTS{What modalities<br/>does it ACCEPT?} -->|Images / audio / files| MULTI[Multimodal attacks<br/>· injection hidden in an image · adversarial perturbation]
  ACCEPTS -->|Text only| VECTOR{RAG / embeddings in the loop?}

  MULTI --> DEPENDS
  VECTOR -->|Yes| VEC[Vector & embedding weaknesses LLM08<br/>· poisoned chunks · embedding-inversion leakage]
  VECTOR -->|No| DEPENDS

  VEC --> DEPENDS
  DEPENDS{Third-party models,<br/>data, or plugins?} -->|Yes| SUPPLY[Supply chain LLM03 + Data/model poisoning LLM04<br/>· poisoned model/dataset · malicious plugin]
  DEPENDS -->|No| SEV

  SUPPLY --> SEV
  SEV{Severity = likelihood × impact} -->|Reachable + high blast radius| P0[P0 — test first]
  SEV -->|Reachable, bounded impact| P1[P1]
  SEV -->|Needs insider / low impact| P2[P2 — test if time]

  %% cross-cutting classes that apply regardless of the branch
  SEV -.also always consider.-> MISINFO[Misinformation LLM09<br/>· confident falsehoods with downstream reliance]
  SEV -.also always consider.-> DOS[Unbounded consumption LLM10<br/>· token/cost exhaustion · wallet-drain DoS]
```

---

## OWASP LLM Top 10 (2025 edition) — the class map

| ID | Class | What the red-teamer probes | Typical highest-impact target |
|---|---|---|---|
| **LLM01** | **Prompt injection** (direct + indirect) | Override instructions via the user turn OR via content the model reads (web/doc/RAG/tool result) | Any model; indirect is the defining risk for RAG + agents |
| **LLM02** | **Sensitive information disclosure** | Coax out PII, secrets, business data, cross-tenant data | Multi-tenant assistants, data-connected bots |
| **LLM03** | **Supply chain** | Poisoned base model, tampered dataset, malicious plugin/adapter | Fine-tuned / plugin-extended systems |
| **LLM04** | **Data & model poisoning** | Corrupt training/fine-tune/RAG data to implant behavior or backdoors | RAG corpora, continuous-learning loops |
| **LLM05** | **Improper output handling** | Model output trusted downstream → XSS, SSRF, SQLi, code exec | Output rendered as HTML / fed to a shell/DB |
| **LLM06** | **Excessive agency** | Induce unauthorized tool calls, privilege escalation, action-taking | Tool-using agents (email, payments, code exec) |
| **LLM07** | **System prompt leakage** | Extract the system prompt, embedded keys, guardrail logic | Any bot with a secret-bearing system prompt |
| **LLM08** | **Vector & embedding weaknesses** | Poison retrieved chunks; embedding-inversion to leak source text | RAG / vector-store-backed systems |
| **LLM09** | **Misinformation** | Elicit confident falsehoods where a human relies on them | Advice/decision-support assistants |
| **LLM10** | **Unbounded consumption** | Token/compute/cost exhaustion; wallet-drain denial-of-service | Metered/paid API-backed deployments |

> **Volatile:** the OWASP LLM Top 10 is versioned (this maps the **2025** edition); category names/IDs shift between editions. Treat this as a 2026-07 snapshot and re-verify the current edition before quoting IDs in a deliverable.

---

## OWASP Top 10 for Agentic Applications (2026 edition) — the companion agentic map

When the target is not a single LLM call but an **agent** (or a multi-agent system) — one that plans, remembers across turns, calls tools, and coordinates with other agents — the LLM Top 10 above still applies to each model call, but it under-describes the *agent-level* risks. The OWASP GenAI Security Project's **Top 10 for Agentic Applications** (the **ASI** series, published December 2025) is the companion taxonomy for those risks. Use it *in addition to* the LLM Top 10 on any tool-using / memory-bearing / multi-agent system — several ASI classes have no LLM-Top-10 equivalent.

| ID | Class | What the red-teamer probes | Closest LLM-Top-10 anchor\* |
|---|---|---|---|
| **ASI01** | **Agent goal hijack** | Redirect the agent's objective / decision path via malicious content it plans over | LLM01 (injection, applied to *goals*) |
| **ASI02** | **Tool misuse & exploitation** | Unsafe tool chaining, ambiguous tool instructions, manipulated tool outputs → harmful actions | LLM06 excessive agency |
| **ASI03** | **Agent identity & privilege abuse** | Inherited / cached / over-broad credentials; the agent acting beyond its authorized identity | *(new — agent identity)* |
| **ASI04** | **Agentic supply chain vulnerabilities** | Malicious or tampered tools, plugins, MCP servers, or agent components | LLM03 supply chain |
| **ASI05** | **Unexpected code execution / RCE** | Agent generates or runs attacker-controlled code in its execution environment | LLM05 improper output handling |
| **ASI06** | **Memory & context poisoning** | Persistent corruption of the agent's memory / stored context so a *later* session misbehaves | LLM04 poisoning *(persistent-memory variant)* |
| **ASI07** | **Insecure inter-agent communication** | Spoofed / tampered / eavesdropped messages between agents in a multi-agent system | *(new — multi-agent)* |
| **ASI08** | **Cascading failures** | One agent's failure or compromise propagating — blast-radius amplification across the fleet | *(new — multi-agent)* |
| **ASI09** | **Human-agent trust exploitation** | Abusing the human's trust in the agent (the agent as a social-engineering vector) | LLM09 misinformation *(trust variant)* |
| **ASI10** | **Rogue agents** | A compromised or misaligned agent diverging from intended behavior, evading oversight | *(new — agent behavior)* |

\* The anchor column is **this plugin's cross-walk** to the LLM Top 10 for readers already fluent in it — **not** an OWASP-canonical mapping. `*(new)*` marks classes with no clean LLM-Top-10 predecessor (the agent-, memory-, and multi-agent-specific risks).

> **When to reach for it:** if the system *plans*, *remembers across turns*, *calls tools*, or *coordinates with other agents*, scope against the ASI list as well as the LLM Top 10 — **ASI03, ASI06, ASI07, ASI08, and ASI10** are the classes the LLM Top 10 does **not** cover. House opinion #4 (excessive agency is where LLM bugs become real-world incidents) maps directly onto ASI01/ASI02/ASI03/ASI10.

> **Volatile:** the ASI series is a 2026 edition (published December 2025; retrieved 2026-07-13 via `WebSearch` — `genai.owasp.org` 403s automated fetch, so IDs/titles were cross-referenced across the OWASP resource page plus multiple secondaries — F5 / Promptfoo / Adversa / Giskard). Category names/IDs shift between editions — re-verify the current edition and IDs against the OWASP GenAI Security Project before quoting them in a deliverable. Source: [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).

---

## MITRE ATLAS — the adversary-lifecycle anchor

Where OWASP names the *risks*, **MITRE ATLAS** (Adversarial Threat Landscape for AI Systems) maps the *adversary tactics & techniques* across the lifecycle — reconnaissance, resource development, initial access, ML model access, execution, persistence, exfiltration, impact. Use ATLAS to structure the *campaign* (how an attacker chains steps, e.g. recon a model → craft an injection → exfiltrate data) and OWASP to enumerate the *findings*. The two are complementary: ATLAS is the kill-chain, OWASP is the checklist. _(ATLAS technique IDs evolve — retrieved 2026-07-09; re-verify before pinning a specific technique ID.)_

---

## Direct vs indirect prompt injection — the distinction that drives everything

- **Direct** — the *user* is the attacker, typing the malicious instruction into their own turn (a jailbreak: roleplay/DAN, encoding, many-shot, crescendo). The blast radius is usually *that user's own session*.
- **Indirect** — the attacker plants the instruction in **content the model later reads** (a web page it browses, a document in the RAG store, an email it summarizes, a tool's response). The victim is a *different* user or the system itself. This is the **defining** LLM-security problem: the model cannot reliably tell "data to process" from "instructions to obey" once both are in the context window.

**Rule:** the instant a system reads attacker-controllable content, treat every such seam as hostile input — indirect injection outranks direct on any RAG or tool-using system.

---

## Severity: likelihood × impact

| | **Impact: low** (words only) | **Impact: med** (data leak, one user) | **Impact: high** (action/exfil, many users) |
|---|---|---|---|
| **Likelihood: high** (public, no auth) | P2 | P1 | **P0** |
| **Likelihood: med** (auth'd user) | P3 | P2 | P1 |
| **Likelihood: low** (insider/complex) | P3 | P3 | P2 |

Impact rises with **what the system can do** (a jailbroken chatbot leaks text; a jailbroken agent with a payments tool takes money) and **how many** it affects (single session vs cross-tenant). Likelihood rises with **reachability** (public + unauthenticated + no rate limit). Set severity at scoping, triage findings against it — don't argue it during the fire.

---

## Seams (AI red-teaming is the adversarial-security layer, not a rival to the others)

- **Quality / capability regression eval, LLM-as-judge, benchmark scoring** → `llm-evaluation-engineering` (the "is it *good*?" question — distinct from "can an adversary *break* it?").
- **Platform content-moderation, T&S policy, abuse-at-scale on user-generated content** → `trust-and-safety` (the safety half of the safety-vs-security split).
- **Application / infrastructure / network penetration testing** → `security-engineering` (the non-AI attack surface).
- **The RAG retrieval/grounding architecture a poisoning/injection finding implicates** → `ai-rag-engineering`; **the Claude app/agent build** → `claude-app-engineering`.

---

## Provenance

- OWASP Top 10 for LLM Applications **2025** edition (LLM01–LLM10 as mapped above) and MITRE ATLAS framing, reviewed 2026-07-09 — **Medium-High confidence** on the durable categories.
- OWASP Top 10 for **Agentic Applications** (ASI01–ASI10, **2026 edition**, published December 2025 by the OWASP GenAI Security Project) — the companion agentic map, added 2026-07-13. Retrieved 2026-07-13 via `WebSearch` (genai.owasp.org 403s automated fetch); IDs/titles cross-referenced across the OWASP resource page + F5 / Promptfoo / Adversa / Giskard — **Medium confidence** (newer framework, exact per-edition titles more volatile than the LLM Top 10; the anchor-to-LLM cross-walk is this plugin's, not OWASP-canonical).
- Direct-vs-indirect injection, excessive-agency-as-highest-impact, and likelihood×impact triage are consensus practice across the LLM-security literature, reviewed 2026-07-09.
- **Volatile:** OWASP edition/IDs (both the LLM Top 10 and the Agentic ASI list), ATLAS technique IDs, named jailbreak techniques, and model-version behaviors change frequently — treat all specifics as a 2026-07 snapshot and re-verify with `ravenclaude-core/deep-researcher` before a client commitment.
