# Accessibility Engineering KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Conformance & criteria

| Term | Definition | Note |
|---|---|---|
| **WCAG** | Web Content Accessibility Guidelines (2.0 / 2.1 / 2.2; 3.0 in draft) | Cite the version + date — criteria and numbering evolve (§3 #8). |
| **Conformance level** | A / AA / AAA, per success criterion | AA is the common legal/contractual floor; AAA is per-criterion, rarely a whole-site target (§3 #1). |
| **Success criterion (SC)** | A single testable requirement (e.g. 1.4.3 Contrast Minimum) | Conformance is per-SC at the target level; a failing Level-A SC fails the page (§3 #1). |
| **POUR** | Perceivable, Operable, Understandable, Robust — the four WCAG principles | The top-level structure criteria hang from. |

## Assistive technology & interaction

| Term | Definition | Note |
|---|---|---|
| **Screen reader** | Software conveying UI as speech/braille (e.g. JAWS, NVDA, VoiceOver) | Test with the AT a population actually uses; date AT/browser versions (§3 #8). |
| **Name / Role / Value** | The accessibility-tree properties AT relies on (SC 4.1.2) | Native elements provide these for free; bad ARIA breaks them (§3 #4). |
| **Focus order** | The sequence keyboard focus moves through (SC 2.4.3) | Must be logical; automated tools cannot judge it (§3 #2 #3). |
| **Live region** | A region that announces dynamic updates to AT (aria-live) | For async/status updates; over-use is as harmful as under-use. |

## Color & visual

| Term | Definition | Note |
|---|---|---|
| **Contrast ratio** | (L_light + 0.05) / (L_dark + 0.05) from relative luminance | Computed, not eyeballed (§3 #5). |
| **Relative luminance** | L = 0.2126R + 0.7152G + 0.0722B over sRGB-linearized channels | The basis of the WCAG contrast formula. |
| **Large text** | >=18pt (24px) or >=14pt (18.66px) bold | Lower threshold: AA 3:1, AAA 4.5:1 (§3 #5). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
