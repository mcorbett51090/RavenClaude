# Use SOSL for cross-object text search — SOQL with LIKE is not a search engine

**Status:** Pattern
**Domain:** Apex / SOQL/SOSL
**Applies to:** `salesforce`

---

## Why this exists

`SOQL` with `LIKE '%search term%'` performs a **full-table scan** — it is the most non-selective query possible, guaranteed to hit the Salesforce optimizer's selectivity thresholds on any object with a meaningful row count. `SOSL` (Salesforce Object Search Language) is backed by a full-text search index and can search across multiple objects in a single statement. When a user enters a search term and the requirement is "find matching records across Contact, Lead, and Account," `SOQL LIKE` queries run in a loop against each object — three full-table scans and three API calls. One `SOSL` query returns results from all three objects with a single index-backed search. Engineers who default to `SOQL LIKE` for text search are choosing the slower, less selective, multi-query path when a purpose-built facility exists.

## How to apply

```apex
// Wrong — full-table scan, three API calls, governor-limit wasteful
String term = '%' + String.escapeSingleQuotes(searchTerm) + '%';
List<Contact> contacts = [SELECT Id, Name FROM Contact WHERE Name LIKE :term];
List<Lead> leads = [SELECT Id, Name FROM Lead WHERE Name LIKE :term];
List<Account> accounts = [SELECT Id, Name FROM Account WHERE Name LIKE :term];

// Correct — single SOSL, cross-object, index-backed
String soslQuery = 'FIND {' + String.escapeSingleQuotes(searchTerm) + '} IN ALL FIELDS '
    + 'RETURNING Contact(Id, Name), Lead(Id, Name), Account(Id, Name) LIMIT 25';
List<List<SObject>> results = Search.query(soslQuery);
List<Contact> contacts = (List<Contact>) results[0];
List<Lead> leads = (List<Lead>) results[1];
List<Account> accounts = (List<Account>) results[2];
```

**Do:**
- Use `String.escapeSingleQuotes()` when constructing SOSL queries with user input — SOSL injection is possible, though less exploitable than SOQL injection.
- Apply `LIMIT` at the SOSL level and per-object level to prevent oversized results.
- Use `IN NAME FIELDS` when you only need to search Name/title fields, `IN ALL FIELDS` for full-text; `IN ALL FIELDS` has a higher compute cost.

**Don't:**
- Use `SOQL LIKE '%term%'` on any object with > 10,000 rows — the query optimizer cannot use an index on a leading-wildcard LIKE.
- Use SOSL as a replacement for SOQL when you need equality filtering on an indexed field (`Account.Id = '001...'`) — SOQL with an indexed equality filter is faster than SOSL for exact-match lookups.
- Pass unconstrained user input directly into a SOSL query string without `escapeSingleQuotes` — SOSL metacharacters (`?`, `*`, `&`, `|`, `!`, `^`, `~`, `:`, `"`, `'`, `(`, `)`, `{`, `}`, `[`, `]`) must be escaped.

## Edge cases / when the rule does NOT apply

For a single-object search on a field that has an indexed, non-wildcard filter (e.g., `Email = :emailAddress`), SOQL with the exact-match index is faster and more selective than SOSL. SOSL is for full-text, cross-object, or wildcard-prefix searches.

## See also

- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns query strategy and is the primary enforcer of this rule
- [`./data-selective-soql-on-indexed-fields.md`](./data-selective-soql-on-indexed-fields.md) — the SOQL selectivity rule that explains why LIKE full-table scans are problematic

## Provenance

Codifies standard Salesforce developer best practice for cross-object text search; Salesforce SOSL developer guide.

---

_Last reviewed: 2026-06-05 by `claude`_
