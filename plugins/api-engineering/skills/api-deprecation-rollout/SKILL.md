---
name: api-deprecation-rollout
description: "Step-by-step playbook for deprecating and sunsetting an API version — header strategy, consumer communication timeline, traffic monitoring gates, and the SDKs/portal update checklist."
---

# API Deprecation Rollout

## When to Use This Skill

When a breaking change requires retiring an existing API version (major bump), or when removing an individual operation/field that consumers depend on.

## 1. Deprecation vs. Sunset

| Term | Meaning | Header |
|---|---|---|
| **Deprecated** | Still works; consumers should migrate | `Deprecation: <date>` |
| **Sunset** | Will stop working on this date | `Sunset: <date>` |
| **Retired** | Endpoint returns `410 Gone` | No header needed |

Both headers use RFC 7231 HTTP-date format: `Deprecation: Sat, 01 Feb 2025 00:00:00 GMT`.

## 2. Rollout Timeline Template

| Phase | Duration | Action |
|---|---|---|
| **Announce** | Day 0 | Publish deprecation notice; add headers to all responses on old version; update developer portal; email registered consumers |
| **Migration window** | 90 days min (180 for high-traffic APIs) | Monitor old-version traffic; publish migration guide; offer upgrade office hours |
| **Sunset warning** | 30 days before retirement | Increase warning cadence; add `Link: <sunset-date>; rel="sunset"` header; block new app registrations on old version |
| **Sunset** | Day N | Return `410 Gone` with a Problem Details body pointing to the new version |
| **Remove** | 30 days after sunset | Remove code, teardown infra, archive spec |

## 3. Required Headers on Every Response (deprecated endpoint)

```
Deprecation: Sat, 01 Feb 2025 00:00:00 GMT
Sunset: Fri, 01 Aug 2025 00:00:00 GMT
Link: <https://api.example.com/v2/orders>; rel="successor-version",
      <https://developer.example.com/migration/v1-to-v2>; rel="deprecation"
```

## 4. OpenAPI Annotation

```yaml
/v1/orders:
  get:
    operationId: listOrdersV1
    deprecated: true
    description: |
      **DEPRECATED** as of 2025-02-01. Sunset: 2025-08-01.
      Migrate to `/v2/orders`. See https://developer.example.com/migration/v1-to-v2.
```

## 5. Traffic Monitoring Gates

Before retiring, confirm all traffic gates are met:

- [ ] Old-version daily active callers < 1% of peak
- [ ] Zero callers in the last 7 days from production app registrations (not test/sandbox)
- [ ] All known SDK versions that target old version have an updated release published
- [ ] Support ticket rate on old-version migration < 2 open tickets

If any gate is red, extend the migration window — do not force a sunset.

## 6. Consumer Communication Checklist

- [ ] Developer portal "Breaking changes" page updated
- [ ] In-app SDK deprecation warning added (console.warn / log.warn on old-version call)
- [ ] Email to registered app owners with: what changes, migration steps, timeline
- [ ] Changelog entry in the API changelog
- [ ] Status page / changelog RSS updated

## 7. The 410 Gone Response Body

```json
{
  "type": "https://api.example.com/problems/version-retired",
  "title": "API Version Retired",
  "status": 410,
  "detail": "The v1 Orders API was retired on 2025-08-01. Migrate to v2: https://developer.example.com/migration/v1-to-v2",
  "instance": "/v1/orders"
}
```

## Pitfalls

- Retiring silently with no `Deprecation`/`Sunset` headers — consumers discover the breakage in production
- Setting a sunset date under 90 days — not enough time for enterprise consumers with release cycles
- Removing the deprecated endpoint before traffic reaches zero — check the gates
- Forgetting to update auto-generated SDKs — client libraries that call the old URL break on sunset even if the docs are updated
- Announcing by email alone — developer portal + headers + changelog are the durable channels; email bounces

## See Also

- [`../../agents/api-platform-engineer.md`](../../agents/api-platform-engineer.md) — developer portal, SDK/codegen, and lifecycle management
- [`../../agents/api-design-architect.md`](../../agents/api-design-architect.md) — versioning strategy and breaking-change classification
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: version only for breaking changes; deprecate on a clock
