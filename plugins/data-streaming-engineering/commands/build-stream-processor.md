---
description: "Build a correct stream processing job: event-time windowing with watermarks, late-data handling, bounded state, backpressure."
argument-hint: "[processing logic + symptom]"
---

You are running `/data-streaming-engineering:build-stream-processor`. Use `stream-processing-engineer` + the `stream-processing` skill.

## Steps
1. Use event-time + watermarks; choose the window type by the question.
2. Handle late data explicitly (allowed lateness + side output).
3. Checkpoint + TTL-bound state; align joins on event-time.
4. Plan backpressure; wire consumer-lag monitoring to observability-sre.
5. Emit (from `templates/stream-processing-job.md`) + Structured Output block.
