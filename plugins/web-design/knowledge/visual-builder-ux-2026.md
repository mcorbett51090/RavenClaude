# Making a builder people enjoy: editor craft for form, card, pass and page builders (2026)

> **Retrieved:** 2026-10-26. Product behaviour is quoted from each product's docs or help centre on that date;
> `[via snippet]` marks claims seen only in a search summary; `[inference]` marks recommendations no source
> states. Library sizes were measured (esbuild 0.25.0 minified, then `gzip -9`). Re-verify versions at use.
>
> **Scope.** The *editor* — what the owner sees while building. The data model of a form builder is
> [`form-builder-2026.md`](form-builder-2026.md); Wallet pass rules are core's
> [`wallet-passes`](../../ravenclaude-core/skills/wallet-passes/SKILL.md) skill; the general craft bar is
> [`interface-craft-fundamentals-2026.md`](interface-craft-fundamentals-2026.md). The procedure is the
> [`visual-builder`](../skills/visual-builder/SKILL.md) skill.

## 0. The short version

1. **The preview is the product.** Every builder that feels good shows the real output beside the controls and
   repaints it on every keystroke — and renders it with the **same code** that renders the published thing.
2. **Insert by clicking first, drag second.** Drag-and-drop is a bonus; every drag has a single-pointer,
   non-drag path (WCAG 2.5.7) and a menu move ("Move up · Move down · Move to…").
3. **Two levels of disclosure, no more** (Nielsen Norman Group): a calm simple mode and an advanced mode.
4. **Constraint-aware editing.** The editor knows the output's limits (a pass slot that truncates, a field that
   won't render, a contrast pair that fails) and says so *while* the owner types, not after publish.
5. **Undo for everything, autosave always, publish deliberately.**

## 1. Editor layouts that work

