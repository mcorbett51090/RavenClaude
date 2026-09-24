# Outreach templates — P0a "needs a human" follow-ups

Both research files (`tec-premortem-findings.md`, `incumbent-check-findings.md`) named specific
outreach as the highest-leverage next step and the way to actually settle several `[unverified]`
findings — but named it as a task, not a message. These are ready-to-send drafts for the four asks.
Each is short on purpose: the goal is a reply, not a pitch. Edit the bracketed fields, and the tone
if it doesn't sound like you.

**Do not send anything until you've read the underlying finding it's chasing** — the "why this
matters" line under each template points at the file/section to check first.

---

## 1. TEC founder outreach (highest-value single action per `tec-premortem-findings.md`)

**Why this matters:** TEC is the closest prior-art competitor, and desk research could only get to
"provisionally dormant since ~2019–2020, evidence consistent with a funding-cliff" — it could **not**
tell apart a demand-side failure (which would trip the plan's STOP trigger) from a supply-side or
funding cause (which wouldn't). Only the founders can settle it. Two people, either channel works.

**Targets:** Hal Friedlander (LinkedIn: `hal-friedlander-39052a2`; also posts as `@HalFriedlander`
on X) and Celina Morgan-Standard (LinkedIn — currently listed as COO, Energy Transition Capital
Management).

**LinkedIn / email draft:**

> Subject: Quick question about TEC's pricing work
>
> Hi [Hal / Celina] — I'm building something in the same space TEC worked in: benchmark pricing
> data so K-12 districts can see whether they're paying more than peers for the same SaaS products.
> I came across TEC's work from 2016-2018 and had a couple of quick questions, if you have five
> minutes:
>
> - What ultimately stopped TEC's active work — funding, adoption, something else?
> - Roughly how many districts paid for the premium tier or Phase 3 procurement support, versus
>   just using the free data-sharing tier?
> - Did any vendors push back on the pricing transparency, and if so, how?
>
> No pressure to reply at length — even a one-line answer on any of these would genuinely help me
> avoid repeating a mistake. Happy to share what I learn back if useful.
>
> Thanks,
> [Your name]

**What to do with the answer:** record it in `tec-premortem-findings.md` under a new dated addendum
(don't edit the original findings — append), and re-run the F11 three-state call against
`preregistration-template.md` §4(d) if the answer changes it.

---

## 2. LearnPlatform demo request (U3, `incumbent-check-findings.md` §"Needs a human" item 1)

**Why this matters:** desk research found no public evidence LearnPlatform still offers TEC-era
cross-district price reports, but Instructure owns the platform that hosted them and years of
district-entered "Price" fields — so the honest state is "no evidence found," not "confirmed absent."
This is the single check most likely to flip criterion (e).

**Draft (sales-inbound form or email):**

> Subject: Question about cross-district price benchmarking in LearnPlatform
>
> Hi — I'm evaluating tools for a K-12 group-purchasing project and wanted to ask a specific question
> before requesting a full demo: does LearnPlatform let a district see what *other* districts are
> paying for a given product, per license and per contract term — something like the TEC Data
> Platform reports from a few years back? If that capability exists today (even in a specific tier
> or state contract), I'd love to see it. If not, no worries — just trying to scope correctly before
> we build something that might already exist.
>
> [Your name / district or org, if using a district-affiliated contact for credibility]

**Questions to ask live if a call happens (from the findings file):**
1. Can a district see what other districts pay for product X, per license and per term?
2. What happened to the TEC-era price reports and data?
3. Is aggregated "Price" field data ever benchmarked across customers?
4. Is any statewide contract-pricing view in use (Texas? Ohio?)?

---

## 3. GovSpend agency demo / trial request (U4, `incumbent-check-findings.md` §"Needs a human" item 2)

**Why this matters:** GovSpend's Agency Launchpad is the closest thing found to an existing
competitor — an average-price graph and "what comparable agencies paid" from real purchase orders.
The open question is whether it normalizes to **per-seat, per-term** SaaS pricing, or stays at raw
PO/line-item level (which would leave Buying Power's normalization work as the real differentiator).
Plan-A Alt 6 already sanctions a trial for internal validation, never resale.

**Draft (trial/demo request, ideally as a district-affiliated buyer if possible — GovSpend's agency
product is agency-facing, so a founder cold-request may get routed to vendor sales instead):**

> Subject: Trial request — agency/district buyer access
>
> Hi — I'd like to trial GovSpend's agency-side product (Agency Launchpad) to evaluate it for
> benchmarking SaaS purchases across K-12 districts. A few things I'd want to confirm during the
> trial, if you can point me at documentation or a rep who can answer them directly:
>
> - Is agency/district access still free for data-sharing agencies, or is it a paid subscription now?
> - For SaaS subscriptions specifically, are line items captured with quantity/seat count and
>   contract term, or only as lump-sum or not-to-exceed totals?
> - Can pricing be expressed on a per-seat-per-year basis?
>
> [Your name / org]

**Live test checklist once access exists (run against the pre-registered products once §1 of
`preregistration-template.md` is filled in):**
1. Are the pre-registered SaaS products present at line-item level with quantity?
2. Can results be expressed per seat per year, and does the contract term show?
3. Is there any contract-term, escalator or renewal-date field?
4. What share of the P0a sample's contracts appear at all? (This doubles as a seedability
   cross-check against criterion (b).)
5. Is agency/district access still free with data sharing, in writing?

Record the outcome in the `decision_record` against criterion (e) as met / not met / partial, with
the specific screen or answer as evidence — per the findings file's closing instruction.

---

## 4. Gluona / Colorado Empowered Learning call request (new finding, not in the original plan)

**Why this matters:** this is the one incidental finding that changes the plan's own assumptions —
a live, state-funded, buyer-side SaaS price benchmark combined with collective negotiation, already
operating in Colorado. It's effectively TEC's model, funded differently, and it's the second
real-world "did this work" data point after TEC itself. It's also a plausible partner or licensee,
not just a competitor to route around.

**Draft:**

> Subject: Learning from Colorado's Equitable EdTech Pricing program
>
> Hi — I'm building a project aimed at giving K-12 districts (starting outside Colorado) visibility
> into fair SaaS pricing, and I came across the Equitable EdTech Pricing / Gluona program. It looks
> like one of the only examples anywhere of this actually running at scale. Would you be open to a
> short call? I'd love to hear:
>
> - Roughly how many districts participate, and what savings you've seen in practice.
> - Whether there's any interest in expanding the model beyond Colorado, or licensing/partnering
>   with something outside the state.
> - What the state-funding structure looks like, and whether it's proven durable.
>
> Happy to work around your schedule.
>
> [Your name]

**What to do with the answer:** feed participation/savings numbers into the plan's §4.1 launch-state
re-rank (this is one more argument for *not* launching in Colorado — it'd be duplicating a state
that already solved this) and note whether a partnership conversation is worth having before or
after P0a concludes.

---

## Suggested sequencing

Send #1 (TEC founders) and #4 (Gluona) first — they're low-friction, likely to get a reply, and
don't require setting up a trial account. Use #2 and #3 (LearnPlatform / GovSpend demos) once you're
ready to actually evaluate them side by side, since a demo eats more of a rep's time and yours.
