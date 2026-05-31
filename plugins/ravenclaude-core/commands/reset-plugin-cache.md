---
description: Disaster-recovery reset of a broken plugin cache (Ragnarök). Dry-run by default; --execute performs an atomic, snapshotted, SHA-pinned reinstall with the original preserved. High blast radius — user-invoked only, with mandatory interactive confirmation. MEMORY.md always survives.
---

You are running **`/reset-plugin-cache`** (themed alias `/ragnarok`) — a **high-blast-radius disaster-recovery** command. In Ragnarök the old world burned and what survived rebuilt better; this command performs an analogous reset of a **genuinely broken** plugin cache. Use it only when a plugin's installed cache is corrupted and a normal `/reload-plugins` won't fix it — not as routine maintenance.

The engine is [`../scripts/reset-plugin-cache.py`](../scripts/reset-plugin-cache.py). Named errors: [`../scripts/_ragnarok-named-errors.json`](../scripts/_ragnarok-named-errors.json). Full design + the resolved security blockers: [`docs/ragnarok-reset-plugin-cache-tee-up.md`](../../../docs/ragnarok-reset-plugin-cache-tee-up.md).

## Safety model (read before running)

- **Dry-run is the default.** `/reset-plugin-cache <plugin>` enumerates what *would* be touched and moves nothing. **Always run the dry-run first and read it.**
- **Execute is opt-in and user-only.** `--execute` requires (a) a **pinned marketplace SHA** (`--pin <sha>` — no floating HEAD) and (b) **your interactive confirmation** (you type the plugin name to confirm). An agent cannot supply that confirmation, so an agent can never trigger an execute — it gets `RAGNAROK_NOT_USER_INVOKED`. **Never bypass the confirmation on a user's behalf.**
- **Atomic + reversible.** The reset snapshots the live cache, fetches a fresh tree pinned to your SHA, **verifies it with `audit-gates.sh` before touching the live cache** (a failed verification aborts with the original untouched), then does a two-rename atomic swap (rolling back if the second rename fails). The pre-reset original is retained for `--ttl-days` (default 30).
- **`MEMORY.md` always survives.** The memory directory lives outside the plugin cache and is never touched.

## How to run it

### 1. Always start with the dry-run

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reset-plugin-cache.py" <plugin>
```

Show the user the dry-run inventory (which cache dir, where the snapshot would go, what SHA it would pin to). **Stop here unless the user explicitly asks to execute.**

### 2. Confirm interactively, then execute

If — and only if — the user wants to proceed, use **AskUserQuestion** to require an explicit, typed confirmation. This is the user-only gate; do not skip it:

> *"This will reset the `<plugin>` plugin cache: snapshot the current one, fetch a fresh copy pinned to `<sha>`, verify it, and atomically swap it in (the original is kept for 30 days). To confirm, this is a high-blast-radius action — do you want to proceed?"*

Only after the user confirms, run with their pinned SHA. Pass the plugin name as the confirmation token (this is what proves a human confirmed — an agent invoking the script directly cannot supply it):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reset-plugin-cache.py" <plugin> \
  --execute --pin <sha> --confirm <plugin>
```

The command body first fetches the marketplace pinned to `<sha>` into a temp dir and passes it as `--fresh-tree`; without a verified fresh tree it refuses (`RAGNAROK_SHA_NOT_FOUND`). On success it prints the new cache location, the retained snapshot path, the swapped-out original, and the audit-record path under `.ravenclaude/runs/<session>/`.

## Named errors (what each means)

- `RAGNAROK_PLUGIN_NOT_INSTALLED` — no cache dir for that plugin; nothing to reset.
- `RAGNAROK_NOT_USER_INVOKED` — execute attempted without the interactive confirmation token (e.g. an agent). Refused.
- `RAGNAROK_SHA_NOT_FOUND` — `--pin` missing/malformed, or no verified fresh tree.
- `RAGNAROK_FRESH_TREE_GATES_FAILED` — the fresh tree failed `audit-gates.sh`; aborted, original untouched.
- `RAGNAROK_ATOMIC_SWAP_PARTIAL` — the swap failed partway; the first rename was rolled back. Inspect the snapshot before retrying.

## When NOT to use it

- The cache isn't actually broken → use `/reload-plugins` or `/plugin marketplace update`.
- You want to *install* a plugin → use the Bifröst install wizard (`/dashboard` → `#/bifrost`), not this.
- You're an agent acting autonomously → you **cannot** run execute; surface the dry-run to the user and let them decide.
