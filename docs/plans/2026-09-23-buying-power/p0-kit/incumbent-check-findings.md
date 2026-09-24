# Incumbent check findings (P0a item 6; criterion (e); U3 / U4 / C19 / C23)

Research date: **2026-09-24**. Researcher: deep-researcher subagent (desk research from public materials; no demos
taken).
Question: does **LearnPlatform by Instructure** (C19), or **GovSpend's agency-facing product** (C23), *already* serve
normalized, buyer-side, cross-district **price** benchmarks for SaaS, at a depth comparable to Buying Power? Default
launch state: Texas.

## Verdict

**Criterion (e) is provisionally NOT triggered by either incumbent on public evidence.** GovSpend comes closer than
the plan assumed, though, and a live demo is still needed to close U4.

| incumbent | cross-district price benchmark for buyers? | normalized SaaS unit price (metric, term, escalator)? | verdict | confidence |
|---|---|---|---|---|
| **LearnPlatform by Instructure** | **No evidence of one today.** The current product is inventory, usage, IMPACT/ROI evaluation, contract and privacy workflow. Its "Price" field and cost analysis use **the district's own** cost per student. The cross-district price reports existed only through the **2017 TEC partnership**, and nothing shows they survived. | No | **Does not meet (e).** Treat as an adjacent product and a possible partner/acquirer (usage data), not a price-benchmark incumbent. | Medium |
| **GovSpend (SmartProcure) agency product** | **Partly yes.** It is not "purely vendor-facing". An **Agency Launchpad** lets agency and district buyers search historical POs by keyword, see an **"AVERAGE PRICE" graph** and "TOP 10 COMPANIES BY LOWEST PRICE", filter by quantity, and "validate pricing". GovSpend markets this as showing districts "what comparable agencies paid". | **No evidence of it.** It works on raw PO line items: keyword search, average price, quantity filter. Nothing found normalizes to effective unit price per license metric, term, bundle or escalator, or covers SaaS contract terms. | **Probably does not meet (e) "at comparable depth"**, but it is a real buyer-side price-*lookup* competitor. **A demo must confirm.** | Low–Medium |

**Bottom line (inference):** the plan's positioning line, "vendors already see what you pay", is **incomplete**.
GovSpend lets *buyers* see raw PO prices too, and for data-sharing agencies that access has historically been
free. So Buying Power's defensible difference is **normalization plus contract terms plus renewal-timed workflow on
SaaS**, not "buyer access to prices" as such. The P0a demo should be built to test exactly that difference (see the
script below).

## Method limit

- [observation: direct] WebFetch and curl to instructure.com, community.instructure.com, support.govspend.com and
  similar vendor domains returned `EGRESS_BLOCKED` / proxy 403 from this environment. **That is transport (class I),
  not evidence about the vendors.**
- So every product fact below comes from **search-engine result snippets** of the named pages. I never opened the
  pages themselves.
- The tags mean the same as in `tec-premortem-findings.md`:
  - `[observation: snippet]` means I saw it in a search result's summary of the named page.
  - `[inference]` means my conclusion.
- **Absence of a feature in marketing snippets is weak evidence of absence (cause class F).** Features gated behind
  a login or a sales demo would not show up. That is why a demo is still required for both products.

## Evidence: LearnPlatform by Instructure

- **Current product scope is evidence, usage and management, not market price.** **Confidence: Medium.**
  - [observation: snippet] instructure.com/learnplatform and the LearnPlatform community article describe LearnPlatform
    as an "edtech effectiveness system" to "organize, streamline and analyze" edtech. It "streamlines processes like
    contract management, pilots, purchasing, and data privacy compliance".
  - [observation: snippet] Its free Inventory Dashboard helps districts "identify cost-saving opportunities … from
    underutilized licenses" and duplicative tools.
- **Its cost features use the district's own cost.** **Confidence: Medium.**
  - [observation: snippet] learnplatform.helpdocs.io, "Configuring Columns": "The Price column displays the per
    affected student per year cost as configured in the Product Details cost calculator". That is the district's
    own entry.
  - [observation: snippet] "What is a Cost Analysis in IMPACT": it assigns a dollar value to usage levels against the
    district's own product cost, to find money spent on unused or under-fidelity licenses.
