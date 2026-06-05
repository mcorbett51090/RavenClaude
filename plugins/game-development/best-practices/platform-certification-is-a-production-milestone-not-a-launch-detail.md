# Platform certification is a production milestone, not a launch detail

**Status:** Absolute rule
**Domain:** Game production
**Applies to:** `game-development`

---

## Why this exists

First-party certification (Sony, Microsoft, Nintendo) and platform review processes (Apple App Store, Google Play) have rejection rates, revision cycles, and turnaround windows that most teams underestimate until they miss their first target launch date because of a certification failure. A certification rejection requires a fix, a new build, and a re-submission — adding 1–3 weeks to the timeline in the best case, much more in the worst. A studio that treats certification as a "launch detail" — something that happens after the game is "done" — has implicitly added a 2–6 week unconstrained buffer to their launch schedule. Building certification readiness as a named milestone, with explicit platform requirement checks and a pre-submission pass, converts that unknown buffer into a managed gate.

## How to apply

Add a "Certification Ready" milestone to the production schedule 4–6 weeks before the target launch date. Include platform requirement verification as explicit done criteria.

```
Certification-Ready milestone done criteria (console/PC example):

  1. Platform requirements review
    — First-party TRCs / TCRs downloaded and reviewed for current SDK version ✓/✗
    — All required system features implemented (cloud save, achievements, accessibility) ✓/✗
    — Age rating submitted (ESRB / PEGI / etc.) ✓/✗

  2. Build stability
    — Zero P0 / P1 crashes in 2-hour certification test session ✓/✗
    — Memory within platform limits on all target SKUs ✓/✗
    — Performance targets met on base hardware (PS5 / XSX / Switch baseline) ✓/✗

  3. Content compliance
    — Any user-generated content moderation systems in place (if applicable) ✓/✗
    — Online features / EULA / privacy policy current ✓/✗

  Timeline model:
    Target launch date: [T]
    Gold master / final submission: T minus 14 days (first-party console)
    Certification Ready milestone: T minus 35 days (allows one re-submission cycle)
    Pre-submission internal pass: T minus 42 days

  Mobile: adjust to platform review window (Apple: 3–7 days; Google: 1–3 days) — shorter
  window but the same "Cert Ready" milestone discipline applies.
```

**Do:**
- Download and review the current platform technical requirements before the Certification Ready milestone — requirements update between SDK versions.
- Include at least one re-submission buffer in the production calendar.
- Brief the QA team on certification test cases specifically (they are different from standard QA cases).

**Don't:**
- Treat platform submission as the last step on launch day — it is a milestone weeks before.
- Assume the previous project's certification requirements still apply — they update.
- Submit a build for certification that hasn't passed an internal certification test pass.

## Edge cases / when the rule does NOT apply

PC-only (Steam/itch.io) releases with no console or mobile targets have a lighter certification requirement (no TRCs, no first-party review) — Valve's review process is less formal. The milestone discipline still applies for timing; the checklist is shorter. Early Access launches on Steam may have different certification requirements than a 1.0 release.

## See also

- [`../agents/gamedev-producer.md`](../agents/gamedev-producer.md) — owns the production schedule and the Certification Ready milestone.
- [`./milestone-definitions-must-include-a-done-criteria-not-just-a-date.md`](./milestone-definitions-must-include-a-done-criteria-not-just-a-date.md) — the companion rule on making milestones real gates; certification is a classic example of a milestone that needs explicit done criteria.

## Provenance

Codifies the platform-certification-as-milestone discipline in game production. The launch-detail misclassification of certification is the most common root cause of console launch-date slippage; the 4–6-week-prior milestone is the standard corrective.

---

_Last reviewed: 2026-06-05 by `claude`_
