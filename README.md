# ravenclaude/session-claims (data branch: never merge)

One JSON file per local Claude CLI session, at `claims/<host>/<session_id>.json`,
written by `scripts/session-claims.py` (installed per machine with
`python3 scripts/session-claims.py install`). The "Overnight session resume" routine
reads these to avoid restarting cloud work that collides with local work.
See docs/overnight-session-resume-routine.md on main.

This branch shares no history with main. Do not open a pull request from it.
