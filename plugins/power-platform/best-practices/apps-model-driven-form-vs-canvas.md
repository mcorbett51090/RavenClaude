# Put heavy, structured, record-centric data entry on a model-driven form — not a hand-built canvas screen

**Status:** Pattern — strong default; build canvas for the same job only with a written reason.

**Domain:** Canvas + Model-driven apps

**Applies to:** `power-platform`

---

## Why this exists

Canvas and model-driven apps solve different shapes of problem, and choosing the wrong one is expensive to unwind. A model-driven form renders **server-side** over a Dataverse model — it is not a tree of Power Fx-evaluated controls, so it doesn't carry the canvas control-count budget, and it gets security (FLS/RLS), business rules, quick-view forms, subgrids, and the timeline for free. A canvas screen gives you pixel-level layout control and Power Fx, but a 30-field "mega-form" rebuilt in canvas is 90+ controls before validation logic, every property re-evaluated by the runtime on relevant changes. When a heavy data-entry surface is slow in canvas after delegation + Monitor + pre-load, the real fix is usually "this should have been a model-driven form," not more canvas tuning.

## How to apply

Match the surface to the shape of the work. Use a Custom Page to get a focused canvas surface inside a model-driven app when you need both.

```text
Record-centric CRUD over Dataverse, structured fields,
needs FLS/RLS + subgrids + timeline + business rules   → Model-driven form
Pixel-perfect / task-flow / kiosk / non-tabular UX,
multi-source, custom branding, mobile-first            → Canvas app
Need a focused canvas surface inside an MDA             → Custom Page (embedded)
Heavy data entry that's slow as a canvas mega-form      → move it to an MDA form
```

**Do:**

- Use model-driven for the classic "list → open record → edit fields → related grids" pattern over Dataverse.
- Use canvas (or a Custom Page) for guided task flows, non-tabular layouts, branded experiences, and multi-connector mashups.
- Embed a Custom Page when one screen of an MDA genuinely needs canvas-style layout — the canvas content is `power-fx-engineer`'s, the MDA shell is `model-driven-engineer`'s.
- Keep one canvas screen under ~500 controls; move overflow data entry to an MDA form.

**Don't:**

- Rebuild a 40-field Dataverse edit form in canvas and then fight the control-count and re-evaluation cost.
- Reach for canvas because "it looks nicer" when the work is structured record CRUD that needs row-level security.
- Re-implement FLS/RLS by hand in canvas Power Fx when a model-driven form enforces it server-side.

## Edge cases / when the rule does NOT apply

- **Mixed app** — a model-driven app with one Custom Page for the one screen that needs canvas layout is the intended pattern, not a compromise.
- **Non-Dataverse source** — model-driven requires Dataverse; if the system of record is SharePoint/SQL/connectors only, canvas (or a code app) is the surface.
- **Mobile-first, offline, or kiosk** — canvas (or a code app) generally fits better than a model-driven form.
- **Very small structured edit** (a handful of fields) — either works; pick by what the rest of the app already is.

## See also

- [`../skills/dataverse-web-resources/resources/ux-decision-guide.md`](../skills/dataverse-web-resources/resources/ux-decision-guide.md) — form/grid/page decision tables, "Custom Page vs Web Resource"
- [`../skills/canvas-app-performance/SKILL.md`](../skills/canvas-app-performance/SKILL.md) §6 — control-count budget; the "move heavy data entry to a model-driven form or Custom Page" escalation
- [`../knowledge/apps-decision-trees.md`](../knowledge/apps-decision-trees.md) — `Decision Tree: App type — canvas vs model-driven vs code app`
- [`../agents/model-driven-engineer.md`](../agents/model-driven-engineer.md), [`../agents/power-fx-engineer.md`](../agents/power-fx-engineer.md)

## Provenance

From the `canvas-app-performance` skill §6 (control-count budget, "form rendering is server-side, not Power Fx-evaluated", escalation when canvas isn't the right tool), the `ux-decision-guide` (Custom Page vs Web Resource, page-level decisions), and the agent ownership boundary in `model-driven-engineer.md` / `power-fx-engineer.md` (Custom Pages jointly owned).

---

_Last reviewed: 2026-05-30 by `claude`_
