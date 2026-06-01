# Guest-user & Experience Cloud sharing — the public-site rubric (verdict escalates to core)

**Status:** Absolute rule — a misconfigured guest user is the single highest-blast-radius public-data-exposure mistake on the Salesforce platform; the *verdict* escalates to `ravenclaude-core/security-reviewer`, but the *mechanics* below are non-negotiable.

**Domain:** Security / sharing (Experience Cloud)

**Applies to:** `salesforce`

---

## Why this exists

The internal sharing model (OWD → role hierarchy → sharing rules) has rules and a tree, but **guest users — the unauthenticated public visitors of an Experience Cloud / Digital Experiences site — follow a different, stricter model**, and it had no coverage. Guest-user misconfiguration is a notorious source of real-world breaches (public sites leaking other customers' records) precisely because engineers reason about it with internal-sharing intuitions that **don't apply**: guest users have no role, don't inherit the role hierarchy, and can't be granted access by ordinary owner-based sharing rules. This rule states the domain mechanics so the design is right; the security *verdict* (is this exposure acceptable) routes to core, per the plugin's "we supply the rubric, core owns the verdict" boundary.

## How to apply

**Know the guest-user constraints (they differ from internal users):**

- The guest user has **no role** and is **not** in the role hierarchy — hierarchy-based sharing never reaches it.
- Org-Wide Defaults for external access (the *external* OWD) gate the guest user; keep them **Private**.
- The org setting **"Secure guest user record access"** must be **on** (it is enforced by Salesforce) — it forces guest access to go through guest-user sharing rules and blocks ownership-based access.
- Records the public site needs are granted **only** via **Guest User Sharing Rules** (criteria-based), never owner-based — and the guest user **cannot be the owner** of records (use a default account/owner for guest-created records).

**Apply least privilege to the guest profile:**

- Grant the **minimum** object/field permissions on the Guest User profile; no `View All`/`Modify All`; lock CRUD to exactly what the site needs (often read on a narrow set, create on a form target).
- Field-level security on the guest profile — hide everything the public page doesn't render.
- Sharing-set / sharing-rule scope must be the **narrowest criteria** that serves the page (e.g. `IsPublished = true`), never "all records."

**Verify before launch:** load the public site **as the guest user** (logged out) and confirm only the intended records/fields are visible — the same "test RLS as the role" discipline, applied to the guest.

**Do:** external OWD Private; "Secure guest user record access" on; criteria-based guest sharing rules only; least-privilege guest profile + FLS; a default owner for guest-created records; test logged-out; **route the exposure verdict to `core/security-reviewer`.**

**Don't:** assume internal OWD/role/hierarchy reaches the guest user; grant broad guest-profile permissions "to make the page work"; let the guest user own records; ship a public site without a logged-out access test.

## Edge cases / when the rule does NOT apply

A purely **authenticated** Experience Cloud site (every visitor logs in, no anonymous access) uses the external-user sharing model (sharing sets, account/contact roles) — guest-user rules don't apply, though external OWD + least privilege still do. A site with **no Salesforce data** (static/marketing pages only) has no record-exposure surface. The exact org-setting names and whether "Secure guest user record access" is enforced-by-default are version-sensitive — `[verify-at-build]`.

## See also

- [`./data-owd-most-restrictive-then-open-deliberately.md`](./data-owd-most-restrictive-then-open-deliberately.md) — the internal OWD rule this parallels (and the external-OWD layer it references)
- [`./enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — CRUD/FLS enforcement the guest profile also needs
- [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md) — the sharing decision trees
- The exposure **verdict** escalates to [`ravenclaude-core/security-reviewer`](../../ravenclaude-core/agents/security-reviewer.md) (house rule: this plugin supplies the rubric, core owns the verdict)
- [Secure guest user / Experience Cloud guest access](https://help.salesforce.com/s/articleView?id=sf.networks_secure_guest_users.htm) — authoritative

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01). Panel 3 **overrode** Panel 2's "hold" with a domain-rubric-vs-verdict distinction: the guest-user *mechanics* (no role, no hierarchy, Secure-guest-user-record-access, guest sharing rules) are domain knowledge the security verdict needs as input — exactly the rubric this plugin owns — while the *verdict* escalates to core. The internal sharing model (`sharing-and-security-model.md`) had zero guest-user coverage. Org-setting specifics are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
