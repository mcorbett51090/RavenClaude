# Scope web_accessible_resources tightly

**Rule.** Expose only the specific files needed, and scope their `matches` to the
specific origins that need them — never `<all_urls>`/`*`.

**Why.** Anything listed is reachable by web pages, so every entry is an attack
surface; a `*` exposure leaks extension internals to every site.

**Smell.** `web_accessible_resources` with `matches: ["<all_urls>"]` or `["*"]`.

**Cite:** plugin §4.7; `knowledge/manifest-v3-architecture.md`.
