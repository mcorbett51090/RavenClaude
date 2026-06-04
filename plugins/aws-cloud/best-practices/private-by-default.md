# Private by default; public by explicit exception

Place workloads in private subnets, reach AWS services via VPC endpoints/PrivateLink, and expose to the internet only through a deliberate load balancer in a public subnet. No public S3 buckets, no `0.0.0.0/0` to SSH/RDP/database ports. Public exposure should be a reviewed decision, never an accident of a default.
