---
id: launch-guard-installer-is-fail-open
title: "The launch-guard installer is fail-open by construction"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 931
summary: "A rc-file installer for a safety mechanism must never itself be able to break the shell it protects — every write is backed up and syntax-validated before it commits."
last_verified: 2026-09-09
covers:
  - plugins/ravenclaude-core/scripts/install_launch_guard.py
covers_digest: "sha256:7583ee7a3bb89fc3696b8def7fb53f0b3d16d6c3540e0d64d7eb5ff9e32a8595"
nuance: "The installer writes into a user's real rc file, so a bug there is the worst failure mode for a safety tool. Every write is backed up first and syntax-validated before it commits."
nuance_evidence:
  measured: 2026-09-08
  control: "install into a scratch zsh $HOME -> exactly one marker block, bash -n/zsh -n clean; re-run install -> block replaced in place, non-marker regions byte-identical; --uninstall -> rc file byte-identical to pre-install; helper deleted after install -> claude --version still works end-to-end through the real sourced shell (fail-open, verified through the real integration point, not just the installer in isolation)"
  falsifier: "an install/re-install/uninstall cycle that leaves the rc file anything other than byte-identical outside the marker span, or a helper deletion that breaks a real shell's claude invocation"
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
`--uninstall` -> rc file byte-identical to pre-install state; the guard helper deleted after install
-> `claude --version` still works end-to-end through the real sourced shell.

Measured 2026-09-08: the installer is exactly as fail-open as the helper it installs. Every write is
preceded by a timestamped backup and followed by a syntax validation of the resulting file before the
edit is committed — a syntax failure restores the backup and the installer exits non-zero naming the
file and reason, rather than leaving a broken rc file behind.

## Why it matters

Falsifier: an install/re-install/uninstall cycle that leaves the rc file anything other than
byte-identical outside the marker span it manages, or a deleted helper breaking a real shell's
`claude` invocation instead of falling through to the real binary.

Probe: `plugins/ravenclaude-core/scripts/install_launch_guard.py`
