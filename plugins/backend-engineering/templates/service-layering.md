# Service layering (pattern)

```
edge/        HTTP / framework adapters (thin)
  -> use-cases/   business logic (plain, testable)
       -> domain/     entities + rules (no framework)
       -> repositories/ data-access (transaction boundaries)
```

- Framework at the edges only.
- Errors: typed (expected vs bug) -> mapped to status at the edge.
- Inputs parsed/validated into domain types at the boundary.
