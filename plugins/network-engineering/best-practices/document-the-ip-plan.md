# Document the IP plan

**Rule:** Every design ships a documented, summarizable IP addressing plan with growth headroom — per-site/per-role blocks, reserved management and point-to-point ranges, and dual-stack consideration for IPv6.

**Why:** an undocumented or un-summarizable address space becomes a convergence tax (big routing tables) and an operational mystery. Summarizable allocation keeps tables small and routing stable.

**Anti-pattern:** ad-hoc /24s handed out with no plan, overlapping ranges across sites, and no headroom — guaranteeing a painful renumber later.
