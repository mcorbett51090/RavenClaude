---
name: form-builder
description: Design or upgrade a tool that lets owners build their own forms — the definition model, field catalog, conditional logic and multi-step pages, versioning while responses exist, live preview, outputs (inbox, CSV, webhooks, email, CRM) and payment fields. Used by web-architect and frontend-implementer; not for a single hand-built form.
---

# Skill: form-builder

**Purpose:** ship a builder where a non-technical owner can make a good form in minutes and a power user can add
logic, payments and integrations — without either one being able to break submissions that already exist.
Primary agents: `web-architect` (model, versioning, outputs), `frontend-implementer` (editor and renderer),
`ux-designer` (simple/advanced split, templates), `accessibility-auditor` (published form and the editor).

Backing knowledge: [`../../knowledge/form-builder-2026.md`](../../knowledge/form-builder-2026.md) (models compared,
the recommended definition shape, field catalog, logic, versioning, outputs, payments). Editor craft:
[`../visual-builder/SKILL.md`](../visual-builder/SKILL.md). The server half of a submission (honeypots,
idempotency, telemetry) is `forms-engineering`'s [`harden-a-form-submission`](../../../forms-engineering/skills/harden-a-form-submission/SKILL.md).

## When to use

- Owners need to create, edit and publish their own forms, and responses must survive later edits.
- An existing builder is a plain list of inputs with no logic, no preview and no versioning.
- A form needs to take money, route to a CRM, or fire webhooks.

Not for: one hand-built contact form (build it with `static-site-implementation`), a survey-research instrument
(`ux-research`), or choosing a hosted form SaaS (`forms-engineering`'s platform axes).

## Procedure

### 1. Fix the model before the UI

1. Write a typed **definition** with `pages`, flat `fields` with stable ids and a machine `key`, allow-listed URL
   `params`, declarative `variables`, `endings` and `outputs`. Derive the JSON Schema used for server type checks
   from it; JSON Schema cannot express visibility or flow.
2. **Draft + immutable versions.** One autosaved draft; publish copies the definition into an append-only version;
   every submission stores `form_version_id` and answers keyed by field id.
3. Decide the edit rules for a published form (knowledge §3): safe, **archive** (delete with data), **fork**
   (type change with data), disallowed (changing a stored option value). Write them into the publish dialog.
4. Keep *published* separate from *accepting responses* (close date, response limit).

### 2. Logic that owners can read and the server can trust

1. Conditions are typed trees (`and`/`or`, typed operands), on fields (`visibleWhen`, `requiredWhen`) and pages
   (`branches` + `fallback`). Formulas are declarative.
2. One small allow-listed interpreter — no `eval`, no expression-string parser from a package with a remote-code
   history — run **identically** in the browser and on the server. Fuzz it with `__proto__` and `constructor`.
3. Validate on every save, block publish on errors: cycles, unreachable pages, dangling targets, formula cycles,
   forward references.
4. On submit the server re-evaluates everything, drops answers to hidden fields, enforces required only on visible
   ones, recomputes variables and any price.

### 3. Field catalog in phases

Ship about fifteen types first (knowledge §4, P1): short/long text, name, email, phone, number, memorable date,
single and multiple choice, dropdown, yes/no, rating/NPS, website, consent, hidden/URL param, content blocks, page
break. Each type carries its `autocomplete` token, `inputmode`, validation with an owner-editable message, and its
accessibility note (fieldset/legend for groups, no placeholder-as-label, no `type=number`, no input masks). P2 adds
scheduling dates, currency, image choice, upload, signature, address, calculated values and payment.

### 4. The editor

Follow [`visual-builder`](../visual-builder/SKILL.md): a document-style canvas (`/` to insert, inline label
editing) with an inspector; **Basic** visible, **Advanced** collapsed (logic, validation, prefill, CRM key);
click-to-insert first, drag second, a menu move on every field; undo/redo as patches; autosave with a conflict
check; a live preview rendered by the **same** renderer as the published form at phone and desktop widths;
templates per vertical. Simple mode offers one show-when condition and one page jump; advanced adds nested groups,
formulas, the logic graph and a JSON view.

### 5. Outputs and payments

- Inbox across versions (archived fields stay as columns), detail view in the captured version, CSV export with
  formula-injection neutralising.
- Webhooks on the Standard Webhooks spec (signed `id.timestamp.payload`, constant id across retries, ~3-day
  backoff, delivery log, replay) with SSRF guards on the owner's URL.
- CRM mapping by field `key`, stored with the published version.
- Payments through the provider's hosted element or checkout (SAQ A); the amount is recomputed on the server from
  the published version and fulfilled from the provider's webhook. Payment-page script hygiene and who attests to
  it are a QSA question, not a guess.

### 6. Verify

| Check | Pass condition |
|---|---|
| Logic parity | a table of answer sets produces identical visibility, required and routing on client and server |
| Version safety | edit, archive and fork a field with responses; old submissions render in their own version; export keeps every column |
| Interpreter safety | fuzz rows with prototype keys and deep nesting are rejected at save |
| Published form | error summary focused with `Error:` in the title; step title in `<title>`; every group in a fieldset; 200 % zoom and 320 px width without loss |
| Editor | the whole builder works without dragging and with a keyboard only (WCAG 2.5.7, 2.1.1) |
| Payment | a tampered client amount is refused; fulfilment happens only from the provider webhook |
