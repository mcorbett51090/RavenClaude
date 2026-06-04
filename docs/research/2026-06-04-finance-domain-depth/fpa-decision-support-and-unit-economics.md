# FP&A Decision Support & Unit Economics — A Practitioner Synthesis

_Research synthesis for FP&A, CFOs, and operators. Authored 2026-06-04. Companion to — not a replacement for — the plugin's `kpi-definition` skill, which holds the dictionary-level definitions (ARR/NRR/LTV-CAC/Magic Number). This document covers the **analytical playbooks, decision rules, benchmark judgment, and error modes** that sit on top of those definitions._

---

## Method note

Queries fanned out across nine sub-topics: Skok/forEntrepreneurs metrics, a16z "16 startup metrics" + Gurley's "dangerous seductions," Bessemer/Sacks burn multiple, magic number, Rule of 40 (incl. Bessemer's "Rule of X"), NRR/GRR benchmarks, CAC-payback channel error, ARR bridge mechanics, cohort/retention "smile," capital-budgeting method selection (NPV/IRR/payback), discount-leakage/price-realization, scenario/tornado/Monte-Carlo presentation, build-vs-buy TCO, and FP&A business partnering. Source quality was high in the canon (Skok/forEntrepreneurs, a16z, Bessemer/BVP, Sacks/Craft, CFI, Wall Street Prep) but several **primary** canon pages — `forentrepreneurs.com`, `a16z.com`, and Gurley's `abovethecrowd.com` — returned **HTTP 403** to the fetcher; their content is therefore cited from search excerpts and corroborating secondary sources (Wall Street Prep, ChartMogul, Medium notes, Visible.vc, CFI), and every load-bearing number is cross-checked against ≥2 independent sources where it carries a `[high]` tag. **All the famous thresholds below — LTV:CAC > 3, CAC payback < 12 mo, Rule of 40, magic number > 0.75, burn multiple < 1 — are practitioner rules-of-thumb, not laws.** They were derived from cohorts of mostly US, mostly venture-backed SaaS companies in specific rate environments; they drift with the cost of capital and the company's stage/segment. Date and segment any benchmark before you quote it to a board.

**Confidence tags:** `[high]` = ≥2 independent credible sources; `[med]` = single credible source; `[unverified — training knowledge]` = recalled, not re-confirmed this session.

---

## 1. Unit economics — the analytical playbook

The definitions live in the KPI dictionary. What follows is the *judgment*: which formula is defensible, what the ratio is actually telling you, and where it lies to you.

### 1.1 Contribution margin is the right denominator — not revenue

Every unit-economics decision should run on **gross-margin (contribution) dollars, not top-line revenue.** A customer paying $1,000/mo at 80% subscription gross margin contributes $800/mo of recoverable economics; the same $1,000 blended with low-margin professional services contributes far less. Using revenue instead of contribution margin systematically *overstates* LTV and *understates* payback. `[high]` (Skok/forEntrepreneurs; Wall Street Prep; CFI)

### 1.2 CAC: fully-loaded, and segment it before you trust it

- **Fully-loaded CAC** includes all sales + marketing cost in the period — salaries, commissions, ad spend, tooling, allocated overhead — not just media spend. A "CAC" that is only ad spend is a media-efficiency number, not an acquisition cost. `[high]` (CFI; Wall Street Prep)
- **Blended vs. paid:** blended CAC averages free/organic/referral customers with paid ones, which **hides a broken paid channel.** Worked example from the field: a SaaS company at $22M ARR reported a 14-month *blended* payback to its board; segmented by channel, organic/partner-referred paid back in ~9 months while paid was far worse — the blend was masking the problem. `[med]` (Fiscallion). Decision rule: **never approve a channel budget increase on a blended number — confirm that channel's standalone CAC/payback first.** `[high]` (Fiscallion; Saras Analytics)
- The cohort discipline: count only **new-logo acquisition cost over new logos.** Folding expansion into the denominator understates CAC (see §1.5 error mode).