- **2025–2026 public output is usage analytics.** **Confidence: Medium.**
  - [observation: snippet] The 2024–25 **EdTech Top 40** report (a PRNewswire / Instructure press release) analyzed
    "64 billion interactions from 3.7 million students". No price benchmarking was mentioned.
  - [observation: snippet] A 2026 Instructure product-update blog and InstructureCon coverage focus on Canvas and
    AI; no LearnPlatform price feature was found.
- **Cross-district price reports existed in 2017, and only through TEC.** **Confidence: Medium.**
  - [observation: snippet] In 2017 the TEC Data Platform, built on LearnPlatform, let members "access price reports
    on the products they are considering … how other districts are buying" (eSchool News, K-12 Dive).
  - [observation: snippet] Also in 2017, Karl Rectanus (Forbes, 2017-11-27) pitched "organization-wide data to
    negotiate contracts at better per-student rates".
  - [inference] No later LearnPlatform material describing cross-district price reports was found. The capability
    appears to have been TEC-specific and not carried forward. This is **exactly the thing to ask in the demo**,
    because Instructure plausibly still holds the historical data.
- **State-level footprint.** [observation: snippet] Ohio considered (2025) statewide adoption of LearnPlatform for
  DPA/SB29 compliance and public inventories. That is compliance, not pricing. No Texas statewide deployment was
  found.
- **Ownership.** [observation: snippet] Instructure closed the LearnPlatform acquisition on 2022-12-15. (This bears
  on T5: districts may distrust analytics owned by a vendor.)

## Evidence: GovSpend (SmartProcure) agency product

- **A buyer-facing module exists.** **Confidence: Medium.**
  - [observation: snippet] support.govspend.com/agency-launchpad: the "Agency Launchpad" is "built with agency
    workflows in mind". Its workflows include:
    - "verifying sole source suppliers";
    - "finding suppliers and comparing pricing";
    - "finding co-ops & contracts";
    - "validating suppliers".
  - [observation: snippet] support.govspend.com/how-to-check-pricing: a keyword search opens "Related Products & Market
    Pricing". The **'AVERAGE PRICE' graph shows the most common pricing for your key terms**. "TOP 10 COMPANIES BY
    LOWEST PRICE" shows the vendors awarded the lowest price on a PO.
  - [observation: snippet] govspend.com/agencies: it gives "government agencies and school districts the procurement
    intelligence to go into every purchase informed — **what comparable agencies paid**", and lets them "review
    pricing, quantities, and supplier information" from historical POs.
- **The data is PO / line-item, with a quantity filter, collected largely through public-records requests.**
  **Confidence: Medium.**
  - [observation: snippet] govspend.com data pages and the support "Data Overview: Spending & POs" page say it
    collects "purchase order number, purchase date, line item details, line item quantity, line item price, and
    vendor". It adds that "a quantity filter … allows users to look at different unit prices", that it "submits tens
    of thousands of public records requests monthly", and that its data goes back to 2015.
  - [observation: snippet] It says it will "aggregate, process, and **normalize**" data.
  - [inference] In context, "normalize" means data cleansing: vendor names, categories, line-item standardization. No
    snippet describes normalization to **effective unit price per license metric**, term length, bundle allocation,
    escalators or renewal terms. **This inference is the crux of U4, and it is exactly what a demo should test.**
- **Agency access pricing is unclear, and sources conflict.** **Confidence: Low.**
  - [observation: snippet] smartprocure.us (older branding): "SmartProcure provides **all participating government
    agencies** with access to the government purchase database **at no cost**". This is give-to-get: agencies share
    POs and get access.
  - [observation: snippet] Third-party 2026 pricing pages (Vendr, Fed-Spend, Software Finder) describe paid, custom-quoted
    subscriptions of about $3K–$15K+ a year. These are aimed at vendors, and none says whether agencies are still free.
  - [inference] If agency access is still free for data-sharing districts, GovSpend is the **cheapest substitute** for
    the "what did others pay" job. That raises the bar for Buying Power's buyer-paid tiers.
