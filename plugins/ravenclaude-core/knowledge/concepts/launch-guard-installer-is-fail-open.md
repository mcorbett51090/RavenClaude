---
id: launch-guard-installer-is-fail-open
title: "The launch-guard installer is fail-open by construction"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 931
summary: "A rc-file installer for a safety mechanism must never itself be able to break the shell it protects — every write is backed up and syntax-validated before it commits."
last_verified: 2026-10-19
covers:
  - plugins/ravenclaude-core/scripts/install_launch_guard.py
covers_digest: "sha256:8a625b4bb2707f0b59ad6773c66dbd857554daa34910c15dfe863134329ac023"
nuance: "The installer writes into a user's real rc file, so a bug there is the worst failure mode for a safety tool. Every write is backed up first and syntax-validated before it commits."
nuance_evidence:
  measured: 2026-10-19
  control: "install into a scratch zsh $HOME -> exactly one marker block, bash -n/zsh -n clean; re-run install -> block replaced in place, non-marker regions byte-identical; --uninstall with no later edit -> rc file byte-identical to pre-install; --uninstall after a later rc edit -> only the marker block removed, the edit kept, a backup taken; --help or an unknown argument -> no rc file touched; helper deleted after install -> claude --version still works end-to-end through the real sourced shell"
  falsifier: "an install/re-install/uninstall cycle that changes anything outside the marker span (including an edit made after install), an unknown argument that edits an rc file, or a helper deletion that breaks a real shell's claude invocation"
  probe: "plugins/ravenclaude-core/scripts/install_launch_guard.py"
nuance_source: "plugins/ravenclaude-core/scripts/install_launch_guard.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/install_launch_guard.py"
  teeth_exit: 1
sources:
  - label: measured during the claude-launch-safeguard FORGE build (anthropics/claude-code#92932)
    url: https://github.com/anthropics/claude-code/issues/92932
---

## What a reader would have assumed instead

That an rc-file installer's own correctness is secondary to the safety mechanism it installs — that
a bug in the installer is a lesser concern than a bug in the guard itself.

## The discriminator

control: install into a scratch zsh `$HOME` -> exactly one marker block, `bash -n`/`zsh -n` clean;
re-run install -> block replaced in place (not duplicated), non-marker regions byte-identical;
`--uninstall` with no later edit -> rc file byte-identical to pre-install state (after a later edit:
only the block removed, the edit kept); the guard helper deleted after install
-> `claude --version` still works end-to-end through the real sourced shell.

Measured 2026-09-08: the installer is exactly as fail-open as the helper it installs. Every write is
preceded by a timestamped backup and followed by a syntax validation of the resulting file before the
edit is committed — a syntax failure restores the backup and the installer exits non-zero naming the
file and reason, rather than leaving a broken rc file behind.

**Corrected 2026-10-19 (repo review corescripts-5, orch-2).** Two gaps in that claim. First,
`--uninstall` copied the pre-install snapshot back unconditionally, so any rc edit made after install
was silently lost. The snapshot is now restored only when the file is exactly what install produced
(`_unchanged_since_install`); otherwise the current file is backed up and only the marker block is
removed. Second, an unknown argument, including `--help`, fell through to the default action, install,
and edited the rc file. `--help` now prints usage and exits 0; an unknown argument exits 2. Both are
in `install_launch_guard.py --self-test` (cases 13 and 14).

## Why it matters

Falsifier: an install/re-install/uninstall cycle that leaves the rc file anything other than
byte-identical outside the marker span it manages, or a deleted helper breaking a real shell's
`claude` invocation instead of falling through to the real binary.

Probe: `plugins/ravenclaude-core/scripts/install_launch_guard.py`
