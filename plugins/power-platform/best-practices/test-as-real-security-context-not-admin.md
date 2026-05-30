# Test under the real user's security context — "worked as admin" is not a test

**Status:** Absolute rule — validating access only as a system admin / author is a non-test that ships security defects.

**Domain:** Power Platform / testing / security

**Applies to:** `power-platform`

---

## Why this exists

Across every Power Platform surface, the **author/admin sees more than the user does** — and that gap is exactly where security defects hide. A System Administrator bypasses Dataverse FLS/RLS and sharing; a Power BI workspace author/admin **bypasses row-level security**; a Power Pages portal admin sees rows an authenticated contact can't. So "it worked when I tested it" is meaningless evidence when "I" am privileged. The `power-platform-tester` agent states it flatly: *"Probe with a non-system-admin test user (security role with the actual production privilege set). 'Worked as admin' is not a test."* The only valid access test runs under the **actual production privilege set** — a real or impersonated non-privileged identity — because that's the only context that reveals what a customer or restricted user truly experiences.

## How to apply

For every access-control claim, reproduce under a least-privileged identity that mirrors production, per surface:

```text
Dataverse / model-driven:
  - create a test user with the PRODUCTION security role (not System Admin), no extra grants
  - probe FLS (can they see the field?), RLS/row scope, sharing, cascade on delete
  - "View as" / impersonate is a shortcut; a real assigned account is the proof

Power BI:
  - RLS: Modeling → View as → Role/Other user  AND a real account assigned to the role
  - remember: workspace authors/admins BYPASS RLS — they are never a valid RLS test identity

Power Pages:
  - sign in as a real PORTAL user (a contact with the intended web role), not the portal admin
  - walk the 9-step "visible in MDA but not in Pages" checklist if a row is unexpectedly hidden/shown

Copilot Studio:
  - test the agent as an end user, not the maker — the maker may have connector/data access the user lacks
```

**Do:**
- Assign the **actual production security role / web role** to a test account and probe with it.
- For Power BI RLS, use **View as role** *and* a real assigned account — authors bypass RLS.
- For Power Pages, test as a real **portal contact**, not the admin.
- Verify both directions: the user **can** see what they should, and **cannot** see what they shouldn't.

**Don't:**
- Conclude "access works" from a session running as System Administrator / workspace admin / portal admin.
- Grant the test user extra privileges "to make the test pass" — you've then tested a configuration that doesn't ship.
- Test RLS as the report author (they don't have RLS applied at all).

## Edge cases / when the rule does NOT apply

- **Pure functional tests** with no access-control surface (does this measure compute the right number, does this flow transform the payload) don't need a downgraded identity — but the moment FLS/RLS/permissions are in scope, they do.
- **Impersonation/"View as"** is a fast first pass, but for a release-gating sign-off, a **real assigned account** is the stronger evidence (it exercises the full auth + role-resolution path).
- A **break-glass admin path** that's *intended* to bypass security is tested as admin on purpose — document that it's deliberate, and still test the non-admin path separately.

## See also

- [`bi-row-level-security-tested-as-role.md`](./bi-row-level-security-tested-as-role.md) — the Power BI specialization of this rule
- [`pages-table-permissions-before-publish.md`](./pages-table-permissions-before-publish.md) — the Power Pages specialization ("test as a portal user, not the admin")
- [`test-data-isolation-and-teardown.md`](./test-data-isolation-and-teardown.md) — isolation in data; this is isolation in identity
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power Pages — Granting a portal user access to a row`
- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — owner ("'Worked as admin' is not a test")

## Provenance

Grounded in the `power-platform-tester` agent's FLS/RLS/sharing and RLS/OLS test discipline, [Power BI RLS](https://learn.microsoft.com/power-bi/enterprise/service-admin-rls) (authors bypass RLS), and the `power-pages-permissions` skill ("test as a portal user, not a portal admin") (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
