---
name: design-ai-redteam-plan
description: Scope an AI red-team engagement by threat-modeling the system (assets, attackers, trust boundaries), splitting safety from security, traversing the attack-taxonomy decision tree to a prioritized OWASP LLM Top 10 / MITRE ATLAS attack list, and setting the rules of engagement plus likelihood×impact success and severity criteria. Reach for this when the user asks "how should we red-team this LLM feature?", "what should we attack first?", "is this a safety or a security problem?", or "what are the rules of engagement?". Used by `ai-redteam-lead` (primary).
---

# Skill: design-ai-redteam-plan

> **Invoked by:** `ai-redteam-lead` (primary). Also consulted by `adversarial-testing-engineer` when execution reveals the scope or threat model is wrong.
>
> **When to invoke:** "How should we red-team <AI system>?"; "what should we attack first?"; "safety or security problem?"; "what are the rules of engagement / disclosure?"; any move from a deployed AI system to a scoped adversarial plan.
>
> **Output:** the threat model + safety-vs-security split + the prioritized attack taxonomy (OWASP LLM Top 10 / MITRE ATLAS) + rules of engagement + likelihood×impact success/severity criteria, captured in the red-team plan.

## Procedure

1. **Characterize the system under test.** Model(s) and version; **what it reads** (user turns only, or web/docs/RAG/tool results — attacker-controllable?); **what it can do** (text only, or tools/code/email/payments/browsing); **what it knows/reaches** (system prompt, user PII, training corpus, other tenants); modalities; and its **trust boundaries** (where untrusted input crosses into a privileged context). A plan with no system characterization is guessing.
2. **Threat-model: assets × attackers × abuse cases.** Name the **assets** (system prompt, RAG data, downstream actions, user data), the **attackers** (external user, a poisoned document, a compromised dependency), and the **abuse cases** (what unauthorized outcome each attacker wants). This is the source the taxonomy is derived from — not a blog's jailbreak list.
3. **Split safety from security.** For each concern, label it: **security** (an adversary induces a boundary violation — this team) vs **safety** (the model produces harmful content on its own — often `trust-and-safety`). Route the safety half out; keep the security half.
4. **Traverse the attack-taxonomy decision tree** in [`../../knowledge/ai-attack-taxonomy-decision-tree.md`](../../knowledge/ai-attack-taxonomy-decision-tree.md) against those inputs:
   - reads attacker-controllable content → **indirect prompt injection (LLM01)** leads,
   - user-only input → **direct injection / jailbreak (LLM01)**,
   - can act via tools → **excessive agency (LLM06)** — high impact,
   - reaches sensitive data / a training corpus → **sensitive-info disclosure (LLM02) / extraction / system-prompt leakage (LLM07)**,
   - accepts images/audio/files → **multimodal**; RAG/embeddings → **vector weaknesses (LLM08)**,
   - third-party model/data/plugins → **supply chain (LLM03) / poisoning (LLM04)**,
   - always also weigh **improper output handling (LLM05), misinformation (LLM09), unbounded consumption (LLM10)**.
5. **Prioritize by likelihood × impact.** Rank the in-scope classes against *this* system's reachability and blast radius (a public unauthenticated bot's system-prompt leak outranks an insider-only exotic). Produce a P0/P1/P2 ordering, not a flat list.
6. **Set the rules of engagement.** Scope (endpoints/models/versions), in/out-of-bounds targets, **data-handling** (no real PII to test infra; canary secrets), a kill-switch, rate/impact limits, and the **responsible-disclosure** terms.
7. **Define success + severity criteria and the flip conditions.** What counts as a successful attack (reproducible bypass, confirmed leak, unauthorized tool call), the severity scale (likelihood × impact), and the 1-2 facts that would re-prioritize the taxonomy. **Capture it all** in [`../../templates/ai-redteam-plan.md`](../../templates/ai-redteam-plan.md).

## Worked example

> User: "We're launching a customer-support RAG assistant that browses our help center and can issue refunds via a tool. How should we red-team it?"

- **System:** RAG assistant, reads the help center (attacker could plant content) + retrieved chunks; **can act** (refund tool = moves money); knows the system prompt + per-customer data.
- **Threat model:** assets = the refund action + customer data + system prompt; attackers = a malicious customer, a poisoned help-center/RAG doc; abuse case = "trick it into issuing an unauthorized refund" and "exfiltrate another customer's data".
- **Safety-vs-security:** "the bot is rude" = safety (→ trust-and-safety); "an injected doc makes it refund attacker" = security (this team).
- **Prioritized taxonomy (decision tree):** **P0** indirect prompt injection (LLM01) → **excessive agency (LLM06)** via the refund tool (unauthorized refund); **P0** cross-customer **sensitive-info disclosure (LLM02)**; **P1** system-prompt leakage (LLM07); **P1** vector/embedding weaknesses (LLM08) via poisoned chunks; **P2** unbounded consumption (LLM10).
- **RoE:** test on staging with a sandboxed refund tool (no real money), canary customer records, kill-switch, coordinated disclosure.
- **Success/severity:** a reproducible unauthorized refund = **P0 (high likelihood × high impact)**. **Flip condition:** if the refund tool gains no dollar cap or human-in-loop, tool-abuse severity rises further.

## Guardrails

- Never name attacks before the threat model — the taxonomy is *derived* from assets × attackers × trust boundaries.
- Always split safety from security and route the safety half to `trust-and-safety`; this team owns the security half.
- Prioritize by likelihood × impact, not by how novel/interesting the attack is.
- No adversarial testing without rules of engagement — scope, data-handling, kill-switch, and disclosure come first.
- Quality/capability regression eval is **not** red-teaming → route to `llm-evaluation-engineering`; non-AI pentest → `security-engineering`.
- Volatile facts (OWASP edition/IDs, ATLAS technique IDs, jailbreak techniques, model-version behavior) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/ai-red-teaming-patterns-2026.md`](../../knowledge/ai-red-teaming-patterns-2026.md).
