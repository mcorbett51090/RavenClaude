# Data Governance & Privacy — best-practice docs

Named, citable rules for the `data-governance-privacy` plugin's specialists. Each file is **one rule**, grounded in this plugin's house opinions and the catalog/privacy/governance engineering craft. Read, applied, and cited as a whole.

---

## Index

_22 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`automate-discovery-and-keep-it-current.md`](./automate-discovery-and-keep-it-current.md) | Absolute rule | A new data source was added and PII scanning hasn't been run. |
| [`least-privilege-data-access.md`](./least-privilege-data-access.md) | Absolute rule | Reviewing database roles or access grants for over-provisioned access. |
| [`classification-drives-controls.md`](./classification-drives-controls.md) | Absolute rule | Determining which security controls apply to a data asset. |
| [`data-subject-rights-are-engineered.md`](./data-subject-rights-are-engineered.md) | Absolute rule | Building or auditing a data-subject request (DSR) pipeline. |
| [`retention-is-a-lifecycle-not-forever.md`](./retention-is-a-lifecycle-not-forever.md) | Absolute rule | A data asset has no defined retention period — add one before it is collected. |
| [`privacy-by-design-and-default.md`](./privacy-by-design-and-default.md) | Absolute rule | Designing a new data model or pipeline — privacy controls go in at design time. |
| [`lineage-enables-impact-analysis.md`](./lineage-enables-impact-analysis.md) | Absolute rule | A schema change is being evaluated — run impact analysis via the lineage graph first. |
| [`you-cant-govern-what-you-cant-find.md`](./you-cant-govern-what-you-cant-find.md) | Absolute rule | Starting a governance program — discovery and catalog come before policy. |
| [`know-your-lawful-basis-honor-consent.md`](./know-your-lawful-basis-honor-consent.md) | Absolute rule | A new use of personal data is proposed — verify the lawful basis before proceeding. |
| [`govern-the-highest-risk-data-first.md`](./govern-the-highest-risk-data-first.md) | Pattern | Prioritizing governance effort across many data assets with limited capacity. |
| [`governance-engineering-not-legal-advice.md`](./governance-engineering-not-legal-advice.md) | Absolute rule | A request requires a legal interpretation — route it out of scope; we engineer the capability. |
| [`pseudonymization-is-not-anonymization.md`](./pseudonymization-is-not-anonymization.md) | Absolute rule | A dataset is claimed to be "anonymized" — verify it meets the re-identifiability standard. |
| [`pii-discovery-before-any-new-pipeline.md`](./pii-discovery-before-any-new-pipeline.md) | Absolute rule | A new data pipeline is being connected — run PII discovery and classify before first load. |
| [`dsr-pipeline-covers-all-systems.md`](./dsr-pipeline-covers-all-systems.md) | Absolute rule | Building or auditing a DSR pipeline — it must cover every system holding the subject's data. |
| [`consent-store-is-a-system-of-record.md`](./consent-store-is-a-system-of-record.md) | Absolute rule | Implementing consent tracking — use an append-only event log, not a mutable boolean flag. |
| [`column-level-masking-before-broad-access.md`](./column-level-masking-before-broad-access.md) | Absolute rule | Granting broad read access to a mart — apply column-level masking on PII columns first. |
| [`business-glossary-entry-for-every-governed-term.md`](./business-glossary-entry-for-every-governed-term.md) | Pattern | A KPI is cited in a stakeholder report — ensure it has a governed glossary entry. |
| [`minimize-collection-at-schema-design-time.md`](./minimize-collection-at-schema-design-time.md) | Absolute rule | A new PII field is proposed — challenge the need before adding it to the schema. |
| [`lineage-must-track-derived-and-copied-pii.md`](./lineage-must-track-derived-and-copied-pii.md) | Absolute rule | A DSR erasure is being scoped — lineage must cover all downstream copies of PII columns. |
| [`stewardship-not-just-policy.md`](./stewardship-not-just-policy.md) | Absolute rule | A governance program has policies but no named steward for a domain — assign one. |
| [`access-request-workflow-not-ad-hoc.md`](./access-request-workflow-not-ad-hoc.md) | Absolute rule | A Confidential or Restricted data access request is being made — route it through the workflow. |
| [`classify-before-you-copy.md`](./classify-before-you-copy.md) | Absolute rule | Any data copy is being created — classify and register in the catalog before copying. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — data-governance-privacy team constitution (§2 house opinions, §3 seams).
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
