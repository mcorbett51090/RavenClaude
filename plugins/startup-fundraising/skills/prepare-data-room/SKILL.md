---
name: prepare-data-room
description: Assemble a founder's fundraising data room — the structured set of documents investors expect in diligence — so a "send me the data" request never stalls the round. Produces a stage-appropriate checklist organized by section (corporate, financials, cap table, product/tech, traction, team, legal/IP) with a what-to-include and a what-to-redact note per item. Reach for this when the user asks "what goes in a data room?" or "I got a diligence request — am I ready?". Used by `fundraising-strategist` (primary).
---

# Skill: prepare-data-room

> **Invoked by:** `fundraising-strategist` (primary). Gates `build-investor-pipeline` (don't go wide before the room exists).
>
> **When to invoke:** "what should be in my data room?"; "an investor asked for diligence materials — what do I send?"; "am I diligence-ready?".
>
> **Output:** a sectioned, stage-appropriate checklist + access/redaction guidance + a readiness verdict.

## Procedure

1. **Right-size to the stage.** A pre-seed data room is light (deck, lean model, cap table, incorporation docs); a Series A room is deep (audited-ish financials, detailed metrics, full contracts). Pull the stage from the `fundraising-strategist` / [`../../knowledge/fundraising-stages-decision-tree.md`](../../knowledge/fundraising-stages-decision-tree.md). Don't over-build a pre-seed room or under-build a Series A one.
2. **Assemble by section** (see the checklist below). For each item, note **what to include** and **what to redact** (e.g., customer names under NDA, employee PII, unsigned drafts).
3. **Reconcile with the deck.** Every claim in the pitch (traction, revenue, market) must match a source in the data room. Mismatches surface in diligence and erode trust — flag any deck claim with no backing document.
4. **Set access controls.** Use a controlled-share folder (e.g., a permissioned drive or a dedicated data-room tool), view/download permissions per investor, and ideally access logging. Don't email sensitive docs as open attachments.
5. **Stage the release.** Share the lighter "first-look" set early (deck, summary metrics, cap-table summary); hold the sensitive set (contracts, detailed financials, full cap table) for investors past the first meeting / in active diligence.
6. **Emit a readiness verdict:** ready / gaps-to-close, with the specific missing or stale items.

## The checklist (stage-appropriate — include what fits the round)

- **Corporate & formation** — certificate of incorporation, bylaws, board consents, prior financing docs (SAFEs/notes/priced-round docs), 83(b) elections.
- **Cap table** — current fully diluted cap table, option-pool detail, all outstanding SAFEs/notes with caps/discounts (pairs with [`../model-cap-table-and-dilution/SKILL.md`](../model-cap-table-and-dilution/SKILL.md)).
- **Financials** — historical P&L / burn, the financial model & projections (model mechanics route to `finance`), runway calc, current bank balance summary.
- **Traction & metrics** — KPI dashboard, cohort/retention, pipeline/ARR/MRR detail, key customer logos (redact names under NDA).
- **Product & technology** — product overview/roadmap, architecture summary, security/compliance posture as relevant.
- **Team** — founder bios, org chart, key hires & plan, employment/IP-assignment confirmations.
- **Legal & IP** — material contracts, customer/vendor agreements, IP assignments & filings, any litigation/disputes. (Binding review of these documents routes to `legal-ops-clm` — this skill organizes the room, it does not opine on the contracts.)
- **Market & GTM** — market sizing (bottom-up), competitive landscape, go-to-market plan.

## Worked example

> Founder mid-seed, an investor just asked for "the data room."

- Stage = seed → medium depth. First-look set: deck, one-page metrics, cap-table summary, lean model, incorporation cert.
- Diligence set (post-first-meeting): full fully-diluted cap table + all SAFEs, detailed P&L/burn + model, cohort retention, top contracts (NDA-name redactions), IP assignments.
- Reconcile: deck says "120% net revenue retention" → confirm a cohort doc in the room backs it. No backing doc → flag before sharing.
- Verdict: ready to share first-look; close two gaps (IP-assignment confirmations, cohort doc) before the diligence set goes out.

## Guardrails

- **Stage-size the room** — over-building a pre-seed room signals inexperience; under-building a Series A room stalls the round.
- **Reconcile every deck claim with a document** — diligence surprises kill deals.
- **Control access and stage the release** — sensitive docs are permissioned, not emailed; full financials/contracts wait for active diligence.
- **Redact PII and NDA-bound names.**
- **This skill organizes the room; it is not legal advice** — the documents' substance routes to `legal-ops-clm`, the model to `finance`.
