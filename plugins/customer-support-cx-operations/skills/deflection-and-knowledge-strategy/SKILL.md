---
name: deflection-and-knowledge-strategy
description: "Run a KB-as-product audit, build a self-service deflection strategy, design AI-deflection intent coverage, and audit macros for hygiene — all grounded in ticket-volume demand signals rather than editorial intuition."
---

# Deflection and Knowledge Strategy

**Purpose:** turn the knowledge base from a static document library into a maintained product,
identify the highest-ROI deflection opportunities from ticket data, and design the content and
intent-coverage plan that makes self-service actually resolve contacts — not just redirect them.

## The operating loop

1. **Map contact volume to content coverage.**
   Pull the top contact categories by volume (30-day window minimum). For each category: does a
   KB article exist? Is it findable? Does it resolve the contact without an agent? Flag the gaps.

2. **Score deflectability.**
   For each gap category: is the resolution scripted (high deflectability) or judgment-intensive
   (low deflectability)? Use `volume × deflectability score` as the prioritization signal.
   Fully scripted + high volume → first content priority.

3. **Estimate deflection ROI.**
   Use `scripts/cx_calc.py deflection-roi` — inputs: deflectable volume, cost per contact, and
   expected containment rate. This gives the financial case for content investment.

4. **Build the content roadmap.**
   For each high-priority gap: write an article brief (title, intent, resolution steps, not-covered
   scope, owner, review cadence). Treat this as a product backlog sprint, not an editorial queue.

5. **Design AI-deflection intent taxonomy.**
   Classify intents into three tiers:
   - **Fully automatable:** high-volume, scripted resolution, low blast-radius (order status,
     password reset, account information). Bot handles end-to-end.
   - **Semi-automatable:** disambiguation required before resolution (billing dispute, subscription
     change). Bot gathers context, humans close.
   - **Must-escalate:** sensitive (legal, safety, account termination), or confidence below threshold.
     Human required; bot opens and routes only.
   Write the handoff spec for each tier (trigger condition + routing target + context handoff format).

6. **Audit macros and canned responses.**
   For each macro: (a) does it contain a hardcoded customer-specific fact without a merge-field
   placeholder? (PII risk) (b) does it return an unconditional "we cannot help" wall? (wall risk)
   (c) is the usage rate below 5% in the last 30 days? (dead macro). Flag, prune, or fix.

7. **Set a KB governance model.**
   Every article needs an owner, a review cadence (quarterly minimum for high-traffic articles),
   and a staleness policy (auto-flag articles older than 90 days with no review if traffic > X/month).

## Anti-patterns

- Measuring deflection by containment rate without verifying resolution quality.
- A KB article that ends with "contact support" for a fully self-serviceable issue.
- An AI deflection flow with no handoff path for low-confidence intents.
- A macro audit that checks formatting but not PII or wall language.
- A content roadmap driven by agent requests rather than ticket-volume demand signals.

## Output

A KB audit report with a prioritized content roadmap (volume × deflectability ranked); a
deflection-ROI estimate; an intent taxonomy with handoff spec; and a pruned macro library with a
governance process. Use
[`../../templates/`](../../templates/) for the artifact shape and
[`../../scripts/cx_calc.py`](../../scripts/cx_calc.py) for all ROI calculations.
