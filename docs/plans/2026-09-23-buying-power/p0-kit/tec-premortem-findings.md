# TEC pre-mortem findings (P0a item 5, F11; U1 / U2 / B-10)

Research date: **2026-09-24**. Researcher: deep-researcher subagent (desk research only; no outreach).
Scope: the Technology for Education Consortium (TEC, techedconsortium.org, EIN 81-0704220). Asks: is it still
operating? If not, why not? Who paid the 10% fee?

## Verdict

**F11 three-state result: "Indirect evidence only, consistent with dormancy or wind-down around 2019–2021."
The cause is NOT established.** This is a *provisional* finding, and the method limit below explains why it is not
a final one.

| question | answer | confidence |
|---|---|---|
| Is TEC still operating in 2024–2026? | **Probably not in any active sense.** No dated TEC activity after June 2020 was found. The last indexed 990 is for 2019 (revenue about $150K). Both named founders now appear to be in other roles. | Medium |
| Did it fail, and why? | Dormancy is likely, but no post-mortem, complaint or stated reason was found. The evidence fits a **funding cliff when the Gates grants ended**. It cannot tell a **demand-side** cause apart from a **supply-side or monetization** one. | Low (for the cause) |
| Who paid the 10% Phase-3 fee (B-10)? | **Probably the buyer (the district).** Every snippet presents the fee schedule as district-facing. It is not settled: no primary text says "paid by the district", and "10% of products procured" is ambiguous between contract value and savings. | Low–Medium |

**What this means for the P0a gate (criterion (d)):** "indirect evidence only" passes *if* the evidence is consistent
with causes the plan already addresses. The evidence here fits T1 (cold start), T6 (a buyer fee that is hard to
procure) and a philanthropy-dependency cause the plan does not name as such (see "Implications"). It gives **no
support** for the STOP trigger, which is a demand-side cause that is now established. **Nothing here shows that
districts wouldn't pay for, or act on, price data. Nothing shows that they would, either.** Treat the P0b
revealed-preference bar as live regardless.

## Method limit (read this before trusting the verdict)

- **Direct retrieval was blocked in this session.** [observation] WebFetch and curl to techedconsortium.org,
  web.archive.org, projects.propublica.org, apps.irs.gov, causeiq.com, gatesfoundation.org, linkedin.com, k12dive.com
  and instructure.com all returned `EGRESS_BLOCKED` / `CONNECT tunnel failed, response 403` from this environment's
  egress proxy. That is **cause class I (transport)**. It is evidence about reachability from this sandbox, **not
  about TEC.**
- So **every source fact below comes from search-engine result snippets.** An intermediate model wrote them, and I
  never opened the underlying pages. Tag convention used below:
  - `[observation: snippet]` means I saw it in a search result's summary of the named page, but did not open the page.
  - `[observation: direct]` means I observed it myself in this session.
  - `[inference]` means my conclusion.
- **The snippets make mistakes.** One search summary claimed a GovTech article was "dated April 2021". Other
  evidence places Friedlander's NYC DOE departure and TEC's founding in about 2015. Every snippet-level fact needs a
  human to open the page before it goes into a decision record.
- **Sanitizer note:** no WebFetch body was ever retrieved, so `sanitize-webfetch-body.py` had nothing to process.
  The search results contained no injection-shaped content.

## Evidence

### A. Timeline of TEC activity (newest first)

