# Schema design — <domain>

## Tables
```sql
CREATE TABLE orders (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid NOT NULL REFERENCES customers(id),
  status      text NOT NULL CHECK (status IN ('pending','paid','shipped','cancelled')),
  total_cents integer NOT NULL CHECK (total_cents >= 0),
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON orders (customer_id);   -- for the actual access pattern
```
- 3NF; constraints in-DB; precise types; timestamptz not naive.
- Denormalization (if any) + its named cost: <...>
