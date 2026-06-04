# Respect the test pyramid

Many fast unit tests, fewer integration tests, a few high-value E2E. The inverted 'ice-cream cone' (mostly slow E2E) is the most common cause of suites that are slow, flaky, and expensive to maintain. Push each assertion to the cheapest level that can catch the defect.
