# Design table permissions before forms, and verify the Anonymous role can't Read

**Status:** Absolute rule — a public-facing Power Pages site with a leaky Anonymous Read permission is a data-breach headline, not a bug.

**Domain:** Power Pages / security

**Applies to:** `power-platform`

---

## Why this exists

Power Pages is internet-facing. Its data security is **table permissions** layered with web roles — not the page UI. Hiding a field in Liquid or CSS does not secure it; the browser already received the source. The recurring failure is two-sided: a table with **no** permission is invisible to everyone (the safe default), so a maker "fixes" the blank form by adding a **Global Read** permission to the Anonymous Users role — and now every anonymous visitor can enumerate every row. Because a single Power Pages form silently consumes a table's permissions, designing the form before the permission model means the form leaks. The `power-pages-permissions` skill states the rule plainly: design auth → web role → table permission → record ownership **before** building any page or form, and default-deny / explicit-grant.

## How to apply

Author table permissions first, scoped as narrowly as the use case allows, and confirm the Anonymous role has **Create-only** (never Read) on submission tables:

```
Table Permission: "Submit Contact Request (anon)"
  Table:      mc_contactrequest
  Web role:   Anonymous Users
  Scope:      Global          (no contact exists yet to own the row)
  Privileges: Create          ← Create ONLY. NOT Read. NOT Write.

Table Permission: "My Support Cases (authenticated)"
  Table:      incident
  Web role:   Authenticated Users
  Scope:      Contact          (rows where the contact-lookup = signed-in contact)
  Privileges: Read, Write
```

**Do:**
- Design auth → web role → table permission → record ownership before the first form.
- Use the narrowest scope: **Self** for "edit my profile", **Contact** for "my cases", **Account** for "my company's data", **Parental** for child tables, **Global** only for truly public reference data or anonymous Create.
- Give the Anonymous role **Create without Read** on submission tables, then add reCAPTCHA.
- Test as a real **portal user**, not as the portal admin (the admin bypasses the experience).

**Don't:**
- Grant **Global Read** to fix a blank list — that exposes every row to every user in that role.
- Rely on Liquid `{% if %}` or CSS `display:none` to protect sensitive data — it's still in the page source.
- Build the form first and bolt permissions on after — the form will leak or fail silently during the gap.

## Edge cases / when the rule does NOT apply

- **Global scope is correct** for genuinely public reference data (country list, product catalog) and for anonymous Create where no owning contact exists yet.
- **Parental scope** requires the parent record to itself be visible — debug permission chains from the top of the relationship.
- Rows created by a **model-driven app** default-own to a system User, not a contact, so they're invisible in Pages even with Contact-scope permission set correctly — populate the contact-lookup on Create (plug-in or the Pages form).

## See also

- [`pages-liquid-and-fetchxml-safety.md`](./pages-liquid-and-fetchxml-safety.md) — the rendering-layer companion (hiding ≠ securing)
- [`bi-row-level-security-tested-as-role.md`](./bi-row-level-security-tested-as-role.md) — the Power BI analogue of "test as the real user"
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power Pages — Granting a portal user access to a row`
- [`../skills/power-pages-permissions/SKILL.md`](../skills/power-pages-permissions/SKILL.md) — the full security-layering playbook + the 9-step "visible in MDA but not Pages" debug walkthrough
- [`../agents/power-pages-engineer.md`](../agents/power-pages-engineer.md) — owner

## Provenance

Grounded in [Power Pages table permissions](https://learn.microsoft.com/power-pages/security/table-permissions) and [Web roles](https://learn.microsoft.com/power-pages/security/create-web-roles) (retrieved 2026-05-30), and the in-house [`power-pages-permissions`](../skills/power-pages-permissions/SKILL.md) skill (the "default-deny, explicit-grant" close).

---

_Last reviewed: 2026-05-30 by `claude`_
