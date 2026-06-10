---
name: security-questionnaire-response
description: Answer a security / vendor-risk questionnaire (SIG, CAIQ, VSA, or a bespoke one) honestly and defensibly — map every answer to an actual control and its SOC 2 / ISO 27001 evidence, state shipped vs roadmap vs not-applicable plainly, flag any unverifiable claim for security-reviewer before it ships, and capitalize answers into a reusable, freshness-dated trust-answer library. Reach for this on any inbound security questionnaire. Used by `rfp-security-response-specialist` (primary).
---

# Skill: security-questionnaire-response

> **Invoked by:** `rfp-security-response-specialist` (primary).
>
> **When to invoke:** "fill out this SIG / CAIQ / vendor security questionnaire"; "the prospect's security team sent a spreadsheet"; "we answer the same security questions every time".
>
> **Output:** evidence-mapped answers + a verification queue for unverifiable claims + a delta to the reusable answer library. See [`../../knowledge/security-questionnaire-and-trust.md`](../../knowledge/security-questionnaire-and-trust.md).

## Procedure

1. **Identify the framework.** SIG (Shared Assessments), CAIQ (CSA Cloud Controls Matrix), a VSA, or a bespoke questionnaire. Each maps to a known control taxonomy — reuse it rather than answering cold.
2. **Answer from actual controls, mapped to evidence.** For every "yes", name the control and the evidence behind it (SOC 2 Type II report section, ISO 27001 Statement of Applicability item, a policy, a config). A claim with no evidence is not a "yes".
3. **State the truth boundary plainly:** **implemented** / **roadmap (dated)** / **not applicable (with why)** / **compensating control**. Never inflate a roadmap control to implemented on a security questionnaire — it's a legal artifact and a fraud/clawback risk.
4. **Flag every unverifiable claim** for `ravenclaude-core/security-reviewer` *before* it ships. If you can't personally tie it to evidence, it goes in the verification queue, not the answer box.
5. **Lean on the SOC 2 / trust package.** Where the buyer will accept the SOC 2 report, the pen-test summary, or the trust center, point there rather than re-answering 300 cells — and offer the trust center to deflect the next one.
6. **Capitalize into the library.** Curate each answer with an **owner** and a **freshness date** into the reusable trust-answer library (in the RFP response matrix template). Stale security answers are a liability — date them.

## Output

The completed questionnaire (or the mapped answer set) + the verification queue (claims pending security-reviewer) + the library delta (new/curated answers with owner + date).

## Anti-patterns this skill prevents

- A "yes" with no control/evidence behind it (audit and clawback risk).
- Inflating a roadmap control to "implemented."
- Re-answering 300 cells by hand when a SOC 2 report / trust center would satisfy the ask.
- An answer library with no owner or freshness date (rots into wrong answers).
- Shipping an unverified security claim without security-reviewer sign-off.
