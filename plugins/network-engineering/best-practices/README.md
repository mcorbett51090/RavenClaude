# Network-engineering best practices

Short, enforceable house rules the agents apply. Each file is one principle with the rationale and the anti-pattern it kills. The advisory hook (`hooks/flag-network-smells.sh`) mechanically flags a subset (any/any rules, telnet, no change window); the rest are judgment the agents carry.

| File | Principle |
|---|---|
| [design-before-config.md](design-before-config.md) | Name the topology + protocol + trade-off before any vendor CLI. |
| [protocol-before-vendor.md](protocol-before-vendor.md) | Name the protocol/method first; the Cisco/Arista/Juniper syntax second. |
| [no-change-without-rollback.md](no-change-without-rollback.md) | Every change ships a baseline, a window, and a tested rollback. |
| [troubleshoot-bottom-up.md](troubleshoot-bottom-up.md) | Isolate the fault bottom-up the OSI stack; confirm each layer with a command. |
| [segment-by-trust.md](segment-by-trust.md) | Segment by trust level; default-deny east-west from a real flow inventory. |
| [document-the-ip-plan.md](document-the-ip-plan.md) | A network without a documented, summarizable IP plan is not designed. |
| [volatile-claims-carry-retrieval-dates.md](volatile-claims-carry-retrieval-dates.md) | Vendor/platform specifics carry a retrieval date + re-verify rider. |
