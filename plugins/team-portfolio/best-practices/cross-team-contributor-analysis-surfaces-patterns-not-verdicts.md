# Contributor analysis surfaces patterns for conversations, not verdicts

**Status:** Pattern
**Domain:** Team portfolio / contributor analysis
**Applies to:** `team-portfolio`

---

## Why this exists

The `cross-team-contributor-analysis` skill produces a matrix of GitHub activity per person per repo. This data is valuable for a supervisor who wants to understand team distribution and spot blocked or siloed contributors. It is not a performance evaluation tool. The difference matters: presenting a contributor matrix to a team as "your performance numbers" changes behavior in ways that harm the team (optimizing for observable commits over high-value invisible work). Presenting it to a supervisor as a conversation-starting signal produces the right outcome (check in with the person, understand the context, then act).

## How to apply

When producing or presenting contributor analysis output:

1. **Frame the output as "signals worth checking in about," not "scores."**
2. **Always include the disclaimer** (see `activity-counts-are-not-performance-metrics.md`) in any supervisor-facing report.
3. **Surface patterns to the supervisor in private**, not in a shared team report. A contributor matrix shared to the whole team creates social pressure to inflate counts.
4. **Pair every pattern with a "possible explanation" list** before the supervisor reaches out:

```
Pattern: Alex has near-zero activity this week.
Possible explanations before concluding "low productivity":
  - On approved PTO or sick leave
  - Blocked on a dependency in another team
  - Work is happening in a tool not captured by GitHub (Confluence, Figma, long-running infra work)
  - The new repo where they are working is not yet in team-portfolio.json
  - Paired with another developer (their commits appear under the pair's login)
```

Only after eliminating the innocent explanations should the supervisor treat the pattern as worth a performance conversation.

**Do:**
- Present contributor patterns as a prompt for a 1:1, not as a finding for a performance record.
- Acknowledge when activity in one repo is structurally different (documentation vs. high-velocity service repo) before comparing counts across repo types.

**Don't:**
- Sort the team by activity count in a public dashboard view.
- Use activity counts from the portfolio output as a factor in a formal performance review without substantial qualitative overlay.

## Edge cases / when the rule does NOT apply

- The supervisor is using the output in a self-check context ("am I spreading my attention across the repos appropriately?") — self-directed reflection on one's own activity counts is a legitimate use with no performance-framing risk.

## See also

- [`../skills/cross-team-contributor-analysis/SKILL.md`](../skills/cross-team-contributor-analysis/SKILL.md) — the analysis skill that produces the patterns this rule governs
- [`../best-practices/activity-counts-are-not-performance-metrics.md`](./activity-counts-are-not-performance-metrics.md) — the upstream rule this one operationalizes for the contributor analysis context

## Provenance

Companion to `activity-counts-are-not-performance-metrics.md`, applied specifically to the contributor analysis context. The distinction between "pattern for a conversation" and "verdict for a record" is behavioral, not technical — it requires an explicit framing rule in addition to the data-labeling rule.

---

_Last reviewed: 2026-06-05 by `claude`_
