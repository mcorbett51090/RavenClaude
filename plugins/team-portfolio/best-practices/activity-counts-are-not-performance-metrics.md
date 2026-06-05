# GitHub activity counts are an activity signal — not a performance metric

**Status:** Absolute rule
**Domain:** Team portfolio / report ethics
**Applies to:** `team-portfolio`

---

## Why this exists

GitHub commit, PR, and issue counts can be observed mechanically. They cannot, by themselves, measure productivity, quality, or contribution value. A developer who ships one well-reasoned architectural change may produce fewer events than a developer churning incremental hotfixes. A developer who spends most of their time in architecture reviews, design docs, and unblocking others will have fewer observable events than one who writes code all day. Presenting raw counts as productivity measures in a supervisor report creates perverse incentives, penalizes high-value low-visibility work, and erodes team trust.

## How to apply

In every portfolio report and dashboard:
- Label the counts as "observable GitHub activity" not "productivity" or "output."
- Include a prominent disclaimer: "Activity counts reflect observable GitHub events (commits, PRs, issues, reviews). They do not capture design work, mentoring, meetings, blocked time, or contributions in other tools."
- Surface the counts as a starting point for a conversation, not a conclusion.

In the optional narrative layer (`templates/activity-narrative.md`): use this for context that the counts can't carry — a sprint where the team was heads-down on design, a week where a P0 incident absorbed all capacity, a planned quiet period before a major release.

**Do:**
- Note unusually high or low counts as worth a check-in, not as a finding.
- Acknowledge when activity in a repo is structurally lower (a documentation repo vs. a high-velocity API repo).

**Don't:**
- Rank team members by total activity count.
- Use the portfolio output in a performance review without substantial qualitative context.
- Present zero-activity weeks as evidence of disengagement without checking PTO, blocked status, or work happening in other tools.

## Edge cases / when the rule does NOT apply

- The supervisor explicitly uses the portfolio output as a lightweight health check signal in a 1:1 context, not as a formal evaluation — the counts serve as a conversation opener and both parties understand the limitations. This is the intended use case.

## See also

- [`../skills/cross-team-contributor-analysis/SKILL.md`](../skills/cross-team-contributor-analysis/SKILL.md) — the analysis skill that surfaces patterns and explicitly warns against performance framing
- [`../CLAUDE.md`](../CLAUDE.md) — §4 house opinion #1 (GitHub is the source of truth) and the narrative layer as the context layer

## Provenance

Derived from the broader principle that observable proxy metrics (commit counts, lines of code) are not productivity metrics — a well-established principle in engineering management. This plugin's data is exclusively observable GitHub events; that framing must be explicit in every consumer-facing output.

---

_Last reviewed: 2026-06-05 by `claude`_