| date | event | tag | source |
|---|---|---|---|
| 2026-09-24 | `techedconsortium.org` still resolves in DNS (to 35.194.34.8, a Google Cloud address). Search engines still index its home, about, services, membership, press, blog and reports pages. The indexed text is undated and present-tense ("has convened more than 100 districts … 5.5 million K-12 students"). | [observation: direct] for DNS; [observation: snippet] for the index | local `getent`/`dig`; web search results for techedconsortium.org/* |
| unknown (2024–26?) | Celina Morgan-Standard, TEC's founder and later CEO, is listed as **COO of Energy Transition Capital Management** (La Jolla, CA / Dorado, PR). TEC appears as a *previous* role ("Previously, Celina was the Founder & Chairman at Technology for Education Consortium"). | [observation: snippet] | ZoomInfo, RocketReach and ContactOut profiles (see Sources) |
| unknown | Hal Friedlander, co-founder and first CEO: his LinkedIn headline reads "Education + Technology Strategic Advisor". ZoomInfo lists him as "Independent Consultant", with a legacy @techedconsortium.org email. | [observation: snippet] | LinkedIn search result; ZoomInfo |
| 2023-03-27 | A Friedlander op-ed in The 74 (with Andrew Buher). His bio reads "founder of the Technology for Education Consortium, a K-12 technology strategic adviser". It does **not** say he is its CEO. | [observation: snippet] | the74million.org contributor page and article |
| 2020-06-16 | An EdSurge piece by Celina Morgan-Standard, bylined "Founder and CEO of TEC". The data it cites is a **2017** TEC survey, not anything newer. | [observation: snippet] | edsurge.com/news/2020-06-16-… |
| 2019 (tax year) | **The latest 990 indexed by ProPublica shows revenue of about $150K, expenses of $95.2K and assets of $93.9K.** ProPublica lists filings for 2015–2019 only. | [observation: snippet] | ProPublica Nonprofit Explorer, EIN 810704220 |
| 2018-11-27 | Harold O. Levy, TEC's board chair (per EdWeek in 2016), died of ALS. | [observation: snippet] | EdWeek and Chalkbeat obituaries (Nov 2018) |
| 2018-03-29 | CNN Money quotes Friedlander as "CEO of the Technology for Education Consortium" on iPad pricing: $367–$499 across 40 districts. | [observation: snippet] | money.cnn.com 2018/03/29 |
| 2017-03 | A Gates Foundation grant, OPP1171570: **$500,000, 23 months** (to about Feb 2019), "to support digital content and education technology". Grantee location: San Diego, CA. | [observation: snippet] | gatesfoundation.org committed-grants page |
| 2017-04 | A TEC report says districts could save "$3 billion a year". It found a 20–40% price spread across 130 districts, 3.8M students and $412M of 2015 spend. | [observation: snippet] | EdWeek Market Brief 2017/04 |
| 2017-02 | The **TEC Data Platform launches at FETC 2017 on LearnPlatform** (Lea(R)n). It covered 50+ member districts, 3.5M students and about $300M of edtech spend. It had 35 "core" districts, and was free to districts that share their data. | [observation: snippet] | eSchool News 2017-02-03; K-12 Dive |
| 2016-03 | EdWeek: TEC "brought together 44 school districts … at no charge to the districts". Harold Levy is board chair and Friedlander is CEO. | [observation: snippet] | EdWeek "Group Probes Ed-Tech Pricing, Buying" (2016/03) |
| 2015 | Founded. Friedlander leaves the NYC DOE CIO role. GovTech reports a **$750,000 Gates grant**. | [observation: snippet] | GovTech "NYC Department of Education CIO Departs…" (date `[unverified]`) |

### B. Claims, with confidence

- **TEC's public activity stops around mid-2020.** **Confidence: Medium.**
  - [observation: snippet] The newest dated TEC-authored item found is the EdSurge piece of 2020-06-16. It cites 2017
    data.
  - [observation: snippet] Searches for "Technology for Education Consortium" with 2021, 2022, 2023, 2024, 2025 or
    2026 returned nothing TEC-specific. They returned only the undated site pages.
  - [inference] Citing a 2017 survey in 2020 suggests no new benchmark dataset was produced after the 2017 platform
    cycle.
- **TEC's revenue fell sharply once the Gates money ended.** **Confidence: Medium on direction, Low on magnitude.**
  - [observation: snippet] Gates gave $750K (reported for 2015) and $500K (March 2017, 23 months).
  - [observation: snippet] The 2019 revenue was $150K.
  - [inference] $150K a year cannot fund a staffed data platform. The 990s for 2016–2018 were **not** seen, so the
    year-over-year trend is unverified.
- **No 990 after the 2019 tax year is indexed.** **Confidence: Medium, as an observation. The meaning is uncertain.**
  - Competing reads, in rough order of likelihood:
    1. **TEC stopped filing.** If it failed to file for three straight years, it would be on the IRS
       auto-revocation list. Not checked; IRS TEOS was blocked.
    2. **Its receipts fell below $50K and it now files a 990-N e-Postcard.** ProPublica does not show those.
    3. **ProPublica is lagging.** This is unlikely for a gap of five or more years.
  - A human can settle this in about 5 minutes on IRS TEOS: search EIN 81-0704220 and check Pub 78, the
    Auto-Revocation List and the 990-N records.
- **Leadership has turned over and moved to other fields.** **Confidence: Medium.**
  - [observation: snippet] TEC was CEO-led by Friedlander (2015–2018), then by Morgan-Standard (by 2020).
  - [observation: snippet] Morgan-Standard is now COO of an energy-investment firm, and Friedlander is described as
    an independent adviser.
  - [observation: snippet] Board chair Levy died in November 2018.
  - [inference] No sign of a successor operator.
- **The website is up but frozen.** **Confidence: Low.**
  - [observation: direct] The domain resolves.
  - [observation: snippet] The indexed text is undated and repeats 2017-era claims ("more than 100 districts, 5.5
    million students"). The services page uses future tense ("will offer district services").
  - The live page, its copyright year and the Wayback snapshot history were **not** viewed, because of the egress
    block.
- **No post-mortem, complaint, litigation, vendor-pushback story or funding dispute was found.** **Confidence: Medium
  that none is easy to find.** It could still exist in LinkedIn posts, conference talks or member-district minutes.

### C. Who paid the 10% (B-10)

- [observation: snippet] techedconsortium.org/services: "an annual TEC premium membership fee of **$20,000 per
  district/learning organization** for Phase 1 and 2 support services. For Phase 3 support services, TEC charges
  **10% of products procured or contracts negotiated**."
  - Phase 1 is needs assessment. Phase 2 is product discovery, including "a market overview of key product usage and
    pricing". Phase 3 is procurement support.
- [observation: snippet] The same page, as paraphrased by search: "TEC believes in transparent pricing. **Schools
  should know what products and services cost in advance** … school leaders and **board members** will agree that
  price transparency is better for schools."
- [observation: snippet] Basic membership was free to districts: "joining TEC is free of charge to all TEC schools and
  districts". EdWeek in 2016 said the same: "at no charge to the districts". Free access was tied to sharing data.
- [inference] **The payer was most likely the district.** Four things point that way:
  - the fee is quoted per district;
  - it sits in a district-facing service menu;
  - the page justifies it to schools and board members;
  - TEC is a procurement-support *consultant*, not a contract-holding GPO.

  No vendor-side fee, admin fee or GPO structure appears anywhere. **Confidence: Low–Medium.** What would settle it:
  - a signed TEC engagement letter in any district's board packet;
  - the 990 revenue line split (program-service revenue from districts vs. contributions).
- [inference] Whether *anyone* bought Phase 3 is **unknown**, and so is the take-up of the premium tier. $150K of 2019
  revenue would fit at most a handful of $20K premium members, plus some other income. That is arithmetic on a
  snippet figure, not evidence of take-up.

## Competing hypotheses considered

1. **TEC is alive and quietly serving a few districts (T7).**
   - For it: the domain resolves and the site is indexed. A small 990-N filer would not show on ProPublica.
   - Against it: no dated activity since 2020, and both founders are in other roles.
   - What would confirm it: a 990-N filed for 2023–2025, or a 2024–26 board item approving TEC services.
   - Current weight: low.
2. **TEC failed on the demand side** (districts wouldn't pay $20K or 10%, or didn't act on the benchmarks). This is
   the plan's STOP trigger.
   - For it: the free tier drew 44 → 130 districts, but revenue after the grants was only about $150K. That fits
     "they'd share for free but not pay."
   - Against it: it fits supply-side or execution causes equally well:
     - no staff or leadership after 2018;
     - dependence on LearnPlatform as the platform partner;
     - hardware mixed into the data (T2);
     - libraries without workflow (T3).
   - This desk evidence **cannot** tell these apart. **Do not record it as "cause established".**
3. **TEC was designed as a time-boxed, grant-funded research project that did its job** (the 2016–17 reports) and then
   stopped by choice.
   - For it: the output peaked in step with the grant windows, and there is no sign of a push to commercialize after
     2018.
   - If true, TEC's fate says **little about market demand**, which weakens the "base rate against us" framing.
   - Only interviews can test it.
4. **The LearnPlatform partnership, and then its 2022 acquisition by Instructure, removed TEC's platform.**
   - TEC's data platform ran on LearnPlatform (2017). Instructure bought LearnPlatform on 2022-12-15.
   - The partnership seems to have gone quiet well before that, so the acquisition is **not** a likely proximate
     cause. It does support T5 (dependence on a partner).

## Implications for the plan (inference)

- **Name a new, candidate cause row for §1.2: "philanthropy-dependent revenue; the free give-to-get tier never
  converted to paid."** This is close to T1 and T6 but not the same thing. If P0a interviews confirm it, the plan
  needs a response. The existing "buyer-paid pricing under thresholds" helps, but the real mitigation is **revealed
  preference before scale** (P0b). The plan already gates on that.
- Keep U2 (who paid) open at "leans buyer". Recalibrate lever (i) only once a primary document is found.

## Needs a human (only a person can do these, or they need unblocked network access)

1. **IRS TEOS check** for EIN 81-0704220 (about 5 minutes; apps.irs.gov/app/eos). Check:
   - Pub 78 status;
   - Auto-Revocation List, with its effective date;
   - any 990-N filings for 2020–2025.

   This alone moves several "Medium" rows above.
2. **ProPublica** (projects.propublica.org/nonprofits/organizations/810704220). Download the 2015–2019 990s and
   record, per year:
   - total revenue;
   - contributions vs. program-service revenue (evidence for who paid);
   - officers, and the Schedule O narrative.
3. **Wayback Machine** (web.archive.org/web/*/techedconsortium.org*). Check:
   - when /services/ first showed the $20K / 10% schedule;
   - when the home page stopped changing;
   - any "closing" or "transition" notice.
