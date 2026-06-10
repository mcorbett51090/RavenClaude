---
description: "Given a government RFP/RFI solicitation (or a description of one), run a full bid-no-bid analysis, build a compliance matrix, and produce a Section L/M-mapped response outline with every mandatory requirement resolved."
argument-hint: "[solicitation number or description, e.g. 'HHS-2026-001, IT modernization, 8(a) set-aside, LPTA, 50pp technical limit']"
---

You are running `/public-sector-govtech:respond-to-rfp`. Use the `public-procurement-strategist`
discipline and the `public-procurement-and-rfp` skill.

## Steps

1. **Bid-no-bid:** score the opportunity on the five criteria (capability, competition, mandatory
   requirements, past performance, strategic value) using the bid-no-bid tree in
   `knowledge/govtech-decision-trees.md`. Output a scored table and a go/no-go recommendation.
   If no-go, stop here with rationale.

2. **Compliance matrix:** extract every "shall/must/will" from the solicitation's Section L, Section M,
   and SOW/PWS. Build a matrix: requirement | source | proposal section | status. Flag every gap
   before proceeding.

3. **Response outline:** produce a Section L/M-mapped outline with:
   - Volume structure (Technical, Management, Past Performance, Price).
   - Per-evaluation-factor: proposed section title, discriminator statement, evidence/data needed.
   - Past-performance slots: 3–5 contract references, each with relevance narrative.
   - Compliance matrix attached as an appendix.

4. **Key risks:** list the top 3 risks (missing past performance, ambiguous mandatory requirement,
   tight page count) with a mitigation for each.

5. Fill `templates/rfp-response-outline.md` with the output, then emit the Structured Output block
   with handoffs (govtech-delivery-lead for post-award planning if go).
