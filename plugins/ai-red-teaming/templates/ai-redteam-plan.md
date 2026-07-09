# AI red-team plan — <system-under-test>

> The one-page plan captured **before** the first attack. Pairs with
> [`ai-redteam-findings-report.md`](ai-redteam-findings-report.md) (what you found and fixed).
> Scoped by the `ai-redteam-lead`; executed by the `adversarial-testing-engineer`.

**Owner / lead:** <name> · **Date:** <YYYY-MM-DD> · **Engagement window:** <start–end> · **Status:** draft / approved / executing / closed

## System under test
- **What it is:** <chatbot / RAG assistant / tool-using agent / multimodal model>
- **Model(s) & version:** <provider · model · version — note: volatile, re-verify behavior before relying on it>
- **What it READS:** <user turns only · or web/docs/RAG chunks/emails/tool results — attacker-controllable?>
- **What it can DO:** <text only · or tools/code exec/email/payments/browsing — the action surface>
- **What it KNOWS / reaches:** <system prompt · user PII · training/fine-tune corpus · other tenants>
- **Modalities accepted:** <text · images · audio · files>
- **Trust boundaries:** <where untrusted input crosses into a privileged context>

## Threat model
- **Assets:** <system prompt · RAG/training data · downstream actions · user/business data>
- **Attackers:** <external user · a poisoned document the model reads · a compromised dependency>
- **Abuse cases:** <the unauthorized outcome each attacker wants>

## Safety-vs-security split
- **Security (this team):** <adversary-induced boundary violations in scope>
- **Safety (→ trust-and-safety):** <harmful-content / model-behavior concerns routed out>

## Attack taxonomy — prioritized (OWASP LLM Top 10 2025 + MITRE ATLAS)
| Priority | Class (OWASP LLM / ATLAS) | Why (likelihood × impact) | Where it applies |
|---|---|---|---|
| P0 | <e.g. LLM01 indirect prompt injection> | <high reachability × high blast radius> | <the untrusted-content seam> |
| P0 | <e.g. LLM06 excessive agency> | <can take real-world action> | <the tool/action> |
| P1 | <e.g. LLM02 sensitive-info disclosure> | <bounded but real> | <the data reached> |
| P1 | <e.g. LLM07 system-prompt leakage> | <...> | <...> |
| P2 | <e.g. LLM10 unbounded consumption> | <needs effort / low impact> | <...> |

> Always also weigh: LLM03 supply chain · LLM04 data/model poisoning · LLM05 improper output handling · LLM08 vector/embedding weaknesses · LLM09 misinformation.

## Rules of engagement
- **Scope (in-bounds):** <endpoints / models / versions / environments — prefer staging>
- **Out-of-bounds:** <what must NOT be touched — production data, third-party systems, other tenants>
- **Data-handling:** <no real PII exfiltrated to test infra · canary/synthetic secrets · where transcripts are stored>
- **Kill-switch:** <how to stop the engagement immediately>
- **Rate / impact limits:** <so a test can't become an outage>
- **Responsible disclosure:** <coordinated-disclosure terms for any third-party-affecting finding>

## Success + severity criteria
- **What counts as a successful attack:** <reproducible policy bypass · confirmed data leak · unauthorized tool call>
- **Severity scale (likelihood × impact):** <P0 high×high … P3 low×low — the triage rubric>

## Seams (not this team)
- **Quality / capability regression eval, LLM-as-judge:** llm-evaluation-engineering
- **Platform content-moderation / T&S policy:** trust-and-safety
- **Application / infra / network penetration testing:** security-engineering
- **RAG retrieval/grounding:** ai-rag-engineering · **the Claude app/agent build:** claude-app-engineering

## Flip conditions
- <the 1-2 facts that would re-prioritize the taxonomy — e.g. "if the agent gains a payments tool, tool-abuse → P0">

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
