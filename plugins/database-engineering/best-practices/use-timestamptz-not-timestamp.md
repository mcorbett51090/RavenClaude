# Store timestamps as TIMESTAMPTZ, not TIMESTAMP

**Status:** Absolute rule
**Domain:** Schema design
**Applies to:** `database-engineering`

---

## Why this exists

PostgreSQL's `TIMESTAMP` (without time zone) stores a bare datetime with no timezone context. When the application server is in UTC but the database server is in a different timezone, or when users in multiple timezones read the same data, `TIMESTAMP` produces silently wrong comparisons and incorrect ORDER BY results. `TIMESTAMPTZ` stores an absolute moment in UTC internally and renders it in the session timezone on retrieval — the correct default for any system with more than one timezone or any deployment that could ever change its server timezone.

## How to apply

```sql
-- Bad: timezone-ambiguous
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()  -- what timezone is this?
);

-- Good: absolute UTC-stored timestamps
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- stored as UTC, rendered per session
);

-- Correct interval query (works regardless of session timezone)
SELECT * FROM orders
WHERE created_at >= NOW() - INTERVAL '7 days';

-- Migration from TIMESTAMP to TIMESTAMPTZ
ALTER TABLE orders
  ALTER COLUMN created_at TYPE TIMESTAMPTZ
  USING created_at AT TIME ZONE 'UTC';  -- interpret existing data as UTC
```

**Do:**
- Use `TIMESTAMPTZ` for every timestamp column as the default.
- Store all timestamps in UTC at the application layer before writing to the database.
- Use `NOW()` or `CURRENT_TIMESTAMP` as the default — these return the current moment in UTC.

**Don't:**
- Use `TIMESTAMP WITHOUT TIME ZONE` unless you are explicitly modeling a local/wall-clock concept (e.g., a meeting time that should render the same in any timezone).
- Store epoch integers as a substitute — `TIMESTAMPTZ` supports range queries, indexes, and arithmetic natively.
- Accept a timezone-naive datetime from user input without normalizing to UTC first.

## Edge cases / when the rule does NOT apply

A scheduling or calendar application may legitimately need `TIMESTAMP` (timezone-naïve) to represent "2 PM on this date, wherever you are" — a recurring meeting time that must not shift when a user changes timezone. In that case, store the timezone separately as a `text` column and document the intentional choice.

## See also

- [`../agents/schema-architect.md`](../agents/schema-architect.md) — owns data type selection and schema design.
- [`./be-explicit-about-null-semantics.md`](./be-explicit-about-null-semantics.md) — null semantics for timestamp columns (nullable vs NOT NULL DEFAULT) are a closely related schema decision.

## Provenance

PostgreSQL documentation on date/time types (postgresql.org/docs/current/datatype-datetime.html). Standard correctness requirement for multi-timezone applications. Codifies `schema-architect`'s data-type discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
