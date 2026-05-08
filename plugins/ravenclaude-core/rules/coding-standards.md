# Rule: Coding Standards (long form)

These rules expand on §2 of CLAUDE.md. When CLAUDE.md and this file conflict, CLAUDE.md wins.

## Read before write
- Open the file you're about to change. Read it top to bottom.
- Open one or two sibling files in the same directory. Note their conventions.
- If the change crosses a module boundary, read the boundary's contract (types, interface file, doc comment) first.

## Naming
- Identifiers describe **intent**, not type. `userIds` not `arr`. `isExpired` not `flag`.
- Functions are verbs. `parseToken`, `loadConfig`, `flushQueue`. Pure data transforms can be nouns when used as values (`asJson`, `toIsoString`).
- Booleans read like English: `isReady`, `hasPermission`, `shouldRetry`. Never `notFinished` (double negative).
- Avoid abbreviations except those already used in the codebase. If the project says `cfg`, use `cfg`; don't introduce `config`.

## Functions
- One job per function. If you're naming it `validateAndSave`, split it.
- Parameters: 0–3 ideal, 4 acceptable, 5+ → take an object.
- Return early. Nest only when nesting reflects real logical structure, not laziness.
- A function that returns `null | undefined | T` is suspicious. Pick one absent value and stick with it.

## Error handling
- Catch where you can act. Catching to log-and-rethrow is rarely useful — let it propagate.
- Never `catch (e) {}` (silent swallow). If you really want to ignore, comment *why* and what evidence proves it's safe.
- Errors at boundaries (HTTP, queue, CLI) get translated to a user-shaped error. Errors inside the system stay raw.

## State & mutation
- Prefer immutable data flowing through pure functions. Mutate only where the language idiomatically does (e.g. building up a list locally before returning it).
- Module-level mutable state is contraband. If you reach for it, justify it in a comment.
- `Date.now()`, `Math.random()`, and similar non-deterministic calls live in **one** clearly named place per module so tests can fake them.

## Comments
- Default: no comment.
- A good comment answers "why is this written this way?" — not "what does this do?"
- Workarounds get a comment with a link to the upstream issue.
- TODO comments require an issue link. `// TODO` alone is forbidden; `// TODO(#1234): …` is fine.

## Files
- One concept per file. If a file has two unrelated concepts, split it before adding a third.
- File names match the primary export when the language has that convention.
- New top-level directories require explicit Team Lead approval — they shape the architecture, not just the file tree.

## Dependencies
- Standard library first. Then a vetted dependency the project already uses. Adding a *new* dependency is a Team Lead decision.
- Never copy-paste a snippet from a license-ambiguous source. If you need to attribute, you probably shouldn't be using it.

## Performance
- Don't optimize before measuring. Don't ship obvious O(n²) over user-scale data either.
- A `for` loop with a known small bound is fine. A nested loop over two unbounded inputs is not.
- Allocate inside loops with care; preallocate or stream when input size is unbounded.

## Tests are part of the change
- Same PR, same commit when reasonable. A "tests follow-up" PR is an anti-pattern.
- Test names describe the behavior under test, not the function name.
- Tests that need real I/O get real I/O (or a test container). Don't mock the database for an integration test.
