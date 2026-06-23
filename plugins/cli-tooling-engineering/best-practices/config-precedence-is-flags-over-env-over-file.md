# Config precedence is flags > env > file > default

**Status:** Absolute rule
**Domain:** CLI configuration
**Applies to:** `cli-tooling-engineering`

---

## Why this exists

When a tool reads settings from several places — a flag, an environment variable, a project config file, a user config file, a built-in default — the order they override each other must be **predictable and documented**, or users can't reason about why the tool did what it did. The universal, least-surprising order is **most-explicit-wins**: a flag the user typed right now beats an env var beats a project file beats a user file beats the default.

## How to apply

Resolve every source into **one config object** early in startup, then pass it down. The order, highest wins:

1. Command-line **flag** (`--timeout 30`)
2. **Environment variable** (`TOOL_TIMEOUT=30`)
3. **Project config file** (`./tool.toml`)
4. **User config file** (`$XDG_CONFIG_HOME/tool/config.toml`)
5. Built-in **default**

**Do:**
- Build the merged config once; cover the precedence with a test (it's the rule most likely to silently regress).
- Discover user config via XDG (`$XDG_CONFIG_HOME` → `~/.config`); document the search path in `--help`.

**Don't:**
- Let a config file silently override an explicit flag — that's the bug users will never figure out.
- Read config lazily from scattered call sites; precedence becomes undefined.

## Edge cases / when the rule does NOT apply

Secrets are a partial exception: prefer env/secret-store over a flag (flags leak into shell history and `ps`), so a tool may *forbid* a `--password` flag and accept only `TOOL_PASSWORD` or a secret file. That's a security override of the convenience ordering, stated explicitly — not a violation of it.

## See also

- [`./design-the-command-surface-first.md`](./design-the-command-surface-first.md)
- [`../knowledge/cli-tooling-decision-trees.md`](../knowledge/cli-tooling-decision-trees.md) — the config-precedence prior.

## Provenance

Codifies the cross-tool config-precedence convention (12-factor config, XDG Base Directory) and CLAUDE.md §2.

---

_Last reviewed: 2026-06-22 by `claude`_
