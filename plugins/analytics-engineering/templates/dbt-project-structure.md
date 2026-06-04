# dbt project structure

```
models/
  staging/
    stg_<source>__<entity>.sql   # 1:1 with source; rename/cast/clean
  intermediate/
    int_<concept>.sql            # compose, business logic
  marts/
    core/
      fct_<process>.sql          # facts (events/transactions)
      dim_<entity>.sql           # dimensions
```

- `ref()`/`source()` everywhere; macros for repeated logic.
- Each model: owner + description + column docs + tests.