4. **Outreach to the founders.** Send a short, respectful note to Hal Friedlander (LinkedIn / @HalFriedlander on X)
   and to Celina Morgan-Standard (LinkedIn). Ask:
   - what stopped TEC;
   - how many districts paid for premium or Phase 3;
   - who paid the 10%;
   - whether vendors pushed back.

   Founders of a mission-driven nonprofit often answer this kind of question. **This is the highest-value single
   action.**
5. **Former member districts.**
   - The 2017 press never named its 35 core districts. Friedlander came from the NYC DOE, which makes it a likely
     early member.
   - Ask TETL / CoSN chapter contacts, or search BoardDocs for "Technology for Education Consortium" and "TEC Data
     Platform" in 2016–2019 agendas, to find 2–3 member CTOs to interview.
   - Ask them whether they used the price reports at renewal, and why they stopped.
6. **The Gates Foundation grant report**, if obtainable via the program officer. It is not public by default.

## Sources consulted (all retrieved 2026-09-24 as search-result snippets, unless marked direct)

- Direct: DNS resolution of techedconsortium.org → 35.194.34.8 (local `getent`). Egress-proxy blocks on the domains
  listed under "Method limit".
- https://techedconsortium.org/ , /about/ , /services/ , /membership/ , /press/ , /blog/ — mission, district counts,
  the $20K / 10% fee schedule, the "Schools should know what products and services cost" framing, and the press list.
