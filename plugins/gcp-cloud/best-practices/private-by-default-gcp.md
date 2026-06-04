# Private by default; public by exception

Use Private Google Access so VMs need no external IP, Private Service Connect for private access to managed/partner services, Cloud NAT for controlled egress, and a default-deny firewall with allows targeted by tag or service account. No external IPs unless required and no admin ports open to the internet — public reachability should be a reviewed exception.