### 1.3 LTV: the correct formula vs. the naive one

**Naive (dangerous):** `LTV = ARPA ÷ churn rate`. This overstates LTV two ways: (1) it treats revenue as if it were profit, ignoring gross margin; (2) at low churn it implies absurd 20–40 year lifetimes. `[high]` (ChartMogul; Wall Street Prep; Janz/Point Nine)

**Correct (gross-margin-based, churn- and discount-adjusted):**

```
LTV = (ARPA × Gross Margin %) / (Revenue churn rate + Discount rate)
```

Adding the discount rate to the denominator is the NPV correction — it caps the geometric series so a near-zero-churn customer doesn't produce an infinite LTV, and it values near-term cash above far-future cash. `[high]` (forEntrepreneurs "True LTV/DCF"; ChartMogul; Wall Street Prep). **Pragmatic alternative for early-stage:** cap assumed lifetime at **3–4 years** rather than inverting a churn rate you've only observed for a few quarters. `[med]` (ChartMogul)

**Gurley's "dangerous seduction" (2012, the canonical caution):** LTV is seductive because of its *simplicity and certainty* — but it is "often calculated incorrectly, shared inaccurately." The structural danger: heavy LTV emphasis correlates with companies posting **massive losses at scale**, because a big LTV number is used as *leverage to justify ludicrous acquisition spend* today against speculative future profit. The fragile assumptions are (a) retention/churn held flat for the whole horizon, (b) gross margin held flat, (c) no discounting, (d) the *marginal* retained customer behaves like the *average*. `[high]` (Gurley, Above the Crowd, via excerpt + Medium notes; a16z echoes)

### 1.4 LTV:CAC — the >3 rule, and why >5 is a *warning*, not a trophy

- **LTV:CAC ≥ 3:1** is Skok's guideline for a sustainable, efficient model — at least $3 of lifetime gross profit per $1 of fully-loaded acquisition cost. `[high]` (Skok/forEntrepreneurs; Wall Street Prep; Burkland; Meritech)
- **Below 3:1** → acquisition is too expensive relative to value retained; fix CAC, churn, or pricing before scaling spend.
- **Above ~5:1** → frequently a signal of **under-investment in growth**: you could profitably acquire more customers but aren't. It can also be a *measurement artifact* — an inflated LTV (naive formula, optimistic churn) producing a flattering ratio. Treat a very high ratio as a question, not a victory. `[high]` (Skok/forEntrepreneurs; Burkland; getmonetizely)

### 1.5 CAC payback — the gross-margin-adjusted form, and the two common formula errors

```
CAC Payback (months) = CAC / (New MRR per customer × Gross Margin %)
```

- **< 12 months** is the canonical "good" SaaS payback (Skok; Meritech pairs it with LTV:CAC ≥ 3 as the joint test of capital efficiency). `[high]` (Skok/forEntrepreneurs; Meritech; Wall Street Prep). For SMB/self-serve, sub-12 (often sub-6) is expected; for enterprise, 18–24 months can still be healthy given longer retention. `[med]` (Wall Street Prep)
- **Two errors that inflate payback 20–40%:** (1) using **total ARPA instead of cohort MRR**, and (2) using **blended gross margin** (which includes low-margin services/implementation) instead of **subscription gross margin.** `[med]` (Fiscallion)
- **The expansion error (subtle):** counting *expansion* MRR in the payback numerator improperly shortens the apparent payback on *new* logos. Acquisition cost recovers from the *initial* contract; expansion is a separate (and cheaper) motion. Keep new-logo payback and net-of-expansion payback as distinct lines. `[high]` (Skok; a16z gross-vs-net caution)

---

## 2. SaaS growth analytics — bridges, retention, and efficiency

### 2.1 The ARR/MRR movement bridge (the waterfall)

The headline ARR number is nearly useless without the **movement bridge** beneath it:

