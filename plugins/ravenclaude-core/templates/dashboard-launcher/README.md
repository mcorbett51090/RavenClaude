# RavenClaude — this repo's config

This folder holds **this repo's** RavenClaude settings. Editing here affects **only this
repo** — never the marketplace clone.

- `comfort-posture.yaml` — your permission + command-review posture (the dashboard writes this).
- `environment-context.md` — optional: which environments you're authorized in.

## Open the comfort-posture dashboard

A point-and-click editor for the settings above. **Save & apply** writes
`comfort-posture.yaml` and updates `.claude/settings.json` in one step. Use whichever is easiest:

- **VS Code (one click):** Terminal → **Run Task** → **RavenClaude: Comfort-posture dashboard**.
- **Terminal (from this repo):** `bash .ravenclaude/dashboard.sh`
- **From anywhere:** `ravenclaude dashboard --project /path/to/this/repo`

Each starts a small **local** server scoped to **this repo**, then **prints the dashboard URL
and opens it in your browser automatically**. The URL is computed fresh at launch — the live
**Codespace-forwarded** address in a Codespace, or `localhost` otherwise — so there is never a
stale link to hunt for or fix (nothing is baked in to rot when a Codespace is rebuilt). In a
Codespace, if the tab doesn't open, use the **Ports** panel → port **8000** → 🌐 **Open in
Browser** — that handles the GitHub sign-in for the private port (a raw link paste can hit an
auth wall). Use a real browser tab, not VS Code's Simple Browser (which blocks the page). Run
the launcher again to restart it, or `pkill -f serve-dashboards.py` to stop it.

> Scoped & safe: the launcher pins this repo's path, and the server refuses to run if it's
> ever pointed at the marketplace clone — so a consumer dashboard can only edit its own repo.

## Containment posture — where the real blast-radius boundary is

The comfort-posture and the command-review tribunal are **model-layer** guardrails: they stop
the agent's own tools (a `Read`, an `Edit`, a `Bash` command) and refuse the dangerous ones.
That covers most of the risk, but it has one honest gap — it can't bound a **subprocess** the
agent spawns. A `deny` on `Read(~/.ssh/**)` stops the agent reading your keys with its Read
tool; it does **not** stop a script the agent writes and runs (`python -c "open('~/.ssh/id_rsa')…"`).
Only the **operating system** can enforce that boundary, because the OS — not the model — holds
the line even when a command is mislabeled or an injected instruction slips through.

So the sanctioned containment posture is **defense in depth**:

1. **Run inside the container (strongest, and the same under any model).** The devcontainer this
   marketplace scaffolds — `ravenclaude init-codespace`, or a GitHub Codespace — is the real
   blast-radius boundary: the agent can only touch what's mounted into the container, and that
   holds whether you run Claude Code, GitHub Copilot CLI, or anything else. For risky or
   parallel work, add a **git worktree** so a run is isolated to its own branch checkout.
2. **Tool-layer deny rules (this repo's posture).** The balanced posture denies reads of host
   credential stores that live outside the repo (`~/.ssh`, `~/.aws`, `~/.config/gcloud`,
   `~/.azure`, `~/.kube/config`, `~/.docker/config.json`) plus in-repo secrets (`.env`, `*.pem`,
   `*.key`). These are honored by Claude Code's permission engine **and** by the Thing's
   `file_read_global` review, so they port to Copilot CLI — but remember they are tool-layer,
   not OS isolation (see the subprocess gap above). Re-tune them in the dashboard.
3. **Claude Code's OS sandbox is Claude-only — do not rely on it under Copilot.** Claude Code can
   add an OS sandbox (Seatbelt / bubblewrap) that *does* contain subprocesses. There is no
   evidence GitHub Copilot CLI honors it, so **under Copilot the container/worktree is your
   containment, not the sandbox.** Don't assume OS isolation you aren't actually running.
