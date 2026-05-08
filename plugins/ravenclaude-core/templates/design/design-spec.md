# Design Spec — *<artifact name, e.g. "Partner onboarding welcome screen" or "Q3 variance dashboard">*

> **Audience:** the implementer (frontend-coder, the user building a Power App, the user assembling a slide deck).
> **Length target:** 1–2 pages. If it's longer, a section probably belongs in a separate spec.
> **BLUF:** the *User task* line below should make it obvious whether this design fits the situation. If it doesn't, stop and rewrite the user task.

**Designer:** *<your name or "designer agent run on YYYY-MM-DD">*
**Date drafted:** YYYY-MM-DD
**Status:** draft / in review / approved / superseded

---

## Artifact
*<One sentence — what is being designed and for what platform / surface. E.g. "A single Power Apps screen for partner CSMs to log a touchpoint in under 30 seconds.">*

## User task
*<One sentence — what the user is trying to accomplish on this artifact. If you cannot write this in one sentence, the design isn't ready.>*

## Audience & context
- **Who:** *<role / persona — e.g. "EdTech Customer Success Manager, 1–3 years tenure">*
- **Device / surface:** *<phone in field, desktop in office, projected slide, printed handout, …>*
- **Mindset:** *<hurried, exploratory, stressed, confident, distracted, …>*
- **Frequency:** *<every day / once a quarter / first-time-only — drives how much the user can be expected to learn>*
- **Reading-level target:** *<8th grade for general; lower for stressed-user contexts; higher only when the audience is technical>*

## Information hierarchy
1. **Primary** — *<the one thing the user came for; everything else supports it>*
2. **Secondary** — *<supports the primary>*
3. **Tertiary** — *<reference data, settings, less-frequent actions — usually too much of this on first draft>*

## Layout (wireframe)

```
+----------------------------------------------+
|  [page title]                       [avatar] |
+----------------------------------------------+
|                                              |
|   < Primary content / primary action >       |
|                                              |
|   [ Secondary controls ]                     |
|                                              |
+----------------------------------------------+
|  [tertiary nav / footer]                     |
+----------------------------------------------+
```

*<Replace the skeleton with the actual layout. Keep it ASCII or simple boxes — pixel fidelity comes later, in the production tool.>*

## Flow (if multi-step)

```
[Entry] → [Step 1: ...] → [Step 2: ...] → [Confirmation]
                ↓
            [Error: ...] → [Recovery: ...]
```

*<Skip this section entirely if the artifact is a single screen / single page.>*

## Visual direction
- **Type scale:** *<heading / body / caption sizes — match existing project type scale if one exists>*
- **Color usage:** *<where color signals state (success / warning / error) vs. where it's decoration. Decoration should be near zero.>*
- **Iconography:** *<library or convention to follow — e.g. "Power Apps default icon set," "Heroicons outline">*
- **Voice / microcopy notes:** *<tone, key phrases the audience expects, words to avoid>*

## Accessibility check
See [`accessibility-checklist.md`](accessibility-checklist.md) — tick each box or flag what's needed.

- [ ] Text contrast ≥ 4.5:1 for body, ≥ 3:1 for large text and UI components.
- [ ] Touch targets ≥ 44×44 px on mobile.
- [ ] All interactive elements keyboard-reachable with visible focus state.
- [ ] No information conveyed by color alone.
- [ ] Reading level appropriate for the audience.
- [ ] Alt-text plan for every non-decorative image.
- [ ] Error messages name the problem AND the fix.

## Open questions for the Team Lead
- *<question that blocks finalizing — e.g. "Is the partner-tier badge required on this screen, or only on the partner detail page?">*

## Hand-off notes for the implementer
- *<Gotchas — non-obvious decisions, what NOT to change without coming back to design>*
- *<Rationale for any unusual choice — so the implementer doesn't "fix" it>*
- *<Anything platform-specific — e.g. "Power Apps gallery control needs a fixed height; don't replace with a flex container">*

---

> **Hard rule:** the implementer executes this spec; the spec doesn't get rewritten by the implementer mid-build. If a constraint forces a change, the implementer surfaces it to the Team Lead, who routes the question back to the designer.
