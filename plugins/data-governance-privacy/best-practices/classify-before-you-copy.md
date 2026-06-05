# Classify data before copying it — never copy first and classify later

**Status:** Absolute rule
**Domain:** Data classification / governance
**Applies to:** `data-governance-privacy`

---

## Why this exists

Unclassified copies of data are governance debt. A CSV export of a customer list emailed to a vendor, a Jupyter notebook with raw PII loaded into `df`, a Snowflake clone created for a partner demo — each of these creates a copy outside the catalog's lineage graph. When an erasure request arrives, the catalog has no record of these copies. When an audit asks "where does this customer's data live?", the catalog cannot answer for the unclassified copies. The rule is simple: if you are going to copy a data asset, classify it first (or confirm the existing classification applies) and register the copy in the lineage graph before the copy exists.

## How to apply

**Pre-copy checklist (enforce in PR review for any pipeline that creates a new data copy):**

```markdown
## Pre-copy classification review

1. Is the source asset already classified?
   [ ] Yes — confirm classification applies to this copy
   [ ] No — CLASSIFY FIRST before creating the copy

2. Does the copy destination fall within the catalog's tracked lineage?
   [ ] Yes (warehouse, catalog-connected BI tool, registered S3 bucket)
   [ ] No (email, personal laptop, unregistered tool) — STOP

3. Is there a lawful basis for creating this copy?
   [ ] The copy serves the same purpose as the source (same basis applies)
   [ ] The copy serves a new purpose — DOCUMENT the basis before creating

4. Does the copy inherit the source's retention policy?
   [ ] Yes — confirmed
   [ ] No — set a retention policy on the copy before creating it
```

**For ML training set creation (high-risk copy type):**
- Never create a training set from PII columns without explicit steward approval.
- Register the training set in the catalog with a link to the source mart and the PII columns it contains.
- Apply the same masking/pseudonymization to the training set that applies to the source.

**Do:**
- Treat a new data copy as a schema change: it requires review, classification, and catalog registration.
- Build the pre-copy checklist into the pipeline acceptance criteria.

**Don't:**
- Create a "quick" CSV export of customer data for a vendor without completing the classification and lawful-basis check.
- Assume the source's classification automatically covers an unregistered copy.

## Edge cases / when the rule does NOT apply

- Backup snapshots created by a managed database service (RDS automated backups, Supabase PITR) are created by the infrastructure layer without per-copy review; document them in the catalog's backup inventory as a class rather than per-backup.

## See also

- [`../agents/data-governance-architect.md`](../agents/data-governance-architect.md) — enforces the pre-copy review in the governance operating model
- [`./classification-drives-controls.md`](./classification-drives-controls.md) — the classification-to-controls rule that this copy-time check feeds

## Provenance

Codifies data-governance-privacy CLAUDE.md §2 house opinion #1 ("You can't govern what you can't find") and house opinion #2 ("Minimize what you collect") applied to data propagation. GDPR Article 25 (data protection by design and by default) extends the design obligation to copies.

---

_Last reviewed: 2026-06-05 by `claude`_
