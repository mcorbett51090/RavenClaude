# Exit codes are a public API

**Status:** Absolute rule
**Domain:** CLI output contract
**Applies to:** `cli-tooling-engineering`

---

## Why this exists

Every script, CI pipeline, and shell `&&` chain that runs your tool decides what to do next by reading its **exit code** — not by parsing its output. If the tool exits `0` on a partial or total failure, everything downstream trusts it and keeps going: the CI job goes green on a broken build, the deploy proceeds on a failed check. The exit code is the most-consumed part of a CLI's interface, so it must be as stable and intentional as any API.

## How to apply

| Code | Meaning |
|---|---|
| `0` | Success — and *only* success |
| `1` | General/unexpected error |
| `2` | Usage error (bad args/flags) — the argparse/getopt convention |
| `3`+ | Distinct **domain** failure classes (document each) |
| `128 + N` | Killed by signal N (SIGINT → 130, SIGTERM → 143) |

**Do:**
- Return `0` only when the operation actually succeeded.
- Map each failure class to a distinct, documented non-zero code so scripts can branch.
- Print the error + a remediation hint to **stderr** before exiting.

**Don't:**
- Catch an error, print it, and fall through to exit `0`.
- Reuse `126`/`127` — the shell owns those ("not executable" / "not found").
- Use a boolean as an exit code (`exit(true)` exits non-zero in most languages — a silent surprise).

## Edge cases / when the rule does NOT apply

Some tools intentionally use exit codes as *data* (e.g. `grep` exits `1` for "no match", `diff` exits `1` for "differences found" — neither is an error). That's fine and idiomatic — but document it loudly, because it inverts the usual "non-zero = failure" reading.

## See also

- [`./data-to-stdout-diagnostics-to-stderr.md`](./data-to-stdout-diagnostics-to-stderr.md)
- [`../knowledge/cli-tooling-decision-trees.md`](../knowledge/cli-tooling-decision-trees.md) — the output/exit-code tree.

## Provenance

Codifies POSIX/shell exit-code conventions and CLAUDE.md §2.

---

_Last reviewed: 2026-06-22 by `claude`_
