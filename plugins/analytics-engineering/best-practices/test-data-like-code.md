# Test transformations like code, in CI

Add not_null, unique, accepted_values, relationships, and freshness tests on the columns that matter and run them in CI and production so the build fails on a violation. An untested transformation ships silent corruption to every downstream dashboard, and the failure surfaces as a stakeholder questioning a number rather than a red build. Data quality is a gate, not an afterthought.
