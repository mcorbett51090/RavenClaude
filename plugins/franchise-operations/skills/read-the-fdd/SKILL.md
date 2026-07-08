---
name: read-the-fdd
description: "A decision-focused read of a Franchise Disclosure Document: what the key Items mean for a buy decision — fees (Items 5-6), total investment (7), restrictions & territory (8/11/12), the Item 19 FPR's scope/cohort/exclusions, and turnover/litigation/bankruptcy (3/4/20) — as franchisee literacy, explicitly NOT legal advice (binding review -> legal-ops-clm). Reach for it when someone hands you an FDD. Used by `franchise-operations-strategist` (primary)."
---

# Skill: read-the-fdd

> **Invoked by:** `franchise-operations-strategist` (primary). **Binding review of the franchise agreement — what's enforceable, what to negotiate — routes to `legal-ops-clm`.** This skill is literacy, not legal advice.
>
> **When to invoke:** evaluating an FDD before signing, or making sense of Item 19.
>
> **Output:** a decision-focused summary of the key Items + the questions to take to counsel. Specifics carry a retrieval date + `[verify-at-use]` (FDDs are edition- and state-specific).

## Procedure

1. **Start with the money Items (5, 6, 7).** Item 5 = initial fees; Item 6 = the ongoing fees (royalty, ad fund, other) that load your unit model; Item 7 = the estimated total initial investment range. Pull these into [`../model-unit-economics/SKILL.md`](../model-unit-economics/SKILL.md).
2. **Read Item 19 for what it excludes.** A Financial Performance Representation is *optional* and *selected*: which units are in the cohort (company vs franchised, tenure, geography), average vs median, gross-vs-net, and the footnotes on what's excluded. A high average with a small top-quartile cohort tells you little about your unit. If there's **no** Item 19, the franchisor isn't disclosing performance — a signal in itself.
3. **Map the restrictions (Items 8, 11, 12).** Item 8 = required purchases/approved suppliers (a margin and sometimes rebate-to-franchisor issue); Item 11 = franchisor obligations, training, systems; Item 12 = territory — is it protected/exclusive, and can the franchisor open nearby or sell online into it?
4. **Read the risk Items (3, 4, 20).** Item 3 = litigation; Item 4 = bankruptcy; Item 20 = the outlet tables — **openings vs closures vs transfers** over the last three years. A high closure/transfer rate is the single most telling number in the document.
5. **Note the agreement terms for counsel (Item 17).** Term/renewal, termination, transfer, non-compete, dispute resolution/venue. Flag these; **do not opine on enforceability** — that's `legal-ops-clm`.
6. **Produce the decision summary + the counsel list.** What the FDD says for the go/no-go, and the specific clauses to have a franchise attorney review.

## Worked example

> Item 20 shows 40 openings, 28 closures, 15 transfers over 3 years.

- Read → net unit growth is thin and churn is high (closures + transfers ≈ the openings). Ask why: market, economics, or franchisor support?
- Item 19 → average AUV cited, but cohort = "franchised units open ≥2 years" (excludes the strugglers that closed) → survivorship-biased; discount it.
- Counsel list → territory (Item 12) exclusivity + termination (Item 17) → to `legal-ops-clm`.

## Guardrails

- **This is literacy, not legal advice** — enforceability, negotiation, and signing route to `legal-ops-clm`.
- **Item 19 is a disclosure, not a projection** — read the cohort and exclusions; build your own model.
- **Item 20 churn is the tell** — closures and transfers over openings often say more than the FPR.
- **FDDs are edition- and state-specific** — verify against the current document.