- **SaaS-specific depth: none found.** **Confidence: Low–Medium.**
  - [observation: snippet] A search for GovSpend plus SaaS, per-license and K-12 benchmark terms surfaced only generic
    K-12 *vendor*-sales material (govspend.com/k-12, FY26 prospecting blog).
  - [observation: snippet] One third-party page notes that GovSpend "only shows formally awarded contracts".
- **Corporate context.** [observation: snippet] SmartProcure / GovSpend was acquired by Thompson Street Capital
  Partners (2021-01-04) and bought Fedmine (2021-08). No 2024–2026 acquisition of a buyer-side benchmarking product was
  found.

## Adjacent players found incidentally (not in scope, but relevant to (e))

- **Gluona / Colorado Empowered Learning, "Equitable EdTech Pricing".** This is the most important incidental
  finding. **Confidence: Medium on existence; its date and current status are unverified.**
  - [observation: snippet] cel.colorado.gov/equitable-edtech-pricing: a state-supported program. A Chrome extension
    collects "licensing fees paid". Each district gets a report on "how the fees benchmark against **bulk purchasing
    agreements recorded nationally**".
  - [observation: snippet] The state pays 100% for the first 5,000 student accounts, then $0.50 per student.
  - [observation: snippet] Gluona aggregates across districts to choose products "most worthy of collective
    bargaining", then negotiates on behalf of Colorado districts.
  - [inference] This is a **live, buyer-side, cross-district SaaS price benchmark, combined with collective
    negotiation**. It is effectively TEC's model, state-funded. It appears **Colorado-only**, so it does not trip (e)
    for Texas, but it:
    - bears on the §4.1 launch-state re-rank (avoid Colorado, or partner);
    - is a natural co-op-style licensee or partner;
    - is a second worked example of the give-to-get arc, and its uptake numbers would be informative.
- **Civic IQ** (civiciq.com): vendor-facing K-12 board-meeting intelligence across more than 13,000 districts.
  - [observation: snippet] It publishes aggregate price commentary on its blog, e.g. "PowerSchool renewals …
    averaging $24,939 versus $10,604 at first purchase".
  - [inference] These are raw board-approval totals (the C43 not-to-exceed problem). They are public, **free "benchmark-like" numbers** that buyers can already find, and they sit on the vendor side. They do not trip (e).
- **EdTech JPA** (California): uniform master-agreement pricing. It is a co-op, and the plan's co-op interviews
  cover it.

## Competing hypotheses considered

1. **LearnPlatform quietly still offers TEC-style cross-district price reports to some customers, or state
   contracts do.**
   - For it: Instructure owns the platform that hosted the 2017 TEC price reports, plus years of district-entered
     "Price" fields.
   - Against it: no public mention since 2017.
   - Only a demo or sales call settles it. **Ask directly.**
2. **GovSpend's agency product already fully serves Buying Power's job, and districts just use raw PO averages.**
   - For it: an average-price graph, a quantity filter, "what comparable agencies paid", and possibly free for
     agencies.
   - Against it: SaaS contracts are poorly captured by PO line items (multi-year, bundled, NTE board totals; C43 /
     CE1), and no term or metric normalization is described.
   - If a demo shows SaaS line items with per-seat unit price and term, this flips toward **STOP/PARTNER**.
3. **A Texas co-op (TIPS, BuyBoard, Choice Partners) or an ESC already does this.** Out of scope for this brief. It
   is covered by P0a item 7 (co-op interviews). Search found nothing either way.

## Needs a human

1. **LearnPlatform demo or sales call** (U3). Ask:
   1. Can a district see what *other* districts pay for product X, per license and per term?
   2. What happened to the TEC-era price reports and data?
   3. Is aggregated "Price" field data ever benchmarked across customers?
   4. Is any statewide contract-pricing view in use (Texas? Ohio?)?
