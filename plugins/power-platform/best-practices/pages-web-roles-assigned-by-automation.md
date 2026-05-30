# Assign web roles via Dataverse automation, not by hand

**Status:** Pattern — strong default; manual assignment is allowed only for a tiny fixed admin set with a written reason.

**Domain:** Power Pages / security

**Applies to:** `power-platform`

---

## Why this exists

A web role is what maps a portal contact to its table permissions — it is the access grant. Assigning web roles **by hand** (an admin opening each contact and adding a role) is unauditable, doesn't scale, and breaks the day someone forgets: a new customer signs up and silently has no access, or worse, an admin grants an elevated role to the wrong contact. The `power-pages-engineer` agent lists "web roles assigned manually by an admin running queries" as an anti-pattern and the contrasting opinion as a rule: "web roles assigned via Dataverse logic, not by hand." The fix is to drive role assignment from a **Power Automate flow or plug-in** on Contact create/update, so every grant is deterministic, logged, and reproducible across dev/test/prod.

## How to apply

Wire a flow on the Dataverse "When a row is added" (Contact) trigger that associates the correct web role based on a contact attribute, instead of manual association:

```
Trigger:  Dataverse — When a row is added → table Contact
Condition: mc_customertier is not empty            (trigger condition, not a runtime filter)
Action:   Relate rows  →  adx_webrole / contact   association
            web role:  resolve by NAME via env var  (e.g. lookup "Customer - Standard")
            contact:   triggerOutputs() contactid
Catch:    log + notify on failure  (top-level Try/Catch/Finally — §3 #10)
```

**Do:**
- Drive web-role assignment from a flow or plug-in keyed off a contact attribute (tier, account type, sign-up source).
- Resolve the web role by **name or alternate key**, never a hard-coded GUID (§3 #11) — GUIDs differ across environments.
- Keep the assignment logic in the **solution** so it travels dev → test → prod with the portal.
- Audit periodically: query which contacts hold which roles and reconcile against the intended rule.

**Don't:**
- Hand-assign web roles in production as the standard onboarding step.
- Hard-code a web-role GUID in the flow — re-bind by name on import.
- Stack overlapping custom web roles with conflicting permission scopes — accumulation is a union, and "why can this person see that?" becomes unanswerable.

## Edge cases / when the rule does NOT apply

- A **tiny, fixed set of internal admins/reviewers** can be hand-assigned once if documented — the cost of automation isn't worth it for 3 static accounts.
- **Anonymous Users** and the default **Authenticated Users** roles are platform-managed; you don't assign those per contact.
- A **B2C/Entra-External-ID first sign-in** may create the contact before your tier attribute is known — handle the "no role yet" state explicitly (default-restricted) rather than failing open.

## See also

- [`pages-table-permissions-before-publish.md`](./pages-table-permissions-before-publish.md) — web roles are how a permission reaches a contact
- [`pages-liquid-and-fetchxml-safety.md`](./pages-liquid-and-fetchxml-safety.md) — `user.roles` checks are UX, downstream of the role grant
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power Pages — Granting a portal user access to a row`
- [`../skills/power-pages-permissions/SKILL.md`](../skills/power-pages-permissions/SKILL.md) — §3 web-role design
- [`../agents/power-pages-engineer.md`](../agents/power-pages-engineer.md) — owner ("web roles assigned via Dataverse logic, not by hand")

## Provenance

Grounded in [Create web roles for your site](https://learn.microsoft.com/power-pages/security/create-web-roles) (retrieved 2026-05-30) and the `power-pages-engineer` agent opinion + anti-pattern list. Aligns with CLAUDE.md §3 #11 (no GUIDs) and §3 #12 (source-control the solution).

---

_Last reviewed: 2026-05-30 by `claude`_
