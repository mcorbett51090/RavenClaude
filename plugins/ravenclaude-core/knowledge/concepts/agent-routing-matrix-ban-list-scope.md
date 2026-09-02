---
id: agent-routing-matrix-ban-list-scope
title: "An anti-duplication ban-list derived from 'every cited leaf string' bans the artifact's own citation discipline"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 916
summary: "Gate 255's vendor-fact ban-list is a scoped projection, not every leaf string in the cited files -- the wider version bans ordinary words and the source's own retrieval date."
last_verified: 2026-09-01
covers:
  - plugins/ravenclaude-core/scripts/check-agent-routing-matrix.py
  - plugins/ravenclaude-core/knowledge/agent-routing-matrix.json
  - plugins/ravenclaude-core/knowledge/agent-routing-matrix.schema.json
  - plugins/ravenclaude-core/knowledge/agent-routing-matrix.md
covers_digest: "sha256:7f2233627795be36ade413f660d231c26ca057b576b2fbb0f2516780985158ea"
nuance: "Deriving the ban-list from every leaf string in the cited files bans ordinary English words (the grok lane's own 'high'/'low'/'architect'/'scanner') and the source's own retrieval date -- contradicting the artifact's own citation requirement."
nuance_evidence:
  measured: 2026-09-01
  control: "the same derivation scoped to only substrate-tier-map.json's per-host-per-tier `model` leaves plus model-catalog.json's id lists produced a ban-list with zero English-word or date entries, while still catching the display-name SKU form (`Claude Opus 5`) a hand-written regex had missed"
  falsifier: "a future substrate-tier-map.json host whose tier row's `model` field itself contains a common English word or a bare date, which would re-admit a false positive under the scoped derivation too"
  probe: "plugins/ravenclaude-core/scripts/check-agent-routing-matrix.py"
nuance_source: "plugins/ravenclaude-core/scripts/check-agent-routing-matrix.py:219-229"
verify:
  tier: "effect"
  strength: "executed"
  class: "gate-self-test"
  probe: "plugins/ravenclaude-core/scripts/check-agent-routing-matrix.py --must-fail"
  teeth_exit: 3
sources:
  - label: this build's own G4a critic (correlated-error pass) and G5 red-team, PR #1067
    url: https://github.com/mcorbett51090/RavenClaude/pull/1067
---

## What a reader would have assumed instead

That the safest anti-duplication design is the broadest one: walk every leaf string in the files
the artifact cites (`substrate-tier-map.json`, `model-catalog.json`) and ban all of them from
appearing in the routing matrix or its doc. More strings banned reads as more protection.

## The discriminator

control: the same derivation scoped to only substrate-tier-map.json's per-host-per-tier `model`
leaves plus model-catalog.json's id lists produced a ban-list with zero English-word or date
entries, while still catching the display-name SKU form (`Claude Opus 5`) a hand-written regex had
missed

Measured 2026-09-01: banning *every* leaf string in the cited files means banning
`substrate-tier-map.json`'s own Grok-lane `effort`/`perspective` values (`high`, `low`,
`architect`, `scanner`, `critic`) — ordinary English words a routing-matrix document cannot avoid —
**and** that file's own `retrieved` date. The artifact's own staleness/citation discipline requires
stamping a cited fact with its retrieval date, so the "ban everything" derivation would forbid the
artifact from citing its own primary source's freshness. The shipped derivation is scoped to just
the `model` field of each tier-map row plus the catalog's id lists — a narrower set that still
contains the display-name form (`"Claude Opus 5"`) a naive regex-based ban-list missed in an earlier
design, without banning the words and dates a real `.md` cannot avoid using.

## Why it matters

Gate 255 check B's own positive control (an empty or under-scoped derivation must not pass green)
exists **because** this trap is easy to reintroduce: "derive from more of the cited file" reads as
strictly safer right up until the derivation swallows the file's own metadata. A future edit that
widens the derivation back toward "every leaf string" would silently make the check unpassable by
any honestly-dated `.md` — the exact self-disabling-detector shape this repo has recorded before,
just reached from the opposite direction (over-broad instead of under-broad).

Falsifier: a future `substrate-tier-map.json` host whose tier row's `model` field itself contains a
common English word or a bare date — which would re-admit a false positive under the scoped
derivation too, and would need the derivation narrowed further (e.g. to a value shape check) rather
than widened.
