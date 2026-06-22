---
name: design-moderation-policy
description: "Design a content-moderation policy from scratch — a policy taxonomy (categories + severity tiers), a proportional enforcement ladder (warn / limit / remove / ban), and a real appeal path — by traversing the enforcement decision tree. Reach for this when the user asks to design or review a moderation policy, or to map a violation to an action. Used by trust-safety-policy-lead (primary)."
---

# Skill: design-moderation-policy

> **Invoked by:** `trust-safety-policy-lead` (primary). Co-driven with `abuse-detection-engineer` when the policy needs a detector to operationalize it.
>
> **When to invoke:** "design a moderation policy for <surface>"; "what action should this violation earn?"; "review our enforcement ladder"; "is our appeals process due process?".
>
> **Output:** a policy taxonomy (categories + severity tiers) + a proportional enforcement ladder + an appeal path + the metric hooks to measure it, written into the [`content-policy-doc`](../../templates/content-policy-doc.md) template.

## Procedure

1. **Define the policy taxonomy first.** Name the violation categories (e.g. spam, harassment, fraud, graphic content, CSAM-class) and, within each, **severity tiers** (low / medium / high / critical). The taxonomy is the spine — an action with no category behind it is arbitrary.
2. **Write each category so a reviewer can apply it the same way twice.** Include a one-line definition, in/out-of-scope examples, and the signals that surface it. Ambiguous categories drive a high appeal-overturn rate downstream.
3. **Map each severity tier to a proportional action on the ladder.** Traverse [`../../knowledge/enforcement-decision-tree.md`](../../knowledge/enforcement-decision-tree.md): severity × user history → **warn → limit (rate-limit / de-amplify / restrict reach) → remove → suspend → ban**. Reserve the irreversible top rungs for clear, severe, or repeat cases.
4. **Attach an appeal path to every action.** Notice (what happened), a reason (which policy, which tier), and a route to contest with a human-review SLA. An action with no appeal is the anti-pattern this team prevents.
5. **Define the measurement hooks now, not later.** For each category, name the prevalence target, the enforcement precision/recall floor, the time-to-action SLA, and the appeal-overturn alarm threshold — these feed [`measure-enforcement-quality`](../measure-enforcement-quality/SKILL.md).
6. **Mark the seams.** PII/data-handling in the policy → `data-governance-privacy`; account-level abuse → `security-engineering`; the detector → `abuse-detection-engineer`.

## Worked example

> User: "Design a spam policy for our marketplace listings."

- **Taxonomy:** category = "spam / deceptive listing"; tiers = low (keyword stuffing) / medium (duplicate listings) / high (phishing / payment-diversion).
- **Ladder:** low → warn + de-rank; medium → limit (cap active listings) + remove the duplicates; high → remove + suspend, ban on repeat.
- **Appeal:** every action notifies the seller with the tier and a one-click contest routed to a human within the SLA (24h for suspend/ban).
- **Measurement:** prevalence of spam impressions per 10k listing views (not "listings removed"); precision floor 0.95 on the auto-remove band; overturn-rate alarm at >10%.

## Guardrails
- Never ship an enforcement action without an appeal path (due process is not optional).
- Never let the action exceed the severity — proportionality is the rule, not the exception.
- Define prevalence and overturn-rate measurement up front; a policy you can't measure you can't tune. See [`../../knowledge/trust-safety-metrics.md`](../../knowledge/trust-safety-metrics.md).
