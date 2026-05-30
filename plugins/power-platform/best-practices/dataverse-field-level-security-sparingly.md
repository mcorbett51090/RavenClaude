# Reach for column-level (field) security only to hide an individual sensitive column — not as a general access model

**Status:** Pattern — a deliberate, narrow tool; broad use is a performance and complexity tax.

**Domain:** Dataverse / Security

**Applies to:** `power-platform`

---

## Why this exists

Column-level security (CLS / field-level security, FLS) hides an **individual column** from users who can otherwise read the row, via a **Column Security Profile** that grants Read/Create/Update per secured column to specific users/teams. It is the right tool for exactly one shape of requirement: "everyone who can see this row should see most of it, but `cnt_salary` / `cnt_ssn` must be hidden from most of them." It becomes an anti-pattern when reached for first, or applied to dozens of columns, because (a) it **overrides role permissions downward per column** — a user with Org-level Read on the table still gets *nothing* on a secured column unless a profile grants it, which produces "the field is blank / missing" confusion that's really an access fact; (b) every secured column adds evaluation cost on reads; and (c) it collides with other design choices — **you cannot put column security on a column used in an alternate key** (Dataverse lets you try, then throws runtime errors). Record-level access (ownership + role scope + sharing) is the primary security model; FLS is a scalpel on top of it.

## How to apply

Use ownership + role scope + sharing for *record* access first; add FLS only for the specific sensitive columns.

```http
# 1) Mark the column secured (attribute metadata).  IsSecured = true.
PATCH /api/data/v9.2/EntityDefinitions(LogicalName='cnt_employee')/Attributes(<salary-attr-id>)
{ "@odata.type": "Microsoft.Dynamics.CRM.MoneyAttributeMetadata", "IsSecured": true }

# 2) Create a Column Security Profile.
POST /api/data/v9.2/fieldsecurityprofiles
{ "name": "Salary Access Profile" }

# 3) Grant the specific permission on the specific column to the profile.
POST /api/data/v9.2/fieldpermissions
{ "entityname": "cnt_employee", "attributelogicalname": "cnt_salary",
  "canread": 4, "cancreate": 4, "canupdate": 4,          // 4 = Allowed, 0 = Not Allowed
  "fieldsecurityprofileid@odata.bind": "/fieldsecurityprofiles(<profile-id>)" }
# 4) Assign users/teams to the profile (without this, even admins-by-role don't see the column).
```

**Do:**
- Use FLS for a **handful of genuinely sensitive columns** (salary, SSN, bank detail) that must be hidden from users who can otherwise read the row.
- Solve **record-level** visibility with ownership, role scope, and sharing — *first*, and usually that's enough.
- Plan FLS and **alternate keys** together at design time — a column can't be both a key column and column-secured.
- Remember to **assign principals to the profile** — securing a column hides it from *everyone* (including role-admins) until a profile grants them back access.

**Don't:**
- Turn on FLS for 30 columns as your access model — "we'll just turn on field security" across a wide table is a future performance incident, not a security design.
- Diagnose a blank secured column as a "missing field." A column you can't see because of FLS still **exists in metadata** — verify schema and access as two separate checks.
- Apply column security to a column that's part of an **alternate key** — runtime errors, no design-time warning.
- Use FLS to do what **record-level** security should — if whole *rows* should be hidden, that's ownership/scope/sharing, not column security.

## Edge cases / when the rule does NOT apply

- **Regulated PII/PCI/PHI columns** can justify FLS even on a moderately wide table — but that change must also route through `ravenclaude-core` `security-reviewer` (house rule).
- FLS is the *correct* (not sparing) choice when the requirement is literally "same row, different column visibility per role" — e.g. an HR record where managers see review notes but not compensation.
- **Masking** (showing partial values like `***-**-1234`) is a related but distinct CLS capability — reach for it when "hidden entirely" is too blunt.
- A secured column legitimately appears **blank in canvas/MDA, Web API, and exports** for unauthorized users — that's the feature working, not a data bug.

## See also

- [`../skills/dataverse-web-api/resources/security-model.md`](../skills/dataverse-web-api/resources/security-model.md) — Layer 7 column-level security setup, "Field Security Overrides Role Permissions," the alternate-key incompatibility gotcha
- [`./dataverse-security-least-privilege-roles.md`](./dataverse-security-least-privilege-roles.md) — the record-level model FLS sits on top of
- [`./dataverse-alternate-keys-and-upsert.md`](./dataverse-alternate-keys-and-upsert.md) — why a key column can't also be column-secured
- [`./dataverse-access-error-is-not-a-schema-error.md`](./dataverse-access-error-is-not-a-schema-error.md) — a hidden column is an access fact, not a schema fact
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Security — record access mechanism (role scope vs team vs sharing)`
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; "FLS sparingly … reach for it only when an individual column needs to be hidden"

## Provenance

Grounded in `skills/dataverse-web-api/resources/security-model.md` (Layer 7 setup steps, `IsSecured`, Column Security Profiles, "Field Security Overrides Role Permissions," the alternate-key + column-security runtime-error gotcha) and the `dataverse-architect` opinions ("FLS sparingly. Use ownership + sharing first"; anti-pattern "'We'll just turn on FLS' applied to 30 columns … a future performance incident"). Masking is noted as a related CLS capability — verify current masking behavior against Microsoft Learn before quoting specifics.

---

_Last reviewed: 2026-05-30 by `claude`_
