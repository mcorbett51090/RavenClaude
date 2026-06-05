# Use Lambda Powertools for structured, correlated Lambda logs

**Status:** Pattern
**Domain:** AWS Lambda / observability
**Applies to:** `aws-cloud`

---

## Why this exists

Unstructured Lambda logs (`print("processing event")`) are unsearchable at scale. CloudWatch Logs Insights can query structured JSON natively, but you have to emit JSON to get the benefit. Lambda Powertools (Python, TypeScript, Java, .NET) adds structured logging, X-Ray tracing, and correlation IDs in one dependency — without which every Lambda function reinvents its own logging shape and request correlation breaks across async chains.

## How to apply

Install the Lambda Powertools layer or package for your runtime, then use the `Logger` utility.

```python
# Python example — Lambda handler with Powertools Logger
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger(service="order-processor")
tracer = Tracer(service="order-processor")

@logger.inject_lambda_context(correlation_id_path="headers.x-correlation-id")
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    order_id = event["order_id"]
    logger.info("Processing order", extra={"order_id": order_id})
    # ... processing ...
    logger.info("Order processed", extra={"order_id": order_id, "status": "complete"})
    return {"statusCode": 200}
```

This emits structured JSON:
```json
{
  "level": "INFO",
  "message": "Processing order",
  "service": "order-processor",
  "correlation_id": "abc-123",
  "order_id": "ord-456",
  "cold_start": true,
  "xray_trace_id": "1-..."
}
```

Then query it in CloudWatch Logs Insights:
```
fields @timestamp, message, order_id, correlation_id
| filter service = "order-processor" and level = "ERROR"
| sort @timestamp desc
```

**Do:**
- Set the `service` name consistently across all functions in a workload.
- Use `inject_lambda_context` to capture cold-start flag, request ID, and correlation IDs automatically.
- Pass `correlation_id_path` to thread a caller-supplied ID through async chains.
- Enable X-Ray active tracing (`xray_trace_id` appears automatically with Tracer).

**Don't:**
- Mix structured and unstructured logging in the same function — Insights patterns break.
- Log entire raw events at INFO level (PII exposure + high ingestion cost); log only the identifying fields.
- Skip the `service` field — it's the primary grouping key in Insights queries.

## Edge cases / when the rule does NOT apply

- **Very small/throwaway scripts** (e.g., one-time data fixup Lambda) where structured logs add no debugging value.
- **Non-Python/TypeScript runtimes without a Powertools port** — roll a thin JSON-logging wrapper that emits the same fields; the structured JSON requirement stands.

## See also

- [`../agents/aws-ops-finops-engineer.md`](../agents/aws-ops-finops-engineer.md) — owns observability design including Lambda tracing.
- [`./cloudwatch-alarms-not-just-dashboards.md`](./cloudwatch-alarms-not-just-dashboards.md) — alarms are most useful when logs are structured and queryable.

## Provenance

Codifies the observability guidance in `aws-ops-finops-engineer`'s remit ("CloudWatch/X-Ray observability hooks") grounded in Lambda Powertools documentation and the AWS Well-Architected Operational Excellence pillar. Structured JSON logging is the prerequisite for meaningful CloudWatch Logs Insights queries.

---

_Last reviewed: 2026-06-05 by `claude`_
