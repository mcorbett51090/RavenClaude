# Wireframe — *<screen / artifact name>*

> **Use this template for quick layout sketches** before committing to a full design spec. A wireframe answers "where does what go?" — not "how does it look?" Save type, color, and polish for the spec.
> **Length target:** one page. If you need more than one wireframe, it's a multi-step flow — see the Flow section in [`design-spec.md`](design-spec.md).

**Sketcher:** *<your name or "designer agent">*
**Date:** YYYY-MM-DD
**Surface:** *<phone / tablet / desktop / projected slide / printed handout>*

---

## User task (one sentence)
*<What the user is trying to do on this screen. If you can't write it, you're not ready to wireframe.>*

## Layout

### Mobile / narrow viewport (≤ 480 px)
```
+--------------------------+
| [hamburger]  [page title]|
+--------------------------+
|                          |
|   < primary content >    |
|                          |
|   [ primary action ]     |
|                          |
|   < secondary content >  |
|                          |
+--------------------------+
| [tab1] [tab2] [tab3]     |
+--------------------------+
```

### Desktop / wide viewport (≥ 1024 px)
```
+----------------------------------------------------------+
| [logo]    [nav item 1]  [nav item 2]  [nav item 3]  [me] |
+----------------------------------------------------------+
|                |                                         |
| [side          |   < primary content >                   |
|  navigation]   |                                         |
|                |   [ primary action ]                    |
|                |                                         |
|                |   < secondary content >                 |
|                |                                         |
+----------------+-----------------------------------------+
```

*<Delete whichever viewport doesn't apply. For a slide deck, replace both with a single slide layout. For a Power Apps screen, replace both with the canvas layout (typically 640×1136 portrait or 1366×768 landscape).>*

## Element notes (anchored to the wireframe)
- **[primary action]** — *<what it does, why it's where it is>*
- **[hamburger]** — *<what's behind it; only include if there's enough secondary nav to justify hiding it>*
- **<primary content>** — *<what data is shown, in what order, prioritized by what>*

## What's deliberately NOT on this screen
*<List things a reviewer might expect to see but you've intentionally left off, with reason. This is often more valuable than what IS on the screen.>*

- *<example: "User profile dropdown — kept on the partner-detail page only; this screen is task-focused.">*

## Open questions
- *<thing that needs the user task or PM input before this can become a full spec>*

---

> **Next step:** when the wireframe stabilizes, promote it to a full [`design-spec.md`](design-spec.md). Don't ship from a wireframe alone — visual hierarchy, accessibility, and microcopy decisions live in the spec.
