---
name: stream-processing
description: "Process streams correctly: aggregate on event-time with watermarks (not processing-time), window deliberately (tumbling/sliding/session), handle late data explicitly, checkpoint and TTL-bound state, join with aligned time, and design for backpressure."
---

# Stream Processing

## Event-time + watermarks
Aggregate on the event's timestamp; a **watermark** closes windows correctly. Processing-time breaks on late/out-of-order events.

## Windows
Tumbling (fixed) / sliding (overlapping) / session (activity gap) — the window IS the question.

## Late data
Allowed lateness + side output, or accept the drop — **never silently** lose late events.

## State & backpressure
Checkpoint stateful operators; **TTL-bound** state (unbounded = OOM). Joins align event-time + hold state. Handle backpressure; monitor consumer **lag** -> observability-sre.
