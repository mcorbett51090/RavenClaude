# FORGE G4a — Critic Brief: Correlated-Error Hunt (Pilot.BM)

**Critic:** G4a (did not author either plan). **Date:** 2026-06-10.
**Mandate:** find errors **both** plans share (correlated / shared-anchoring), attack the premise, emit a probability×impact risk matrix. No third plan.

**Headline finding (read first):** Both plans treat "close 10–25 paid local listings" as a *build/sequencing* problem (Stripe wiring, when-to-pitch, GSC proof) when it is a **founder-market-fit** problem. Neither plan ever asks whether *this owner* — a US-based financial analyst with Bermuda **regulatory/professional** ties, not a Bermuda-resident with retail-SMB relationships — will actually do a grinding, recurring, in-person local sales job. The load-bearing revenue line (60–75% of the model) sits on an unexamined assumption about the human, and both plans inherited the assumption identically from the research's revenue table. That is the expensive shared blind spot this gate exists to catch.

---

## (a) Correlated errors both plans share

### CE-1 — The directory-sales motion is treated as a wiring problem, not a founder-fit problem ★ most important
**Both plans** lavish detail on *how* to bill (Stripe Checkout/Billing, webhook → tier flip, claim-and-upgrade email) and *when* to pitch (Plan B's GSC-traction gate, Plan A's "close 3 before launch"). **Neither** interrogates *who closes the sale and whether they can/will*. Selling a $30–50/mo listing to a Bermuda hair salon, dive operator, or restaurant is repeated relationship-based local B2B sales — phone calls, walk-ins, follow-ups, churn-chasing, renewal pitches — **forever**, not once. The research even flagged "Requires active sales" and both plans nodded at it (Plan A risk #1, Plan B blocker #3) then **moved on as if naming it neutralizes it**. It doesn't.
- **Why it's wrong:** the owner profile in the prompt (financial analyst, US-based, ties via *regulatory* work) is close to the *opposite* of the profile that closes retail-SMB listings (Bermuda-resident, embedded in the local merchant community, comfortable with cold in-person sales). FMF is unproven and both plans assume it.
- **Infects:** Plan A's entire critical-path framing ("billing is the longest pole" — false; *the human sales motion* is the longest pole and isn't on the DAG); Plan B's whole monetization-sequencing section and revenue ramp table (every directory-revenue cell assumes a close-rate nobody has tested).
- **Probe outcome:** This is not de-risked by "view/click proof of value" (Plan A) — proof-of-value improves *renewal*, but you must *close the first sale in person* to ever show a renewal. Both confuse retention mechanics with acquisition.

