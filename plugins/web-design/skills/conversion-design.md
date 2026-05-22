---
name: conversion-design
description: Design and audit conversion-focused screens — funnel definition, friction-vs-trust balance, form field selection (every field is a cost), one CTA per screen discipline, social-proof placement, microcopy patterns, and the conversion-rate measurement plan. Reach for this skill when designing or reviewing a landing page, sign-up flow, checkout, or any "convert visitor → action" screen. Used by `ux-designer` (primary) + `content-strategist`.
---

# Skill: conversion-design

**Purpose:** Design and audit conversion-focused screens. Used by `ux-designer` (primary) and `content-strategist` for the copy + microcopy layer.

Conversion design is the discipline of removing everything that isn't moving the user toward the action. It's a subtractive craft. Most "low-converting" pages are over-designed: too many CTAs, too many form fields, too many competing trust signals, too much hedging copy. The fix is rarely "add more"; it's "cut the noise so the signal is unmistakable."

## When to use

- Designing a new landing page, sign-up flow, pricing page, or checkout
- Auditing a screen with a known conversion problem (analytics shows funnel drop)
- Building a microsite or campaign page where the entire purpose is one action
- Reviewing a redesign before launch — the "is this still a conversion screen?" sanity check

## 1. Funnel definition (the load-bearing step)

Before you touch the design, write the funnel out:

```
Stage              Surface(s)                      Primary event              Friction sources
─────────────────  ──────────────────────────────  ─────────────────────────  ────────────────────────
Awareness          Ads, organic, social            Page view                  Targeting accuracy
Consideration      Landing, product, pricing       Scroll-depth, video-play   Clarity, trust, fit
Intent             CTA click                       click_primary_cta          CTA copy, position, count
Conversion         Form, checkout, sign-up         submit_success             Field count, friction
Activation         Onboarding, first-value         first_value_event          Time-to-value
```

Every screen owns **one** stage. A pricing page that tries to also do "awareness" by re-explaining the product fails at both. Decide which stage the screen serves, then design for that stage's job.

## 2. One thing per screen

The strongest predictor of conversion: how clear is the next action? Apply ruthlessly:

- **One primary CTA per screen** (max two, if and only if the two CTAs serve two genuinely distinct segments — e.g. "Start free trial" + "Talk to sales" for self-serve vs enterprise)
- **No competing CTAs** within the same viewport. Newsletter signup in the footer doesn't compete with the primary CTA above; a "subscribe to our blog" mid-hero does.
- **Repeat the same CTA** through the page (3–5 placements is normal for a long page) — don't invent new CTAs, repeat the one
- **Reference aesthetic:** Linear, Cal.com, Resend, Vercel landing pages — one CTA, repeated, page-length-agnostic

## 3. Form field reduction

Every form field is a cost. Industry rule of thumb: each additional required field reduces completion by ~5–7%. The discipline:

- **What does the business genuinely need to fulfill this action?** That's the minimum.
- **What's nice to have?** Move it to a post-conversion progressive-profiling step.
- **What does Sales want?** Sales wants more; the funnel wants less. The funnel wins unless Sales can show data otherwise.
- **Replace** dropdowns with smart defaults (geo-IP for country, browser-locale for language)
- **Replace** "confirm email" with email validation
- **Replace** "create password" with magic-link auth where the security model allows
- **Use a single name field** ("Name") not first / last / middle unless you legitimately need them apart

### Sign-up form field benchmarks (2026, self-serve SaaS)

| Field count | Typical completion | Use case |
|---|---|---|
| 1 (email only) | 35–50% | Newsletter, waitlist, magic-link sign-up |
| 2–3 | 20–30% | Standard SaaS sign-up |
| 4–6 | 10–18% | "Request a demo" / B2B with qualification |
| 7+ | < 10% | You are losing money on this form |

## 4. Trust signals — when to use which

Trust signals are not interchangeable. Pick by the visitor's specific objection:

| Trust signal | Best for | Anti-pattern |
|---|---|---|
| **Customer-logo bar** | "Is this legit / is anyone using it" | Logos of customers who churned, or who never used the paid tier |
| **Testimonial quote** | "What's it actually like to use" | Anonymous quotes; "John D., Marketing Manager" — needs full name + photo + company |
| **Case study** | "Will this work for someone like me" | Generic case studies; the visitor needs to see their own segment |
| **Third-party rating** (G2, Capterra) | "How does this stack up vs alternatives" | Showing a 4.2 if the category leader has 4.8 |
| **Press / award badges** | "Have credible outsiders endorsed this" | Self-awarded badges; expired press; "as seen on" without a real story |
| **Stat / proof point** ("Trusted by 10k+ teams") | "Is there scale" | Round numbers with no source; vague "thousands of customers" |
| **Security / compliance badges** (SOC 2, GDPR) | "Can I get this past procurement" | Decorative — only when the buyer actually requires it |
| **Founder / team photo** | Small-team transparency, indie SaaS | Stock photos masquerading as the team |

**Placement rule:** trust signals belong next to the objection they answer. Logos near the hero (legitimacy), testimonials near the long-form pitch (depth), security badges near the pricing / signup (procurement objection).

