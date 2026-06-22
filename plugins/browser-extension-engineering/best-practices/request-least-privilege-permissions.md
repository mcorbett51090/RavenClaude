# Request least-privilege permissions

**Rule.** Request the narrowest permissions that work: prefer `activeTab` to broad
`<all_urls>`; narrow `host_permissions` match patterns over broad host access;
optional/runtime permissions over install-time. The default verdict on any
permission is "remove it" — keep it only if a concrete feature breaks without it.

**Why.** Every permission is a store-review risk and a user-trust cost; broad host
access triggers the scary "read all your data on all sites" warning and lengthens
review.

**Smell.** `<all_urls>` for a click-to-act extension; all permissions at install.

**Cite:** plugin §4.1; the permissions-minimization tree in
`knowledge/manifest-v3-architecture.md`.
