# Connectivity Troubleshooting Runbook — <symptom>

## Scope
- **Affected:** <who/what> · **Not affected:** <who/what> · **Since:** <when> · **What changed:** <recent changes>

## Boundary
- Working point: <...> → break localized to: <segment>

## OSI walk (bottom-up — stop at first failing layer)
| Layer | Check | Command | Result |
|---|---|---|---|
| L1 | link/errors/duplex/SFP | `show interface` | |
| L2 | VLAN/ARP/MAC/STP/trunk | `show mac address-table` / `show arp` / `show spanning-tree` | |
| L3 | route/gateway/ACL/MTU | `ping` / `traceroute` / `show ip route` | |
| L4 | port/firewall/NAT | `nc -vz host port` / firewall session | |
| L7 | DNS/TLS/app/LB | `dig` / `curl -v` / LB pool status | |

## Conclusion
- **Fault:** <ranked most-likely> · **Confirmed with:** <command + output>
- **Fix:** <cause fix> · **Guardrail:** <prevent recurrence> · **Recorded:** <where>
