---
id: dependency-update-sweep
title: "The host roster is read live from host-support.json, never hardcoded"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 920
summary: "dependency-sweep.py discovers drift via the repo's existing citation-marker convention, host-scoped; the host roster itself is derived from host-support.json, not a guessed list."
last_verified: 2026-09-03
covers:
  - plugins/ravenclaude-core/scripts/dependency-sweep.py
  - plugins/ravenclaude-core/scripts/host-version-probe.py
  - plugins/ravenclaude-core/skills/dependency-update-sweep/SKILL.md
  - plugins/ravenclaude-core/skills/dependency-update-sweep/tests/fixtures/changelog-delta.txt
  - plugins/ravenclaude-core/skills/dependency-update-sweep/tests/fixtures/fake-doc.md
  - plugins/ravenclaude-core/skills/dependency-update-sweep/tests/fixtures/generate-fake-hooks.py
  - plugins/ravenclaude-core/skills/dependency-update-sweep/tests/fixtures/host-support-slice.json
covers_digest: "sha256:4794d588249bad9fc7c86ee7eef3bd4d922f0286ecd4b1ccdb3b0017e320b0ca"
nuance: "The marker-scan's host-scoping bug undercounted findings by masking cross-host false positives: an unscoped scan of `copilot` returned 175 findings because it matched citations naming ANY tracked host, not just copilot; scoping `host_re` to a single host dropped that to 85 (and a `gemini` scan, previously flooded by copilot/codex/cursor citations, to 27)."
nuance_evidence:
  measured: 2026-09-03
  control: "the same scan re-run with host_re built from a single-host-scoped {\"hosts\": {host_id: host_cell}} slice, compared against the unscoped full-hosts-dict build on the identical repo state"
  falsifier: "a future host-support.json restructuring that removes the per-host component-cell nesting this scoping depends on"
  probe: "plugins/ravenclaude-core/scripts/dependency-sweep.py"
nuance_source: "plugins/ravenclaude-core/scripts/dependency-sweep.py"
verify:
  tier: "none"
  rationale: "The host-scoping fix is proven by the tool's own self-test suite (scan 12/12, classify 10/10, queue 5/5, apply 21/21), including a regression check for this exact bug; re-verifying the finding-count delta against the live repo means re-running the scan, not a separate staged check."
sources:
  - label: "/code-review found the pre-fix undercount and this session verified the fix's measured effect"
    url: https://github.com/mcorbett51090/RavenClaude/pull/1101
---

## What a reader would have assumed instead

That scanning "for copilot" and scanning "for any host" would return the same superset/subset relationship regardless of implementation — i.e. that a host-scoped scan is just a filtered view of the unscoped one, so the unscoped count would always be >= any single host's real count in a way proportional to the number of tracked hosts.

## The discriminator

control: the same scan re-run with host_re built from a single-host-scoped `{"hosts": {host_id: host_cell}}` slice, compared against the unscoped full-hosts-dict build on the identical repo state
Measured 2026-09-03: `scan_markers`'s `host_re` was built from every tracked host's citation tokens combined, so a citation naming ANY tracked host matched regardless of which host was actually being scanned. A `copilot` scan returned 175 findings pre-fix; scoping the regex to only `copilot`'s tokens dropped it to 85 — more than half were false attributions to the wrong host. A `gemini` scan, previously flooded by copilot/codex/cursor citations that happened to share surrounding text, dropped to 27.

## Why it matters

The sweep's queue output (`queue --host <id>`) is host-scoped by design — a maintainer sweeping `copilot` after a version bump should see only findings that actually concern copilot, not every host-version-sensitive citation in the repo. The unscoped bug would have made every host's queue nearly identical (dominated by cross-host noise) and buried the small number of findings that genuinely needed action behind ones that didn't. The fix reuses Gate 208's `host_tokens`/`host_regex` helpers but calls them with a single-host slice of `host-support.json`, never the full dict — the general-purpose helper answered a broader question than the per-host queue needed.

Falsifier: a future `host-support.json` restructuring that removes the per-host `components.<type>.<host_id>` nesting this scoping depends on.
