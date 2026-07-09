# museum-cultural-institution-operations

> The **museum-operations layer** for Claude Code — the team that answers *"how does this museum/cultural institution steward its collection AND run a financially sustainable, accredited, visitor-serving operation?"* Two agents: the **museum-operations-lead** (admissions, membership/development, visitor experience, facilities, board/accreditation, and the earned-vs-contributed revenue mix) and the **collections-and-engagement-specialist** (collections stewardship, exhibitions, loans, and digital collections/access).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Should we accession / deaccession this object?" | An ethics-gated call (AAM/AAMD: deaccession proceeds fund collection care/acquisition **only**), the provenance/NAGPRA due-diligence checklist, and the collections-policy path |
| "Run the provenance / NAGPRA due diligence on this piece." | An ownership-history review flagging 1970-UNESCO / Nazi-era / cultural-patrimony red flags, with the transaction held until cleared |
| "TMS vs Axiell vs PastPerfect vs CollectionSpace?" | A decision-tree-driven CMS choice scoped by collection size, budget, and staff — plus migration cost and the conditions that would flip it |
| "Plan this temporary / traveling exhibition." | An exhibition project plan: concept → checklist & loans → interpretation → budget (earned + contributed) → critical-path schedule → install/condition → evaluation |
| "Publish our collection online — open access or not?" | A rights- and cultural-sensitivity-cleared publish plan: open-access/CC decision, IIIF + DAMS + online catalog, and the access-vs-rights trade-off |
| "Design our membership tiers and renewal program." | Behavior-based tiers + an acquisition-and-renewal/retention engine + the pricing model + its earned-vs-contributed contribution |
| "Timed ticketing, dynamic pricing, or free admission?" | A pricing-model recommendation modeling the access-vs-revenue trade-off, not a peer copy |
| "What's a healthy earned-vs-contributed revenue mix — and how do we hold it?" | A named mix target with named earned levers (admissions, membership, retail, venue, café) and contributed levers (development, sponsorship, endowment, grants) |
| "Prep us for AAM accreditation." | The Core Documents / collections-management-policy / code-of-ethics audit treated as an operating discipline, not a paperwork sprint |

**Two rules it never breaks:** *the collection is a public trust* (deaccession proceeds fund collection care/acquisition only — never operations; provenance due diligence before any accession/loan/acquisition), and *mission and money are one conversation* (every earned-revenue move is weighed against access and mission, and every mission move is costed).

## What's inside

- **2 agents** — `museum-operations-lead` (admissions/pricing, membership/development, visitor experience, facilities, board/accreditation, earned-vs-contributed mix) and `collections-and-engagement-specialist` (accessioning/deaccessioning ethics, cataloging, provenance/NAGPRA, loans, condition/environment, CMS, exhibitions, and digital collections/IIIF access).
- **3 skills** — `manage-collections-and-exhibitions`, `grow-membership-and-visitor-revenue`, `publish-digital-collections-and-access`.
- **2 knowledge files** — a Mermaid museum-operations decision tree (accession/deaccession ethics gate, pricing model, CMS choice, digital-publish rights gate, revenue-mix target) and a 2026 museum-operations-patterns reference (collections lifecycle & ethics, exhibition lifecycle, membership/revenue-mix patterns, admissions models, digital access, governance/accreditation, dated CMS/tooling map).
- **2 templates** — an exhibition project plan and a membership program plan.

## Where it sits among the nonprofit/cultural plugins

```
nonprofit-fundraising   →  generic individual-donor STRATEGY   ("the annual fund / major-gift / planned-giving engine")
event-management        →  generic event PRODUCTION            ("logistics / AV / run-of-show for the gala or opening")
grants-management       →  the grant LIFECYCLE                 ("prospect → write → comply → report")
marketing-operations    →  audience marketing & campaigns      ("promote the membership / the exhibition")
museum-cultural-institution-operations (HERE)  →  STEWARD the collection + RUN the institution  ("care for the objects; keep the museum solvent, accredited, and open")
```

This plugin **runs the museum** and **consumes** those disciplines rather than replacing them: it names the contributed-revenue need `grants-management` fills, the event `event-management` produces, and the donor engine `nonprofit-fundraising` runs — while owning the museum-*specific* work (collections ethics, exhibitions, membership, admissions, accreditation, digital collections) that none of them cover.

## Domain stance

Concept-first and ethics-gated: AAM accreditation & Core Documents, AAMD deaccession ethics, ICOM Code of Ethics, NAGPRA/repatriation, provenance & 1970-UNESCO/Nazi-era due diligence, the exhibition project lifecycle, the earned-vs-contributed revenue mix, admissions/pricing models (timed / dynamic / pay-what-you-wish / free), and digital access (IIIF, open-access/Creative Commons, rights statements, DAMS). Fluent across the collections-management systems — **TMS (Gallery Systems), Axiell, PastPerfect, CollectionSpace** — as options, not defaults. Standards revisions, CMS pricing/features, and IIIF/rights specifics carry retrieval dates — re-verify before a board or client commitment.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install museum-cultural-institution-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
