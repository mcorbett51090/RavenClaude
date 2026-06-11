# FERPA is a design constraint, not an afterthought

**Status:** Absolute rule.

**Rule:** Student education records carry legal handling requirements. Data flows, dashboards, and
early-alert systems are designed FERPA-aware from the start — built around who has a legitimate
educational interest — not retrofitted after the fact.

## Why

FERPA governs personally identifiable information in student education records: who may access it,
for what purpose, and how it may be disclosed. An early-alert dashboard or shared spreadsheet that
exposes student risk data to people without a legitimate educational interest is a compliance
violation, regardless of good intentions. Retrofitting access control onto a system already in use is
expensive and leaves exposure in the gap.

## What it looks like in practice

- Before building, classify the data (is it an education record?) and map who has a legitimate
  educational interest in each field.
- Access control is scoped to that interest; disclosure points (to parents, third parties, vendors)
  are identified and governed.
- Compliance specifics are flagged for verification against current regulation, state law, and
  institutional counsel — not asserted from memory.

## Anti-pattern

Building a student-risk dashboard or sharing cohort records first and asking about FERPA later. The
hook flags student-data handling described with no FERPA/privacy note.
