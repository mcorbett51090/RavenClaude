# Message-pass across the content-script isolation boundary

**Rule.** Content scripts run in an isolated world and cannot share JS objects
with the page or the background. Communicate via `runtime`/`tabs` messaging (or
`connect` ports for streams), and `return true` from an async `sendMessage`
listener to keep the response channel open.

**Why.** Reaching for shared globals across the boundary silently fails; a
forgotten `return true` drops async responses.

**Smell.** Content script reading a `window`/background global instead of sending
a message.

**Cite:** plugin §4.3; messaging section of
`knowledge/manifest-v3-architecture.md`.
