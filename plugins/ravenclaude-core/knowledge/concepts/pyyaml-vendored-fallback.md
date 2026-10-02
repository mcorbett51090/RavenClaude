---
id: pyyaml-vendored-fallback
title: "No PyYAML, no commands: the vendored fallback"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 942
summary: "A stock macOS python3 has no PyYAML. Without it the tribunal failed closed on every Bash command, so the plugin now ships a pure-Python PyYAML that each yaml importer appends to sys.path."
last_verified: 2026-10-02
covers:
  - plugins/ravenclaude-core/scripts/vendor/README.md
  - plugins/ravenclaude-core/scripts/vendor/yaml/LICENSE
  - plugins/ravenclaude-core/scripts/vendor/yaml/__init__.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/composer.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/constructor.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/cyaml.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/dumper.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/emitter.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/error.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/events.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/loader.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/nodes.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/parser.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/reader.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/representer.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/resolver.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/scanner.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/serializer.py
  - plugins/ravenclaude-core/scripts/vendor/yaml/tokens.py
covers_digest: "sha256:4991259f5da458e262da66106f60bb457db563b11bef95c4abb45476434d2a1c"
nuance: 'Without PyYAML the tribunal cannot parse its posture or catalog and fails closed, denying even `ls` as "tampering with the Thing". The vendored copy is APPENDED to sys.path, so an installed PyYAML still wins.'
nuance_evidence:
  measured: 2026-10-02
  control: "the same plugin with scripts/vendor/ removed, run under the same PyYAML-less python3, denies `ls -la` again; with the vendor dir present it is allowed and curl|sh is still denied"
  falsifier: "a PyYAML-less python3 on which thing-orchestrator.sh denies a read-only command while scripts/vendor/yaml is present"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate292-yaml-vendor-fallback.sh"
nuance_source: "plugins/ravenclaude-core/scripts/vendor/README.md:1-30"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-decision"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate292-yaml-vendor-fallback.sh"
  teeth_exit: 1
sources:
  - label: reported on a fresh MacBook install (first command failed on hooks)
    url: https://github.com/mcorbett51090/RavenClaude/blob/main/plugins/ravenclaude-core/scripts/vendor/README.md
---

## What a reader would have assumed instead

That a guardrail hook missing an optional parser degrades gracefully. It does the opposite: the
tribunal treats "cannot read my own config" as a reason to deny, which is correct fail-closed
behaviour. So a missing module looks exactly like a security verdict.

## The discriminator

Run the same command under a `python3` with no site-packages (`python3 -S`), once with
`scripts/vendor/` present and once with it removed. Only the vendor dir changes, and only the
verdict on `ls -la` flips.

## Why it matters

The first command on a fresh Mac failed, and the deny reason pointed at tampering, not at a missing
module. A hand-written YAML-subset parser was rejected because the catalog is a block of security
regexes, and parsing them differently would silently weaken a gate. Auto-installing was rejected
too: Homebrew Python refuses `pip install` (PEP 668), and a hook that runs `pip` would be an
unapproved supply-chain change.
