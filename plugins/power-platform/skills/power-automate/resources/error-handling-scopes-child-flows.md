# Error Handling, Scopes, and Child Flows

## Top-Level Try-Catch-Finally Pattern
Every production flow should have a top-level Scope named **Try**, **Catch**, and **Finally** (or similar).
- Configure **run after** on Catch and Finally appropriately.
- In Catch: log error, send notification, terminate with proper status.

## Child Flows
- Extract reusable logic into child flows.
- Define clear input/output schemas.
- Use **Respond to a Power App or flow** action in the child.
- Child flows inherit the solution context and connection references of the parent when called from within a solution.

## Scope Best Practices
- Use Scopes to group related actions and limit the blast radius of errors.
- Parallel branches inside Scopes for independent work.
- Terminate action inside Catch to control final flow status.

## Dataverse Trigger Specifics
- Use **Filter rows** and **Run only when columns change** to reduce noise.
- Control recursion with proper update logic or depth checks.
- Prefer alternate keys over GUIDs in expressions.