## 5. CTA copy patterns

Cleverness loses to specificity. The best-performing CTAs say what happens next.

| Generic | Specific | Why specific wins |
|---|---|---|
| "Get started" | "Start free trial" | Reduces ambiguity about commitment |
| "Submit" | "Send message" | Names the outcome |
| "Learn more" | "See pricing" / "Read the docs" | Names the destination |
| "Sign up" | "Create free account" | Reassures it's free |
| "Click here" | (rewrite the surrounding sentence) | "Click here" is a 1998 anti-pattern |
| "Buy now" | "Add to cart" / "Subscribe — $X/mo" | Sets the expectation |

**Microcopy under the CTA earns its space.** "No credit card required." "Free for 14 days, no questions." "We'll never share your email." A single 8-word reassurance under the button can recover meaningful conversion.

## 6. Pricing-page conversion patterns

Pricing is its own discipline; the consensus 2026 patterns:

- **Three tiers, middle is the recommended default** — visually emphasized (border, badge, slightly larger card). Anchors the decision around the middle, where most users land.
- **Annual / monthly toggle** — discount the annual; show the per-month-when-billed-annually number
- **Enterprise tier "Contact us"** — no price; this is the qualification gate
- **Feature comparison table below the cards** — for the careful comparison shoppers
- **FAQ below the table** — handles the standard objections (refund policy, cancellation, security)
- **Same CTA on every tier** ("Start free trial" or "Get started") — don't make the user think about which button is right

## 7. Error states and inline validation

Errors as helping, not punishing. Patterns that work:

- **Inline validation on blur**, not on submit. Tell the user immediately, not at the end.
- **Specific error copy** — "Email already in use — sign in instead?" not "Invalid input"
- **Recovery action in the error** — if email already exists, link to sign-in *from inside the error*
- **Never red-as-the-only-signifier** — icon + color (§3 #10 in plugin CLAUDE.md)
- **Field-level errors at the field**, not in a global banner above the form
- **Preserve user input on error** — never blank a form on submit failure

## 8. Measurement plan

A conversion design isn't done until the measurement is wired:

- **Event taxonomy** — what events fire on the funnel? `page_view`, `cta_click`, `form_field_focus`, `form_submit`, `submit_success`, `submit_error`
- **Segment by source** — paid vs organic vs direct vs referral; conversion rates can differ 5x across sources
- **Funnel definition in the analytics tool** — declared once, used in every report
- **Cohort by week** — daily noise is high; weekly cohort smooths the signal
- **A/B test only what's likely to move the needle** — CTA copy, hero headline, form-field count. Don't A/B-test button colors. Don't A/B-test things that affect < 5% of visitors.
- **Statistical significance gate** — don't ship a winner with p > 0.05. Plan the test duration upfront based on expected effect size and baseline traffic.

## Hygiene checklist

- [ ] Funnel stages defined; this screen owns exactly one stage
- [ ] One primary CTA (or two with documented segment justification)
- [ ] CTA copy is specific (names outcome or destination)
- [ ] Form field count is the minimum that fulfills the action
- [ ] Trust signals placed adjacent to the objection they answer
- [ ] Inline validation on blur; field-level errors; user input preserved on error
- [ ] No dark patterns (pre-checked boxes, hidden cost, decoy options, fake scarcity)
- [ ] Mobile experience verified (CTAs above fold on smallest target device)
- [ ] Event tracking wired before launch, not after
- [ ] Funnel baseline measured before any A/B test starts

## Anti-patterns

- **Vague CTAs** — "Learn more", "Get started" without context, "Submit"
- **Dark patterns** — pre-checked newsletter consent, hidden recurring charges, "confirmshaming" ("No thanks, I don't want to save money"), fake countdown timers, fake "X people viewing this now"
- **Two competing primary CTAs** with equal visual weight in the same viewport
- **Newsletter modal on first scroll** — interrupting the user before they've seen the value
- **Carousel / slider as the hero** — fights for attention with itself; clicks are vanishingly rare on slides 2+
- **Long-form pitch with no progressive disclosure** — every section visible at once means none of them get read
- **Pricing page with five tiers** — paralysis. Three is the maximum, four if there's a genuine enterprise tier
- **"Contact sales" as the only path** for a product priced under $5k/year — self-serve buyers bounce
- **Mid-page "subscribe to our newsletter" form on a sign-up page** — competes with the primary action
- **Lorem ipsum in launched mocks** — hides the real layout problem caused by realistic copy lengths
- **Form labels as placeholders only** — accessibility broken, plus the label vanishes when the user types
- **No empty / loading / success state designs** — only the happy path is mocked

## See also

- Template: [`../templates/design-brief.md`](../templates/design-brief.md)
- Skill: [`./content-audit.md`](./content-audit.md)
- Skill: [`./information-architecture.md`](./information-architecture.md)
- Knowledge: [`../knowledge/design-references.md`](../knowledge/design-references.md)
- Agent: [`../agents/ux-designer.md`](../agents/ux-designer.md)
- Agent: [`../agents/content-strategist.md`](../agents/content-strategist.md)
