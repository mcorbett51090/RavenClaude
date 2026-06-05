# Use transitive membership APIs for groups-within-groups — direct membership misses nested access

**Status:** Primary diagnostic
**Domain:** Microsoft Graph / directory workloads
**Applies to:** `microsoft-graph`

---

## Why this exists

`GET /groups/{id}/members` returns only the **direct** members of a group. When a group contains other groups (nested groups), a user who is a member of the nested group is a member of the parent group but does not appear in the direct members list. Applications that check authorization by calling `/members` and testing whether a user ID is in the result will silently deny access to users who are members via a nested group. Entra supports transitive membership via dedicated endpoints — using them is not optional when nested groups exist in the tenant.

## How to apply

| Intent | Wrong endpoint | Correct endpoint |
|---|---|---|
| Get all users (incl. nested) in a group | `GET /groups/{id}/members` | `GET /groups/{id}/transitiveMembers?$filter=... &$select=id,userPrincipalName` |
| Check if a user is a member (any level) | Check `/members` array | `POST /users/{userId}/checkMemberGroups` or `POST /users/{userId}/getMemberObjects` |
| List all groups a user belongs to (any level) | `GET /users/{id}/memberOf` | `GET /users/{id}/transitiveMemberOf` |

```http
# Check if user is a member of a group (transitive):
POST /v1.0/users/{userId}/checkMemberGroups
Content-Type: application/json

{
  "groupIds": ["{groupId}"]
}
# Returns array of group IDs the user IS a member of (transitive)
```

**Do:**
- Use `transitiveMemberOf` when populating group-based authorization claims — this is the correct input for any RBAC check.
- Page the transitive membership list — large groups with deep nesting can return thousands of members.
- Combine with `$filter=@odata.type eq '#microsoft.graph.user'` on `transitiveMembers` to exclude nested-group objects from the result.

**Don't:**
- Use `GET /groups/{id}/members` for access-control checks without confirming with the tenant admin that nested groups are never used — they almost always are.
- Call `transitiveMemberOf` on every request in a hot path — cache the result for the token lifetime or use claims-based group assignment in the Entra app registration for lighter-weight checks.
- Perform the transitive expansion yourself in code by recursively calling `/members` — this is rate-limit-intensive and misses platform caching.

## Edge cases / when the rule does NOT apply

For small, known-flat groups (e.g., a team of 5 direct members with no nested groups and a documented "no nested groups" policy), the direct members endpoint is acceptable. Document the policy.

## See also

- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns directory and group workloads
- [`./api-page-to-exhaustion.md`](./api-page-to-exhaustion.md) — transitive membership results are paged; never read only the first page

## Provenance

Codifies CLAUDE.md §3 #4 ("page everything; assume more than one page") and the `graph-workloads-engineer` domain knowledge on transitive membership; Microsoft Graph transitiveMemberOf and checkMemberGroups documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
