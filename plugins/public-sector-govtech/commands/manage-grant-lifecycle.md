---
description: "Step through the full federal grant lifecycle for a specific award: post-award setup, restricted-fund structure, budget modification analysis, progress and financial reporting, subrecipient monitoring, and single-audit readiness — all framed against 2 CFR 200 (Uniform Guidance)."
argument-hint: "[lifecycle stage and award context, e.g. 'post-award setup for HHS SAMHSA grant $500K, 2 CFR 200 applies, one subrecipient']"
---

You are running `/public-sector-govtech:manage-grant-lifecycle`. Use the `grants-management-analyst`
discipline and the `grants-management` skill.

## Steps

1. **Stage determination:** based on the argument, identify the current lifecycle stage
   (pre-award / post-award setup / ongoing management / closeout / single-audit readiness).
   If no argument is given, ask which stage applies.

2. **Notice of Award review (post-award):** confirm award number, CFDA/ALN, period of performance,
   approved budget by object class, special conditions requiring prior approval. Flag any special
   conditions that require immediate action.

3. **Restricted-fund setup:** recommend a restricted-fund account coding structure and document the
   commingling prohibition (2 CFR 200.302(b)(3)).

4. **Budget modification analysis (if applicable):** determine whether the requested change requires
   prior approval under 2 CFR 200.308. Draft the prior-approval request letter if needed.

5. **Single-audit readiness (if applicable):** draft the SEFA listing, identify Type A programs
   (≥ $750K threshold), and produce an internal-controls gap list against the OMB Compliance
   Supplement for the major program.

6. Fill `templates/grant-narrative.md` sections relevant to the current stage, then emit the
   Structured Output block with handoffs (govtech-delivery-lead if the grant funds a technology program;
   gov-accessibility-and-records-advisor for any public-facing deliverables in scope).
