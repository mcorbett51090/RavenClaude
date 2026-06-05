# Use Aurora Serverless v2 for spiky relational workloads

**Status:** Pattern
**Domain:** AWS compute / databases
**Applies to:** `aws-cloud`

---

## Why this exists

Teams reach for RDS Multi-AZ by default regardless of traffic shape and end up paying for provisioned capacity 24/7 for workloads that only need the database for minutes at a time. Aurora Serverless v2 scales capacity in fine-grained increments (0.5 ACU steps) in seconds — matching burst without a standing fleet. Conversely, teams who deploy Aurora Serverless v2 for high-throughput OLTP misread the cost model and pay more than a provisioned cluster would cost. The right choice is driven by traffic shape.

## How to apply

Evaluate Aurora Serverless v2 when:

- Traffic is spiky, intermittent, or unpredictable (dev/test, SaaS tenant-per-DB, batch jobs).
- You want automatic scaling without managing instance classes.
- Cost control matters and idle periods are significant.

```hcl
# Terraform — Aurora Serverless v2 cluster
resource "aws_rds_cluster" "this" {
  cluster_identifier      = "app-${var.env}"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"          # Serverless v2 uses "provisioned" engine_mode
  engine_version          = "15.4"
  database_name           = var.db_name
  master_username         = var.db_user
  manage_master_user_password = true               # Secrets Manager-managed password
  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 16
  }
  storage_encrypted       = true
  deletion_protection     = true
  skip_final_snapshot     = false
}

resource "aws_rds_cluster_instance" "writer" {
  cluster_identifier = aws_rds_cluster.this.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.this.engine
  engine_version     = aws_rds_cluster.this.engine_version
}
```

**Do:**
- Set `min_capacity = 0.5` only for truly intermittent workloads; set a floor that matches your baseline if latency on cold ACU acquisition matters.
- Pin an Aurora version and test before upgrading (minor versions can change planner behavior).
- Use `manage_master_user_password = true` — never hardcode the password.
- Add a reader instance for read-heavy workloads; a single writer can't distribute reads.

**Don't:**
- Use Serverless v2 for sustained high-throughput OLTP (provisioned is cheaper per ACU-hour).
- Confuse Serverless v2 with Serverless v1 — v1 had a cold-start pause; v2 does not.
- Skip `deletion_protection` and `skip_final_snapshot = false` on prod clusters.
- Assume Serverless v2 can scale to zero — `min_capacity = 0.5` is the true floor; it never idles to zero like Lambda.

## Edge cases / when the rule does NOT apply

- **High-frequency, sustained OLTP** (e.g., 1000+ concurrent connections at steady state): a provisioned Aurora cluster with a fixed instance class is cheaper.
- **PostgreSQL-specific extensions not yet GA on Aurora** — verify extension compatibility before committing.
- **Regulatory requirements mandating deterministic compute capacity** — Serverless auto-scaling may not satisfy every compliance posture.

## See also

- [`../agents/aws-compute-platform-engineer.md`](../agents/aws-compute-platform-engineer.md) — owns the database selection decision at a service level.
- [`./encrypt-at-rest-and-in-transit.md`](./encrypt-at-rest-and-in-transit.md) — storage encryption applies to Aurora clusters.

## Provenance

Derives from the AWS compute decision tree in `knowledge/aws-cloud-decision-trees.md` (Aurora Serverless v2 leaf for spiky relational workloads) and the AWS Aurora documentation. Standard Aurora Serverless v2 guidance from AWS re:Invent 2023 and the Aurora user guide.

---

_Last reviewed: 2026-06-05 by `claude`_
