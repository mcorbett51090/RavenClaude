---
id: ledger-global-flags-precede-subcommand
title: "--actor and --repo-root go before the verb, not after"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 933
summary: "rc ledger's --repo-root/--actor are top-level argparse flags; placing them after the subcommand fails outright with 'unrecognized arguments' — verified live while building source-control-coordinator."
last_verified: 2026-09-09
covers:
  - plugins/ravenclaude-core/agents/source-control-coordinator.md
  - plugins/ravenclaude-core/commands/coordinate.md
  - plugins/ravenclaude-core/knowledge/coordinator-ledger-convention.md
  - plugins/ravenclaude-core/scripts/ledger.py
covers_digest: "sha256:4d1b160d5263ed4c21cbb9d391bb057b00346554beebacbcdc2ea6ce9b12d472"
nuance: "--repo-root/--actor are ledger.py's TOP-LEVEL parser flags, added before add_subparsers(); a build plan citing them AFTER `append` fails with 'unrecognized arguments', verified live. A companion claim (fresh ledger = exit 2/UNKNOWN) was also wrong: cmd_init always appends a ledger_init event, so the true fresh state is exit 0/PASS."
nuance_evidence:
  measured: 2026-09-09
  control: "rc ledger --repo-root <dir> append --type state --item <id> --set state=in_progress --actor coordinator -> 'ledger.py: error: unrecognized arguments: --actor coordinator'; the same call with --actor moved between --repo-root and append succeeds (exit 0, machine.actor lands correctly in the written event)"
  falsifier: "a ledger.py release that adds --actor to the append subparser directly, making both orders valid"
  probe: "plugins/ravenclaude-core/scripts/ledger.py"
nuance_source: "plugins/ravenclaude-core/scripts/ledger.py:1896-1922 (parser.add_argument('--repo-root', ...) / parser.add_argument('--actor', ...) both precede sub = parser.add_subparsers(); p_append never re-adds --actor)"
verify:
  tier: "reachability"
  strength: "static"
  class: "static-resolution"
  probe: "plugins/ravenclaude-core/scripts/ledger.py"
  teeth_exit: 2
sources:
  - label: "source-control-coordinator build (PR #1146), live CLI verification against a scratch ledger, 2026-09-09"
    url: https://github.com/mcorbett51090/RavenClaude/pull/1146
---

# --actor and --repo-root go before the verb, not after

`rc ledger`'s exact CLI surface was documented and cited many times before this build (Citation #5 in
the build plan, this repo's own `agents/architect.md`-shaped precedent authoring), but no prior citation
had actually driven the CLI end-to-end with `--actor` present. The build plan's own §4.4 ledger usage
table — the exact invocations `source-control-coordinator.md` and `coordinate.md` both cite for claiming
and releasing a handoff item — placed `--actor coordinator` *after* `append`, on every single row.

## Why it silently looked right

`--repo-root`/`--actor` are genuinely real, documented flags on `ledger.py`'s parser. Nothing about the
flag names, their defaults, or their presence in `--help` output signals that position matters. The
failure only surfaces the moment the exact invocation is run:

```
$ rc ledger --repo-root <dir> append --type state --item <id> --set state=in_progress --actor coordinator
ledger.py: error: unrecognized arguments: --actor coordinator
```

argparse's subparser model treats each subcommand (`init`, `open`, `append`, `project`, ...) as its own
independent parser. A flag added to the *parent* parser before `add_subparsers()` is only visible
*before* the subcommand token on the command line — a subparser has to explicitly re-declare a flag to
also accept it after its own name, and `append`'s subparser (`p_append`) never does.

## The fix, and why it generalizes

Move both global flags between `--repo-root` and the subcommand:

```
rc ledger --repo-root <primary> --actor coordinator append --type state --item <id> --set state=in_progress
```

Verified live: this form succeeds (exit 0), and `machine.actor` in the written JSONL event correctly
carries `"coordinator"`. Every citation in `coordinator-ledger-convention.md` and both new agent/command
files now places `--actor` in this position — this concept exists so the *next* mechanism that shells
out to `rc ledger` (or documents doing so) doesn't silently re-introduce the same defect, since nothing
about reading the flag's own `--help` text reveals the ordering constraint.

## The companion exit-code correction

The same build plan claimed a freshly-initialized ledger returns exit 2 (UNKNOWN) "by design." Verified
live: `rc ledger init` always appends a `ledger_init` event as part of initialization (`cmd_init`,
`ledger.py`), so a fresh ledger has `parsed_records: 1`, not 0 — `cmd_project`'s exit-2 branch fires only
on `parsed_records == 0`, which `rc ledger init` never produces. The true fresh-ledger state is exit 0
(PASS, 0 open items). A *literal* zero-event ledger (no init marker at all — e.g. a hand-created empty
`.jsonl`) is the actual exit-2 case, and it is not a state `rc ledger init` ever leaves behind.
