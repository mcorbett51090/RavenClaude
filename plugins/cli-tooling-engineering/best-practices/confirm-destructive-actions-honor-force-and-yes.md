# Confirm destructive actions, honor --force and --yes

**Status:** Absolute rule
**Domain:** CLI safety
**Applies to:** `cli-tooling-engineering`

---

## Why this exists

A CLI runs with the user's full permissions and no undo. An irreversible operation — delete, overwrite, force-push, drop, prune — that proceeds silently is one fat-fingered command away from data loss. But a hard interactive prompt is equally wrong in automation, where there's no human to answer it and the script hangs forever. The resolution: **confirm by default, but provide an explicit non-interactive escape hatch.**

## How to apply

**Do:**
- Prompt for confirmation before an irreversible action **when attached to a TTY** (show exactly what will be affected).
- Honor a `--force` / `-f` or `--yes` / `-y` flag to skip the prompt for scripted use.
- When **not** a TTY and no `--yes` was given, **refuse with a clear error** (exit non-zero) rather than hang on a prompt or silently proceed.
- Offer a `--dry-run` for high-blast operations so users can preview.

**Don't:**
- Proceed with a destructive default just because stdin isn't interactive.
- Make `--yes` the implicit default — the safe path is the one a user gets when they pass nothing.

## Edge cases / when the rule does NOT apply

A tool whose *entire purpose* is the destructive action (e.g. `rm` itself) follows platform convention rather than prompting on every call — but even those gate the widest-blast variants (`rm -i`, "type the resource name to confirm"). Scope the confirmation to genuinely irreversible, wide-blast operations, not every write.

## See also

- [`./fail-fast-with-actionable-errors.md`](./fail-fast-with-actionable-errors.md)
- [`./respect-no-color-and-detect-the-tty.md`](./respect-no-color-and-detect-the-tty.md) — the same TTY-detection mechanic.

## Provenance

Codifies the destructive-action confirmation convention and CLAUDE.md §2; aligns with the marketplace's high-blast/irreversible-action posture.

---

_Last reviewed: 2026-06-22 by `claude`_