```
Beginning ARR
  + New        (new-logo ARR — dated to service start, not order date)
  + Expansion  (upsell/cross-sell/seat growth on existing logos)
  − Contraction(downgrades on existing logos)
  − Churn      (lost-logo ARR — dated to contract end, not when you learned of it)
= Ending ARR
```

`[high]` (AccountAim; Ordway; The SaaS CFO; HiBob). The diagnostic value is in the *composition*, not the net: **if contraction + churn is growing faster than expansion, the growth engine is fragile even when net ARR still rises.** A bridge that's net-positive only because New is masking rising Churn is a leading indicator of a retention problem. `[high]` (AccountAim; Ordway). Dating discipline matters: book New at service start and Churn at contract end, or the bridge will misattribute timing.

### 2.2 NRR / GRR — benchmarks (segment- and date-stamped)

| Metric | Concerning | Good | Best-in-class | Notes |
|---|---|---|---|---|
| **NRR** | < 100% | 100–120% | **> 130%** | Venture-backed median ~106% (ChartMogul 2024, N≈2,100) `[high]` |
| **GRR** | < 85% | ~90% (median) | **> 95%** | Private-SaaS median ~92% `[med]` |

**Segment splits matter more than the headline** `[high]` (Optifai; ProductQuant; SaaS Capital):
- Enterprise (ACV > $100K): median NRR ~118%; best-in-class 135%+
- Mid-market ($25K–$100K): median ~108%; best-in-class 125%+
- SMB (< $25K): median ~97%; best-in-class 110%+

GRR vs. NRR judgment: **GRR tells you what you're losing; NRR tells you what you keep after expansion.** A 130% NRR sitting on an 80% GRR is a leaky bucket being papered over by a few expanding whales — concentration risk hiding inside a great-looking headline. Always read them as a pair. `[high]` (FE International; a16z gross-vs-net)

### 2.3 Cohort / retention analysis — the "smile"

Group customers by signup period; track the cohort's retained revenue over time. Two curves to keep separate `[high]` (Glencoyne; CFO Pro Analytics; Fiscallion):
- **Logo retention** — how many customers stay (count-based).
- **Net-revenue retention curve** — how much *revenue* stays (expansion-inclusive).

The **"smile"** is the prized pattern: net-revenue-retention curve dips early (initial churn), flattens, then **curves back above 100%** as expansion from survivors outpaces churn. A net-revenue cohort curve that bends upward is the visual proof of a durable expansion motion; one that only ever decays is a transactional business wearing a subscription label. `[high]` (Glencoyne; Userpilot). Rough churn anchors by motion: SMB monthly ~5–8%/mo logo churn (60–70% annual retention); mid-market annual 15–25% annual churn; enterprise 5–15%. `[med]` (Fiscallion)

### 2.4 Efficiency metrics — magic number, burn multiple, Rule of 40

**Magic number** (sales efficiency): `(ΔQuarterly revenue × 4) / prior-quarter S&M`. `[high]` (The SaaS CFO; CFI; Wall Street Prep)
- **< 0.5** → sales motion is stressed; don't pour in more S&M, fix the engine.
- **0.5–0.75** → ambiguous; investigate before scaling.
- **> 0.75** → efficient; "pour on the gas." `[high]`
- **> 1.0** → very strong; almost certainly under-investing in growth.

**Burn multiple** (Sacks/Craft, 2020): `Net burn / Net new ARR` — dollars burned per dollar of new ARR. Lower = more efficient. `[high]` (Sacks, Bottom Up; Airtree; CFI; Scale VP)
- **< 1.0** = amazing · **1.0–1.5** = great · **1.5–2.0** = OK/watch · **> 2.0** = concerning. `[high]`
- It *worsens* (rises) earlier-stage; lifecycle average across seed→IPO is ~1.6x. `[high]` (Scale VP; Versatile VC)
- Bessemer's **Efficiency Score** is essentially the reciprocal (Net new ARR / Burn). `[high]` (Wall Street Prep; Versatile VC)

