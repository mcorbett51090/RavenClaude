# Accessibility Checklist — *<artifact name>*

> **Use this as a gate, not a goal.** Every item is required at the WCAG AA level for any artifact that ships to users. If you're going to ship something failing one of these, name the failure explicitly and the timeline to fix.

**Reviewer:** *<your name or "designer agent">*
**Date:** YYYY-MM-DD
**Artifact:** *<screen / page / slide / dashboard / handout — and where it lives>*
**Target standard:** WCAG 2.1 AA (default) / *<other if mandated>*

---

## Vision

- [ ] **Text contrast — body text** ≥ 4.5:1 against its background.
- [ ] **Text contrast — large text (≥ 18 pt or ≥ 14 pt bold)** ≥ 3:1.
- [ ] **UI component contrast** (buttons, inputs, focus rings, icons that convey meaning) ≥ 3:1 against adjacent colors.
- [ ] **No information conveyed by color alone.** Status, errors, required fields use icon + text + color, not just color.
- [ ] **Resizable text.** Layout doesn't break at 200% browser zoom.
- [ ] **Avoid pure red/green pairings** for critical state distinctions (deuteranopia is the most common color-vision deficiency).

## Motor

- [ ] **Touch targets ≥ 44×44 px** on mobile / touch surfaces (Apple HIG / Material guidance).
- [ ] **Click targets ≥ 24×24 px** on desktop, with adequate spacing.
- [ ] **No precision-required gestures.** No "draw a circle to confirm" — provide a button alternative for any drag / pinch / multi-touch action.
- [ ] **Forgiving input.** Form fields tolerate spaces, dashes, and capitalization variants users naturally type (especially for phone numbers, emails, partner IDs).

## Keyboard / focus

- [ ] **All interactive elements reachable via Tab** in a logical order.
- [ ] **Visible focus state** on every interactive element (don't `outline: none` without replacing it).
- [ ] **Focus order matches visual order.**
- [ ] **No keyboard traps.** User can always Tab out of any component.
- [ ] **Skip-to-content link** for keyboard users on long pages.

## Screen reader / structure

- [ ] **Semantic structure.** One `<h1>` per page; headings nest without skipping levels.
- [ ] **Landmarks defined** (`<header>`, `<nav>`, `<main>`, `<footer>`, or ARIA equivalents).
- [ ] **Alt text on every meaningful image.** Decorative images have empty alt (`alt=""`).
- [ ] **Form fields have associated labels.** Placeholder text is not a substitute for a label.
- [ ] **Buttons describe their action**, not just "click here." (`aria-label="Approve partner Acme Corp"`, not `aria-label="Approve"`.)
- [ ] **Tables have headers.** Data tables use `<th scope>`; layout tables are replaced with CSS.
- [ ] **Live regions announced** for async updates (loading states, success / error toasts).

## Cognitive

- [ ] **Reading level appropriate for audience.** Default 8th grade for general users; lower for stressed-user contexts (oncall, error recovery, financial-emergency screens).
- [ ] **Plain language.** Define jargon on first use; prefer short sentences.
- [ ] **Error messages name the problem AND the fix.** *"Email already in use — sign in instead?"* beats *"Validation error 422."*
- [ ] **Consistent placement.** The same action lives in the same place on every screen.
- [ ] **No unexpected context changes** when a control receives focus or a value changes.
- [ ] **Time limits explained and extendable** when present.

## Content / media

- [ ] **Captions on video.** Auto-generated is acceptable for internal; reviewed for external.
- [ ] **Transcripts for audio-only content.**
- [ ] **No auto-playing audio**, especially with sound.
- [ ] **Reduced-motion option respected** (`prefers-reduced-motion`) — animations can be paused or skipped.

## Sign-off

| Check | Status | Notes |
|-------|--------|-------|
| All items above ticked or explicitly waived | ☐ | *<who approved any waivers>* |
| Tested with a screen reader | ☐ | *<which one — VoiceOver, NVDA, JAWS — and which screens>* |
| Tested keyboard-only | ☐ | |
| Tested at 200% zoom | ☐ | |
| Tested on a real mobile device (not just emulator) | ☐ | *<which device>* |

---

> **Waiver rule:** if you ship with an item un-ticked, write a one-line note here naming what's failing, who approved the ship, and the date by which it'll be fixed. *"Won't fix"* is not an acceptable note for an external-facing artifact.
