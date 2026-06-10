---
name: rfp-response
description: Respond to an RFP/RFI/RFQ — decide go/no-go before committing effort, then build a compliant, scannable requirement-by-requirement response matrix (comply / partial / roadmap / no-bid), thread the win themes, and run the compliance checklist so the bid isn't disqualified on a technicality. Reach for this when a formal RFP/RFI lands. Used by `rfp-security-response-specialist` (primary).
---

# Skill: rfp-response

> **Invoked by:** `rfp-security-response-specialist` (primary).
>
> **When to invoke:** "we got an RFP — should we respond?"; "help me structure this RFP response"; "is this RFI worth answering?".
>
> **Output:** a go/no-go verdict and, if go, a requirement-by-requirement response matrix + compliance checklist, using [`../../templates/rfp-response-matrix.md`](../../templates/rfp-response-matrix.md).

## Procedure

1. **Qualify the bid (go/no-go).** Traverse the RFP go/no-go tree in [`../../knowledge/se-engagement-decision-trees.md`](../../knowledge/se-engagement-decision-trees.md): Is there a relationship/champion, or is this a cold/compliance bid? Does the requirement set fit our strengths, or is it **wired for an incumbent** (over-specific requirements that match one competitor)? Is the effort justified by the win probability and deal size? A clean no-bid frees the team for a winnable one.
2. **Decompose into requirements.** Extract every stated requirement into the matrix, one row each. Don't summarize the document — answer it line by line; evaluators score on the matrix.
3. **Classify each requirement honestly:** **comply** (shipped) / **partial** (with the workaround) / **roadmap** (with a date, marked as such) / **no-bid** (cannot meet). Never inflate roadmap to comply — it surfaces in the POC or the contract.
4. **Thread the win themes.** From discovery (or the public record), weave the 2-3 reasons *this buyer* should pick you through the responses — not generic boilerplate.
5. **Run the compliance checklist.** Page limits, section order/numbering, mandatory forms, format, and the **deadline**. Per [`../../knowledge/security-questionnaire-and-trust.md`](../../knowledge/security-questionnaire-and-trust.md). RFPs are disqualified on technicalities before the prose is ever read.
6. **Route the security section** to `security-questionnaire-response` — it has its own evidence-mapping discipline.

## Output

The go/no-go verdict (with reasoning) + the response matrix + the passed compliance checklist. Capture reusable answers into the trust-answer library.

## Anti-patterns this skill prevents

- Reflexively bidding every RFP (burning the team on unwinnable, incumbent-wired bids).
- A narrative response that doesn't answer the requirements line by line.
- Inflating roadmap items to "comply."
- A great response disqualified on a format/deadline technicality.