**Rule of 40:** `Revenue growth % + Profit margin % ≥ 40`. `[high]` (Wall Street Prep; CloudZero; Bessemer)
- **The GAAP-vs-cash trap:** the "margin" term is *not* a free choice. Private companies often use EBITDA; public companies/investors increasingly use **FCF margin** (harder to manipulate). Mixing growth-on-GAAP-revenue with a cash-margin, or comparing your EBITDA-based 42 against a peer's FCF-based 42, is apples-to-oranges. **State the margin definition every time.** `[high]` (Wall Street Prep; CloudZero)
- **Bessemer's "Rule of X"** argues 40 is dated and that growth compounds value while margin is linear — so weight growth ~2x: `(2 × Growth %) + FCF margin %`. Bessemer's Good/Better/Best: ~40 / ~50 / ~70+. `[high]` (Bessemer via search; SaaS Barometer)

### 2.5 a16z's ambiguous-/vanity-metric warnings (the "get real" list)

The recurring abuses to police in any pack `[high]` (a16z 16 Startup Metrics, via excerpt + Visible.vc/easyVC corroboration):
- **Bookings ≠ revenue ≠ billings.** Bookings = contract value signed; revenue is recognized over the term; billings ≈ revenue + Δ deferred revenue. Don't headline "bookings" as if it were revenue.
- **ARR ≠ run-rate.** Annualizing a single strong month (run-rate) is not contracted recurring ARR — it smuggles in non-recurring spikes.
- **Gross vs. net churn.** Net (revenue) churn nets upsell against losses and *understates* the actual loss; gross churn is the true bleed. Report both, never net-only.
- **GMV ≠ revenue** (marketplaces): revenue is only the *take* of GMV.
- **Cumulative/"total" charts hide a decelerating growth rate** — any cumulative line always rises. Show period-over-period rate, label the Y-axis, and show absolute numbers alongside percentages (big % off a small base means little).

---

## 3. Investment cases & capital allocation

### 3.1 The discipline of a business case

A defensible case rests on four rules, and most bad cases break at least one `[high]` (CFI; Umbrex; Financial Edge):
1. **Incremental cash flows only** — model the *difference* the decision makes, not the whole entity's flows.
2. **Ignore sunk costs** — money already spent is irrelevant to the go-forward decision; including it is the classic fallacy.
3. **Charge opportunity cost** — the next-best use of the capital/people is a real cost of saying yes.
4. **Discount at a risk-appropriate rate** — use WACC only if the project's risk ≈ the firm's; riskier projects need a higher **hurdle rate** than WACC. `[high]` (CFI; Financial Edge)

### 3.2 Hurdle rate vs. WACC

WACC is the firm's blended cost of capital and is the *floor*. The **hurdle rate** is the rate management actually requires — often WACC **plus a risk premium** for project-specific risk, and adjusted by capital rationing. Discounting a high-risk new-market bet at the corporate WACC systematically overvalues it. `[high]` (Financial Edge; CFI; Damodaran — risk-matched discount rate principle `[unverified — training knowledge]` on exact phrasing)

### 3.3 Method selection — NPV vs. IRR vs. payback

```
DECISION TREE — which capital-budgeting method leads?

Is the decision go/no-go on value creation, or a ranking of mutually exclusive projects?
├─ Ranking mutually exclusive projects, OR cash flows change sign more than once
│     └─► LEAD WITH NPV.  IRR mis-ranks mutually exclusive projects (scale/timing
│         differences) and can yield multiple/no IRR with sign-flipping flows.
│         NPV is additive and assumes reinvestment at the discount rate (realistic).
│         [high — CFI; Wall Street Prep; AFP]
├─ Communicating return to a non-finance / IRR-native audience (PE, ROI culture)
│     └─► REPORT IRR alongside NPV, but let NPV break ties. Sanity-check IRR with
│         MIRR when reinvestment-rate distortion is material. [high]
├─ Liquidity / runway is the binding constraint (startup, distressed, cash-rationed)
│     └─► PAYBACK (or discounted payback) as a SCREEN, never the sole decision rule —
│         it ignores everything after the cutoff and (undiscounted) ignores TVM.
│         Use it to gate, then decide on NPV. [high]
└─ Comparing projects of very different size
      └─► Use NPV for the accept/reject; use Profitability Index (NPV/investment)
          when capital is rationed and you must rank per dollar invested. [med]
```

