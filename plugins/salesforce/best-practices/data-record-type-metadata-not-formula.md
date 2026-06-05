# Resolve Record Type IDs from Schema metadata — never hard-code them

**Status:** Absolute rule
**Domain:** Apex / data modeling
**Applies to:** `salesforce`

---

## Why this exists

A Record Type ID is a 15- or 18-character alphanumeric string that differs between every Salesforce org — production, every sandbox, and every scratch org has different IDs for the same Record Type. Hard-coding a Record Type ID in Apex, a Flow formula, or a Validation Rule expression is a constant deployment failure: the code works in the sandbox that produced it and fails with "invalid record type" or silently assigns the wrong type in every other org. The house opinion #5 ("no hard-coded IDs — query or use custom metadata") is explicitly about this pattern.

## How to apply

```apex
// Wrong — hard-coded, environment-specific
Account acc = new Account(RecordTypeId = '0125g000000XXXXX', Name = 'Acme');

// Correct — resolved from Schema at runtime
Id partnerRecordTypeId = Schema.SObjectType.Account
    .getRecordTypeInfosByDeveloperName()
    .get('Partner')
    .getRecordTypeId();

Account acc = new Account(RecordTypeId = partnerRecordTypeId, Name = 'Acme');
```

In a TestDataFactory, cache the lookup:

```apex
public class TestDataFactory {
    private static Map<String, Id> recordTypeCache = new Map<String, Id>();

    public static Id getRecordTypeId(String sObjectType, String developerName) {
        String key = sObjectType + ':' + developerName;
        if (!recordTypeCache.containsKey(key)) {
            recordTypeCache.put(key,
                Schema.getGlobalDescribe().get(sObjectType)
                    .getDescribe().getRecordTypeInfosByDeveloperName()
                    .get(developerName).getRecordTypeId()
            );
        }
        return recordTypeCache.get(key);
    }
}
```

**Do:**
- Use `getRecordTypeInfosByDeveloperName()` (not `getRecordTypeInfosByName()`) — `DeveloperName` is the API name and is stable across orgs; `Name` is the label and can be localized.
- Cache the lookup in a static variable inside the calling class or TestDataFactory to avoid redundant `getDescribe()` calls within a transaction.
- In Flows, use the `$ObjectType.Account.RecordTypes['DeveloperName'].Id` global reference rather than a hard-coded ID.

**Don't:**
- Use `getRecordTypeInfosByName()` for programmatic lookup — labels can be translated and are not guaranteed stable.
- Store a Record Type ID in a Custom Setting or Custom Metadata record — it will be org-specific and will break on sandbox refresh.
- Use a hard-coded ID in a Validation Rule formula — the formula editor accepts it, but the ID will be wrong in every other org.

## Edge cases / when the rule does NOT apply

When querying `RecordType` SOQL for analytics or reporting (not for assignment), you may use `DeveloperName` or `SobjectType` as the filter instead of the ID — this is portable. The rule targets ID hard-coding on record creation/assignment.

## See also

- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns Apex data operations and is the primary enforcer of this rule
- [`./apex-test-data-with-testfactory-not-seealldata.md`](./apex-test-data-with-testfactory-not-seealldata.md) — the TestDataFactory pattern used for the caching example above

## Provenance

Codifies house opinion #5 ("no hard-coded IDs — records, RecordTypes, profiles — query or use custom metadata") from CLAUDE.md; standard Salesforce deployment best practice.

---

_Last reviewed: 2026-06-05 by `claude`_
