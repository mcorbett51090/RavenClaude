---
name: thread-hygiene
description: "Use on long hub threads (CoS, Deputies) or before handing work to a new session: persist state to a file, start a fresh thread per distinct task."
---
# Thread hygiene (session handoff + compaction)
Source: RavenClaude `ravenclaude-core/skills/session-handoff`, `best-practices/compact-proactively-and-persist-state-before-compaction.md` @52fcb08.
1. Fresh thread per distinct task; don't keep image-heavy threads open.
2. Before a thread gets long, write state to `/workspace/state/handoff/<bot>-<topic>.md`: goal, decisions (with who decided), open Matthew decisions, in-flight bot handoffs, file paths.
3. A new thread starts by reading that file, not by replaying history.
4. Hub tracking (open decisions, in-flight work) lives in files, so a Deputy can pick it up.
