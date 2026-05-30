# Bind every variable in dynamic SOQL — never concatenate user input

**Status:** Absolute rule — string concatenation of untrusted input into SOQL is an injection vulnerability; the verdict escalates to core.

**Domain:** Apex / SOQL security

**Applies to:** `salesforce`

---

## Why this exists

Apex offers a static query syntax (`[SELECT ...]`) and a dynamic one (`Database.query(String)`). The dynamic form is necessary when the object, fields, or filters aren't known at compile time — but the moment a query is built by **concatenating a string**, any user-controlled value can break out of its literal and rewrite the `WHERE` clause. The classic is a filter like `'... WHERE Name = \'' + userInput + '\''` where `userInput` is `x' OR Name != '` — now the query returns every row, bypassing the intended filter and, with it, any data scoping the query relied on. **Bind variables** (`:var`) pass values as parameters, not as query text, so they cannot alter the query structure. This is house opinion #8; the security *verdict* is owned by `ravenclaude-core/security-reviewer`.

## How to apply

Prefer the static `[...]` form. When dynamic SOQL is genuinely required, pass values through a bind map (or `:var` in the bound overload) — never `+`. If a value must be concatenated (an identifier that can't be bound, like a field or object name), validate it against an allow-list, never against user free-text.

```apex
// DON'T — concatenated user input; injectable
String soql = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';
List<Account> a = Database.query(soql);          // x' OR Name != ' returns everything

// DO — bind the value; structure is fixed, value is a parameter
String soql = 'SELECT Id FROM Account WHERE Name = :searchName WITH SECURITY_ENFORCED';
List<Account> a = Database.queryWithBinds(
    soql,
    new Map<String, Object>{ 'searchName' => userInput },
    AccessLevel.USER_MODE);                       // bound + FLS-enforced + user mode

// If you MUST concatenate an identifier (field/object name), allow-list it:
Set<String> allowedFields = new Set<String>{ 'Name', 'Industry', 'AnnualRevenue' };
if (!allowedFields.contains(fieldName)) {
    throw new IllegalArgumentException('Field not permitted: ' + fieldName);
}
String soql2 = 'SELECT Id FROM Account WHERE ' + fieldName + ' = :val';   // identifier vetted, value bound
```

**Do:**
- Use the static `[SELECT ...]` form unless the query shape is genuinely runtime-determined.
- Bind every **value** with `:var` or a bind map (`Database.queryWithBinds` / `getQueryLocatorWithBinds`).
- Allow-list any **identifier** (object/field name) you must concatenate — never accept it as free text.
- Add `WITH SECURITY_ENFORCED` / `AccessLevel.USER_MODE` so the dynamic query also enforces FLS.
- Escalate any injection finding to `ravenclaude-core/security-reviewer`.

**Don't:**
- Build a `WHERE` clause with `+` and user input — that is the vulnerability by definition.
- Rely on `String.escapeSingleQuotes` alone as the primary defense — it's a fallback for unavoidable concatenation, not a substitute for binding.

## Edge cases / when the rule does NOT apply

`String.escapeSingleQuotes()` is the **fallback** when a value truly cannot be bound (rare) — it neutralizes quote-breakout but not every injection vector, so binding is always preferred. Identifiers (object names, field names, an `ORDER BY` column) **cannot** be bound — they must be allow-listed against a known set, never escaped-and-concatenated from user input. A query built entirely from **trusted, hard-coded** strings with no external input isn't an injection risk, but binding it costs nothing and keeps the pattern uniform. The static `[...]` form binds Apex variables automatically and is never injectable.

## See also

- [`./apex-query-selectively-with-indexes.md`](./apex-query-selectively-with-indexes.md) — the bound collections you filter on must also be selective
- [`./enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — bind *and* FLS-enforce user-context queries
- [`../skills/soql-authoring/SKILL.md`](../skills/soql-authoring/SKILL.md) — step 3 binds every variable
- [`../knowledge/apex-decision-trees.md`](../knowledge/apex-decision-trees.md) — the security-enforcement decision tree
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns binding; injection verdict escalates to `ravenclaude-core/security-reviewer`

## Provenance

Codifies house opinion #8 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../skills/soql-authoring/SKILL.md`](../skills/soql-authoring/SKILL.md) step 3 and the `salesforce-reviewer` rubric item 8. The `Database.queryWithBinds` / `AccessLevel.USER_MODE` APIs and the SOQL-injection mechanism are documented Apex platform behaviors; exact method signatures tagged `[verify-at-build]`. Security verdict escalation per [`../CLAUDE.md`](../CLAUDE.md) cross-plugin seams.

---

_Last reviewed: 2026-05-30 by `claude`_
