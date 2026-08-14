# Unbounded star path

**Date:** 2026-08-14
**Tags:** cypher, path-cost, supernode
**Unverified** — teaching scenario, not a production incident.

A “show me everyone connected to this influencer” query shipped as an unbounded star expansion from a User node. The influencer was a supernode. The query did not return; the engine burned CPU on unbounded expansion.

**Fix:** type the edge and cap hops:

```cypher
MATCH (u:User {id:$id})-[:FOLLOWS*1..2]->(n:User) RETURN n
```

If the product is “everyone,” that is an algorithm / export job, not a traversal.

See [`../best-practices/bound-variable-length-paths.md`](../best-practices/bound-variable-length-paths.md).
