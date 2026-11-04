# UI pattern standing bar (captured 2026-11-04)

> **Last reviewed:** 2026-11-04. **Confidence:** high that the grades below are what the capture reported; low that any provisional row is true. This file records a Claude Code session summary. It is not a re-fetch of the underlying sources.
>
> **Source:** Claude Code session "RavenPower-website open PRs", <https://claude.ai/code/session_01Kf1chpP7g7i2pRJM2feCE3>, text captured 2026-11-04 from the visible session. UX research run 1 finished a partial adversarial pass: 21 of 109 extracted claims were verified before the verification step hit its budget. Navigation, design tokens, and skeletons were the solid slice. A gap-fill run and the agent-accessibility run were still going at capture.

Read this file before you spec portal or app chrome, cite a UI benchmark, or turn a portal walk into a finding. The assistive-technology and coding-agent rule text lives in [`../../accessibility-engineering/knowledge/portal-and-agent-accessibility-2026-11.md`](../../accessibility-engineering/knowledge/portal-and-agent-accessibility-2026-11.md). Apply that file when the work is markup, audit, or agent legibility.

## How to use the grades

| Grade | What the capture did | What you do |
|---|---|---|
| **Solid** | Adversarially checked in run 1. Enough to build a rule. | Follow the rule. Name the grade and the capture date. |
| **Provisional** | Sourced in the session, not verified before capture. | Use it only as a labeled default. Re-verify before a stakeholder commitment or before you add a CI gate this repo does not already have. |
| **Discarded** | The claim failed verification. | Leave it out. Do not cite it as support or as a counter-claim. |

Three limits bind every row:

1. **The 109-claim extract is not in this repo.** Run 1 wrote it to a Claude sandbox path (`run1-extracted-claims.json`). Do not reconstruct it, summarize claims that are not on this page, or invent the other 88.
2. **The gap-fill had not landed.** Forms and interaction beyond the Baymard trio below, WCAG 2.2 AA with exact criterion numbers, performance measurement in CI, linting, and how agents get UI right or wrong are absent. Leave them absent.
3. **A portal QA walk is not a study.** The checklist at the bottom is an example. It does not become a research conclusion.

## Solid rules

### Navigation

Apply this to primary navigation on a portal, dashboard, or signed-in tool:

1. Use a persistent, visible left rail.
2. Give every rail item a visible text label.
3. Always mark the current location, including on pages opened from outside the rail.
4. Open and close a nested section with a click-activated disclosure **button** that sets `aria-expanded` and points at the panel with `aria-controls`.
5. Keep local or secondary navigation visually quieter than the main rail: less weight, smaller type, or lower emphasis. It is not a second rail of equal weight.

Markup checks for the button, the current location, and screen-reader behavior are in the accessibility-engineering file. Follow both files together.

### Design tokens