Core rules: **NPV > 0 → accept.** **IRR > hurdle rate → accept** (but NPV wins on conflict). **Payback < target → passes the screen only.** `[high]` (CFI; Wall Street Prep; Fiveable; AFP)

### 3.4 Build-vs-buy

The financial frame is **5-year TCO + opportunity cost**, not the sticker price `[high]` (Neontri; SoftwareSeni; Jaspersoft):
- Build TCO over 5 yrs ≈ **5–10×** initial dev cost (maintenance ~15–20%/yr of build; ~80% of lifetime cost is post-launch). Buy ≈ **2–3×** license over 5 yrs, but hidden integration/training can add **150–200%** on top of the license. `[med]` (Neontri; SoftwareSeni)
- **Opportunity cost** is the decisive, frequently-omitted term: engineer-hours spent building commodity internal tools are hours *not* spent on the differentiating product.
- Default heuristic: **buy for commodity, build for differentiation; hybrid/compose by default.** `[high]` (Neontri; BETSOL)

---

## 4. Pricing & discounting analytics

### 4.1 Price realization / net (pocket) price

**Price realization = realized (pocket) price ÷ list price** — the simplest measure of commercial discipline. The **waterfall from list → invoice → pocket** exposes leakage: on-invoice cuts (promos, volume, early-pay) can take ~33% off list; off-invoice leakage (rebates, freight, penalties, allowances) can push pocket to ~51% off list. Leakage between list and pocket is commonly **40–70% of total margin erosion**, and firms realize only ~43% of intended price *increases* on average. `[med]` (Umbrex NPR; transformpricing; SBI; cityshiftfinance)

### 4.2 The discounting math (why it's a "death spiral")

The leverage is brutal and worth memorizing for the room:
- On a **40% gross margin, a 10% price cut isn't a 10% margin hit — it's a 25% one** (40% → 30%). `[high]` (transformpricing; Kakas)
- A **1% price drop can cut operating profit ~8%**, requiring an **~18.7% volume increase** just to break even on profit. `[high]` (Kakas; cityshiftfinance)
- The "spiral": a discount wins the deal but sets a **lower price anchor** that propagates to other accounts and renewals — a self-reinforcing downward ratchet. `[med]` (transformpricing; twobrainbusiness)

**FP&A's job:** quantify the *volume required to offset* before a discount is approved, and govern discount authority by tier. Discount-leakage recovery is one of the highest-ROI margin programs because it recovers margin from activity the business already runs — no new customers, no new product. `[high]` (cityshiftfinance; SBI)

### 4.3 Value-based vs. cost-plus framing

Cost-plus prices off your costs (ignores willingness-to-pay, leaves money on the table or prices out of the market); value-based prices off the customer's realized value. FP&A's contribution is the **value quantification** — the ROI the buyer earns — which both justifies premium pricing and defends against discount pressure with evidence rather than reflex. `[unverified — training knowledge]` (framing is standard pricing canon; not re-confirmed against a primary source this session)

---

## 5. Scenario & sensitivity analysis for decisions