### CE-2 — "One product / 3 audiences" is accepted from scope; it is plausibly **three jobs** competing for one owner's hours
**Both plans** accept the 3-audience frame as a given (it's locked in scope.md) and treat the directory as the unifying "spine" that makes it one product. But the *spine* is a shared **data table**, not a shared **business motion**. The three audiences require three fundamentally different ongoing jobs: (1) Visitors = SEO/affiliate content marketing (write evergreen, chase rankings); (2) the directory = recurring local **field sales** (CE-1); (3) Movers = legally-sensitive **compliance editorial** that must be re-verified forever. A shared Postgres row does not make these one job — it makes one website serving three businesses that each demand a different skill and a different weekly cadence from **the same solo owner**.
- **Why it's wrong:** the plans reason "shared spine ⇒ one product ⇒ one owner can run it." The spine is shared at the *storage* layer and divergent at the *labor* layer, which is the layer that's scarce.
- **Infects:** the "launch all 3 at once" decision both plans honor without challenge; both content-cadence models, which sum hours but don't confront that the hours are **non-fungible** (sales charisma ≠ SEO writing ≠ regulatory fact-checking).
- **Note:** Plan B's depth-asymmetry (Visitors deep, others skeleton) is a *partial* mitigation but still launches all three motions; it reduces content hours, not the three-distinct-skills problem.

### CE-3 — "High-end" is treated as a design-system line item; it is an unfunded *perpetual* mandate (photography especially)
**Both plans** assert the "high-end / design-forward" positioning is the white-space differentiator (Plan A: "invest here," a token/type-scale design system; Plan B: "on-brand typography, photography"). **Neither budgets what high-end actually costs on an ongoing basis** — most acutely **professional Bermuda photography**: rights-cleared, location-shot, seasonally refreshed imagery is the single biggest visual driver of "premium feel," and it is expensive, recurring, and on-island (hard to do from the US). Plan A's run-cost (~$1.5–2.5k/yr) is infra only — **zero** for design labor or photography. Plan B's stack table costs infra only too. "High-end" is named as free differentiation by both.
- **Why it's wrong:** premium feel is 80% imagery + editorial polish + ongoing design iteration, ~20% framework. Astro buys you *fast*, not *beautiful*. Both plans conflate Core-Web-Vitals performance with luxury aesthetic.
- **Infects:** the core differentiation thesis of both plans (the "white space" only exists if execution is genuinely high-end); the cost model (an unbudgeted $3–8k/yr photo+design line flips the already-marginal break-even).

### CE-4 — Content freshness is priced as a treadmill but the *regulated* freshness liability is under-priced by both
**Both plans** do model content maintenance (Plan A: freshness CI, `verified_on`, quarterly re-verification; Plan B: explicit quarterly cycle, 2 hrs/quarter for gov.bm audits). Credit where due — this is the *least* correlated of the errors. **But both under-price the *regulated* slice specifically:** Bermuda immigration/fees/tax changed as recently as Oct 30 2025 (WFB closed Feb 2025), and the Mover tools (comp calculator, pathway tree, Assessment-Number) encode *live legal/financial figures* whose staleness is not a quality defect but a **liability event**. Plan B budgets "2 hrs/quarter" to audit *all* Mover pages against policy change — that is implausibly light for a decision-tree + a salary calculator + a duty-trap explainer that each must be provably current. Plan A is better (quarterly tool re-verification, build-gate) but still treats it as owner-discipline, not as a structural cost that competes with the sales and writing hours.
- **Why it's wrong:** both assume freshness is *cheap because the owner does it*; "owner-does-it" is exactly the scarce-hours resource CE-2 already over-subscribed. Re-verification is not free; it's the third claim on the same overloaded calendar.
- **Infects:** the legal-exposure risk both plans acknowledge but assign to "owner owns the cadence"; the break-even math (which counts owner hours as $0).

### CE-5 — Static-first is correct for content but both under-weight the app-shaped claim/billing/account surface
**Both plans** chose Astro static-first (correctly, for SEO/cost). But the directory's **claim-your-listing → upgrade → recurring billing → tier-state → past-due/dunning → owner self-serve edits** is a genuine **app** with auth, sessions, webhook-driven state, and a logged-in editing surface. Plan A acknowledges "one stateful island" + Node SSR endpoints but still frames it as small; Plan B leans on Directus's admin GUI but then needs a *public* claim/upgrade flow Directus doesn't give you out of the box (its admin is for the *owner*, not for 25 business owners self-serving their own listings + payment). **Both underweight that "let a business claim, pay for, and edit their own listing" is the most complex thing in the build** and it's bolted onto a static site as an afterthought "island."
- **Why it's wrong:** the interactive Mover tools are genuinely static (client-side rulesets — both got this right). But the *paid claim/account* flow is not, and it's the load-bearing revenue surface, so the complexity lands exactly where failure is most expensive.
- **Infects:** Plan A's "billing is one deployable, ~$5/mo Fly machine" cost/effort estimate; Plan B's "Directus = owner manages listings, near-zero ops" claim (Directus doesn't solve *third-party* self-serve claim+pay).

### CE-6 — Both inherited the research's revenue table as a *forecast* when it is a *conditional ceiling*, and "pays for itself" silently redefined
**Both plans** treat the research's "owner-writes → +$3.2k Y1 / +$10.5k Y2" as the plan's target outcome. But that figure is **doubly conditional**: it assumes (i) the directory sells (CE-1, untested) AND (ii) owner content labor is counted at **$0**. Plan B is admirably honest in one line ("profitable only if the owner values their time below ~$20/hr"), then proceeds as if that caveat is cost-free. **Neither plan confronts that "pays for itself" has quietly been redefined** from "generates cash surplus" to "doesn't bleed cash *while consuming 12–16 hrs/wk of unpaid expert labor indefinitely.*" At even $50/hr (a financial analyst's opportunity cost), 12 hrs/wk = ~$31k/yr of foregone value — the project is **deeply** cash-and-opportunity negative under its own success scenario.
- **Why it's wrong:** the success signal ("pays for its own hosting + content costs") was met by *redefining content cost to zero*. That's circular: the only path to break-even is to not count the largest cost.
- **Infects:** the success criterion in scope.md itself, and every "break-even" claim in both plans. The owner's stated bar ("must pay for itself") is arguably **not met** by either plan once labor is honestly priced — they meet a weaker bar and don't flag the swap loudly enough.

---

## (b) Premise verdict: **REFRAME** (don't build as-is; don't kill)

**Reasoning.** The idea is not dead — the research found a genuine white space (no high-end, logistically-complete, opinionated Bermuda guide exists) and a genuinely under-served high-intent hook (Visitors / "getting around" / no rental cars). That asset is real and worth capturing. But the **as-specified shape — launch all 3 audiences + a load-bearing local-sales directory + perpetual regulated editorial, run solo by a US-based analyst — stacks three unproven, non-fungible labor bets on top of each other and calls their sum "one product that pays for itself."** Both plans optimize the *execution* of that shape brilliantly while leaving its *premise* untested.

**The sharper framing (recommend to owner):**
1. **Nail Visitors-only first as a focused affiliate + SEO content site.** It's the volume engine, the margin engine, requires *zero local sales* (affiliates are passive after setup), and the "Getting Around" page is the proven wedge. This validates the riskiest assumption (can this owner produce high-end content that ranks?) **without** betting on the unproven local-sales motion or the regulated-editorial liability.
2. **Treat the directory as a Phase-2 *test*, not a Phase-0 spine** — explicitly to disprove CE-1 before building billing infra around it: hand-sell **3 paid listings in person** as a pure sales experiment *before* writing one line of Stripe webhook code. If the owner can't close 3, the load-bearing stream is fiction and no architecture saves it. (Both plans say "close 3" but as a *launch gate after the build*; flip it to a *pre-build kill-gate*.)
3. **Defer Movers tools until Visitors traffic proves the audience** — the regulated-editorial liability (CE-4) and the comp/pathway tools are the highest-consequence, lowest-validated work; don't carry that risk on day one.
4. **Re-price "high-end"** with an actual photography + design line, or **explicitly downgrade the promise** to "clean, fast, opinionated" (achievable free) rather than "high-end" (not free). Pick one honestly.

This reframe keeps the real asset, kills the correlated bets, and turns the single biggest unknown (CE-1 founder-sales-fit) into a cheap pre-build experiment instead of a post-build discovery.

**Why not "build as-is":** it commits design+billing+regulated-tool engineering before the load-bearing revenue assumption (CE-1) or the differentiation premise (CE-3) is tested. **Why not "don't build":** the Visitors wedge is a real, low-cost, separable bet that's worth making.

---

## (c) Risk matrix (probability × impact)

| # | Risk | Prob | Impact | Plan element it infects |
|---|---|---|---|---|
| R1 | Owner lacks founder-market-fit / willingness for recurring in-person local listing sales → load-bearing revenue never materializes (CE-1) | **H** | **H** | Both: entire directory-revenue model; Plan A critical path; Plan B revenue ramp |
| R2 | "Pays for itself" is only true by counting owner labor at $0; honestly priced, project is opportunity-cost-negative (CE-6) | **H** | **H** | scope.md success signal; both break-even claims |
| R3 | Three non-fungible labor jobs (sales / SEO writing / regulated editorial) overload one solo owner → burnout → thin content → HCU penalty (CE-2) | **H** | **H** | "launch all 3" decision; both cadence models |
| R4 | "High-end" unfunded (no photography/design budget) → differentiation promise unmet → white space not actually captured (CE-3) | **M–H** | **H** | Both differentiation thesis + cost models |
| R5 | Paid claim/upgrade/account flow is app-shaped, underestimated on a static-first base → billing surface late/buggy (CE-5) | **M** | **H** | Plan A "$5/mo Fly machine"; Plan B "Directus = near-zero ops" |
| R6 | Stale regulated figure on a Mover tool (tax/permit/duty) → liability event; quarterly 2-hr audit too light (CE-4) | **M** | **H** | Both Mover tools; legal-exposure risk |
| R7 | Visitors SEO ("Getting Around" page) doesn't rank under Google HCU → no traffic → directory pitch has no proof → cascade failure | **M** | **H** | Both: traffic→directory dependency (Plan B makes it explicit) |
| R8 | `.bm` domain ineligible (needs Bermuda entity) → branding/identity scramble at launch | **M** | **L–M** | Both Phase-0 gate (both already flag + .com fallback — well-handled) |
| R9 | Concierge tier over-invested as base-case (15-yr incumbent, 12–24mo cycle) | **L** | **M** | Plan A §3.3 keeps it upside (good); Plan B keeps it Phase 2+ (good) — low residual |
| R10 | Movers inflow volume too small to justify the Movers build at all (`[unverified]`) | **M** | **M** | Both Movers tier sizing; both flagged it as a settling step (handled) |

**Reading:** R1–R4 are the cluster that should drive the decision — all High/High, all **correlated** across both plans, all rooted in the same shared anchor (the research revenue table + the locked 3-audience scope accepted without interrogating the *owner-labor* premise underneath them). The reframe in (b) is designed to convert R1–R4 from post-build discoveries into pre-build, cheap-to-run tests.
