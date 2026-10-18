---
id: project-settings-env-reaches-hooks
title: "A repo's settings env reaches every hook; the launch line and the guard close it"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 945
summary: "Project settings env (PATH, BASH_ENV, THING_SEAT_*) reaches hooks; a hardened launch line plus a quarantine guard stop it."
last_verified: 2026-10-18
covers:
  - plugins/ravenclaude-core/hooks/env-integrity-guard.sh
  - plugins/ravenclaude-core/hooks/_rc-runtime.sh
  - plugins/ravenclaude-core/hooks/pretool-record-check.sh
  - scripts/check-hook-launch-line.py
covers_digest: "sha256:0f2a9495d5aedd74a1ddb9dd5183ab4220e60b1ace16b74f16090b183dd84f02"
nuance: "Claude Code 2.1.260 exports project settings env into every hook (sh -c): a planted BASH_ENV ran in every bash hook, a planted PATH chose jq. The hardened launch line keeps them out; env-integrity-guard.sh denies every tool call. A real LD_PRELOAD library cannot be stopped, only refused."
nuance_evidence:
  measured: 2026-10-18
  control: "test-hook-env-hardening.sh: the pre-hardening 'bash \"${CLAUDE_PLUGIN_ROOT}/…\"' form DOES source a planted BASH_ENV; the hardened commands do not, and the guard denies"
  falsifier: "a hooks.json command without the /usr/bin/env -u … /bin/bash --noprofile --norc prefix, or a planted PATH/BASH_ENV/THING_SEAT_* key that does not deny"
  probe: "plugins/ravenclaude-core/hooks/tests/test-hook-env-hardening.sh"
nuance_source: "plugins/ravenclaude-core/hooks/env-integrity-guard.sh; scripts/check-hook-launch-line.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-hook-env-hardening.sh"
  teeth_exit: 1
sources:
  - label: "Claude Code docs: What runs before you trust a folder (env block and settings hooks are used)"
    url: https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder
  - label: "Claude Code docs: hooks reference (shell form runs sh -c; a hook inherits the parent environment)"
    url: https://code.claude.com/docs/en/hooks
---

## What a reader would have assumed instead

That a hook runs with the user's own environment, so a cloned repository can only add
hooks the user sees in `/hooks`, not change how RavenClaude's own hooks run.

## The discriminator

control: `bash plugins/ravenclaude-core/hooks/tests/test-hook-env-hardening.sh`. The old
command form sources a planted `BASH_ENV` (marker written). Under the hardened launch line
no marker is written, a fake `jq`/`bash` on a planted `PATH` is never used, and
`env-integrity-guard.sh` denies the call with `project settings plant execution-control env
(<keys>); this repo is quarantined`.

## Why it matters

The `env` block is not a hook, so neither the trust dialog nor `/hooks` shows it, and a
`claude -p` run applies it in a folder that was never trusted. Without the launch line a
planted `THING_SEAT_ACTIVE` would also have switched command review off. The seat-child
lock (`_rc-runtime.sh`) and the pre-tool record check (`pretool-record-check.sh`) cover the
recursion guard and a review hook that never started.

Falsifier: a hooks.json command without the hardened prefix, or a planted key that does not
deny. Probe: `plugins/ravenclaude-core/hooks/tests/test-hook-env-hardening.sh`.
