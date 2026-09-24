# ravenclaude/usage-meter — data branch

This branch is written by the **RavenClaude usage meter**, an hourly claude.ai Routine created by
`/routine-reserve setup` (ravenclaude-core). It is **data, not code**, and it is never merged: it is an
orphan branch with no history in common with any other branch.

| Path | What it is |
|---|---|
| `routine-reserve.py` | The engine the meter runs. The meter checks its sha256 before every run and refuses on a mismatch, so edit it only by re-running `/routine-reserve setup`. |
| `samples/YYYY-MM-DD/*.jsonl` | One file per meter firing. Kept 35 days, then pruned. |

**What a sample holds:** Routine ids, names, schedules, run times, token counts and `cost_usd`, the
model, and whether the meter's own session was attended. **What it never holds:** prompts, session
titles, repo URLs or branches, connectors, environment ids.

Keep this repository **private**. To stop the meter, run `/routine-reserve uninstall`; this branch can
then be deleted by hand.
