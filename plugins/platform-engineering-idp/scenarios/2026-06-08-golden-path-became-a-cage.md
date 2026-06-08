---
scenario_id: 2026-06-08-golden-path-became-a-cage
contributed_at: 2026-06-08
plugin: platform-engineering-idp
product: generic
product_version: "unknown"
scope: likely-general
tags: [golden-path, escape-hatch, shadow-platform, paved-road]
confidence: high
reviewed: false
---

## Problem

A platform team's golden path for services was strict by design — a single supported runtime, a fixed
deploy manifest, no way to override the defaults. It worked for the common case, but three product
teams with legitimate needs (a GPU workload, a latency-sensitive service needing a different runtime,
a team with a regulatory data-residency constraint) couldn't use it. Instead of asking, they quietly
built their own deploy tooling. The platform team discovered three **shadow platforms** during an
incident when one of them paged the wrong on-call.

## Context

- The path forbade deviation: there was no documented "off-road" mode, so stepping off meant fully
  rolling your own — including re-implementing CI, observability, and secrets handling badly.
- The platform team had treated deviation as non-compliance, so teams hid it rather than surfacing it.
- The hidden tooling had none of the baked-in security baseline or observability the path provided.

## Attempts

- Considered: tightening enforcement (block all non-path deploys). Rejected — it would push the shadow
  platforms deeper and break three teams with genuine needs.
- Tried: adding a documented **escape hatch** per the **pave-the-80 / keep-an-escape-hatch** rule —
  stepping off the road became explicitly allowed and unsupported, with the baked-in security
  baseline + observability still available as opt-in modules even off-road.
- Tried (the move that worked): treated the recurring escapes as a **signal to pave variants**. The
  GPU workload and the alternate-runtime need each recurred enough to justify a new supported variant
  of the path; the data-residency case stayed a documented escape. The shadow tooling was retired
  because the supported variants were now easier.

## Resolution

**A golden path with no escape hatch becomes a cage, and a cage breeds shadow platforms you can't see
or secure.** The fix wasn't more enforcement — it was an explicit escape hatch plus paving the
recurring escapes into supported variants. Visibility returned because deviation was no longer
punished, and the security/observability baseline reached the teams that had been hiding.

**Action for the next engineer:** never ship a paved road without a documented, allowed-but-unsupported
escape hatch, and instrument escapes so recurring ones become new variants. Cross-reference
[`../best-practices/pave-the-80-keep-an-escape-hatch.md`](../best-practices/pave-the-80-keep-an-escape-hatch.md)
and [`../best-practices/a-recurring-escape-is-a-signal-to-pave-a-variant.md`](../best-practices/a-recurring-escape-is-a-signal-to-pave-a-variant.md).

**Sources:** Pattern-level field note; no product-version-specific claims. Team/workload specifics are
illustrative.
