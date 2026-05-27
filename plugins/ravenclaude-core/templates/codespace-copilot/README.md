# Codespace auto-setup for GitHub Copilot CLI

Drop these two files into a repo's `.devcontainer/` and **opening that repo's
Codespace sets everything up automatically** — no commands to type. When the
Codespace builds, `ravenclaude-post-create.sh` runs and:

1. installs GitHub Copilot CLI if it's missing (needs Node 22+),
2. clones the RavenClaude marketplace once (to `~/RavenClaude`),
3. wires this repo for Copilot (skills + enforcement hooks + MCP),
4. seeds and applies a **balanced** comfort-posture,
5. adds an `rc` alias.

Then, in a new terminal, you just type **`rc`** to launch Copilot with RavenClaude.

## Files

| File | Purpose |
| --- | --- |
| `devcontainer.json` | Codespace definition; its `postCreateCommand` runs the script below. |
| `ravenclaude-post-create.sh` | The auto-setup itself. Idempotent — safe on every rebuild. |

## Three ways to use it

1. **One command (from a marketplace clone):**
   ```shell
   bash ~/RavenClaude/scripts/ravenclaude init-codespace --project /path/to/your/repo
   ```
   This copies both files into the repo's `.devcontainer/`. Commit them, then
   (re)build the Codespace.

2. **By hand:** copy `devcontainer.json` and `ravenclaude-post-create.sh` into
   your repo's `.devcontainer/`, commit, and (re)build the Codespace.

3. **A GitHub template repo (truly one-button):** put these files in a repo and
   mark it a **template** (Settings → Template repository). Every new repo you
   create "from template" inherits the `.devcontainer/`, so it self-configures
   the first time its Codespace opens.

## Notes & overrides

- **Private marketplace:** the clone uses your Codespace's `gh` auth. If the
  clone fails, run `gh auth login` and rebuild.
- **Forked the marketplace?** Set `RAVENCLAUDE_REPO` (e.g. `youruser/RavenClaude`)
  and/or `RAVENCLAUDE_DIR` in `devcontainer.json` `containerEnv` or your Codespace
  secrets — the script reads both.
- **Already have a `devcontainer.json`?** `init-codespace` won't overwrite it;
  merge the `postCreateCommand` line in by hand instead.
- The script does **not** create a marketplace clone inside your repo — it clones
  to `~/RavenClaude` and points Copilot at it live, so updates are just
  `ravenclaude update` (which `rc` runs for you before each launch).
