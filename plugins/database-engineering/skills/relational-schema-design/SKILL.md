---
name: relational-schema-design
description: "Design a correct relational schema: normalize to 3NF, denormalize only with measured evidence and a named consistency cost, push constraints (PK/FK/UNIQUE/CHECK/NOT NULL) into the database, and choose precise data types."
---

# Relational Schema Design

## Normalize first
3NF by default: each fact once, relationships via keys. Most 'we must denormalize' instincts are premature.

## Denormalize deliberately
Only with a measured read benefit AND the write/consistency cost named — often a **materialized view** or **covering index** is better than redundant columns.

## Constraints in the DB
PK on every table, FK for every relationship, NOT NULL/UNIQUE/CHECK to make illegal states unrepresentable. The app is not a trustworthy enforcer.

## Types
Precise numeric/temporal/text; `uuid`/`enum`/`jsonb` where they fit. `text` for everything + naive timestamps are smells.