- https://projects.propublica.org/nonprofits/organizations/810704220 — EIN, filings 2015–2019, 2019 revenue
  $150K / expenses $95.2K / assets $93.9K.
- https://www.gatesfoundation.org/about/committed-grants/2017/03/opp1171570 — $500K, March 2017, 23 months, San
  Diego.
- https://www.govtech.com/education/k-12/NYC-CIO-Leaves-the-Education-Department-to-Work-on-Procurement-Problems.html
  — Friedlander's departure and the $750K Gates grant (article date unverified).
- https://www.edweek.org/technology/group-probes-ed-tech-pricing-buying/2016/03 — 44 districts, no charge, Levy as
  chair.
- https://marketbrief.edweek.org/sales-marketing/k-12-schools-could-save-billions-by-sharing-ed-tech-prices-report-says/2017/04
  — the $3B report and the 20–40% spread.
- https://www.eschoolnews.com/district-management/2017/02/03/edtech-pricing-data-platform/ — platform launch, 50+
  districts, LearnPlatform.
- https://www.k12dive.com/news/digital-ed-tech-pricing-library-brings-transparency-to-procurement/435883/ — 35 core
  districts, free with data sharing.
- https://marketbrief.edweek.org/meeting-district-needs/pressure-building-for-education-companies-over-price-transparency-in-k-12-market/2017/07
  — TEC's procurement service includes peer pricing.
