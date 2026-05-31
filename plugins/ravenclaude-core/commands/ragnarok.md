---
description: Themed alias for /reset-plugin-cache — the high-blast-radius plugin-cache disaster-recovery command (dry-run by default, user-only execute, atomic + snapshotted + SHA-pinned, MEMORY.md survives). See /reset-plugin-cache for the full flow.
---

# Ragnarök

`/ragnarok` is the **themed alias** for the primary command **[`/reset-plugin-cache`](./reset-plugin-cache.md)** — *in Ragnarök the old world burned and what survived rebuilt better.* It performs a disaster-recovery reset of a genuinely-broken plugin cache: dry-run by default, user-only `--execute` with mandatory interactive confirmation, a SHA-pinned reinstall verified by `audit-gates.sh` before an atomic two-rename swap, the original retained 30 days, and `MEMORY.md` always preserved.

**Use the primary name `/reset-plugin-cache`** — it carries the full safety flow, the named errors, and the dry-run-first discipline. This alias exists only so the themed name resolves; it adds no behavior. Run the same engine: [`../scripts/reset-plugin-cache.py`](../scripts/reset-plugin-cache.py).