- **Sensitivity** flexes **one driver at a time** to find what moves the answer most. **Scenario** flexes a **coherent set** of drivers together to tell a story (base / upside / downside). Best practice runs **sensitivity first** (find the few drivers that matter), **then** scenario (build stories around them). `[high]` (Golimelight; Bodmer)
- **Tornado diagram** is the executive-facing output of sensitivity: drivers ranked by impact width, widest at top — it answers "which assumptions actually decide this?" at a glance, and shows whether risk is skewed up or down. `[high]` (Bodmer; SmartOrg)
- **Monte Carlo** assigns a *distribution* to each driver and simulates thousands of outcomes, producing a probability statement — _"70% chance ARR lands $12–14M"_ — instead of a single point. Reserve it for decisions where the *shape* of risk (tail risk, P10/P50/P90) matters, not routine forecasts. `[med]` (Golimelight)
- **Presentation rule: give executives a range with the key swing drivers named, not a single point estimate** — and always **attach the scenario to a decision/trigger.** A base/upside/downside that doesn't change what anyone does is "scenario theater." `[high]` (Golimelight; FP&A Trends)

---

## 6. Business partnering — the decision-support operating model

- The modern FP&A role has shifted from **reporting the past to supporting forward decisions** — guiding where money is spent, framing uncertainty, and being in the room *before* the decision, not after. `[high]` (FP&A Trends; NetSuite; Unit4)
- **Lead with the "so what," not the table.** Start with the bottom line / recommendation so the audience knows where to look, then support it; numbers without a "what to do" are half a deliverable. Waterfall and tornado visuals carry the story faster than a grid. `[high]` (CFI FP&A storytelling; FP&A Trends)
- **Operating rhythm:** pre-define the **trigger points** that prompt an operating decision (pipeline expansion/contraction, sales performance, runway thresholds) and review the bridge/cohort/efficiency metrics on a set cadence, so partnering is a routine, not a fire drill. `[med]` (FP&A Trends)

---

## 7. The error-mode catalogue (what actually goes wrong)

| # | Error mode | Why it's wrong | Fix |
|---|---|---|---|
| 1 | **Naive LTV** (`ARPA ÷ churn`) | Ignores gross margin and discounting; implies absurd lifetimes at low churn | Gross-margin-based + discount rate in denominator; or cap at 3–4 yrs (§1.3) `[high]` |
| 2 | **Blended CAC/payback** | Averages free + paid, hiding a broken paid channel | Segment by channel; gate budget on standalone channel payback (§1.2) `[high]` |
| 3 | **Expansion in CAC payback numerator** | Acquisition cost recovers from the *initial* contract, not upsell | Separate new-logo payback from net-of-expansion (§1.5) `[high]` |
| 4 | **Blended GM / total ARPA in payback** | Inflates payback 20–40% via low-margin services | Use subscription GM + cohort MRR (§1.5) `[med]` |
| 5 | **LTV:CAC > 5 read as a win** | Usually under-investment in growth, or an inflated LTV artifact | Treat high ratio as a question; pressure-test the LTV (§1.4) `[high]` |
| 6 | **Net ARR without the bridge** | Hides rising churn masked by New | Always show new/expansion/contraction/churn composition (§2.1) `[high]` |
| 7 | **NRR-only, no GRR** | A few expanding whales paper over a leaky bucket | Report NRR and GRR together (§2.2) `[high]` |
| 8 | **Rule of 40 on mixed bases** | GAAP-growth + EBITDA vs. peer's FCF-margin is apples-to-oranges | State the margin definition; pick one and hold it (§2.4) `[high]` |
| 9 | **Bookings/run-rate as revenue** | Overstates recurring, recognized revenue | Distinguish bookings/billings/ARR/run-rate explicitly (§2.5) `[high]` |
| 10 | **Payback as the sole capital-budget rule** | Ignores all cash after cutoff and (undiscounted) TVM | Screen with payback, decide with NPV (§3.3) `[high]` |
| 11 | **IRR to rank mutually exclusive / sign-flipping projects** | Mis-ranks on scale/timing; multiple-IRR problem | NPV breaks the tie; MIRR for reinvestment distortion (§3.3) `[high]` |
| 12 | **Sunk cost in the business case** | Already spent — irrelevant to go-forward | Incremental cash flows only (§3.1) `[high]` |
| 13 | **WACC as hurdle for a risky project** | Under-prices project-specific risk | Risk-matched hurdle = WACC + premium (§3.2) `[high]` |
| 14 | **Reflexive discounting** | 10% off a 40% margin = 25% margin loss; sets a spreading anchor | Compute offsetting volume before approval; govern discount authority (§4.2) `[high]` |
| 15 | **Scenario theater** | Base/upside/downside attached to no decision | Tie every scenario to a trigger/decision; name the swing drivers (§5) `[high]` |
| 16 | **Point estimate to executives** | False precision hides risk | Present ranges + tornado; reserve point estimates for committed numbers (§5) `[high]` |

