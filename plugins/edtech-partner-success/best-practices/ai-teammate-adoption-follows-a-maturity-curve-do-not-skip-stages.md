# AI teammate adoption follows a maturity curve — do not skip stages

**Status:** Pattern
**Domain:** EdTech PSM operations
**Applies to:** `edtech-partner-success`

---

## Why this exists

ChurnZero's AI Marketplace and Gainsight's AI agents have made AI-assisted CS workflows a real operational tool, not a roadmap item. PSMs adopting AI teammates (for signal triage, meeting recap drafts, follow-up automation) frequently make two symmetric mistakes: (1) over-adopting — letting AI-generated content reach partners unreviewed — or (2) under-adopting — treating every AI draft as untrustworthy and manually rewriting everything, which eliminates the efficiency gain. Both errors come from skipping the maturity-curve stages. Moving from None → Piloting → Standardized → Differentiated → Outcome-architect in sequence — rather than jumping from None to Standardized — prevents both the credibility failure and the efficiency loss.

## How to apply

Assess the PSM team's current AI adoption stage and apply stage-specific guidance. Do not skip from Piloting to Differentiated without a Standardized stage.

```
AI teammate adoption maturity curve:
  Stage 1 — None: No AI tools in the CS workflow. Entry point for most PSMs today.
    Next move: identify one low-risk, high-repetition task (meeting recap drafts, follow-up email drafts)
    and pilot with a 100% human-review gate.

  Stage 2 — Piloting: AI draft exists; PSM reviews and rewrites most of it.
    Next move: identify which draft types consistently need minimal editing (< 20% change rate)
    and create a standardized review checklist for those.

  Stage 3 — Standardized: AI drafts pass through a checklist review, not a full rewrite.
    Next move: use AI for signal triage (which accounts need attention today) with a
    spot-check validation — PSM reviews the triage output, not every individual signal.

  Stage 4 — Differentiated: AI handles signal triage and routine drafts; PSM focuses on
    high-judgment interactions (QBRs, recovery conversations, expansion pitches).
    Next move: build a feedback loop so AI errors surface and the checklist improves.

  Stage 5 — Outcome-architect: PSM designs the AI workflow and the quality gates;
    the AI handles the volume layer; the PSM handles the relationship layer.

Hard rules at every stage:
  — AI-generated partner-facing content requires a human review before sending
  — AI does NOT touch FERPA-restricted data or student-level records
  — AI does NOT decide on escalation — that is always a human judgment
```

**Do:**
- Assess current stage honestly before adopting new AI tools.
- Introduce one AI-assisted workflow at a time and build the review checklist before expanding.
- Document which AI outputs are "route to human" vs. "checklist-review" vs. "safe to expedite."

**Don't:**
- Send AI-drafted partner-facing content without human review at any stage.
- Use AI tools that require FERPA-restricted student data to generate outputs.
- Let AI decide when to escalate a partner risk — escalation thresholds are a human judgment.

## Edge cases / when the rule does NOT apply

Internal-only outputs (draft agenda, summary of a call recording, meeting notes) have a lower bar for human review than partner-facing content. An AI-generated draft QBR structure that a PSM then personalizes is lower risk than an AI-drafted customer email sent without review.

## See also

- [`../agents/partner-success-manager.md`](../agents/partner-success-manager.md) — the primary consumer of AI-teammate tools in the PSM workflow.
- [`../agents/learning-analytics-analyst.md`](../agents/learning-analytics-analyst.md) — designs and interprets signal-triage outputs that AI tools may assist with.

## Provenance

Grounded in the plugin's knowledge file `ai-teammate-adoption-psm-self.md` (last reviewed 2026-06-04). The maturity-curve framing is adapted from the ChurnZero AI Marketplace and Gainsight AI adoption patterns; the stage definitions reflect the PSM community's observed adoption arc.

---

_Last reviewed: 2026-06-05 by `claude`_
