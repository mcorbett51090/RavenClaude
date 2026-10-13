---
name: stop-and-reread
description: "Use when the same tool+error repeats 3 times, a fix looks impossible, or before each step of a multi-step build: stop, re-read the brief verbatim, then take the documented default or escalate."
---
# Stop-and-reread
Source: RavenClaude `ravenclaude-core/skills/wall-handling`, `spec-reread-ritual` @52fcb08.
1. **Wall = same tool + same error 3×**, a missing API surface, or a fix that needs inventing behaviour. STOP. Do not invent APIs, delete checks, suppress errors, or retry a 4th time.
2. Then: take the documented default with an inline note, OR hand off per NOT-MY-JOB (auth/connector walls → Auth be572ce0; SCM → Sage f3c066b2), OR escalate a Matthew decision via CoS (recommended option first).
3. **Re-read before acting:** before each step of a multi-step build, re-read the relevant brief/spec section verbatim and quote it in your work log; no work from memory.
4. Blocker-first: after a wall, move to the earliest unblocked item; never idle with an unblocked queue.
5. Never route around an Auto-review block; gates → CoS.
