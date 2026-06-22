# Sample code is production code

**Stance:** every snippet, quickstart, and sample app is held to production
standards, because it is copied verbatim into real codebases.

## Why

Developers don't read sample code — they copy it. A sample with a hardcoded API key
teaches a secret-leak to everyone who pastes it; a happy-path-only snippet breaks
the moment a rate limit or auth expiry shows up in production; an unpinned
dependency rots into a confusing error when a breaking change ships. The blast
radius of a bad sample is every developer who trusted it, and the trust you lose is
not recoverable.

## In practice

- **It runs from a clean checkout** with documented, minimal setup. If it doesn't
  run from clean, it isn't done.
- **No hardcoded secrets** — env vars or a secret manager, never a literal key.
  Teach the secure pattern; route deep auth/secret questions to
  `security-engineering`. (The hook flags hardcoded secrets.)
- **Handle real errors** — rate limits, auth expiry, bad input. (The hook flags
  swallowed/ignored errors.)
- **Pin versions** so the sample doesn't rot.
- **Show the value path, including the hard parts** — a toy that hides them sets up
  a cliff.

## Smell

A code sample with `apiKey = "sk-..."` in it, an empty `catch {}`, or a sample
nobody has run from a clean machine since it was written.
