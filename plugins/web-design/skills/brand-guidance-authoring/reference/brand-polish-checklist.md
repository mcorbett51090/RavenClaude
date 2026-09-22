# Brand-polish checklist — a structured self-check, not an oracle

**Owning skill:** [`brand-guidance-authoring`](../SKILL.md). Answers the honest caveat
[`ravenclaude-core/knowledge/visual-feedback-loop.md`](../../../../ravenclaude-core/knowledge/visual-feedback-loop.md)
states about itself — the model's visual taste "reliably catches broken layouts and obvious ugliness;
it's weaker on subtle brand polish." This file is what that caveat now points at.

> **Scope statement, required reading before running this checklist:** this is a structured self-check,
> not an oracle. It catches the named generic patterns from
> [`anti-pattern-catalogue.md`](anti-pattern-catalogue.md); it does not detect a page that is
> un-generic and simply bad. A clean pass here is not a design-quality verdict.

## When to run this

After a page (or a set of pages) is built and rendered — never during authoring. **Run in a fresh
context**: hand the checker the rendered page (a screenshot via `chrome-devtools-mcp` if available, or
a structural DOM/CSS read otherwise per
[`visual-feedback-loop.md`](../../../../ravenclaude-core/knowledge/visual-feedback-loop.md)'s two
"seeing" modes) plus the project's own `brand-guidance.md` — **nothing else from the build session**. A
checker that was in the room while the page was authored will rationalize what it sees instead of
checking it.

**Advisory only — at G3 and at G5 (`gold-standard-website-pipeline`), never a launch blocker.** A
finding here routes back to `visual-designer` for a judgment call; it does not fail a gate the way the
pipeline's structural checks do.

## Procedure

For each of the 10 rows below, read the project's `brand-guidance.md` §7 `override.status` for that ID:

- **`relaxed` or `replaced`** → skip this row. Contributes **zero findings**, regardless of what the
  page actually does. The checklist cannot overrule an explicit, rationalized project decision — that
  decision was already made, with a stated reason, at authoring time.
- **`enforced`** (the default) → check the rendered page against the row's observable form in
  [`anti-pattern-catalogue.md`](anti-pattern-catalogue.md). Present → a finding. Absent → no finding for
  that row.

| # | ID | Check |
|---|---|---|
| 1 | `AP-01` | Does the display/heading typeface resolve to Inter, Roboto, Open Sans, Arial, or `system-ui`? |
| 2 | `AP-02` | Does any hero/section background use a multi-stop gradient in the 250–300° hue band? |
| 3 | `AP-03` | Is there a 3-column grid whose cells are each exactly icon + h3 + p, with no other content type? |
| 4 | `AP-04` | Is there a `border-radius ≥ 12px` container whose direct child also has `border-radius ≥ 12px` and its own background? |
| 5 | `AP-05` | Is there a ≥90vh, centered hero over a photographic (non-product) background? |
| 6 | `AP-06` | Does any numeral present as a customer count / uptime / rating / "trusted by" with no cited source? |
| 7 | `AP-07` | Do 2+ sections use an asymmetric mixed-span (bento) grid? |
| 8 | `AP-08` | Does `backdrop-filter: blur()` appear on a non-modal, non-nav surface? |
| 9 | `AP-09` | Are wheel/scroll events intercepted to drive horizontal panel advance? |
| 10 | `AP-10` | Does an emoji occupy an icon slot anywhere? |

## Output shape

**No aggregate score. No numeric total. No pass/fail threshold.** The output is a named finding list:

- **Zero findings** — a clean pass.
- **One or more findings** — each finding names the row ID and the observed instance (what was seen,
  where), using the pipeline's existing severity vocabulary from `gold-standard-website-pipeline/
  SKILL.md` §5:

| Severity | Meaning here |
|---|---|
| **P0** | The pattern is the page's dominant visual signature (e.g. the entire hero is the AP-02 gradient) |
| **P1** | The pattern is present and prominent but not dominant |
| **P2** | The pattern is present in a secondary/below-the-fold location |
| **P3** | A borderline or partial match — flag it, let a human confirm |

Each finding is falsifiable — it names an ID and a location, not a verdict. Nothing here computes a
sum, an average, or a pass bar over these findings.

## Worked example

A marketing homepage was checked against all 10 rows, with `brand-guidance.md` showing `AP-01` at
`override.status: relaxed` (rationale: "the client's existing brand system is built on Inter; a
typeface change is out of scope for this engagement").

**Result:**

- `AP-01` — skipped (relaxed override, per the procedure above).
- `AP-02` — **P1 finding.** The pricing-page hero uses a `#6366f1 → #a855f7` gradient background,
  falling inside the banned 250–300° hue band. Prominent but not the page's dominant visual element.
- `AP-03`, `AP-04`, `AP-05`, `AP-06`, `AP-07`, `AP-08`, `AP-09`, `AP-10` — no finding.

Output: one P1 finding on `AP-02`, routed back to `visual-designer`. No score, no total, no pass/fail
line — the finding list above **is** the output.

## Hygiene checklist

- [ ] Exactly 10 rows, one per `anti-pattern-catalogue.md` ID — set-diff against that file is empty in
      both directions.
- [ ] The file states verbatim that a `relaxed`/`replaced` override row contributes zero findings.
- [ ] Severity labels used are exactly `P0`/`P1`/`P2`/`P3` — no fifth label invented.
- [ ] No numeric total, weighted score, or pass/fail threshold appears anywhere in this file.
- [ ] A worked example is present, showing the finding-list output shape end-to-end.

## See also

- [`anti-pattern-catalogue.md`](anti-pattern-catalogue.md) — the 10 rows this checklist runs against
- [`../SKILL.md`](../SKILL.md) — the authoring procedure that produces `brand-guidance.md`
- [`../../../../ravenclaude-core/knowledge/visual-feedback-loop.md`](../../../../ravenclaude-core/knowledge/visual-feedback-loop.md) — the render→see→critique→iterate canon this checklist plugs into
- [`../../gold-standard-website-pipeline/SKILL.md`](../../gold-standard-website-pipeline/SKILL.md) — G3 (structural, fail-closed) and G5 (visual-feedback loop) are the two places this checklist is consulted, always advisory
