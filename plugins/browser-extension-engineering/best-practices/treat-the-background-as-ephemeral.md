# Treat the MV3 background as an ephemeral service worker

**Rule.** The background service worker can be killed at any idle moment. Keep no
load-bearing global state, register all listeners at the **top level**, persist to
`chrome.storage` and rehydrate per event, and use `chrome.alarms` (not
`setTimeout`) for long timers.

**Why.** The #1 MV3 migration bug: state in a global vanishes when the SW is
recycled, and listeners added in an async callback miss the events that should
wake the worker.

**Smell.** Background variables that "reset randomly"; `addListener` inside a
`.then()`/`await`.

**Cite:** plugin §4.2; lifecycle mechanics in
`knowledge/manifest-v3-architecture.md`.
