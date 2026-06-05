---
scenario_id: 2026-06-05-save-system-migration
contributed_at: 2026-06-05
plugin: game-development
product: generic-engine
product_version: "unknown"
scope: likely-general
tags: [save-system, serialization, schema-version, migration, backward-compat, live-service]
confidence: high
reviewed: false
---

## Problem

A live mobile RPG shipped a content update that added a field to the player-inventory structure. On release, a wave of players hit a hard crash on launch — specifically the engaged, paying players who had the *oldest* saves. The new build deserialized the save file directly into the updated data structure; an old save lacked the new field (or had an old layout), and the deserializer threw on the mismatch, corrupting or rejecting the file. There was no save-version number, so the loader couldn't even tell an old save from a new one.

## Context

- Engine-agnostic (the save-migration problem is identical whether the save is JSON, binary, a Unity `ScriptableObject` blob, a protobuf, or a SQLite row — any persisted structure that outlives the code that wrote it).
- Live service: there are **saves in the wild from every prior version**, and they belong disproportionately to the highest-value players (the ones who've played longest have the oldest, most-evolved saves).
- The save format had no `schema_version` field, so the new loader had no way to branch on "what wrote this?"
- The crash was on *load*, before any UI — so an affected player had no path to recover in-game.

## Attempts

- Tried: a hotfix that wrapped the deserialize in a try/catch and reset a failed save to defaults. Outcome: it stopped the crash but **wiped progress** for exactly the long-tenured paying players who hit it — trading a crash for a worse retention/refund event. Catching the error is not the same as migrating the data.
- Tried: adding the missing field with a default at load. Outcome: fixed *this one* field but was a point patch — the next schema change would reintroduce the same class of bug, because there was still no versioning to branch on.
- Tried (the fix): introduced an explicit **`save_version` integer** in the save envelope and a **migration chain** — small, ordered, idempotent functions `migrate_vN_to_vN+1` that run in sequence from the file's stored version up to the current version before the data is handed to the game. v0→v1 added the new inventory field with a sensible default; future steps append to the chain. Loading became: read version → run each migration step in order → deserialize the now-current structure. Outcome: old saves of every vintage loaded and upgraded cleanly; the crash class was structurally closed, not patched.

## Resolution

**A persisted save is a schema that outlives its code — version it and migrate it forward; never deserialize an old save straight into a new structure.** The pattern:

1. **Stamp every save with a `save_version`** from day one (even v1). Without it, the loader can't tell what wrote the file and can't choose how to read it. This is the single change that makes everything else possible — add it before you ever need it.
2. **Migrate, don't reset.** A failed load that resets to defaults destroys the progress of your most-engaged players — the worst possible cohort to punish. The right move is to *transform* the old data into the new shape.
3. **Use an ordered, idempotent migration chain** — one small `vN → vN+1` step per schema change, run in sequence from the file's version to current. Each step is independently testable; the chain composes across any version gap (a v3 client reads a v0 save by running 0→1→2→3).
4. **Test load against real old saves**, not just freshly-written ones — keep a corpus of saves from prior shipped versions in CI. The bug only ever appears on data the *current* build didn't write.

The trap: the dev build only ever loads saves the dev build wrote, so the migration gap is invisible until it hits live players — and it hits the oldest, highest-value saves first.

**Action for the next engineer:** before shipping any change to a persisted save structure on a live game, confirm there's a `save_version` and a migration step for the change, and that load is tested against a corpus of real saves from every shipped version. Reset-to-default is a last resort that costs you your best players, not a migration strategy. This is the game-save analogue of expand/contract schema migration; the live-service operating discipline is the team's §3 #7.
