This is a concept-document revision task—pure analytical writing work. No repo investigation is needed; the weaknesses are well-specified and the document is self-contained. Let me work through each major and minor weakness and produce the revised v5.

The four major weaknesses cut deep and interlock:
1. Buyer/trigger collision (narrowed buyer has least acute pain)
2. Income-floor math is circular (assumes steady-state in a build year)
3. The reconciliation engine is the hardest thing in fintech, budgeted as a 4-month solo build with no basis
4. The subscription has no standalone payers left

These force a genuine reshaping, not caveats. Here is the revised document.

---

# Closebook + Leash — Concept Document v5

*An AI workbench that makes a finance team's own qualified reviewer dramatically faster at the recurring, deadline-bound parts of close and cash forecasting — the reviewer still owns and signs every number, the AI does the legwork on a visible leash, and every figure carries a "show your work" trail you can hand a lender, board, or auditor. Sold as a hands-on consulting service by a financial-analyst founder, with no pretense of software-style scale. The honest ceiling is one person's calendar, and v5 stops pretending otherwise.*

---

## 0. What changed from v4 (and why)

v4 made the liability posture honest (the buyer's own reviewer signs; no supplied CPA) and the wedge sharp (cross-system, signed, governed). But a round-4 review found that **four of v4's load-bearing beams were resting on each other rather than on the ground.** Each fix below removes an internal contradiction rather than adding a hedge.

1. **The narrowed buyer and the "forced trigger" were mutually exclusive — v5 re-picks the trigger to match the buyer it actually serves.** v4 kept the old "fundraise/covenant/SOC deadline or the deal dies" trigger language, but that acute, deal-at-risk pain lives at the *under-reviewed* firm v4 deliberately excluded. A firm that already has a controller signing a cross-system close every month already survives those deadlines — that *is* the controller's job. So v4 was selling a painkiller's price tag against a vitamin's pain. **v5 replaces the "deal-at-risk" trigger with the trigger that actually bites the has-a-reviewer buyer: reviewer-capacity strain** — the controller is the bottleneck, close eats 5–10 days they don't have, a new system or a board cadence just got added, and the choice is "hire a $130k+ senior accountant, buy more software the controller still has to drive, or get the existing reviewer's throughput up." v5 sells against the *cost of the next finance hire*, not against a collapsing deal. This is a real budget with a real comparison, and it fits the buyer v4 chose. (Section 3.)
2. **The income-floor math was computed for a steady-state year and silently applied to the build year — v5 reconciles them and funds the runway honestly.** v4's "$140–200k margin off ~40 weeks" assumed ~52 weeks of full-price delivery while the roadmap spent Months 0–6 building an engine and selling one at-cost deal. Year 1 *is* the build year; under v4's own schedule it clears ~$40–70k, far under the $160–200k floor. **v5 stops treating Year 1 as a normal income year.** It is explicitly a **part-time-build / part-time-income runway**, funded by Matt keeping partial analyst income (or a defined savings draw) while the engine is built *manually, in delivery, on real customer books* — not in an unpaid solo sprint. The steady-state floor math now applies to **Year 2**, which is where it belongs. (Section 7 + 8.)
3. **The reconciliation engine — now the entire moat — was budgeted as a 4-month solo build of the hardest thing in enterprise finance software, with no basis. v5 rejects the "build a general engine" framing entirely.** A deterministic cross-system reconciliation engine that generalizes across every SMB's idiosyncratic QuickBooks/Bill.com/Gusto exports is the decade-long, large-team problem BlackLine and FloQast still work on; an LLM "just writing the join logic" over unseen messy exports is exactly where determinism breaks. **v5 does not build a general engine. It builds per-engagement, customer-specific reconciliation scripts by hand (Matt + the agent as a coding assistant), reviewed and re-run by the buyer's reviewer — bespoke, not general.** The reusable asset is a *library of patterns and scaffolds*, not a product that auto-reconciles a stranger's books. This is slower and doesn't scale like software — and that is the honest truth of the business, now stated as the plan rather than discovered as a failure. (Sections 3a, 4c, 9 Risk #3.)
4. **The evidence-pack subscription had no standalone payers left — v5 stops calling it a scale lever and tells the truth: this is a capacity-bound consulting business with no software leverage today.** v4's churn fix bundled the pack free with active retainers and restricted standalone sales to already-active accounts — leaving the paying set approximately empty. v5 demotes the subscription to **a retention/packaging feature of the retainer, not a revenue line**, and removes the claim that anything in the model scales past Matt's calendar. The spin-out remains a *gated, low-probability* future option, not a plan. (Section 7 + 9 Risk #10.)

(Carried forward: assets are reasoning playbooks, not a close engine; deterministic compute is the real differentiator; the tribunal has only judged marketplace-dev decisions and must be wired to finance; the insurance trigger is unverified-secondary and demoted; "Evidence Pack," not "Certificate"; the single-signer rule = the buyer's own reviewer, never Matt, never a supplied CPA.)

---

## 1. One-line pitch

**An AI assistant that drafts the recurring, deadline-bound parts of your close and 13-week cash forecast from your actuals across all your systems and shows its work line-by-line — so your own overloaded controller checks and signs in hours instead of days, getting more throughput out of the reviewer you already have instead of hiring the next one.**

> **The honest qualifier leads, and it names who signs:** the AI drafts; **the buyer's own qualified reviewer signs.** This is never "CFO-grade output" on its own — it is *the buyer's reviewer producing their normal signed output faster*, because they review a fully-sourced, deterministically-computed draft instead of assembling it by hand. **That signer is never Matt** (a financial analyst, not a CPA) **and is never a CPA we supply.** If a company has no such reviewer, it is not a customer we can serve today. This single-signer rule is the entire liability posture, so it leads.
>
> **And the honest ceiling leads too:** this is a hands-on consulting service. Its capacity is one person's calendar. v5 does not promise software-style scale, because the load-bearing asset (cross-system reconciliation) is built bespoke per customer, not as a general engine. See Section 7.

## 2. Why this shape (honoring the judges)

All three internal judges scored the two concrete-deliverable plays highest and proposed the same merge: lead with the finance deliverable (a pain the buyer already pays for), embed governance as the trust mechanism that deliverable already needs.

- **Verdict's** gateway-API model is dev-facing and folds in only as a possible, low-probability **Phase-2 fork** (Section 7), not the lead.
- **Aegis's** evidence-pack export grafts in as the governance layer's enterprise face — *the human-behavior trail, not a binder documenting our own framework.*
- **Forge** is the **internal delivery method** (`/wrap` → `contribute-finding` → FORGE), not a sellable thing. Verified built: `commands/wrap.md`, the contribution skills, `skills/forge-pipeline`.

> **Why this pairing leads over the other 22 plugins — an honest answer, not "the judges said so."** The internal-panel score is a *design* signal, not a *market* signal. The market reasons this pairing is the wedge: (1) it sits on **Matt's only native-habitat domain** — he *is* a financial analyst, not a Salesforce admin or a freight broker, so finance is the one domain where founder credibility is real, not borrowed; (2) close + cash is a **calendar-forced, recurring, already-budgeted** chore (Section 3); (3) the rare governance assets need a *high-stakes, human-signed, auditable* deliverable to matter, and finance is the cleanest such deliverable in the catalog. **One service, one buyer, one substrate.**

## 3. The buyer and the purchase trigger

**The buyer is precisely defined: a company that already employs a qualified finance reviewer** — a controller, accounting manager, or fractional CFO who today signs the close — **and whose books span more than one system** (an accounting suite plus a separate billing/payroll/expense tool), so the close is a cross-system assembly job, not a one-tool button. Practically, the **~50–150-person company where a controller exists but is the bottleneck**, not the 20-person founder-does-finance shop.

**Why we deliberately exclude the no-reviewer company:** the entire risk mitigation is "deterministic compute + a *qualified human signs*." If no qualified human exists in-house, the only way to supply one is to contract a CPA to sign work they didn't produce — which no competent CPA accepts for a marginal fee. v5 refuses to build on that dependency. The no-reviewer market reopens only if the deterministic engine ever becomes defensible enough to stand without a same-firm signer — a future bet, not a launch claim.

### 3a (trigger). The trigger that actually bites THIS buyer — reviewer-capacity strain, not a deal-at-risk deadline

**v5's most important correction.** Earlier versions inherited a "forced event" trigger — fundraise diligence, covenant loan, SOC window, board demanding a clean 13-week cash view *they can't produce*. But that acute, "we cannot produce this and a deal is at risk" pain lives at the **under-reviewed** firm — the one without enough qualified reviewer capacity. v5 *excluded* that firm. A 50–150-person company that already has a controller signing a cross-system close every month **already clears those deadlines today** — surviving them is literally the controller's job, and they are doing it. Selling that buyer a $30k+ engagement against a deadline they already beat is selling a vitamin at a painkiller's price. It won't convert.

**So v5 picks the trigger that is genuinely acute for the buyer it chose: the reviewer is the bottleneck, and the alternative is spending money to relieve them.** Concretely, the wallet opens when:

- **Close is eating 5–10 days of the controller's month** and the company is growing, so the squeeze is getting worse, not better.
- **A new system was just added** (new billing platform, an acquisition, a new payroll provider) and the cross-system stitch the controller does by hand just got harder.
- **The board or a lender moved to a tighter cadence** (monthly cash reporting, faster close) — not a one-time deal, an *ongoing* expectation the current process can't sustain without the controller working nights.
- **The realistic next step is otherwise to hire** — a $110–160k fully-loaded senior accountant, or another tool the controller still has to drive. v5 is sold explicitly as **the cheaper, faster alternative to that hire**: same throughput gain, fraction of the cost, no headcount, and the existing trusted reviewer keeps the signature.

> **This is the honest demand thesis, and it matches the buyer:** the pain is "our existing reviewer is maxed out and the company is asking them for more" — a recurring, budgeted, comparison-against-a-hire decision, not a one-time crisis. It converts at the price of *part of an FTE*, which is exactly the engagement's price band (Section 7). We are not promising to rescue a collapsing close; we are making a known-good close cost less reviewer time than it does today, and pricing against the salary line the buyer would otherwise spend.

**Structural, permanent pain (no market education needed):** month-end close burns 5–10 days every cycle, much of it hand-stitching systems; the cross-system 13-week cash view is slow to rebuild each time; SOC/audit prep eats a quarter. These recur on the calendar regardless of any one deal.

**The governance trigger is secondary until verified.** v1 leaned on a cyber-insurance / questionnaire trigger (ISO GenAI E&O exclusions Jan 2026), sourced only to secondary aggregators. **Until re-verified against the primary ISO filing and actual carrier language, the governance trigger is a "closes-faster nice-to-have," not a co-equal pillar.** The business case stands on reviewer-capacity strain alone.

> **Quarantined statistics:** the upstream "34%-more-confident-when-wrong" and "47%/22% monitoring" figures are unverified secondary-aggregator numbers and must **never** appear in buyer-facing material without primary-source verification.

### 3b. Why "make your existing reviewer faster" beats the reviewer's own in-tool AI

The buyer's controller already owns the GL and increasingly has **Excel Copilot or their accounting suite's native AI** drafting in-tool. So why pay Matt? **The value is not "draft a number faster in one tool" — it's "assemble, source, and make defensible a package that spans tools and ends in a signed artifact a third party will accept."** An in-tool assistant helps inside the one system its data sits in. It does **not**:

1. **Stitch across systems.** The painful part of a real close is reconciling the accounting suite against billing, payroll, and expense — different schemas, different cutoffs. v5 builds per-customer reconciliation scripts for exactly that seam (4c). An Excel-native agent presupposes the consolidated workbook already exists — which *is* the work.
2. **Produce a third-party-facing evidence trail.** A lender/board/auditor wants "show me how this number was built and who controlled the AI that touched it." In-tool AI produces a number, not a lineage card + a pre-action Stop + a decision log.
3. **Carry a governance posture the auditor asks about.** "What is your AI allowed to do, and what did you block?" — the leash answers this; a drafting assistant cannot.

> **The honest hedge:** if Microsoft or an accounting suite ships **cross-system consolidation + an AI-action audit trail**, this wedge narrows fast. So the offering is **consulting-first** (Section 7), renting a window, not claiming a fortress.

## 4. The offering — what is real day one vs. what gets built

This separates **the supervised analyst service that works today** (LLM reasoning over GL exports, the buyer's reviewer signs) from **the engineering that makes it faster and more defensible** — which in v5 is *built bespoke inside engagements*, not as a pre-built product.

### 4a. Day-one deliverables (drafted by the workbench; the buyer's reviewer signs)

The buyer provides exports (CSV/JSON) from each system. With Matt-plus-the-agents producing the draft and **the buyer's own reviewer signing**, they receive:

1. **Month-end close package draft** — variance commentary and board-pack exhibits, drafted from their actuals across systems. The agent reasons from the verified `month-end-close`, `variance-commentary`, `board-pack-composition` playbooks; the **numbers are computed by deterministic scripts the agent writes and the reviewer re-runs** (4c), not free-typed by the LLM.
2. **13-week direct-method cash forecast draft** — covenant-headroom view with action triggers.
3. **Driver-based operating forecast** and, in a live transaction, a **DCF/valuation view**.
4. **SOC/audit-prep control walkthrough** drafted to satisfy an auditor on review.
5. **The "show your work" lineage card under every figure** — source ledger rows → transformation applied → who signed → timestamp. *(Day one this is a **human-authored source trail**: the reviewer's recon workpaper rendered as a card. It does not yet include a tribunal verdict; see 4b.)*

### 4b. The Leash layer — scoped honestly

The rare governance assets are real (verified: `guard-destructive.sh`, `guard-web-access.sh`, `guard-recursive-spawn.sh`, the `thing-decide.py` tribunal, `comfort-posture.yaml`, the `/ragnarok` kill switch). **But the tribunal has only ever adjudicated marketplace-development decisions, and no wiring connects a finance action to a Sága record.** So:

| Leash feature | Status today | What's needed |
|---|---|---|
| **The Stop** — block an AI agent from an irreversible/high-stakes action (restate a closed period, write to a production ledger, touch credentials, move money) with a plain-English reason | **Real** — guard hooks fire on tool calls now | Define finance-specific "high-stakes action" patterns (e.g. any write to a locked-period file) |
| **The leash dial** (Strict / Balanced / Exploratory) | **Real** — `comfort-posture.yaml` + `set-posture` | Map the three levels to finance-relevant tool scopes |
| **Kill switch** (`/ragnarok`) | **Real** | None |
| **Gated AI judgment with a logged verdict under a finance number** | **Aspirational** — the tribunal works but has never judged a finance call, and the lineage card isn't wired to it | Route a defined class of finance judgment calls through `thing-decide.py`, link the Sága record to the figure's lineage card. *Until this ships, the lineage card sells only the human-authored source trail — itself real and valuable.* |
| **Evidence pack / questionnaire crosswalk** (Aegis-grafted) | Buildable from the decision log | Map to one real insurer + one vendor-security (SIG/CAIQ-style) questionnaire + NIST AI RMF / ISO 42001 clauses |

### 4c. The middle layer — bespoke, customer-specific reconciliation scripts (NOT a general engine)

**This is v5's sharpest reframing, and it directly answers the "you can't build BlackLine solo in 4 months" objection.** The gap between "an LLM that has read good accounting prose" and "numbers a reviewer will sign" is a deterministic calculation/reconciliation layer. v4 called this "the product" and budgeted a *general* cross-system engine as a 4-month solo build. **That is the wrong thing to build and v5 does not build it:**

- A general engine that auto-reconciles *any* SMB's idiosyncratic QuickBooks/Bill.com/Gusto exports — solving cross-system identity resolution with no shared key, per-system cutoff/timing, currency, partial postings, and per-customer schema variation — is a multi-year, large-team problem (BlackLine, FloQast). An LLM "just writing the join logic" over an unseen customer's messy exports is *exactly* where determinism breaks: the agent guesses the join key, the mapping, the timing rule. **One person does not build that in four months, and v5 stops claiming it.**

- **What v5 actually builds is bespoke, per-engagement.** For each customer, Matt + the agent (as a coding assistant) hand-build reconciliation/variance/cash-roll scripts **tailored to that customer's specific systems and chart of accounts**, which **the buyer's reviewer reads and re-runs**. The determinism comes from the script being fixed, reviewed, and reproducible *for that customer* — not from a general engine that generalizes across strangers' books. The cross-system-identity problem is solved **once per customer, by a human deciding the join rules with the agent's help**, not auto-solved at runtime.

- **The reusable asset is a pattern library, not a product.** What `/wrap` deposits back into the marketplace are **scaffolds and recurring patterns** — common COA shapes, typical QuickBooks↔billing tie-out structures, JE-pattern templates — that make the *next* bespoke build faster to assemble. They do **not** make the next customer's reconciliation automatic; a human still confirms the mapping. v5 is explicit (Section 7): **Company A's mapping does not make Company B's reconciliation free; it makes Matt's next build modestly faster to hand-assemble.** That is a real, compounding efficiency — but it is consulting leverage, not software leverage.

- This is what makes a number defensible — **reproducible by the buyer's reviewer**, not generated. It directly answers the existential liability (Risk #1): LLM-generated numbers are the danger; **a fixed, reviewer-re-run script plus the reviewer's signature is the mitigation.**

> **Backed by ten verified finance knowledge files** (ASC 718/805/740, WACC sourcing, accrual/cutoff discipline, FP&A models, variance triage) — so the *reasoning* draws on canon. The *arithmetic* is deterministic, hand-built, customer-specific code. Reasoning from canon ≠ computing the number, and bespoke ≠ general — v5 keeps all three separate on purpose.

## 5. Why RavenClaude uniquely — mapping to verified assets

| Capability | Verified asset (checked this session) | Honest status |
|---|---|---|
| Seven finance specialists | `plugins/finance/agents/` (controller, treasury-analyst, fpa-analyst, financial-modeler, valuation-analyst, board-pack-composer, audit-prep-specialist) | Reasoning agents; controller's `tools:` line grants Read, Edit, Write, Grep, Glob, Bash, WebFetch, WebSearch — data work in practice is `Bash`/`Grep`/`Glob` over GL CSV/JSON exports |
| Nine finance playbooks | `plugins/finance/skills/` | Reference prose, not executable engines |
| Accounting canon | `plugins/finance/knowledge/` — 10 files | Real; informs reasoning, not arithmetic |
| Lineage card (source trail) | Reviewer recon workpaper format | Real day one |
| Lineage card (gated-AI-action verdict) | `thing-decide.py` + Sága log | **Not yet wired to finance — build milestone** |
| Bespoke reconciliation scripts | Hand-built per engagement (agent-assisted) | **Built in delivery, not pre-existing; the pattern library compounds, the engine does not generalize** |
| The Stop | `guard-destructive.sh` + 2 siblings | Real; needs finance action patterns |
| Leash dial / kill switch | `comfort-posture.yaml`, `/ragnarok` | Real |
| Embedded dashboard | data-platform skills (`jwt-embed-issuance`, `embed-csp-and-iframe-sandboxing`, RLS) | **Guidance skills, not a shipped isolation layer** |
| Compounding delivery (internal) | `commands/wrap.md` + contribution skills + `forge-pipeline` | Real |

**The moat — stated without overclaim, and honest about how much of it is "Matt."** v4 named a three-part moat; a fair reading is that **only one part is a transferable, buildable asset, and the other two are Matt himself:**

- **Transferable / buildable:** the **bespoke-but-pattern-backed cross-system reconciliation discipline + the lineage/decision-log governance trail**. The pattern library compounds across engagements; the governance assets harden on real finance data. This is the part that could outlive any single engagement — but it is *partial* (each customer still needs a human-confirmed mapping) and it is the part still being built.
- **Not transferable — it is Matt:** **senior-judgment quality** (leaves when he's at capacity or stops) and **native-habitat founder credibility** (a financial analyst selling to finance operators). These are real competitive advantages *for a solo consulting business* and the honest reason this beats a generic dev doing the same — but they are **single-person dependencies, not assets that scale or sell.** v5 names them as what they are rather than dressing two restatements of "Matt is good" as a moat.

> **The honest summary:** the durable, buildable edge is the **integrated cross-system lineage + governance trail**; the rest of the advantage is founder-fit, which is exactly why this is a **consulting service whose ceiling is Matt's calendar** (Section 7), not a defensible software moat. We rent a window with a credible founder; we don't claim a fortress.

**On the reviewer's own in-tool AI** — see 3b. The durable distinctions are cross-system assembly, a third-party-facing signed package + lineage + decision log, and a pre-action Stop + governance posture the auditor asks about — none of which an in-tool drafting assistant produces.

## 6. Simplicity packaging — the honest first run

v1 promised a non-developer connects QuickBooks and sees their variance in 5 minutes. **Impossible today** (no connector, mapping is hours-to-days, the reconciliation scripts are hand-built per customer). v5 tells the truth and still lands an aha — and **leads the demo with finance value, not with a fear the buyer doesn't yet have.**

**The demo that works *today* — and v5 is honest that a canned sample doesn't prove the wedge.** On a **provided sample multi-system GL set**, the prospect watches the workbench produce a **variance-explained close summary with a live lineage card under each figure** — click a number, see the source rows *from each system* and the script that computed and reconciled it. **The skeptical controller's correct objection is "run it on MY exports," and v5 answers it honestly rather than dodging:** the sample demo proves the *output shape and the leash*, not that we've already reconciled their books — that takes a paid mapping working-session (hours-to-days). **So the demo is explicitly framed as "here is the deliverable and the control surface; here is what the first working-session with your books produces, and here is its honest timeline" — not as "this runs on your data in minutes."** Then, as the trust close, ask the AI to do something reckless ("restate last quarter's locked close") and watch the Stop block it in plain English. Order matters: lead with the deliverable the buyer came for; present the Stop as *how we keep that deliverable safe.*

**The aha for *their* books is staged honestly — and the early customer is a paid co-development partner, not a week-one-product buyer:**

| Phase | What the buyer is promised | Why this is truthful |
|---|---|---|
| **Design-partner phase (Year 1, while reconciliation patterns are being hand-built on real books)** | "We build your first close *with you* over **4–6 weeks**. You're a co-development partner at a reduced rate; your reconciliation scripts are built bespoke for your systems, and you get the reusable result and a continuing discount." | The reusable patterns don't exist yet — they're being built *in* these engagements (4c). The first customers are honestly the test bed and priced accordingly (Section 7). No "signed draft in week one" claim. |
| **Later phase (Year 2+, pattern library + scripts mature for common stacks)** | "After a one-time guided **mapping working-session** (Matt + your reviewer walk the chart of accounts once, the agent drafts the mapping from our pattern library, your reviewer corrects it), your **actual** first close or 13-week-cash draft is on screen within the engagement's first **week or two** *for a common system stack* — longer if your stack is unusual — every figure linked to its source rows and computing script, with a green Leash status light and a dated evidence pack." | The pattern library now accelerates a common stack; mapping-then-draft is the remaining per-customer cost. "Week or two" honestly reflects that this is for *common* stacks; unusual ones are still hand-built. |

**What the buyer never sees:** an agent, a tribunal, a YAML file, a JSON log, or the word "governance." It surfaces only as three readable things: **"What our AI is allowed to do," "What we blocked," "How every number traces back."** (Honors the dashboards-over-slash-commands and plain-language rules.)

## 7. Pricing & business model — capacity-bound consulting, with Year 1 funded as a runway and no false scale lever

**Consulting-first, and v5 stops gesturing at scale it doesn't have.** Matt's validated capacity is 4–6 builds/year solo. **The honest ceiling of this business is one person's ~40 deliverable weeks. There is no software-style leverage in the model today** — the load-bearing asset (cross-system reconciliation) is hand-built per customer (4c), and the one previously-claimed uncapped line (the evidence-pack subscription) has no standalone payers (below). v5 prices and plans inside that truth.

**The cost truth (internal, not a line item):** the dominant, *fixed, front-loaded* cost per engagement is **cross-system mapping + messy-data cleanup + hand-building that customer's reconciliation scripts**, roughly constant regardless of how many deliverables ride on top. v5 packages it buyer-facing inside a single fixed-price engagement that always ends in a signed deliverable, and prices that engagement to **clear margin standalone**:

| Buyer-facing package | Price | What the buyer sees | (Internal: mapping + script-build cost absorbed) |
|---|---|---|---|
| **"First Close"** — onboarding + first signed close package + 13-week cash | **$30–38k fixed** (steady-state; Year-1 design partners pay less — see runway below) | One price, one outcome: *their first signed, fully-sourced, cross-system close and cash view.* No separate setup line. | ~$10–14k of this is mapping/cleanup + bespoke script-build; the buyer pays for the **close**, and the price clears margin after that cost in steady state |
| **+ Forecast & Board pack** | +$12–16k | A board-ready package | Mapping + scripts already done |
| **+ Audit & Valuation** | +$16–20k | Diligence/audit readiness | Mapping + scripts already done |

> **Year 1 is a runway, not an income year — the fix for v4's circular math.** v4 computed a steady-state floor and applied it to a year the roadmap spent building. v5 reconciles them by **declaring Year 1 a build-while-delivering runway:**
> - **Months 0–6 (Year 1 H1):** Matt **keeps partial analyst income or draws a defined savings runway** while building reconciliation patterns *inside* 1–2 paid design-partner engagements (priced at $18–22k each — see "is that really at-cost?" below). There is **no unpaid solo engine sprint**; the build happens in delivery on real books. Expected Year-1-H1 cash: partial salary/draw + ~$18–40k design-partner revenue.
> - **Months 6–12 (Year 1 H2):** 2–3 full-price First Closes ($30–38k) as the pattern library starts to help. Realistic Year-1 *consulting* margin: ~$50–90k — **explicitly below the steady-state floor, and explicitly bridged by the retained partial income / savings draw.** This is stated as the plan, not discovered as a shortfall.
> - **The $160–200k opportunity-cost floor is a YEAR-2 target**, where it belongs. Year-2 steady-state math below.

> **Year-2 steady-state floor math (where the build year is behind us):**
> - 4 First Closes/yr at $30–38k clearing ~$18–24k margin each (after the now-faster mapping+script-build) ≈ **$72–96k from anchors** off ~20 weeks.
> - ~6 expansion add-ons ($12–20k, ~3–4 wks each, mapping done → ~$10–16k margin) ≈ **$60–96k** off ~20 weeks.
> - **Anchors + expansions ≈ $132–192k margin off ~40 weeks**, plus 2–3 capped retainers — **clears the $160–200k floor in Year 2 without requiring most anchors to expand.** Expansion turns a viable year into a good one; the anchor stands alone.

**The recurring layer — repriced to reflect liability and touch:**
- **Run-it retainer — $5–9k/mo.** Operating a *signed* close monthly is the **highest-liability, highest-touch** line. It is a premium service and **does not get low-touch until** the bespoke scripts for that customer can run a delta-close with the reviewer reviewing only exceptions — a per-customer maturity point reached after several months on that account, **not** a general engine milestone. The buyer's *own* reviewer signs each monthly close, so there is no third-party-CPA fee.
- **Evidence pack — NOT a standalone revenue line; a retention feature of the retainer.** v4 tried to sell this at $99/$499/mo and called it "the only uncapped revenue." v5 traces that and finds it empty: a buyer with enough close activity to keep the pack *live* is by definition an active retainer client who'd get it **free**; the set that would pay standalone but isn't already active is ~empty. **So v5 stops calling it a revenue line.** The evidence pack is **bundled into the run-it retainer** as a retention/defensibility feature (it makes the retainer stickier and more auditor-ready), regenerated via the deterministic fast-path (re-render already-logged verdicts from disk — **never** live tribunal `claude -p` re-adjudication, see Risk #10). **There is no separate subscription SKU at launch.** If a genuinely passive "keep-current" market ever appears, it can be priced later — but v5 does not count it.

**Capacity arithmetic (honest, and now without a false scale lever):** a build is 4–6 weeks; Year-2 caps the model at **~4 anchors + ~6 expansions + 2–3 retainers/year** for one person — and **that is the ceiling.** There is no uncapped line left in the model. v5 states plainly: **this is a lifestyle/solo-consulting business sized to one person's calendar, clearing a strong analyst salary in Year 2, with no built-in path past ~40 delivery weeks until and unless the spin-out below is proven.**

**The consulting-vs-product tension — a *gated, low-probability* fork, not a plan.** v1 implied bespoke finance builds auto-spawn a horizontal governance SaaS. They don't, and v5 says so emphatically: **the bespoke per-customer reconciliation value does not productize** (4c), and a spin-out (Verdict's gateway API) would be sold to **developers** — a different buyer. So:
- **What compounds (consulting leverage, not software leverage):** (1) the **reconciliation pattern library** that makes the *next bespoke build faster to assemble* (not automatic); (2) **finance-specific Stop patterns + tribunal decision categories** that recur and harden the governance IP on real data; (3) **sales proof** — a real anonymized artifact beats slideware.
- **What does NOT compound:** Company A's reconciliation does not make Company B's automatic; a human still confirms B's mapping. **v5 stops claiming Company A makes Company B free** — it makes Matt's hand-assembly modestly faster, nothing more.
- **The fork is gated and unlikely, not sequenced:** *only if* the recurring finance-governance categories prove stable across ≥3 engagements (a sample the 18-month roadmap *barely* reaches — see Risk in Section 8) does scoping a standalone governance product for the developer buyer become defensible. **Default expectation: stay a consulting service permanently.** The spin-out is a low-probability option, explicitly not the income plan.

> **Is the $18–22k design-partner price really "at-cost"? — v5 reconciles it honestly (the v4 gap).** v4 asserted "at-cost" while its own cost truth (~$8–12k mapping) plus *unfinished-engine debugging* almost certainly put a 4–6-week design-partner engagement **below** cost. v5 stops calling it "at-cost" and calls it what it is: **a deliberately subsidized co-development rate that is likely slightly below true cost once Matt's time is valued at his analyst rate.** That subsidy is **funded by the Year-1 retained-income/savings runway above**, and it is *worth it* because these 1–2 engagements (a) build the pattern library v5's later speed depends on and (b) produce the first reference customers (Risk #6). v5 books the design-partner phase as **a funded customer-acquisition + R&D cost, not as profitable revenue** — which is the only honest accounting for it.

## 8. Eighteen-month roadmap (sequenced honestly; Year 1 = funded runway, not income year)

v4 double-booked an unpaid engine build against the first paying engagement and computed a floor the schedule couldn't deliver. v5 sequences so the build happens *inside paid (subsidized) delivery* and the steady-state floor is a Year-2 target.

**Months 0–3 — stand up the demo + Stop patterns; line up design partners. (Matt on partial income / savings runway.)**
- Build the **finance-value-first demo** on a sample multi-system GL set (lineage card leads, Stop closes) — honestly framed (Section 6) as "output shape + control surface," not "runs on your books now."
- Define finance **Stop patterns** (locked-period writes, ledger writes, money movement).
- Source 1–2 **design partners** from Matt's **own finance network** (Risk #6).
- *Stretch, may slip:* wire one class of finance judgment calls through `thing-decide.py` and link the Sága record to a lineage card.

**Months 3–8 — design-partner engagements: build reconciliation patterns ON real books, in paid (subsidized) delivery.** This replaces v4's unpaid solo engine sprint. Each design partner ($18–22k subsidized co-dev rate, Section 7) gets a working first close in 4–6 weeks; Matt + the agent **hand-build that customer's reconciliation scripts and harvest reusable patterns via `/wrap`.** The "engine" is never a general product — it's an accumulating pattern library plus bespoke scripts. *This is where the load-bearing asset actually gets built, and it's funded as R&D + customer acquisition, not booked as profit.*

**Months 8–12 — first full-price engagements as patterns start to help.** Run normal engagements at $30–38k First Close; "week or two for a common stack" aha (Section 6) becomes truthful only for stacks the library now covers. Map the evidence pack to one real insurer + one vendor-security questionnaire + NIST AI RMF / ISO 42001 clauses. Use the real anonymized design-partner artifact as the demo. **Year-1 consulting margin ~$50–90k — below floor by design, bridged by the runway (Section 7).**

**Months 12–18 — reach Year-2 steady-state base; instrument the compounding claim.** ~4 First Closes + expansions, 2–3 capped retainers — the Year-2 floor math (Section 7). Bundle the evidence pack into retainers (fast-path regeneration only; no standalone SKU). **Instrument delivery hours from day one to *measure* whether the pattern library actually speeds builds**, rather than asserting it.

> **The fork-gate is honestly under-powered at 18 months — v5 says so instead of overclaiming.** v4 claimed "4–6 closed engagements by month 18" so the "stable across ≥3 engagements" test is evaluable — but that reused the optimistic throughput the build-year can't deliver. v5's realistic count by month 18 is **1–2 design partners + 2–4 full-price = 3–6 engagements**, and the *full-price* subset (the relevant population for a productizable pattern) may be only 2–4. **So the stability sample may still be marginal at month 18.** v5 does not pretend otherwise: **if the sample is under-powered, the fork stays un-evaluated and the default (stay consulting) holds — which is fine, because the fork was always low-probability upside, not the plan.** *Hard rule: do not build a multi-tenant SaaS backend until ≥3 full-price engagements close and the pattern library demonstrably cut build hours.*

## 9. Honest risks

1. **The numbers are the existential liability — mitigated by design, not disclaimer.** A mis-stated close or covenant calc is far higher-stakes than a flawed dashboard. *Mitigation, structural:* numbers come from **fixed, customer-specific scripts the buyer's own reviewer re-runs and signs** (4c), never LLM free-text; sold as **analyst-assist, never auto-pilot**; the Stop turns "an AI touched the numbers" into a visible control.

2. **The signer is the buyer's own reviewer — never Matt, never a supplied CPA.** Matt is a verified financial analyst, **not a licensed CPA** (memory/user_role.md). v5 serves only companies with their own in-house reviewer. *Residual risk:* this narrows the market to the ~50–150-person, multi-system, has-a-controller segment — and (new in v5) means the **trigger had to be re-picked to reviewer-capacity strain** (Section 3a), because the acute deal-at-risk pain lives at the under-reviewed firm we exclude. v5 accepts the narrower, capacity-strain demand as the price of a defensible posture.

3. **The cross-system reconciliation layer is the hardest part — so v5 does NOT build a general engine; it builds bespoke per customer, and accepts that this caps scale.** A general engine generalizing across every SMB's messy exports is a multi-year, large-team problem (BlackLine/FloQast); LLM-written join logic over unseen exports is where determinism breaks. **v5's plan is bespoke, human-confirmed, per-customer scripts + a compounding pattern library — explicitly consulting leverage, not software leverage** (4c, Section 7). *Residual risk, stated plainly:* this means **no software-style scale and a hard ceiling at Matt's ~40 delivery weeks**; the pattern library speeds hand-assembly but never makes the next customer automatic. v5 treats "can a general engine even be built solo?" as **answered NO**, and builds the business that survives that answer rather than betting on the build that doesn't.

4. **The governance evidence is currently about the wrong subject.** Verified: the Sága records are *marketplace-development* decisions; the tribunal has never judged a finance action. **Until the wiring ships (a stretch that may slip), the lineage card sells only the human-authored source trail** — real and valuable, but the "gated-AI-judgment-under-a-number" story is aspirational and must not be sold as live.

5. **Solo capacity is the binding constraint AND the ceiling — Year 1 is a funded runway, not an income year.** Section 7 now reconciles the math with the roadmap: Year 1 clears only ~$50–90k consulting margin and is **bridged by retained partial income / a defined savings draw** while the pattern library is built inside subsidized design-partner work; the **$160–200k floor is a Year-2 target.** v4's error — applying steady-state math to a build year — is fixed. *Residual risk:* if Matt has no runway to bridge Year 1, the plan doesn't start; this is a real precondition, named as one.

6. **First-deal sourcing is a single-channel concentration risk — and v5 names a real second channel as contingency rather than restating the risk.** Matt's **own finance network** (he is a practicing financial analyst) is the primary channel; his wife's Partner-Success network is *not* a finance-buyer channel and is dropped (memory/project_psm_means_partner_success.md). v4 offered only "the design partner doubles as the reference" — a restatement, not a mitigation. **v5 adds a concrete second channel: fractional-CFO / outsourced-controller firms and the buyer's own audit/lender relationships as referral partners** — these firms sit next to exactly the has-a-reviewer, capacity-strained buyer (Section 3a), refer rather than compete (they're not selling AI tooling), and convert warm. *If the personal network underperforms, the contingency is to court 2–3 fractional-CFO practices as a referral channel before spending on cold outreach.* Concentration acknowledged; a named alternative path now exists.

7. **It is NOT an accredited compliance artifact — so it is not called a "Certificate."** No accredited body stands behind it; certification revenue accrues to Schellman/BSI. **Renamed "Evidence Pack" (and "Leash Status Report") everywhere**, sold as "evidence you can show," never "certified/compliant." Any human attestation is the **buyer's reviewer's**, under the buyer's own E&O.

8. **The insurance/E&O trigger is unverified and demoted.** Sourced only to secondary aggregators. Until re-verified against the primary ISO filing and carrier language, it is a **secondary "closes-faster" driver, not a co-equal demand pillar** (Section 3). The case stands on reviewer-capacity strain alone.

9. **The governance engine is single-tenant, file-on-disk, dogfooded on one repo.** "Works for us" ≠ "survives hostile multi-tenant SaaS." True tamper-evidence, multi-tenant isolation, and SSO are real engineering; the data-platform RLS/JWT skills are **guidance, not a shipped isolation layer.** This is exactly why the default is a *service*, not SaaS, and why the spin-out is gated and low-probability.

10. **Per-decision token/latency cost — and the evidence pack must dodge it because it is no longer a paid line.** The tribunal runs `claude -p` seats — live calls per gated action; a deterministic fast-path (cheap rules for low-stakes, the panel only for genuinely irreversible finance actions) is required before any per-decision cost is promised. **The evidence pack is bundled into the retainer, not a standalone subscription** (Section 7) — its regeneration re-renders already-logged verdicts from disk and **never re-adjudicates**, so it carries no per-pull panel cost. *v5's correction:* v4 called this pack "the only uncapped revenue," but its own churn fix left it with ~zero standalone payers, so **v5 demotes it from a revenue line to a retention feature** — there is no scalable revenue line left in the model, and v5 stops implying there is.

11. **Incumbent encroachment + a closing window — the competitor is the reviewer's own in-tool AI.** Because v5 serves the has-a-reviewer buyer, the head-on competitor is Excel Copilot / accounting-suite native AI (Section 3b). The defense is **cross-system assembly + a third-party-facing signed package + a governance trail** — jobs in-tool drafting assistants structurally don't do. *Honest hedge:* if Microsoft or an accounting suite ships **cross-system consolidation + an AI-action audit trail**, this wedge narrows fast. The moat is **integrated cross-system lineage + the governance trail (buildable), plus founder-fit (Matt, not transferable)** — durable for a solo consulting window, not permanent. We rent the window; we don't claim a fortress.

---

*Verified against this session's repo checks: finance assets are reasoning playbooks; the controller agent's `tools:` line grants Read, Edit, Write, Grep, Glob, Bash, WebFetch, WebSearch (`plugins/finance/agents/controller.md:4`) — data work in practice is `Bash`/`Grep`/`Glob` over GL exports. Matt is a financial analyst, NOT a CPA (memory/user_role.md), so the signer is always the buyer's own in-house reviewer. His wife is a Partner Success Manager in B2B SaaS, not a finance network (memory/project_psm_means_partner_success.md), so first-deal sourcing is Matt's own finance network plus a named fractional-CFO referral contingency. Guard hooks, tribunal, posture engine, and `/ragnarok` are real but unwired to finance; the insurance E&O trigger is demoted to unverified/secondary; the behavioral statistics remain quarantined from buyer-facing use. v5's four structural fixes over v4: (1) re-picked the purchase trigger from "deal-at-risk deadline" to "reviewer-capacity strain / cheaper-than-the-next-hire," because the deal-at-risk pain lives at the under-reviewed firm v4 excluded; (2) reconciled the income-floor math with the roadmap by declaring Year 1 a funded part-income/savings runway and moving the $160–200k floor to Year 2; (3) rejected the "build a general reconciliation engine solo in 4 months" framing entirely — v5 builds bespoke per-customer scripts + a compounding pattern library (consulting leverage, not software leverage), and accepts the resulting hard ceiling at ~40 delivery weeks; (4) demoted the evidence-pack subscription from "the only uncapped revenue line" to a bundled retainer retention feature, since its own churn fix left it with ~zero standalone payers — and stopped implying any scale lever exists. Minor fixes: moat re-stated as one buildable asset (cross-system lineage/governance) plus two named single-person dependencies (judgment, founder credibility); the demo reframed to concede a canned sample doesn't prove reconciliation of the prospect's books; the fork-gate conceded as possibly under-powered at 18 months with "stay consulting" as the safe default; a real second sourcing channel (fractional-CFO referral firms) named; the $18–22k design-partner price reconciled as a runway-funded subsidized R&D/acquisition cost, not "at-cost."*