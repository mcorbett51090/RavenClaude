---
name: visual-builder
description: Make a builder — form, contact card, Wallet pass, page or email — visually appealing and easy for owners. Covers editor layout, a live preview rendered by the same code as the output, insert and reorder without dragging, simple and advanced modes, undo and autosave, draft and publish with blast radius, templates and constraint-aware warnings.
---

# Skill: visual-builder

**Purpose:** the owner should feel they are editing the real thing, never filling in a settings page — and should
never be able to publish something that breaks or that the output cannot show. Primary agents: `ux-designer`
(layout, modes, onboarding), `visual-designer` (theme, motion, selection states), `frontend-implementer`
(preview, drag and drop, undo, autosave), `accessibility-auditor` (keyboard and non-drag paths).

Backing knowledge: [`../../knowledge/visual-builder-ux-2026.md`](../../knowledge/visual-builder-ux-2026.md).
Domain rules: forms → [`form-builder`](../form-builder/SKILL.md); Wallet passes and contact cards → core's
[`wallet-passes`](../../../ravenclaude-core/skills/wallet-passes/SKILL.md) (`pass-builder.md`, `pass-types.md`,
`contact-card-vcard.md`). Craft bar → [`interface-craft`](../interface-craft/SKILL.md).

## Procedure

### 1. Decide what the preview is

- Render the preview with the **same code** that renders the published output (the form renderer, the card page,
  the pass compiler's placement plan). Two renderers drift, and the owner learns not to trust the preview.
- Where the output belongs to someone else's renderer (Wallet, an email client), say "approximation" on the
  preview and offer **test-issue to my own device** as the last step before publish.
- Multi-target outputs get a preview strip (iPhone new and old OS, Watch, Android; or phone and desktop), each with
  "not shown here" badges for content that will not appear there.

### 2. Lay out the editor

- Controls left, live preview right (sticky on desktop; a Preview tab on phones). An inspector opens on selection
  with **Basic** visible and **Advanced** collapsed. Two disclosure levels, no more.
- A left rail with **Add** (palette grouped by purpose) and **Outline** (tree; reorder here too).
- Onboarding in the order the owner thinks (for a card: name → contact → company, title, website → logo →
  photo → colour and layout). Templates first: "Blank · Template · Duplicate".

### 3. Make every action reachable without dragging

- Click a palette item to insert after the selection. Drag is a bonus layer (Pragmatic drag and drop is about
  7 KB gzipped for a vanilla DOM; dnd-kit DOM if you want keyboard dragging out of the box at ~36 KB).
- Every item's handle opens "Move up · Move down · Move to…"; announce the move with the item name and new position;
  return focus to the handle. Keyboard shortcuts with `aria-keyshortcuts`.

### 4. Undo, autosave, publish

- Commands as patches with inverses; coalesce keystrokes per field; never record selection.
- Autosave the draft 1–2 s after the last change with a revision check; a conflict asks instead of overwriting.
- The header always says the state: "Saved · Unpublished changes · Affects N items".
- Publish shows a short diff, calls out destructive changes, and states the blast radius (how many cards,
  passes or live forms change).

### 5. Make it beautiful without making it fragile

- Theme from brand tokens; check text at 4.5:1 and borders, focus rings and marks at 3:1 **while the owner picks**,
  auto-adjust with a note. Offer a brand colour suggested from the uploaded logo.
- Calm selection (one item, clear outline), hover that never shifts layout, motion under 300 ms on transform and
  opacity, reduced-motion respected.
- Constraint-aware warnings inline as the owner types: a pass field that will be dropped, a contrast pair that
  fails, a logic rule that can never fire, an image below the slot's minimum.

### 6. Verify on the rendered builder

| Check | Pass condition |
|---|---|
| Preview fidelity | preview and published output come from one renderer; a planted difference is caught |
| Non-drag path | the whole builder works with a mouse and no dragging, then with a keyboard only |
| Announcements | a screen reader hears each move with the item's new position |
| Focus | focus is never hidden under the sticky preview or header at 390 px (WCAG 2.4.11) |
| Targets | 24 × 24 px minimum (WCAG 2.5.8), 44 px for primary touch actions |
| Undo | N edits then N undos restore the definition byte for byte |
| Autosave | two tabs: the second save gets a conflict, not a silent overwrite |
| Both themes, both widths | 390 and 1440 px, light and dark, no overflow, no console errors |
