# Design before config

**Rule:** Name the topology, the protocol, and the trade-off *before* any vendor CLI. The deliverable is the design and the reason for it, not a paste of `interface GigabitEthernet0/1`.

**Why:** config without a settled design is how networks accrete into something no one understands. The design — topology, addressing, redundancy, segmentation, enforcement — is the artifact that survives a vendor swap and a staff change.

**Anti-pattern:** answering "design our network" with a config snippet. Answer with the design + the rejected alternatives first; config intent comes after the design is agreed.
