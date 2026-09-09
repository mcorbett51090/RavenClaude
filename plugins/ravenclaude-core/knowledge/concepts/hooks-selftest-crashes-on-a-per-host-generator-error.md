---
id: hooks-selftest-crashes-on-a-per-host-generator-error
title: "`rc hooks selftest` crashes the whole run on one host's generator error"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 932
summary: "A single host projector (e.g. generate-gemini-hooks.py) raising a hard error takes down the entire multi-host selftest, not just that host's row."
last_verified: 2026-09-08
covers:
  - plugins/ravenclaude-core/scripts/hooks-selftest.py
covers_digest: "sha256:8fb6a243abe0319347a963522d9373d9abe28b0506f3d90c0a45410aabdacd23"
nuance: "hooks-selftest.py's per-host loop calls each host's `check-sessionstart-matcher-regression.py` extractor via a bare subprocess.run(..., check=True) with no try/except — one host's generator raising CalledProcessError propagates as an uncaught traceback that aborts every OTHER host's row too, not just the failing host's."
nuance_evidence:
  measured: 2026-09-08
  control: "with the underlying generator fixed (a missing skip-map entry added), the identical `rc hooks selftest --json` invocation completes cleanly with a full per-host row set and Gate 266's Phase 8 assertions (A8.1-A8.7) all pass"
  falsifier: "a future hooks-selftest.py revision that wraps each host's extractor call and reports a per-host FAIL row instead of raising"
  probe: "plugins/ravenclaude-core/scripts/hooks-selftest.py"
verify:
  tier: "none"
  rationale: "The failure mode is a real, reproduced crash (a genuine forge/prompt-optimizer merge into origin/main triggered it live via a newly-added hooks.json entry with no Gemini skip-map coverage), but the fix that would close this nuance permanently — per-host exception isolation inside hooks-selftest.py itself — is a design change to a file this entry's author did not write and has not modified; staging a CI check for it here would assert a fix that was not made."
sources:
  - label: reproduced live during the forge/prompt-optimizer merge into origin/main, this session — traceback ending in generate-gemini-hooks.py's CalledProcessError, root-caused to a missing skip-map entry, fixed there
    url: https://github.com/mcorbett51090/RavenClaude/pull/1098
---

## What a reader would have assumed instead

That `rc hooks selftest`'s per-host design (one row per host, each independently marked PASS/FAIL/TIER) means a single host's evaluation failing would show up as one red row while every other host's row still renders — the same isolation the tool's own `--json` schema (`{host, declared_tier, achieved_tier, wired_set, runtime, verdict}` per row) implies.

## The discriminator

control: with the underlying generator fixed (a missing skip-map entry added), the identical `rc hooks selftest --json` invocation completes cleanly with a full per-host row set and Gate 266's Phase 8 assertions (A8.1-A8.7) all pass.

Measured 2026-09-08: merging `forge/prompt-optimizer`'s new `hooks.json` entry (a `UserPromptSubmit` registration with no corresponding Gemini skip-map or lane) into `origin/main` made `bash plugins/ravenclaude-core/bin/rc hooks selftest --json` crash outright with an uncaught `subprocess.CalledProcessError` from deep inside `_wired_set_check` -> `_extract_gemini` -> `_run_host_generator` -> `generate-gemini-hooks.py`. The traceback took down the WHOLE command, not just Gemini's row — `Gate 266: Phase 8 on-demand front door` failed all 8 of its A8.x assertions in the same run, because the tool never got far enough to emit its `--json` array at all.

## Why it matters

A cross-host self-test whose failure mode is "the entire tool crashes" rather than "one row reports FAIL" hides exactly the information an operator needs most: which host is broken and why. In this instance the underlying cause (a hook registered with no per-host skip-map entry) was itself a real, separate, already-documented failure mode in `generate-gemini-hooks.py` (see its own `_SKIP` dict and header comment) — but `hooks-selftest.py`'s lack of per-host exception isolation meant that one omission escalated from "Gemini's row would show a clear projector error" into "the whole selftest front door is down," which is a materially worse failure for anyone trying to diagnose it from the tool's own output alone.

Falsifier: a future `hooks-selftest.py` revision that wraps each host's extractor call and reports a per-host FAIL row instead of raising.
