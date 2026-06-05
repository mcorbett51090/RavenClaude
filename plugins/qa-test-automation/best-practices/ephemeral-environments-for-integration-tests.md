# Use ephemeral environments for integration tests — shared envs cause flakiness

**Status:** Absolute rule
**Domain:** Test infrastructure
**Applies to:** `qa-test-automation`

---

## Why this exists

A shared "integration" or "QA" environment that multiple CI runs read from and write to is a flakiness factory. Run A's test data bleeds into Run B's assertions; a broken deployment by Team C fails Run D's tests; environment drift from manual changes makes failures non-reproducible. Ephemeral environments — spun up per CI run, torn down afterward — eliminate the shared-state problem by making each test run the only tenant of its environment.

## How to apply

Use Testcontainers for service dependencies in integration tests (database, message broker, cache). For more complex scenarios requiring a full stack, use Docker Compose in CI or a Kubernetes namespace-per-PR pattern.

```java
// Java + Testcontainers: ephemeral Postgres per test class
@Testcontainers
class OrderRepositoryTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
        .withDatabaseName("orders_test")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void saves_and_retrieves_an_order() {
        // test against a fresh Postgres container — no shared state
    }
}
```

```yaml
# GitHub Actions: ephemeral service containers per CI run
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 3s
          --health-retries 5
```

**Do:**
- Start containers in the test framework's setup hook and stop them in teardown — keep the lifecycle in code, not in shared infrastructure.
- Use health-check options on service containers; don't sleep waiting for them to be ready.
- Seed test data in the test or its factory — never rely on data that a previous test run created.

**Don't:**
- Run integration tests against a shared staging database in CI.
- Use `sleep` to wait for a container to be ready — use `waitingFor(Wait.forHealthcheck())`.
- Assume the container hostname is `localhost` in Docker-in-Docker; check the Testcontainers docs for your runner.

## Edge cases / when the rule does NOT apply

End-to-end tests covering a full deployed stack (not just integration tests) may need a persistent shared environment when the cost of spinning up the full stack per run is prohibitive. In that case, enforce strict test-data isolation (each test creates and cleans up its own data with unique identifiers) to prevent cross-run contamination.

## See also

- [`../agents/test-infrastructure-engineer.md`](../agents/test-infrastructure-engineer.md) — owns ephemeral environment design and test infrastructure.
- [`./isolate-test-data.md`](./isolate-test-data.md) — even with ephemeral environments, per-test data isolation is required.

## Provenance

Codifies the Testcontainers project's core value proposition (testcontainers.com) and the "test environment parity" principle from the 12-Factor App methodology (dev/test/prod parity).

---

_Last reviewed: 2026-06-05 by `claude`_
