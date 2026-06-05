# A data-subject request pipeline must cover every system that holds the subject's data

**Status:** Absolute rule
**Domain:** Privacy / DSR engineering
**Applies to:** `data-governance-privacy`

---

## Why this exists

A DSR pipeline that covers the CRM but not the data warehouse, the warehouse but not the backup snapshots, or the primary database but not the analytics exports is a failed capability. "We can't locate all their data" is not an acceptable response to an erasure or access request — it is a regulatory violation. The catalog and lineage system is the prerequisite: the DSR pipeline can only span the systems it has been told about. An incomplete catalog produces an incomplete DSR, and an incomplete erasure leaves PII in systems the subject has the right to have it removed from.

## How to apply

**System inventory for DSR scope (maintain in the data catalog):**

```markdown
## Systems holding personal data for [domain]

| System | Data types | DSR method | SLA |
|---|---|---|---|
| Postgres (production DB) | Account, user profile | SQL DELETE/export | 24 hours |
| Data warehouse (marts) | Behavioral events, aggregates | dbt snapshot deletion + mart rebuild | 48 hours |
| Backup snapshots | Full DB | Documented exclusion (financial record retention) OR re-point | Per retention policy |
| S3 raw data lake | Raw event logs | S3 lifecycle rule + manifest delete | 72 hours |
| CRM (Salesforce) | Contact, company | SFDC API delete | 48 hours |
| Email marketing (HubSpot) | Contact, email history | HubSpot GDPR delete | 24 hours |
| Support tool (Zendesk) | Ticket, conversation body | Zendesk GDPR API | 24 hours |
```

**DSR pipeline automation:**

```python
def execute_erasure_dsr(subject_id: str) -> dict:
    results = {}
    # Ordered by blast radius (most impactful first)
    results['warehouse'] = erase_from_warehouse(subject_id)
    results['crm'] = erase_from_crm(subject_id)
    results['support'] = erase_from_support(subject_id)
    results['marketing'] = erase_from_marketing(subject_id)
    results['raw_lake'] = erase_from_raw_lake(subject_id)
    # Verify no residue in any system
    results['verification'] = verify_erasure_complete(subject_id)
    return results
```

**Do:**
- Maintain the system inventory in the catalog and update it when a new data source is added.
- Automate the erasure pipeline rather than relying on manual per-system requests.
- Include the verification step — an erasure that hasn't been verified hasn't been completed.
- Document any systems where retention obligations prevent full erasure and communicate this to the subject.

**Don't:**
- Scope the DSR pipeline to only the "obvious" systems (prod DB, CRM) and leave the warehouse, backups, and SaaS tools out.
- Accept "we don't know if it's in there" as an answer — the catalog should remove this uncertainty.

## Edge cases / when the rule does NOT apply

- Backup snapshots that cannot be partially deleted (binary backup files) may be documented as an exclusion with a time-limited retention policy — the subject is informed of the exclusion and its end date. This is an acceptable documented exception, not a blanket exemption.

## See also

- [`../agents/privacy-compliance-engineer.md`](../agents/privacy-compliance-engineer.md) — builds and operates the DSR pipeline
- [`./data-subject-rights-are-engineered.md`](./data-subject-rights-are-engineered.md) — the parent rule this specializes

## Provenance

Codifies data-governance-privacy CLAUDE.md §2 house opinion #4 ("Data-subject rights are an engineered capability. Access, erasure, and portability must be executable across every system that holds the person's data"). GDPR Article 17 (right to erasure) and Article 15 (right of access) both require completeness.

---

_Last reviewed: 2026-06-05 by `claude`_
