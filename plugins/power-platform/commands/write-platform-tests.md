---
description: Write Power Platform tests that catch real defects — run as the real security context (not admin), isolate and tear down test data, and treat DAX correctness as code. Covers Dataverse logic, app behavior, and BI measures.
argument-hint: "[what to test, e.g. 'the approval flow' or 'sales RLS']"
---

# Write platform tests

You are running `/power-platform:write-platform-tests`. Design tests for what the user named (`$ARGUMENTS`), following this plugin's `power-platform-tester` discipline. The recurring failure is "passed as admin, broke for real users" — these tests are built to catch exactly that.

## When to use this

Before shipping Dataverse logic, an app, a flow, or a BI model — especially anything with security (roles, RLS, sharing) or aggregation correctness.

## Steps

1. **Test as the real security context, not admin** (`test-as-real-security-context-not-admin`): exercise the feature as a user with the actual role/sharing — admin has god-mode and hides privilege/RLS bugs. For Power BI, **view-as-role** (`bi-row-level-security-tested-as-role`).
2. **Data isolation + teardown** (`test-data-isolation-and-teardown`): create test data the test owns and tears down; never depend on (or pollute) shared environment data.
3. **DAX correctness as code** (`test-dax-correctness-as-code`): pin expected measure outputs as assertions so a model refactor can't silently change a number.
4. Cover: the happy path, the **denied** path (a user who should NOT see/do it), bulk/volume where relevant, and the fault path.
5. Produce the test plan + the concrete test artifacts (test users/roles to create, the assertions, the teardown).

## Guardrails

- A test that only runs as admin is a false-confidence test — always include the real-user and denied-user cases.
- Never leave test data behind in a shared environment.
- Tee up the test-user/role setup as explicit steps; some require admin action the human runs.
