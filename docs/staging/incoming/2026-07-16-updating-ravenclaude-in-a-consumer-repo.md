<!-- RAVENCLAUDE-STAGING-METADATA
type: best-practice
topic: other
proposed-by: consumer engagement — BTCSIReporting Codespace (Copilot CLI), updating ravenclaude-core skills/hooks in a project repo
proposed-on: 2026-07-16
target-file: docs/best-practices/updating-ravenclaude-in-a-consumer-repo.md
status: pending
-->

# Updating RavenClaude in a consumer repo (Copilot-CLI install): `git pull` + re-materialize symlinks, never a reinstall

**Status:**
- **Pattern** — strong default; deviate only with a written reason.

**Domain:** Agent operability / plugin distribution (cross-domain).

**Applies to:** Any consumer project that consumes `ravenclaude-core` via the `scripts/ravenclaude` Copilot-CLI installer (`.claude/skills/` symlinks + `.github/hooks/ravenclaude.json` adapter), rather than via Claude Code's native `/plugin` marketplace mechanism.

---

## Why this exists

On the Copilot-CLI distribution path there is **no plugin cache to bust and no reinstall to run**. `.claude/skills/` is a set of symlinks into a local marketplace clone that Copilot reads live from disk on every session start, so an update is just `git pull` on the clone plus re-materializing the symlinks. Sessions waste time when someone treats it like Claude Code's cached-plugin model (looking for a cache to clear) or, worse, "fixes" a PATH problem by symlinking the launcher into `/usr/local/bin` — which silently breaks the script's self-location. This doc records the two-step update and the three setup failure modes that recur across Codespace rebuilds.

## How to apply

**The update is two idempotent steps + a reload:**

```bash
# 1. Pull latest marketplace + regenerate the Copilot package (touches no project repo)
bash /home/codespace/RavenClaude/scripts/ravenclaude update

# 2. Re-wire skills + hooks into THIS project (idempotent: adds/removes symlinks to match upstream)
cd /workspaces/<repo>
bash /home/codespace/RavenClaude/scripts/ravenclaude install --project .

# 3. In the active Copilot session
/skills reload      # or relaunch — Copilot caches the skills list at session start
```

Then commit the re-wire: `git add -A && git commit -m "chore(ravenclaude): update skills + hooks to latest"`. Review `git diff --stat HEAD` first — expect updated `.claude/skills/*` symlinks, new `create mode 120000` entries for added skills, and a regenerated `.github/hooks/ravenclaude.json`.

The `rc` alias (added to `~/.bashrc` by `ravenclaude setup`) combines update + launch: `rc` pulls, regenerates, and starts Copilot in one command — but the per-project `install` step is still separate when you want the repo's committed symlinks refreshed.

**Do:**
- Fix a missing `ravenclaude` command by adding the real scripts dir to `$PATH` in `~/.bashrc` (`export PATH="$HOME/RavenClaude/scripts:$PATH"` — idempotent; `ravenclaude setup` adds it), or invoke by full path.
- On a fresh Codespace where skills are missing, run `ravenclaude status --project /workspaces/<repo>` first — it reports skill count, hook presence, and `package:` state.
- If `ravenclaude status` shows `package: MISSING`, run `ravenclaude update` to regenerate `plugins/ravenclaude-core/copilot/` (normal after a `postCreateCommand` timeout on a fresh build).
- Check the committed `plugins` symlink target with `readlink /workspaces/<repo>/plugins` — the correct target is `/home/codespace/RavenClaude/plugins`.

**Don't:**
- **Don't** `sudo ln -s .../scripts/ravenclaude /usr/local/bin/ravenclaude`. The script locates the marketplace via `MARKET="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`; invoked through a `/usr/local/bin` symlink, `MARKET` resolves to `/usr/local`, breaking update/regeneration/dashboard with errors like `dashboard-launcher template missing (/usr/local/plugins/ravenclaude-core/...)`. Fix PATH instead.
- **Don't** hunt for a plugin cache to clear — there isn't one on this path; the symlinks are live from disk.

## Edge cases / when the rule does NOT apply

- **Claude Code host, not Copilot CLI.** Under Claude Code the distribution path is the native marketplace (`/plugin marketplace update ravenclaude` + `/reload-plugins`), which *does* have a cache. This doc is the Copilot-CLI symlink path only.
- **Broken `plugins` symlink after a rebuild.** The committed symlink rots when the checkout user differs: the RavenClaude repo's own devcontainer uses `remoteUser: vscode` (embeds `/home/vscode/...`), while consumer Codespaces default to the `codespace` user (`/home/codespace/...`). If wrong: `rm plugins && ln -sf /home/codespace/RavenClaude/plugins plugins && git add plugins && git commit`.
- **PATH not active in a shell opened immediately after container start** — `~/.bashrc` may not have re-sourced; `source ~/.bashrc` or use the full script path for that session.
- **`git pull` merge conflict on the clone** — the marketplace clone has local commits not yet on `origin/main`; push or resolve those first.

## See also

- [`plugins/ravenclaude-core/skills/update-ravenclaude/SKILL.md`](../../../plugins/ravenclaude-core/skills/update-ravenclaude/SKILL.md) — the update skill.
- [`plugins/ravenclaude-core/knowledge/copilot-cli-customization.md`](../../../plugins/ravenclaude-core/knowledge/copilot-cli-customization.md) — how the Copilot adapter surfaces skills/hooks.
- [`surface-credential-location-in-environment-context`](2026-06-09-surface-credential-location-in-environment-context.md) — companion Copilot-CLI session-start orientation pattern.

## Provenance

Consumer Codespace engagement (BTCSIReporting, Copilot CLI), 2026-07-16: an update session documented the two-step `ravenclaude update` + `install` flow and diagnosed the recurring initial-setup failures — `package: MISSING`, the rotted `plugins` symlink (vscode-vs-codespace user path), inactive PATH, and the `/usr/local/bin` self-location trap. Consumer paths generalized; repo-specific identifiers removed.

---

_Last reviewed: 2026-07-16 by consumer-engagement contribution (Copilot-CLI update flow)_
