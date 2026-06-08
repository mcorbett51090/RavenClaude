---
description: "Verify keyboard operability and screen-reader parity hands-on with the assistive technology real users use. Reach for this on a parity question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Test assistive tech

You are running `/accessibility-engineering:test-assistive-tech` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Walk it by keyboard — No traps, visible focus, logical order, every control reachable and operable (§3 #3).
2. Test with a screen reader — Name, role, value, state changes, and live-region announcements conveyed correctly (§3 #3).
3. Cover the AT a population uses — Multiple screen readers/magnification/switch as scope demands; date the AT/browser versions (§3 #8).
4. Rank the gaps — Order AT-found defects by user-impact via `accessibility_calc.py remediation`.

## Output
An AT-session report naming the keyboard/screen-reader parity gaps automated tools missed, ranked by user-impact. See [`../skills/test-assistive-tech/SKILL.md`](../skills/test-assistive-tech/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
