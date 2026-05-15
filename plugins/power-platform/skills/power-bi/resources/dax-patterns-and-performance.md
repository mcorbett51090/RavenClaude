# DAX Patterns and Performance

## Core Principles
- Put business logic in measures, not duplicated across visuals or calculated columns.
- Use calculation groups (via Tabular Editor) for common patterns (time intelligence, currency conversion, etc.).
- Prefer variables (`VAR`) in measures for readability and performance.
- Avoid circular dependencies and unnecessary context transitions.

## Performance Tools
- DAX Studio (query plan, server timings, VertiPaq analyzer)
- Tabular Editor (best practice analyzer, calculation groups, scripting)
- Performance analyzer in Power BI Desktop
- XMLA endpoint for advanced diagnostics on large models

## Common Patterns
- Time intelligence with proper date table and `SAMEPERIODLASTYEAR()`, `TOTALYTD()`, etc.
- Role-playing dimensions via calculation groups or separate tables.
- Dynamic measures with field parameters or calculation groups.
- Incremental refresh + partitioning for large fact tables.

## When to Escalate
- Very large models or complex composite model scenarios → consider architecture review with `dataverse-architect` or broader team if Dataverse is involved.