2. **GovSpend agency demo, or a trial account as a district user** (U4). Plan-A Alt 6 already allows a trial for
   internal validation. Do a live test on 2–3 of the pre-registered target SaaS products, in Texas districts:
   1. Are SaaS subscriptions present at line-item level with quantity? Or only as lump sums or NTE totals?
   2. Can results be expressed per seat per year, and does the term show?
   3. Is there any contract-term, escalator or renewal-date field?
   4. What share of the P0a sample's contracts appear at all? This doubles as a seedability comparison (CE1).
   5. **Is agency or district access still free with data sharing in 2026, and on what terms?**
3. **Gluona / Colorado Empowered Learning.** One call to learn:
   - participation counts and actual savings;
   - whether they are expanding beyond Colorado;
   - whether they would license or partner.

   This doubles as prior-art evidence for the TEC pre-mortem.
4. Record each demo outcome in the `decision_record` against criterion (e) as **met / not met / partial**, with the
   specific screen or answer as evidence.

## Sources consulted (all retrieved 2026-09-24 as search-result snippets unless marked direct)

- Direct: EGRESS_BLOCKED responses for instructure.com, community.instructure.com and support.govspend.com.
- https://www.instructure.com/learnplatform ; https://www.instructure.com/learnplatform-k-12 — current product
  positioning.
- https://community.instructure.com/en/kb/articles/660238-what-is-learnplatform — feature description.
- https://www.instructure.com/k12/products/learnplatform/inventory-dashboard — the Inventory Dashboard (underused
  licenses).
- https://learnplatform.helpdocs.io/article/agjij9pznk-configuring-columns — the "Price" column is the district's own
  per-student cost.
- https://learnplatform.helpdocs.io/article/oa24r236xd-what-is-a-cost-analysis-in-impact — IMPACT cost analysis
  (own cost).
- https://www.instructure.com/press-release/new-learnplatform-instructure-report-shows-k-12-districts-are-more-selective-about
  — EdTech Top 40, 2024–25 (usage).
- https://www.instructure.com/resources/blog/new-tools-elevate-teaching-learning-and-student-success-july-2026-product-updates
  — 2026 product updates (Canvas/AI).
- https://www.govtech.com/education/k-12/instructure-acquires-learnplatform-for-ed-tech-evaluation ;
  https://www.prnewswire.com/news-releases/instructure-acquires-learnplatform-adding-evidence-based-edtech-application-insight-to-the-instructure-learning-platform-301704507.html
  — the acquisition, closed 2022-12-15.
- https://www.forbes.com/sites/matthunckler/2017/11/27/learnplatform-aims-to-bring-transparency-and-savings-to-murky-12-billion-edtech-purchasing-market/
  — Rectanus in 2017 on per-student rate negotiation.
- https://www.eschoolnews.com/district-management/2017/02/03/edtech-pricing-data-platform/ — the TEC-era price
  reports on LearnPlatform.
- https://www.instructure.com/landing/ohio-doe and the Ohio legislative testimony (2025) — Ohio statewide
  consideration (compliance).
- https://govspend.com/agencies/ — "what comparable agencies paid"; historical POs for pricing.
- https://support.govspend.com/agency-launchpad ; https://support.govspend.com/how-to-check-pricing ;
  https://support.govspend.com/data-overview-spending-pos — Agency Launchpad, the AVERAGE PRICE graph, the quantity
  filter, line-item fields.
- https://govspend.com/govspend-platform/our-data-advantage/ — aggregate / process / normalize; public-records
  collection.
- https://smartprocure.us/ — "all participating government agencies … at no cost".
- https://www.vendr.com/marketplace/gov-spend ; https://fed-spend.com/blog/govspend-pricing-2026-cost-alternatives ;
  https://softwarefinder.com/accounting-software/govspend — third-party 2026 pricing (vendor-side, custom-quoted).
- https://www.tscp.com/news/thompson-street-capital-partners-announces-the-acquisition-of-govspend/ ;
  https://www.businesswire.com/news/home/20210811005058/en/ — 2021 ownership and the Fedmine deal.
- https://cel.colorado.gov/equitable-edtech-pricing ; https://www.gluona.org/membership — the Colorado buyer-side SaaS
  price benchmark and collective negotiation.
- https://blogs.civiciq.com/2026/04/02/powerschool-government-contracts-k-12-sis-market-share-pricing-competitor-analysis/
  — vendor-side public price commentary.