1. Author the token source in the **W3C Design Tokens format, 2025.10**.
2. Say, next to the file, that 2025.10 is a **Design Tokens Community Group report**, not a W3C Recommendation and not a W3C standard.
3. **Name tokens by meaning.** Components consume names such as `color.text.muted` and `space.section`. Appearance names (`blue-500`, `16px-gap`) belong only on primitive values that semantic tokens point at.
4. Build the pipeline in [`web-design`'s `design-tokens-scaffolding` skill](../../web-design/skills/design-tokens-scaffolding/SKILL.md): primitives, semantics, CSS variables, theme build. That skill already calls this format a Community Group draft. When you name the format out loud, say "community-group report 2025.10".

### Loading skeletons

1. A skeleton reserves the **size of the content it stands in for**: the width and height the loaded block will occupy, including its media and text, so the page does not jump when the content arrives.
2. A generic short bar in place of a taller card fails this rule.
3. **Numeric timing.** This capture established only that Primer's published time thresholds are the numeric loading rule that survived verification. The millisecond values were not in the captured notes. Do not invent them, and do not relabel another plugin's numbers as Primer. [`web-design`'s `interface-craft` skill](../../web-design/skills/interface-craft/SKILL.md) has its own delay-and-hold guidance from a different source. That guidance is not this capture's Primer finding.

## Discarded claims

These four failed verification. Leave them out of specs, audits, and citations.

| Failed claim | What you do instead |
|---|---|
| "Icon-only nav is an NN/g rule" | Follow the labeled-rail rule above. Do not cite Nielsen Norman Group for icon-only primary navigation. The capture also does not establish the reverse citation ("NN/g forbids icon-only"). |
| "Exactly one `aria-current`" | Mark the current location. Do not lint, and do not require, that the document contain exactly one `aria-current`. The capture does not say why uniqueness failed, so do not invent the exception list. |
| A BBC/7digital 43% figure | Do not cite it. The capture does not preserve what the 43% measured. |
| "DTCG handles theming without duplicating token files" | Store each mode's values in a place you can point at. The format does not erase that. Say where the per-mode values live. |

## Provisional — label the row before you follow it

Write the grade into the deliverable: "provisional, 2026-11-04 capture, not re-fetched."

### Platform features

- The Popover API is Baseline since January 2025.
- `position-area` is newly available in 2026, so a layout that uses it needs a fallback.
- Same-document view transitions are Baseline since October 2025.
- Cross-document view transitions use the `pageswap` and `pagereveal` events.

Ship a support check with any of these. [`web-design` `web-platform-capabilities-2026.md`](../../web-design/knowledge/web-platform-capabilities-2026.md) and [`modern-css-2026.md`](../../web-design/knowledge/modern-css-2026.md) are the implementation homes. If they disagree with this list, this list does not win — re-verify. This list was not verified.

### Core Web Vitals

LCP 2.5s, INP 200ms, and CLS 0.1, each at the 75th percentile.

[`web-design`](../../web-design/CLAUDE.md) already uses these numbers as its field budget (`core-web-vitals-tuning`). This capture does not newly verify them, and it is not a reason to drop that budget. It is also not a primary source you may cite as verified. When a document needs a source, cite web-design's dated knowledge or re-fetch the metric, and keep this capture marked provisional.

### Forms (Baymard)

Until someone re-reads Baymard:

- Validate a field on blur.
- Once an error is showing, re-validate that field on each keystroke.
- Show positive validation as well as errors.

Stop there. The gap-fill on forms and interaction had not landed, so do not extend this into a forms pattern library.

### Motion

WCAG 2.3.3 (Animation from Interactions) is **AAA**, not part of an AA target. Gating interaction-triggered motion behind `prefers-reduced-motion` remains sensible. How an audit records that split is in the accessibility-engineering file. `web-design` already requires `prefers-reduced-motion` on animation; this row does not remove that requirement.

### Agent tooling

Every agent-tooling claim from this capture is unverified. The solid pattern rules above are not permission to build WebMCP, a hosted MCP server, or an `llms.txt` gate. Follow the accessibility-engineering file's split between provisional practice and unverified tools.

## Portal walk — example checklist, not research

A local walk on 2026-11-04 (fixture data, light theme, five personas, 24 routes, rail destinations clicked) is QA. The items below are example checklist rows for a portal review. One product's bug does not become a user-research finding. The walk's P2/P3 labels are that walk's ranks, not this plugin's severity scale.

1. **Every rail item a persona can see lands inside the portal shell.** A bare "Not found", with no rail and no way back, is a defect. When the page requires a role the account lacks, hide the item or explain the role inside the shell. The walk's example: a Forms item was on the rail for every persona and returned a bare 404 unless the account owned or administered an org. A sibling item built the same way (Sheets) loaded.
2. **A page opened from outside the rail still shows where the person is.** The walk's example: Cards opened from the account menu and highlighted nothing in the rail.
3. **The account menu exposes the current item to assistive technology.** The walk found no current-item marker on Profile, security, connectors, sessions, what's-new, or help. That is a checklist miss. It is not evidence for the discarded "exactly one `aria-current`" claim.
4. **The rail label and the page heading use the same words.** The walk's example: rail "Members", heading "Members area".
5. **A rail item with no icon, beside items that have one, is a visual alignment check.** It is not, by itself, an accessibility failure. The walk's example: Forms was plain text while its group had glyphs.

The walk also recorded, as checked-and-fine context rather than rules: rail links that were in scope landed where they pointed; a missing-site persona saw locked items with a call to action; the empty persona saw a completion form; the light theme was the default; flag-off routes 404 by design. Those observations stay observations about that fixture walk.

## What not to produce from this file

- A reconstructed 109-claim JSON, or a "complete" pattern guide that fills the gap-fill from memory.
- A provisional row promoted to solid because it matches training knowledge.
- A discarded row brought back as balance.
- A change to another product repository. This file is the standing bar for future work. It is not a patch list.
