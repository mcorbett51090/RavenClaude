# Isolate test data

Each test should create and tear down its own data via factories/builders. Shared mutable fixtures are the leading cause of order-dependence and flake, and they make parallelization unsafe. Isolation is the precondition for a fast, parallel, trustworthy suite.
