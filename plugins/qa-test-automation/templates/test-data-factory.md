# Test data factory (pattern)

```
buildUser(overrides) -> { id: uuid(), email: unique(), ...defaults, ...overrides }
```
- Each test calls a factory; never reuses another test's row.
- Ephemeral DB per run (Testcontainers); torn down after.
- Local == CI by containerizing the dependency.
