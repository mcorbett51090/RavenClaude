# The WCAG floor — `report-regeneration`

**Status:** knowledge-bank deliverable (plan §9 — "WCAG-floor honesty note"). Reference only — the six-leg harness (V5 = render referee) lives in [`core-architecture-spec.md`](core-architecture-spec.md); the tool wiring lives in [`per-format-toolchain.md`](per-format-toolchain.md). This document answers one question: **what does the accessibility gate actually prove, and what does it honestly not?**

**The one rule that governs everything below (plan §7): "The gate is a floor, not conformance." Every QA report states this explicitly. An empty manual-residue section is itself a defect (over-claim).**

---

## 1. The number, and why it's marked `[unverified]`

**Automated tooling covers only the machine-checkable ~30–50% of WCAG** (claims-table claim 18). The exact figure is the widely-cited community range — carried here **verbatim, not laundered**:

> `[unverified — treat as order-of-magnitude, not a spec number]`

Source: [W3C WAI tools list](https://www.w3.org/WAI/test-evaluate/tools/list/) (2026-07-16); axe-core's WCAG 2.x rule coverage is referenced in the same results. No authoritative spec assigns a single percentage to "how much of WCAG is machine-checkable" — the range is a practitioner consensus, not a W3C number. Treat any claim more precise than "roughly a third to half" as overstated.

---

## 2. What's covered — the deterministic, proven part

| Gate | Format | What it proves | Source |
|---|---|---|---|
| **axe-core** | HTML | The standard open-source automated engine (Deque). Runs against the Playwright-rendered fidelity copy. Structural/programmatic WCAG 2.2 AA checks — the class of thing a script can assert without judgment (e.g. presence of alt attributes, contrast ratios computed from rendered color values, ARIA-role validity, heading-hierarchy structure). | Claim 18. |
| **veraPDF** | HTML→PDF and Office→PDF (both) | Free, open-source, PDF-Association-backed validator; validates **PDF/UA-1, PDF/UA-2, WCAG 2.2, and PDF/A locally**, no cloud. The concrete local check for both output formats' accessible-PDF copy. | Claim 19. |
| **LibreOffice PDF/UA export** | Office | `--headless` export with "Universal Accessibility (PDF/UA)" **auto-enables tagged PDF and cannot be disabled** — the tagging itself is structurally guaranteed by the export path, then veraPDF validates the result rather than trusting it on faith. | Claim 15. |
| **WeasyPrint `pdf/ua-1`** | HTML | Emits PDF/UA tags, but the docs state output is **"not guaranteed to be valid"** — 2026 GitHub issues show active work on form-field + table-structure tagging. This is why it is gated by veraPDF downstream, never trusted standalone. | Claim 10. |

**Deterministic anchor in the rubric (`report-gold-standard-rubric`):** the **Inclusive** dimension's hard anchor is "per-format a11y gate green (axe-core HTML / veraPDF Office-PDF)" — this is what "proven" means in this plugin's vocabulary: axe/veraPDF passing, nothing more, nothing less.

---

## 3. What's NOT covered — the manual residue (plan §7, named explicitly, not invented here)

The plan names the manual-WCAG residue explicitly: **meaningful alt-text quality, reading-order sense, plain-language.** These map onto the rubric's own judged-residue column:

| Rubric "Inclusive" component | Deterministic anchor | Judged residue |
|---|---|---|
| Alt-text | axe/veraPDF check *presence* | axe/veraPDF cannot judge whether alt-text is *accurate or specific* to the visual — "Bar chart" passes the presence check exactly as well as "Bar chart of Q4 2026 revenue, $1.23M, up 8% QoQ" does. Alt-text **quality** is LLM-judged, advisory (`report-gold-standard-rubric/SKILL.md`). |
| Reading order | axe/veraPDF/tag-tree structural order | Whether the *sequence* actually makes sense to a screen-reader user (not just "a tag order exists") is a judgment call, not a structural fact. |
| Language | — | Plain-language / comprehension quality has no automated proxy in either gate. |

These three residues are not gaps this document apologizes for — they are the honest boundary of what a script can assert. **The QA report's manual-residue section listing them is required, not optional**: Phase 2's acceptance test states it explicitly — *"the QA report's manual-residue section is non-empty (an empty one would over-claim the ~30–50% automated a11y floor)"* (plan §5, Phase 2). This is enforced at the schema level too — `fidelity-receipt.schema.json`'s `manual_residue` field description: *"An EMPTY residue on a shipped report is itself a defect (over-claim)."*

---

## 4. The a11y-uplift-vs-fidelity policy (binding — REQ-4, RT2/critic P1)

**The tension.** The template is "old, already-distributed" and very plausibly carries **baked-in a11y defects in `frozen`/static content** — a decorative logo with no alt-text, a low-contrast brand header. Fixing such a defect **directly violates V2's zero-diff-outside-anchors guarantee** ("did anything change outside the bound anchors?" — `core-architecture-spec.md` §5). A regeneration engine that silently "improves" frozen chrome is, by the harness's own definition, no longer byte-stable, and V2 is what makes template fidelity a *decidable diff* in the first place (`core-architecture-spec.md` §1). Accessibility and fidelity are pulling in opposite directions on exactly this class of node.

**This is a genuine-preference call, not a technical one.** It is surfaced as a named decision, routed through **`decision-review` to Matt** (plan §7):

| Option | What it means | Consequence |
|---|---|---|
| **Preserve** (fidelity wins) | The baked-in defect ships, unchanged, in the `frozen` region | Flagged as manual-residue — never claimed as passed. This is the **default, absent a ruling.** |
| **Fix** (accessibility wins) | The defect is corrected | Logged as an **intentional fidelity deviation** — that specific node is explicitly exempted from V2's zero-diff check, not silently excluded from it. |

**Why "preserve + flag" is the default rather than "fix":** fixing without a ruling would mean V2 silently tolerates an undeclared exception, which erodes the property the whole architecture is built on ("nothing changed outside the bound anchors" as a decidable, provable fact — `core-architecture-spec.md` §1). Preserving and flagging keeps the guarantee intact and routes the actual judgment call — is this client's brand-header contrast worth an intentional fidelity deviation — to the human who can weigh it, per template, per client.

---

## 5. Per-format notes

- **HTML:** the fidelity copy (Playwright) and the accessible copy (WeasyPrint `pdf/ua-1`) are **two separate render outputs**, precisely because headless-Chromium print does not reliably produce a tagged PDF (claim 11 — see [`per-format-toolchain.md`](per-format-toolchain.md) §2 for the pending confirming spike). axe-core runs against the HTML fidelity copy; veraPDF runs against the WeasyPrint PDF/UA copy.
- **Office:** a single LibreOffice `--headless` export path produces both the deliverable PDF and its tags (cannot be disabled), so there is no fidelity-vs-accessible split the way HTML has one — veraPDF runs once, against that export.
- **Power BI (input):** there is no Power BI a11y gate in this plugin — the old PBIR-JSON accessibility checklist (alt text/title/tab-order/contrast) is **dropped**, because there is no PBIR output to check (`plan §7`; `core-architecture-spec.md` §1). The embedded PBI screenshot is handled as an ordinary **image node**: meaningful alt-text is required on it exactly as on any other image, subject to the same data-leak gate the alt-text of any node is subject to (`core-architecture-spec.md` §6).

---

## 6. Cross-references

- The V5 render-referee leg + the six-leg harness: [`core-architecture-spec.md`](core-architecture-spec.md) §5.
- Tool wiring per format (axe/veraPDF/WeasyPrint/LibreOffice), Tier-A/Tier-B split: [`per-format-toolchain.md`](per-format-toolchain.md).
- Judged-vs-proven scoring mechanics for the Inclusive dimension: `skills/report-gold-standard-rubric/SKILL.md`.
