# Solution-Aware Flows and Connection References

## Why This Matters for ALM / Git / ADO
Flows inside solutions export as JSON with `connectionReferences` and environment variable references. Hard-coded connection IDs or values cause import failures or wrong bindings in test/prod.

## Rules
1. **Always use Connection References** for every connector in a solution-aware flow.
2. **Use Environment Variables** for any value that differs by environment (SharePoint site, list ID, Dataverse env URL, etc.).
3. After import, re-bind connection references in the target environment.
4. Test the full import + re-bind process on a clean environment before promoting.

## Common Failures
- Flow imports but actions show "Connection not found" or uses wrong connection.
- Expressions still contain hard-coded GUIDs or site URLs.
- Child flows not properly referenced in the solution.

## Git / Source Control Notes
- Flow JSON under Workflows/ can be large and noisy on diffs.
- Focus code reviews on `connectionReferences`, trigger conditions, and env var usage.
- Small, frequent changes are easier to review than large designer edits.

See also `solution-alm-engineer` for pipeline patterns that include flow validation.