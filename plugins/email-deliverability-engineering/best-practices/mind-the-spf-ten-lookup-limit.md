# Mind the SPF 10-DNS-lookup limit (and never use +all)

**Rule.** SPF evaluation may not exceed 10 DNS lookups (counting `include`, `a`,
`mx`, `ptr`, `exists`, `redirect`, recursively). Over 10 → `permerror` → DMARC
fail. Audit the `include:` chain; flatten or prune. Publish exactly one SPF
record. Never paper over a problem with `+all`.

**Why.** Over-limit SPF and duplicate SPF records both `permerror` *silently*;
`+all` authenticates the entire internet.

**Smell.** A deep `include:` chain, two SPF TXT records, or `+all`/`?all`.

**Cite:** RFC 7208 §4.6.4 (lookup limit).