---

## 8. Quick-reference: which efficiency metric for this business / stage?

```
DECISION TREE — pick the lead efficiency metric

What decision are you informing?
├─ "Should we spend more on sales & marketing right now?"
│     └─► MAGIC NUMBER (>0.75 → invest; <0.5 → fix the engine first)   [high]
├─ "Are we converting cash into growth efficiently?" (cash-efficiency / fundraise lens)
│     └─► BURN MULTIPLE (<1 amazing, 1–1.5 great, >2 concerning); reciprocal = BVP Efficiency Score   [high]
├─ "Is each acquired customer worth acquiring?" (unit-economics lens)
│     └─► LTV:CAC (≥3) + CAC PAYBACK (<12mo) together — Meritech's joint capital-efficiency test   [high]
├─ "Are we durable — growing AND profitable enough to be financeable?"
│     └─► RULE OF 40 (state the margin basis!) or Bessemer RULE OF X (2×growth + FCF) for growth-weighted view   [high]
└─ "Is our revenue base sticky / expanding?"
      └─► NRR + GRR (as a pair) and the net-revenue COHORT 'smile'   [high]

Stage modifier:
  Pre-PMF / seed   → burn multiple naturally high (2–3); LTV horizons unreliable, cap at 3–4 yrs.
  Growth / Series A→C → magic number + LTV:CAC + payback are most actionable.
  Scale / pre-IPO  → Rule of 40 / Rule of X + FCF-margin discipline dominate the conversation.
```

---

## Source-quality assessment

**Strong, multi-sourced (`[high]`):** the LTV:CAC>3 / payback<12mo rules (Skok/forEntrepreneurs corroborated by Meritech, Wall Street Prep, Burkland); the correct LTV formula (ChartMogul + Wall Street Prep + Point Nine); ARR-bridge mechanics (AccountAim, Ordway, The SaaS CFO); NRR/GRR benchmarks (Optifai, ProductQuant, SaaS Capital, ChartMogul); magic number 0.75 (The SaaS CFO, CFI, Wall Street Prep); burn multiple thresholds (Sacks primary + Airtree + CFI + Scale VP); Rule of 40 + GAAP/cash caveat + Bessemer Rule of X (Wall Street Prep, CloudZero, Bessemer); capital-budgeting method selection (CFI, Wall Street Prep, AFP, Fiveable); discounting math (transformpricing + Kakas + cityshiftfinance); a16z metric-ambiguity warnings (a16z excerpt corroborated by Visible.vc/easyVC). **Single-source (`[med]`):** the channel-segmentation worked example and the 20–40% payback-inflation figure (Fiscallion); GRR private-median 92%; build-vs-buy TCO multiples (Neontri/SoftwareSeni); price-leakage 40–70% (Umbrex/SBI). **`[unverified]`:** the precise wording of Damodaran's risk-matched-rate position and the value-based-pricing framing — both standard canon, not re-confirmed against a primary source this session. **Blocked domains:** `forentrepreneurs.com`, `a16z.com`, and Gurley's `abovethecrowd.com` all returned HTTP 403 to the fetcher; their content is cited from search excerpts plus corroborating secondaries, which is why the headline canon claims still clear the `[high]` two-source bar. **Caveat to carry to any board:** every threshold here is a stage-/segment-/rate-environment-dependent rule of thumb, not a law — date it and segment it before quoting.