| Layout | Who | Copy | Avoid |
|---|---|---|---|
| **Document canvas** — type on the page, `/` to insert, `@` to reference an answer, Markdown-style shortcuts | Tally | inline label editing, keyboard-first insert, logic in context | logic scattered through a long document with no overview `[inference]` |
| **Three-pane** — palette, canvas, inspector, plus Preview / Logic / JSON / Translation / Themes tabs | SurveyJS Creator (v2 opens one inspector category at a time) | advanced surfaces as tabs; a collapsed inspector | a dense property grid as the first thing an owner sees `[inference]` |
| **Card editor beside a live phone** | Popl ("Preview Card"), HiHello (live editing), Linq (preview panel), Wave (preview before saving) | the phone frame next to the fields; "preview as a visitor" | a double save (Blinq's app saves per field, then again at the top) |
| **Graph view** — pages as nodes, branches as edges | Fillout page logic, Typeform Logic Map `[via snippet]` | the graph as a *view* of branch data | the graph as the only way to edit |
| **Device-frame preview with front/back** | pass designers (see core's [`pass-builder.md`](../../ravenclaude-core/skills/wallet-passes/references/pass-builder.md)) | iPhone and Android renders side by side, front and back | claiming the preview *is* Wallet — it is an approximation |

**Recommended default** `[inference]`: a canvas or form on the left, the live preview on the right (sticky on
desktop, a "Preview" tab on phones), an inspector that opens on selection with **Basic** visible and
**Advanced** collapsed. A left rail toggles **Add** (palette grouped by purpose) and **Outline** (tree, where
reordering also works).

## 2. Drag and drop in a vanilla-DOM app

| | Pragmatic drag and drop (Atlassian) | dnd-kit DOM | SortableJS |
|---|---|---|---|
| Version (2026-10-26) | 4.0.0, 2026-09-24 | `@dnd-kit/dom` 0.5.1 (pre-1.0); `@dnd-kit/core` 6.3.1 is React-only | 1.15.7 |
| Framework | any view layer, headless | DOM package + framework adapters | vanilla |
| Size, gzip (measured) | core adapter + reorder **7.0 KB**; with hitbox, live region, auto-scroll **10.1 KB** | manager + draggable + droppable + sortable **35.6 KB** | **12.9 KB** |
| Accessibility | none built in, by design; Atlassian's guideline prescribes a **menu** of outcomes, not arrow keys, plus `announce()` and focus return | built-in plugin: roles, live-region announcements, keyboard sensor (Space/Enter to lift, arrows to move, Escape to cancel) | nothing documented in the README |

**Pick** `[inference]`: Pragmatic drag and drop for pointer drags, plus your own "Move up / Move down / Move to…"
menu on every item's handle, plus a live-region announcement with the item name and its old and new position.
Choose dnd-kit DOM only if keyboard *dragging* out of the box is worth 35 KB and a pre-1.0 API. GitHub's
accessible sortable-list research found arrow keys clash with screen-reader browse keys, and that a **move
dialog** was preferred even by people who don't use voice control.

Mobile: press-and-hold to lift (Blinq, Popl), a six-dot handle on desktop (Popl), and never steal vertical
scroll from the canvas.

## 3. Undo, autosave, draft and publish

- **Undo as patches.** Immer's `produceWithPatches` returns `[next, patches, inversePatches]`; inverse patches are
  the basis for undo and redo. Coalesce keystrokes in one field into one step; treat a multi-item drag as one
  step; never record selection changes; clear redo on a new command `[inference]`.
- **Autosave the draft** 1–2 s after the last change, sending the same patches with the draft revision; a stale
  revision gets a 409 and the client re-fetches and rebases or asks `[inference]`. Show the state in plain words:
  "Saved · Unpublished changes".
- **Publish creates an immutable version** (Form.io full-copy revisions); changes go live only on publish
  (Fillout). At publish, show a short diff and call out anything destructive `[inference]`.
- **Template edits that propagate need an impact preview.** HiHello and Wave propagate a team template change to
  every card, and Wave's docs warn about it. Say "This change updates 42 cards" before saving `[inference]`.

## 4. Simple and advanced modes

Progressive disclosure works when the split between initial and secondary features is right and the way to the
second level is obvious; more than two levels "typically have low usability" (NN/g). Neither HiHello, Blinq,
Popl, Linq nor Wave documents a simple/advanced toggle — they split by **surface** (the phone app edits the card
quickly; the web dashboard holds forms, templates and integrations). SurveyJS uses an "Advanced mode" switch in
its theme editor.

A working split `[inference]`:

| Builder | Simple | Advanced |
|---|---|---|
| Form | field types, required, options, one show-when condition, one page jump, theme presets, email notification | nested conditions, formulas, regex, URL params, logic graph, translations, JSON view, webhooks, CRM mapping |
| Contact card | the onboarding order (below), colour from logo, layout presets | custom blocks, per-field team locks, exchange-form fields, analytics |
| Wallet pass | pass type, colours, logo, the fields the type needs | every field slot, back fields, locations, relevance dates, barcode options, push messages |

**Onboarding order that works** (Blinq): name → work email and phone → company, title, website → logo
(auto-detected from the company name) → photo → colour and layout. Popl marks missing information with caution
icons. HiHello offers a searchable field picker with popular fields pinned.

## 5. Making it visually appealing (the craft bar)

- **Theme from the brand, contrast-checked as you go.** Typeform's whole theme is about ten knobs — four
  colours, font, corner radius, alignment, font size, background — which is the right size for simple mode.
  Check text at 4.5:1 and non-text (input borders, focus rings, checkmarks) at 3:1 (WCAG 1.4.3, 1.4.11) while
  the owner picks, and auto-adjust with a note when a pair fails.
- **Suggest the brand colour from the uploaded logo.** None of the card products researched documents it
  `[absence not proven]`; with a contrast-guarded palette behind it, it is a visible differentiator.
- **Selection is obvious and calm.** One selected item at a time, a clear outline, the inspector titled with the
  item's name, hover affordances that never shift layout.
- **Motion with purpose.** A dropped item settles into place; a deleted item collapses; nothing animates on every
  keystroke. Follow [`interface-craft-fundamentals-2026.md`](interface-craft-fundamentals-2026.md) §motion
  (under 300 ms, transform and opacity, reduced-motion first).
- **Empty states teach.** A blank form says "Type `/` to add a question" (Tally); a blank card starts from
  "Start from text" or a template.
- **Templates gallery first** — "Blank · Template · Duplicate an existing one" — seeded per vertical (contact,
  quote request, booking, intake, order with deposit, feedback/NPS).
- **Keyboard shortcuts** (Tally's set is a good default): Esc selects the block, ↑/↓ move the selection,
  ⌘/Ctrl+Shift+↑/↓ move the block, ⌘/Ctrl+D duplicates, ⌘/Ctrl+Z undoes, ⌘/Ctrl+K opens the command menu, `/`
  inserts. Expose them with `aria-keyshortcuts`.
- **Test-issue to your own device.** For anything that ends up on a phone (a Wallet pass, a contact card), the
  last step before publish is "Send to my phone".

## 6. Verifying a builder

Read the rendered builder, not the source ([`interface-craft`](../skills/interface-craft/SKILL.md) Step 3):

| Check | How |
|---|---|
| The preview matches the published output | render both from the same definition; diff the DOM or the image |
| Every drag has a non-drag path | operate the whole builder with a mouse, without dragging; then with a keyboard only |
| Reordering is announced | a screen reader hears the item name and its new position |
| Focus never hides behind sticky chrome | tab through at 390 px with the sticky preview open (WCAG 2.4.11) |
| Targets are big enough | 24 × 24 CSS px minimum (WCAG 2.5.8), 44 for primary touch actions |
| Undo restores exactly | apply N edits, undo N, compare the definition byte for byte |
| Autosave survives a reload and a second tab | edit in two tabs; the second save gets a conflict, not a silent overwrite |

## Sources (retrieved 2026-10-26)

Tally help (create a form, keyboard shortcuts, conditional logic) · SurveyJS Creator overview and v2 release notes
· Fillout page logic · Typeform theme API; Logic Map help `[via snippet]` · Form.io form revisions · Popl
support (rearrange content, lead capture, insights) · HiHello features, templates and new edit experience posts ·
Blinq support (editing cards, creating your first card, team cards) and team-templates docs · Linq page settings
help · Wave Connect docs (profiles, templates, lock fields) · Atlassian Pragmatic drag and drop README, about page
and accessibility guidelines · dnd-kit docs (quickstart, sensors, accessibility plugin) · SortableJS README ·
GitHub engineering blog, accessible sortable list · Immer patches docs · npm registry (versions and dates) ·
Nielsen Norman Group, progressive disclosure · WCAG 2.2 Understanding 1.4.3, 1.4.11, 2.4.11, 2.5.7, 2.5.8.
