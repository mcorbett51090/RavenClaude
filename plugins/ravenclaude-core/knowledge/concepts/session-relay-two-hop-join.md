---
id: session-relay-two-hop-join
title: "The peer session's SendMessage name is not derivable from its own session_id"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 917
summary: "resolve-worktree-session.sh's two-hop worktree->pid->name join exists because the obvious one-hop guess -- deriving the ListAgents ref from session_id -- is false."
last_verified: 2026-09-01
covers:
  - plugins/ravenclaude-core/scripts/resolve-worktree-session.sh
  - plugins/ravenclaude-core/skills/session-relay/SKILL.md
  - plugins/ravenclaude-core/knowledge/cross-session-messaging.md
covers_digest: "sha256:7015365f398eb00723c9f8c7d8355a9304eb5948c9929b9a06089e0d85fa5b42"
nuance: "ListAgents' bracketed [ref] does not derive from a session's session_id: this
  authoring session's own id (d20158bb-...) shares no substring with its displayed
  [2eb70b]. The real join is worktree -> worktree-guard's pid -> that pid's
  ~/.claude/sessions/<pid>.json 'name' field, which DOES match the ListAgents display."
nuance_evidence:
  measured: 2026-09-01
  control: "resolve-worktree-session.sh run from inside this session's own worktree resolved
    session_id d20158bb-d28e-497d-9eb5-87fcaff2c96e and peer_name matthewcorbett-bc; ListAgents
    called in the same turn showed this session as matthewcorbett-bc [2eb70b] -- the name
    matched exactly, the bracketed ref shares no substring with the session_id."
  falsifier: "a session whose ~/.claude/sessions/<pid>.json 'name' field disagreed with its own
    ListAgents-displayed name; none was found in the 13 peers enumerated this session"
  probe: "plugins/ravenclaude-core/scripts/resolve-worktree-session.sh"
nuance_source: "plugins/ravenclaude-core/knowledge/cross-session-messaging.md \"The correlation problem\""
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/resolve-worktree-session.sh"
  teeth_exit: 1
sources:
  - label: "session-relay build, 2026-09-01 -- live ListAgents/session-registry comparison in this authoring session"
    url: "plugins/ravenclaude-core/knowledge/cross-session-messaging.md"
---

## What a reader would have assumed instead

That a session's `ListAgents`-displayed name/ref is some transform of its own `session_id` —
a hex prefix, a hash, something derivable — so a script wanting to `SendMessage` a specific
peer could compute the address from an id it already has (e.g. from a registry keyed by
`session_id`, which is exactly what `worktree-guard.sh`'s own session files use).

## The discriminator

control: this authoring session's own `session_id` is `d20158bb-d28e-497d-9eb5-87fcaff2c96e`;
`ListAgents`, in the same turn, displayed this session as `matthewcorbett-bc [2eb70b]` — no
substring of the id appears in the ref, and the derivation hypothesis fails on direct
inspection, not by absence of testing.

What *does* match: `~/.claude/sessions/<pid>.json`'s own `name` field for that same pid read
back `"matthewcorbett-bc"` — the exact string `ListAgents` shows, with no `[ref]` suffix
needed (`SendMessage`'s own contract: a bare name matching exactly one live agent delivers).
So `resolve-worktree-session.sh` performs two hops instead of one: worktree path →
`sha256(realpath(toplevel))` → `worktree-guard.sh`'s registry → live `pid`/`branch` → that
pid's `~/.claude/sessions/<pid>.json` → `name`. Verified end-to-end against this real checkout,
not just the fixture self-test (8/8): a call from inside this worktree returned
`peer_name: "matthewcorbett-bc"`, matching the live `ListAgents` row exactly.

## Why it matters

Falsifier: a live session whose registry `name` field disagreed with its own `ListAgents`
display — none was found this session, but the entry stays falsifiable rather than assumed.

Probe: `plugins/ravenclaude-core/scripts/resolve-worktree-session.sh --self-test` (8/8).

A cross-session relay tool that guessed the peer's address from `session_id` (the field every
other RavenClaude registry — `worktree-guard.sh`, the run-artifact substrate, the hook-event
log — is keyed on) would silently address nobody: `SendMessage` would either error on an
unmatched name or, worse, land on a coincidentally-similar unrelated session. The two-hop join
is not an optimization over a simpler one-hop lookup; the one-hop lookup does not exist.
