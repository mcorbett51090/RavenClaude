# Staffing decision trees — which diagnostic for which symptom

> **Last reviewed:** 2026-06-04. The "what do I look at first" reference for the `staffing-engagement-lead` and `staffing-operations-analyst`. When a client presents multiple simultaneous symptoms, **traverse the relevant tree top-to-bottom before picking a method** — do not pattern-match the loudest symptom to the first tool. Higher branches win over lower ones on ties.

**The most expensive wrong-first-pick in this plugin:** treating an **order-quality** problem (uncompetitive bill rates, aged/un-workable orders) as a **recruiter-performance** problem and "fixing" the recruiters. Always rule out order quality and supply before touching headcount.

---

## Decision Tree: Fill rate has declined

1. **Is the comparison crossing a seasonal boundary?** (healthcare surge/summer peak; education spring-recruit/fall-start cycle) → **YES:** re-cut YoY same-period before anything else; the decline may be a calendar artifact (§3 #5). Route: segment specialist for the cycle shape. → **NO:** continue.
2. **Which fill-rate denominator moved?** (orders received vs. workable vs. submittals-accepted) → if **dead/on-hold/uncompetitive orders grew the base**, it's an **order-quality** problem, not a fill problem. Route: `recruiting-funnel-strategist` (order-aging cut). → else continue.
3. **Split supply vs. order-quality** (§3 #6): are submittals-per-workable-order down (**supply**) or are workable orders themselves uncompetitive/aged (**demand/order-quality**)? → **Supply:** sourcing-channel + capacity work (`recruiting-funnel-strategist`); is pay rate competitive vs. market? (`healthcare`/`education` specialist). → **Order-quality:** bill-rate competitiveness + intake discipline (segment specialist).
4. **Is time-to-fill also slow?** Pair them (§3 #2). A high-fill/slow-speed disease is losing placements to faster competitors — different fix than low-fill/fast. Include the **credentialing clock** in the time (§3 #7).
5. **Only after 1–4:** if supply is healthy, orders are workable and competitive, and speed is fine, *then* examine recruiter execution — normalized for reqs-per-recruiter (§3 #4).

## Decision Tree: Margin / spread is compressing

1. **Decompose bill − pay − burden** before calling it pricing (§3 #3). → continue.
2. **Did bill rate fall?** (rate-cycle pressure, MSP rate caps, mix shift to lower-bill segments) → Route: `healthcare-staffing-specialist` for rate-cycle context + segment mix.
3. **Did pay rate rise faster than bill?** (candidate-supply scarcity forcing pay up) → supply-side; pair with fill-rate tree.
4. **Did a burden line move?** Walk the stack — taxes, **malpractice (locums)**, **housing/stipends (travel)**, insurance, credentialing cost, bench/idle time. A rise here masquerades as a pricing problem.
5. **Is bench/idle time the driver?** → redeployment-rate lever (cheapest placement; `recruiting-funnel-strategist`).
6. **Is it segment mix at the portfolio level?** (more low-margin per-diem, less high-margin allied) → not a per-deal problem; a portfolio-mix decision (`staffing-engagement-lead` synthesis).

## Decision Tree: A recruiter (or team) looks like it's underperforming

1. **Is the recruiter being fed?** Reqs-per-recruiter and order-quality first (§3 #4). An under-fed recruiter on aged/uncompetitive orders is a supply problem in a performance costume. → if under-fed: fix supply/order-quality, not the recruiter.
2. **Is the desk's order mix harder?** (credentialing-heavy segment, rural/hard-to-fill roles) → normalize the comparison for order difficulty.
3. **Is it speed or conversion?** Pull submittal-to-interview and offer-acceptance; a quality problem (low interview rate) ≠ an activity problem (low submittals).
4. **Only after 1–3:** if fed comparably, comparable mix, and the funnel ratios are genuinely below peers, *then* it's an execution conversation. Even then, lead with the specific stage that's off.

## Decision Tree: Aged-order pileup

1. **Are the aged orders workable?** Split nominal vs. workable. Dead/on-hold orders should leave the active denominator (they're distorting fill rate and capacity reads).
2. **Why are workable ones aging?** → **uncompetitive bill rate** (order-quality; intake/pricing), **supply gap** (sourcing/pay), or **credentialing bottleneck** (accept→start fallout, §3 #7)? Route to the matching specialist.
3. **Is intake discipline the root?** Orders accepted that the firm can't competitively fill inflate aging and depress fill rate — an intake/qualification problem, not a recruiting one.

## Decision Tree: "Are we competitive in this market?"

1. **Name the segment** — competitiveness in allied ≠ in travel nursing ≠ in school therapy. Don't average (§3 #9).
2. **Pull SIA-anchored sizing + the competitor map** ([`competitor-landscape.md`](competitor-landscape.md)); place the client by segment.
3. **Win/lose by lane** — where does the client's shape (dual-segment, allied + school therapy breadth) advantage it, and where do scale players (Aya/AMN travel; CHG/Jackson locums; Presence/eLuma teletherapy software; ESS/Kelly subs; TSSG therapy roll-up) lead?
4. Route synthesis to `staffing-engagement-lead` for the exec readout.

---

## How to use these
- Traverse top-to-bottom; **the first branch that matches selects the route** — don't keep going to a lower branch you "like better."
- Every tree's early branches are the cheap, high-leverage cuts (seasonality, denominator, supply-vs-order-quality). Spending the engagement's first hour there prevents the expensive wrong-first-pick.
- When two trees apply (fill *and* margin both down), run them in parallel and let `staffing-engagement-lead` reconcile — a shared root cause (e.g., segment-mix shift) often sits under both.