- https://money.cnn.com/2018/03/29/technology/apple-ipad-schools/index.html — Friedlander as CEO in March 2018.
- https://www.edsurge.com/news/2020-06-16-with-budget-cuts-looming-here-s-how-districts-will-decide-what-to-cut-or-keep
  and https://www.edsurge.com/writers/celina-morgan-standard — Morgan-Standard as founder/CEO in June 2020; cites a
  2017 survey.
- https://www.the74million.org/contributor/hal-friedlander/ — the March 2023 bio ("strategic adviser").
- https://www.zoominfo.com/p/Celina-Morgan-standard/1370127860 , https://rocketreach.co/celina-morgan-standard-email_1125737
  — current COO role; TEC listed as previous.
- https://www.zoominfo.com/p/Hal-Friedlander/1338518636 and https://www.linkedin.com/in/hal-friedlander-39052a2 —
  "Independent Consultant" and "Education + Technology Strategic Advisor".
- https://www.edweek.org/education/harold-o-levy-former-new-york-city-schools-chief-dead-at-65/2018/11 — the board
  chair's death.
- https://www.linkedin.com/company/technology-for-education-consortium-tec- — 106 followers, 3 employees listed.

## Addendum — 2026-09-24 (same research date, follow-up WebSearch pass)

Follow-up searches, using `WebSearch` rather than `WebFetch`, to chase the "Needs a human" items that
turn out to be search-crawlable rather than fetch-only. `WebFetch`/`curl` remain `EGRESS_BLOCKED` on
every domain tried (`gofundme.com` added to the block list this pass) — that's a re-confirmation of the
method limit above, not a new finding.

- **False lead, ruled out: `tec-coop.org` is a different, unrelated organization.** [observation: snippet]
  It's **The Education Cooperative (TEC)**, a Massachusetts public educational collaborative founded in
  **1968**, running the **TEC Student Data Privacy Alliance** (DPA negotiation support, not pricing) across
  1,900+ districts in 10 states since 2017. The only connection is the shared "TEC" initials. **Do not
  conflate this with Technology for Education Consortium (techedconsortium.org, EIN 81-0704220) in any
  future pass** — a plausible-looking domain match cost real time to rule out this round.
  - Incidentally relevant, not as prior art but as a base-rate data point: it's an existence proof that a
    nonprofit district-collaborative negotiation service **can** sustain multi-year, multi-state operation
    in an ed-tech-adjacent space (legal/privacy terms, not price). Weak evidence against "this kind of
    model can't work at all"; says nothing about the pricing-specific mechanism.
- **New, unresolved lead: a GoFundMe "charity" page exists for "Technology for Education Consortium
  Inc"** (`gofundme.com/charity/technology-for-education-consortium-inc`). **Confidence: very low, on
  significance.** [observation: snippet]
  - GoFundMe auto-generates a charity landing page for many registered 501(c)(3)s regardless of whether
    anyone has ever run a real fundraiser through it — so **this could be evidence of an active or past
    funding appeal, or could be nothing at all.** `WebFetch` to the page itself was `EGRESS_BLOCKED`, so
    the goal amount, amount raised, dates and campaign description (if any exist) were not seen.
  - **What would settle it (new "Needs a human" item, ranks below founder outreach in value but is
    5 minutes of work):** open the URL directly and note whether it shows a real campaign with a
    description/date, or only the generic "support this charity" template with no activity. If it shows
    a real, dated appeal, that's a second independent data point for the funding-cliff hypothesis and
    should be timestamped and cross-checked against the 2019 990.
- **IRS auto-revocation status and BoardDocs member-district names: still not resolved by search.**
  General IRS auto-revocation/990-N policy pages surfaced, but nothing specific to EIN 81-0704220's
  current status. No BoardDocs board-minute results named specific TEC member districts. These remain
  genuinely fetch-only or account-only tasks — items 1 and 5 of "Needs a human" above still stand as
  written.
