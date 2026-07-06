# Protocol before vendor

**Rule:** Name the protocol/method first ("iBGP with route reflectors for scale", "OSPF totally-stubby area at the edge"); the Cisco/Arista/Juniper syntax second.

**Why:** principles are portable across vendors and across years; syntax is a footnote that changes per platform and per release. A reader who understands *why* iBGP needs route reflectors can implement it on any box.

**Anti-pattern:** leading with `router bgp 65001 / neighbor ...` before establishing that BGP (and route reflection) is the right call for the boundary and scale.
